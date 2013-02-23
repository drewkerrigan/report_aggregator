import sys, re
from BashoBenchAggregator import BashoBenchAggregator
from MdcAggregator import MdcAggregator 

def bb_filename(filename):
    matchObj = re.match( r'(.*)\/(.*)_(.*)-(.*)-(.*)\/(.*)\/(.*)\/(.*)_latencies.csv', filename, re.M|re.I)
    
    if matchObj:
        if (matchObj.group(6) == "tag_RiakServers_cluster1"):
            cluster = "AWS"
        elif (matchObj.group(6) == "slsmallriakservers"):
            cluster = "SLsm"
        else:
            cluster = "SLmd"
 
        return "[" + cluster + "] " + matchObj.group(2) + " " + matchObj.group(3) + "." + matchObj.group(5) + "." + matchObj.group(8) + " (" + matchObj.group(4) + ") TS:" + matchObj.group(7)
    else:
        return filename

def mdc_filename(filename):
    matchObj = re.match( r'(.*)\/(.*)-(.*)-(.*)\/aws_benchmark\/(.*)\/mdc_results.csv', filename, re.M|re.I)
    if matchObj:
        return "[AWS] functionality_mdc-repl (" + matchObj.group(4) + ") TS:" + matchObj.group(5)
    else:
        return filename
    
def bb_latency_summary(rows):
    s_rows = {}
    
    for row in sorted(rows.iterkeys()):
        if (row.rfind('rollup') >= 0):
            name = row[:row.rfind(' (')]
            if name not in s_rows.keys():
                s_rows[name] = {'121': '','13': ''}
            if (row.rfind(' (1.2.1') >= 0):
                s_rows[name]['121'] = rows[row]['mean']
            elif (row.rfind(' (1.3') > 0):
                s_rows[name]['13'] = rows[row]['mean']
    
    print "Name,1.2.1 Mean Latency,1.3 Mean Latency"
    
    for s_row in sorted(s_rows.iterkeys()):
        print s_row + ',' + str(s_rows[s_row]['121']) + ',' + str(s_rows[s_row]['13']) 

results_base_dir = sys.argv[1]

bb_report = BashoBenchAggregator(results_base_dir + "/*/*/*/*latencies.csv", bb_filename, ' TS:')
bb_report.render()

print " "

bb_latency_summary(bb_report.rows())

print " "
print "MDC"

mdc_report = MdcAggregator(results_base_dir + "/*/*/*/mdc_results.csv", mdc_filename, ' TS:')
mdc_report.render()
    