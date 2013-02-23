import glob
from operator import itemgetter

class SummaryStat:
    def __init__(self):
        self.reset()

    def add(self, value):
        if value not in self.values:
            self.values[value] = 1
        else:
            self.values[value] += 1
        self.count += 1

    def add_many(self, values):
        for value in values:
            self.add(value)

    def add_dict(self, dict_values):
        self.values = dict_values.copy()
        self.count = sum(dict_values.values())

    def add_summary(self, summary):
        for key in summary.values:
            bucket = self.values.get(key, 0)
            bucket += summary.values[key]
            self.values[key] = bucket
            self.count += summary.values[key]

    def reset(self):
        self.values = {}
        self.count = 0

    def spread(self):
        return min(self.values.keys()), max(self.values.keys())

    def sum_values(self):
        return sum([value * count for  value, count in self.values.items()])

    def min(self):
        return min(self.values.keys())

    def max(self):
        return max(self.values.keys())

    def mean(self):
        numerator = self.sum_values()
        return float(numerator)/float(self.count)

    def median(self):
        center = self.count/2
        values = []
        for key, value in self.values.items():
            values.extend([key] * value)
        return sorted(values)[center]

    def variance(self):
        mu = self.mean()
        s = 0
        for value, count in self.values.items():
            s += ((value-mu)**2)*count
        return float(s)/(self.count-1)

    def stdev(self):
        return self.variance()**.5

    def modes(self):
        return sorted(self.values.items(), key=itemgetter(1), reverse=True)

    def histogram(self):
        return self.values

    def pmf(self):
        pmf = {}
        for value in self.values:
            pmf[value] = float(self.values[value]) / float(self.count)
        return pmf

    def hist_range(self, start, stop, hist=None):
        if not hist:
            hist = self.values.copy()
        else:
            hist = hist.copy()
        keys = range(start, stop + 1)
        for key in keys:
            if key not in hist:
                hist[key] = 0
        return hist

    def pmf_range(self, start, stop):
        return self.hist_range(start, stop, hist=self.pmf())

    def cdf(self, hist=None):
        cdf_hist = {}
        total = 0
        if not hist:
            hist = self.values

        for key in sorted(hist.keys()):
            total += hist[key] * key
            cdf_hist[key] = total
        return cdf_hist

    def cdf_range(self, start, stop):
        hist = self.hist_range(start, stop)
        return self.cdf(hist)

class ReportAggregator():
    _rows = None
    _glob_path = None
    _rollup_filter = None
    _filename_fun = None
    
    def __init__(self, glob_path, filename_fun = None, rollup_filter = None):
        self._glob_path = glob_path
        self._filename_fun = filename_fun
        self._rollup_filter = rollup_filter

    def _build_row_dict(self):
        row_dict = {}

        for field in self.file_columns():
            row_dict[field] = SummaryStat()
            
        return row_dict

    def rows(self):
        if self._rows != None:
            return self._rows
        
        self._rows = {}
        row_dicts = {}

        for stat_file in glob.glob(self._glob_path):
            name = stat_file
            
            if(self._filename_fun != None):
                name = self._filename_fun(name)
                
            row_dicts[name] = self.build_row_dicts(stat_file)

        if self._rollup_filter != None:
            row_dicts = dict(row_dicts.items() + self.rollup(row_dicts).items())

        for name in row_dicts:
            self._rows[name] = self.process_row(row_dicts[name])
            
        return self._rows
    
    def rollup(self, rows):
        rollup = {}
        
        for row in rows:
            ind = row.rfind(self._rollup_filter)
            name = "rollup " + row[:ind]
            
            if name not in rollup.keys():
                rollup[name] = self._build_row_dict()
            
            for field in self.file_columns():
                for val in rows[row][field].values:
                    rollup[name][field].add(val)

        return rollup

    def render(self):
        print 'name,' + ','.join(self.columns())
        rows = self.rows()
        for row in sorted(rows.iterkeys()):
            print row + ',' + ','.join([str(rows[row][key]) for key in self.columns()])