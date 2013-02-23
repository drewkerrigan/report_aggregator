import csv
from ReportAggregator import ReportAggregator
    
class BashoBenchAggregator(ReportAggregator):
    
    def build_row_dicts(self, filename):
        row_dict = self._build_row_dict()
    
        with open(filename, 'rb') as summary_file:
            reader = csv.reader(summary_file)
            reader.next()
    
            for row in reader:
                row = map(str.strip, row)
                vals = map(float, row)
                elapsed, window, n, minimum, mean, median, nine5, nine9, nine9_9, maximum, errors = vals[:11]
                row_dict['elapsed'].add(elapsed)
                row_dict['n'].add(n)
                row_dict['min'].add(minimum/1000)
                row_dict['mean'].add(mean/1000)
                row_dict['median'].add(median/1000)
                row_dict['95'].add(nine5/1000)
                row_dict['99'].add(nine9/1000)
                row_dict['99.9'].add(nine9_9/1000)
                row_dict['max'].add(maximum/1000)
                row_dict['errors'].add(errors)
                row_dict['ops/sec'].add(n/window)
                
        return row_dict

    def process_row(self, row):
        new_row_dict = {}
        new_row_dict['elapsed'] = row['elapsed'].max()
        new_row_dict['n'] = row['n'].sum_values()
        new_row_dict['min'] = row['min'].min()
        new_row_dict['mean'] = row['mean'].mean()
        new_row_dict['mean_std_dev'] = row['mean'].stdev()
        new_row_dict['median'] = row['median'].median()
        new_row_dict['95'] = row['95'].mean()
        new_row_dict['99'] = row['99'].mean()
        new_row_dict['99.9'] = row['99.9'].mean()
        new_row_dict['max'] = row['max'].max()
        new_row_dict['errors'] = row['errors'].sum_values()
        new_row_dict['mean_ops/sec'] = row['ops/sec'].mean()
        new_row_dict['mean_ops/sec_std_dev'] = row['ops/sec'].stdev()
        return new_row_dict
    
    def columns(self):
        return ['elapsed','n','min','mean','mean_std_dev','median','95','99','99.9','max','errors','mean_ops/sec','mean_ops/sec_std_dev']
    
    def file_columns(self):
        return ['elapsed','n','min','mean','median','95','99','99.9','max','errors','ops/sec']