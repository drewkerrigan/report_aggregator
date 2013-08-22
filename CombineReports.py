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
                stats_arr[i][0] = (stats_arr[i][0] + float(elapsed)) / 2
                stats_arr[i][1] = (stats_arr[i][1] + window) / 2
                stats_arr[i][2] = int(stats_arr[i][2] + n)
                stats_arr[i][3] = int(min(stats_arr[i][3], minimum))
                stats_arr[i][4] = (stats_arr[i][4] + mean) / 2
                stats_arr[i][5] = int((stats_arr[i][5] + median) / 2)
                stats_arr[i][6] = int((stats_arr[i][6] + nine5) / 2)
                stats_arr[i][7] = int((stats_arr[i][7] + nine9) / 2)
                stats_arr[i][8] = int((stats_arr[i][8] + nine9_9) / 2)
                stats_arr[i][9] = int(max(stats_arr[i][9], maximum))
                stats_arr[i][10] = int(stats_arr[i][10] + errors)
            
            i += 1
            
    return stats_arr

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
                stats_arr[i][0] = (stats_arr[i][0] + float(elapsed)) / 2
                stats_arr[i][1] = (stats_arr[i][1] + window) / 2
                stats_arr[i][2] = int(stats_arr[i][2] + total)
                stats_arr[i][3] = int(stats_arr[i][3] + successful)
                stats_arr[i][4] = int(stats_arr[i][4] + failed)
            
            i += 1
            
    return stats_arr

parser = argparse.ArgumentParser(description='Combine basho_bench results into a single directory')
parser.add_argument('-i', '--input', dest='inputs', nargs='+',
                   help='list of basho bench result directories')

parser.add_argument('-o', '--output', dest='output',
                   help='result directory')

args = parser.parse_args()

if not os.path.exists(args.output):
    os.makedirs(args.output)

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
    f = open(args.output + "/" + latency_name, 'w+')
    f.write("elapsed, window, n, min, mean, median, 95th, 99th, 99_9th, max, errors\n")
    for row in latency_dict[latency_name]:
        f.write(','.join(map(str,row)) + '\n')
    f.close

# #Write Summary
summary_arr = []
for directory in args.inputs:
    summary_arr = build_summary(summary_arr, directory + '/summary.csv')
    
f = open(args.output + '/summary.csv', 'w')
f.write("elapsed, window, total, successful, failed\n")
for row in summary_arr:
    f.write(','.join(map(str,row)) + '\n')
f.close