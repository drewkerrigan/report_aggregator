#!/usr/bin/env python
import sys, csv, glob, re
    
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

results_base_dir = sys.argv[1]

latency_dict = {}
for latency_file in glob.glob(results_base_dir + "/*/*latencies.csv"):
    matchObj = re.match( r'(.*)\/(.*)\/(.*)', latency_file, re.M|re.I)
    if matchObj:
        latency_dict[matchObj.group(3)] = []

#Write Latencies
for latency_name in latency_dict:
    for latency_file in glob.glob(results_base_dir + "/*/" + latency_name):
        stats_arr = build_latencies(latency_dict[latency_name], latency_file)
    
    f = open(latency_name, 'w')
    f.write("elapsed, window, n, min, mean, median, 95th, 99th, 99_9th, max, errors\n")
    for row in stats_arr:
        f.write(','.join(map(str,row)) + '\n')
    f.close

#Write Summary
stats_arr = []
for stat_file in glob.glob(results_base_dir + "/*/summary.csv"):
    stats_arr = build_summary(stats_arr, stat_file)
    
f = open('summary.csv', 'w')
f.write("elapsed, window, total, successful, failed\n")
for row in stats_arr:
    f.write(','.join(map(str,row)) + '\n')
f.close