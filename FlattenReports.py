#!/usr/bin/env python
import os, sys, csv, glob, re, argparse
    
def build_latencies(stats_arr, filename):
    i = 0

    with open(filename, 'rb') as summary_file:
        reader = csv.reader(summary_file)
        reader.next() #skip header line

        for row in reader:
            row = map(str.strip, row)
            vals = map(float, row)
            elapsed, window, n, minimum, mean, median, nine5, nine9, nine9_9, maximum, errors = vals[:11]
            
            if len(stats_arr) <= i:
                stats_arr.append([elapsed, window, n, minimum, mean, median, nine5, nine9, nine9_9, maximum, errors])
            else: 
                stats_arr[i][0] = int(max(stats_arr[i][0], float(elapsed)))
                stats_arr[i][1] = (stats_arr[i][1] + window)
                stats_arr[i][2] = int(stats_arr[i][2] + n)
                stats_arr[i][3] = int(min(stats_arr[i][3], minimum))
                stats_arr[i][4] = (stats_arr[i][4] + mean)
                stats_arr[i][5] = int((stats_arr[i][5] + median))
                stats_arr[i][6] = int((stats_arr[i][6] + nine5))
                stats_arr[i][7] = int((stats_arr[i][7] + nine9))
                stats_arr[i][8] = int((stats_arr[i][8] + nine9_9))
                stats_arr[i][9] = int(max(stats_arr[i][9], maximum))
                stats_arr[i][10] = int(stats_arr[i][10] + errors)

            i += 1

    return stats_arr

def flatten_latencies(stats_arr, num_reports):
    flat_arr = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    for i in range(0, len(stats_arr)):
        flat_arr[0] = int(max(stats_arr[i][0], flat_arr[0]))
        flat_arr[1] += stats_arr[i][1]
        flat_arr[2] += stats_arr[i][2]
        flat_arr[3] = int(min(stats_arr[i][3], flat_arr[3]))
        flat_arr[4] += stats_arr[i][4]
        flat_arr[5] += stats_arr[i][5]
        flat_arr[6] += stats_arr[i][6]
        flat_arr[7] += stats_arr[i][7]
        flat_arr[8] += stats_arr[i][8]
        flat_arr[9] = int(max(stats_arr[i][9], flat_arr[9]))
        flat_arr[10] += stats_arr[i][10]

    print flat_arr

    flat_arr[1] = flat_arr[1] / num_reports
    flat_arr[4] = flat_arr[4] / len(stats_arr) / num_reports
    flat_arr[5] = flat_arr[5] / len(stats_arr) / num_reports
    flat_arr[6] = flat_arr[6] / len(stats_arr) / num_reports
    flat_arr[7] = flat_arr[7] / len(stats_arr) / num_reports
    flat_arr[8] = flat_arr[8] / len(stats_arr) / num_reports

    return flat_arr

def build_summary(stats_arr, filename):
    i = 0

    with open(filename, 'rb') as summary_file:
        reader = csv.reader(summary_file)
        reader.next() #skip header line

        for row in reader:
            row = map(str.strip, row)
            vals = map(float, row)
            elapsed, window, total, successful, failed = vals[:5]
            
            if len(stats_arr) <= i:
                stats_arr.append([elapsed, window, total, successful, failed])
            else:
                stats_arr[i][0] = stats_arr[i][0] + float(elapsed)
                stats_arr[i][1] = stats_arr[i][1] + window
                stats_arr[i][2] = int(stats_arr[i][2] + total)
                stats_arr[i][3] = int(stats_arr[i][3] + successful)
                stats_arr[i][4] = int(stats_arr[i][4] + failed)
            
            i += 1

    return stats_arr

def flatten_summary(stats_arr, num_reports):
    flat_arr = [0, 0, 0, 0, 0]

    for i in range(0, len(stats_arr)):
        flat_arr[0] += stats_arr[i][0]
        flat_arr[1] += stats_arr[i][1]
        flat_arr[2] += stats_arr[i][2]
        flat_arr[3] += stats_arr[i][3]
        flat_arr[4] += stats_arr[i][4]

    flat_arr[0] = flat_arr[0] / len(stats_arr) / num_reports
    flat_arr[1] = flat_arr[1] / len(stats_arr) / num_reports
            
    return flat_arr

parser = argparse.ArgumentParser(description='Combine basho_bench results into a single directory')
parser.add_argument('-i', '--input', dest='inputs', nargs='+',
                   help='list of basho bench result directories')

# parser.add_argument('-o', '--output', dest='output',
#                    help='result directory')

args = parser.parse_args()

# if not os.path.exists(args.output):
#     os.makedirs(args.output)

latency_dict = {}

for directory in args.inputs:
    for latency_file in glob.glob(directory + "/*latencies.csv"):
        matchObj = re.match( r'(.*)\/(.*latencies.csv)', latency_file, re.M|re.I)
        if matchObj:
            if matchObj.group(2) not in latency_dict:
                latency_dict[matchObj.group(2)] = []
            latency_dict[matchObj.group(2)] = build_latencies(latency_dict[matchObj.group(2)], latency_file)

#Write Latencies
for latency_name in latency_dict:
    print latency_name
    print "elapsed, window, n, min, mean, median, 95th, 99th, 99_9th, max, errors"
    print (','.join(map(str,flatten_latencies(latency_dict[latency_name], len(args.inputs)))))

# #Write Summary
summary_arr = []
for directory in args.inputs:
    summary_arr = build_summary(summary_arr, directory + '/summary.csv')
    
print "\nsummary.csv"
print "elapsed, window, total, successful, failed"
print (','.join(map(str,flatten_summary(summary_arr, len(args.inputs)))))