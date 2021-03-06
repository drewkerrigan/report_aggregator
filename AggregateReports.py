import sys, re
from BashoBenchAggregator import BashoBenchAggregator
from MdcAggregator import MdcAggregator 

def bb_filename(filename):
    AUTHmatchObj = re.match( r'(.*)\/(.*)_(.*)-auth-(.*)_(.*)\/(.*)\/(.*)\/(.*)_latencies.csv', filename, re.M|re.I)
    matchObj = re.match( r'(.*)\/(.*)_(.*)-(.*)-(.*)\/(.*)\/(.*)\/(.*)_latencies.csv', filename, re.M|re.I)
    AAEmatchObj = re.match( r'(.*)\/(.*)_(.*)-(.*)-(.*)_(.*_.*)\/(.*)\/(.*)\/(.*)_latencies.csv', filename, re.M|re.I)
    
    if AUTHmatchObj:
        test_type = AUTHmatchObj.group(2)
        protocol = AUTHmatchObj.group(3)
        version = AUTHmatchObj.group(4)
        backend = "bitcask"
        test_group = AUTHmatchObj.group(5)
        cluster = AUTHmatchObj.group(6)
        timestamp = AUTHmatchObj.group(7)
        operation = AUTHmatchObj.group(8)
    elif AAEmatchObj:
        test_type = AAEmatchObj.group(2)
        protocol = AAEmatchObj.group(3)
        version = AAEmatchObj.group(4)
        backend = AAEmatchObj.group(5)
        test_group = AAEmatchObj.group(6)
        cluster = AAEmatchObj.group(7)
        timestamp = AAEmatchObj.group(8)
        operation = AAEmatchObj.group(9)
    elif matchObj:
        test_type = matchObj.group(2)
        protocol = matchObj.group(3)
        version = matchObj.group(4)
        backend = matchObj.group(5)
        test_group = ""
        cluster = matchObj.group(6)
        timestamp = matchObj.group(7)
        operation = matchObj.group(8)
    
    if (cluster == "tag_RiakServers_cluster1"):
        cluster = "AWS"
    elif (cluster == "slsmallriakservers"):
        cluster = "SLsm"
    elif (cluster == "slnewsmallriakservers"):
        cluster = "SLsm2"
    else:
        cluster = "SLmd"
        
    if test_group != "":
        version = version + "_" + test_group
        
    if (matchObj or AAEmatchObj):
        return "[" + cluster + "] " + test_type + " " + protocol + "." + backend + "." + operation + " (" + version + ") TS:" + timestamp
    else:
        return filename

def mdc_filename(filename):
    matchObj = re.match( r'(.*)\/(.*)-(.*)-(.*)_(.*)\/(.*)\/(.*)\/mdc_results.csv', filename, re.M|re.I)
    if matchObj:
        if (matchObj.group(6) == "aws_benchmark"):
            cluster = "AWS"
        else:
            cluster = "SL"
            
        return "[" + cluster + "] functionality_mdc-repl_" + matchObj.group(5) + " (" + matchObj.group(4) + ") TS:" + matchObj.group(7)
    else:
        return filename
    
def bb_latency_summary(rows, stat):
    s_rows = {}

    for row in sorted(rows.iterkeys()):
        if (row.rfind('rollup') >= 0):
            name = row[:row.rfind(' (')]
            if name not in s_rows.keys():
                s_rows[name] = {'121': '','13rc2': '','13rc4aoff': '','13rc4aon': ''}
            if (row.rfind(' (1.2.1)') >= 0):
                s_rows[name]['121'] = rows[row][stat]
            elif (row.rfind(' (1.3rc2') > 0):
                s_rows[name]['13rc2'] = rows[row][stat]
            elif (row.rfind(' (1.3)') > 0 or row.rfind(' (1.3rc4_AAE_OFF') > 0):
                s_rows[name]['13rc4aoff'] = rows[row][stat]
            elif (row.rfind(' (1.3rc4_AAE_ON') > 0):
                s_rows[name]['13rc4aon'] = rows[row][stat]
    
    print "Name,1.2.1,1.3rc2,1.3rc4,1.3rc4 AAE"
    
    for s_row in sorted(s_rows.iterkeys()):
        print s_row + ',' + str(s_rows[s_row]['121']) + ',' + str(s_rows[s_row]['13rc2']) + ',' + str(s_rows[s_row]['13rc4aoff']) + ',' + str(s_rows[s_row]['13rc4aon'])

results_base_dir = sys.argv[1]

bb_report = BashoBenchAggregator(results_base_dir + "/*/*/*/*latencies.csv", bb_filename, ' TS:')
bb_report.render()

print " "
print "Latency"
bb_latency_summary(bb_report.rows(), 'mean')

print " "
print "Ops/Sec"
bb_latency_summary(bb_report.rows(), 'mean_ops/sec')

print " "
print "MDC"

mdc_report = MdcAggregator(results_base_dir + "/*/*/*/mdc_results.csv", mdc_filename, ' TS:')
mdc_report.render()
    