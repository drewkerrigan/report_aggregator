import csv
from ReportAggregator import ReportAggregator
    
class MdcAggregator(ReportAggregator):    
    def build_row_dicts(self, filename):
        row_dict = self._build_row_dict()
        
        with open(filename, 'rb') as summary_file:
            reader = csv.reader(summary_file)
            for row in reader:
                row_dict['elapsed'].add(float(row[0]))
        
        return row_dict

    def process_row(self, row):
        new_row_dict = {}
        new_row_dict['elapsed'] = row['elapsed'].mean()
        return new_row_dict
    
    def columns(self):
        return ['elapsed']
    
    def file_columns(self):
        return self.columns()