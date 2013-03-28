import sys, re
from BashoBenchAggregator import BashoBenchAggregator
from MdcAggregator import MdcAggregator 

def bb_filename(filename):
    matchObj = re.match( r'(.*)\/(.*)_latencies.csv', filename, re.M|re.I)

    if matchObj:
        return "op:" + matchObj.group(2) + " TS:" + matchObj.group(1)
    else:
        return filename

results_base_dir = sys.argv[1]

bb_report = BashoBenchAggregator(results_base_dir + "*latencies.csv", bb_filename, ' TS:')
bb_report.render()