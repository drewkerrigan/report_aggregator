report_aggregator
=================

This set of scripts was designed for aggregating large numbers of basho bench and other custom csv result files into a single csv file.

# Example Usage
## Download ReportAggregator and Results
```
git clone git://github.com/drewkerrigan/riak_benchmarking.git
git clone git://github.com/drewkerrigan/report_aggregator.git
```

## Generate New Results CSV:
```
cd report_aggregator
python AggregateReports.py ../riak_benchmarking/results > summary.csv
```
Check summary.csv for aggregated results

## For other directory structures
Use AggregateReports.py as an example and create your own name regex and directory structure. Here are the relevant bits:
```
def bb_filename(filename):
    matchObj = re.match( r'(.*)\/(.*)_latencies.csv', filename, re.M|re.I)
    
    if matchObj:
    	return "op:" + matchObj.group(2) + " TS:" + matchObj.group(1)
    else:
        return filename

bb_report = BashoBenchAggregator("your_timestamp/*latencies.csv", bb_filename, ' TS:')
bb_report.render()
```

This will generate a complete CSV with additional rollups by operation (portion of the name before ' TS:'). If you want to design a new aggregator for a different type of CSV file, use BashoBenchAggregator.py and MdcAggregator.py as an example.