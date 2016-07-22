import os
import pandas as pd
from collections import OrderedDict


class WebTabExc(Exception):
    def __init__(self):
        Exception.__init__(self, "Invalid tab; missing chart properties")


class ChartProperties(object):
    """
    type heatmap, plateheatmap, line, table, arearange
    shape circle square
    """
    def __init__(self, plot_type="", subtitle="", x_label="", x_value="", y_label="", y_value="",
        lower_percentile="", lower_quartile="", upper_percentile="", upper_quartile="",
        median="", mean="", shape="", value="", label="", minimum="", maximum="", min_color="",
        mid_color="", max_color=""):
        self.type = plot_type
        self.subtitle = subtitle
        self.x_label = x_label
        self.x_value = x_value
        self.y_label = y_label
        self.y_value = y_value
        self.lower_percentile = lower_percentile
        self.lower_quartile = lower_quartile
        self.upper_percentile = upper_percentile
        self.upper_quartile = upper_quartile
        self.median = median
        self.mean = mean
        self.shape = shape
        self.value = value
        self.label = label
        self.min = mininum
        self.max = maximum
        self.min_color = min_color
        self.mid_color = mid_color
        self.max_color = max_color

    def add_y_value(self, val):
        if self.y_value:
            if isinstance(self.y_value, list):
                self.y_value.append(val)
            else:
                self.y_value = [self.y_value, val]
        else:
            self.y_value = val

    def to_dict(self):
        # we want a static order; could be defined in __slots__
        od = OrderedDict()
        od['type'] = self.type
        if self.subtitle:
            od['subtitle'] = self.subtitle
        if self.x_label:
            od['x_label'] = self.x_label
        if self.x_value:
            od['x_value'] = self.x_value
        if self.y_label:
            od['y_label'] = self.y_label
        if self.y_value:
            od['y_value'] = self.y_value
        if self.lower_percentile:
            od['lower_percentile'] = self.lower_percentile
        if self.lower_quartile:
            od['lower_quartile'] = self.lower_quartile
        if self.upper_percentile:
            od['upper_percentile'] = self.upper_percentile
        if self.upper_quartile:
            od['upper_quartile'] = self.upper_quartile
        if self.median:
            od['median'] = self.median
        if self.mean:
            od['mean'] = self.mean
        if self.shape:
            od['shape'] = self.shape
        if self.value:
            od['value'] = self.value
        if self.label:
            od['label'] = self.label
        if self.min:
            od['min'] = self.min
        if self.max:
            od['max'] = self.max
        if self.min_color:
            od['min_color'] = self.min_color
        if self.mid_color:
            od['mid_color'] = self.mid_color
        if self.max_color:
            od['max_color'] = self.max_color
        return od


class WebTab(object):
    """
    filename should likely always be a list and then returned as a single item
    """
    def __init__(self, filename, tab_name="", status="", chart_properties=None):
        self.filename = filename
        self.tab_name = tab_name
        self.status = status
        if chart_properties is None:
            self.chart_properties = ChartProperties()
        else:
            self.chart_properties = chart_properties

    def update_status(self, status):
        if not self.status:
            self.status = status
        else:
            if "warn" in self.status and "fail" in status:
                self.status = "fail"
            elif "pass" in self.status and ("fail" in status or "warn" in status):
                self.status = status
            # else if was already "fail" and we don't update

    def to_dict(self):
        od = OrderedDict()
        # paired-end
        if isinstance(self.filename[0], list):
            od['filename'] = self.filename
        # single-end; just need the filename
        else:
            od['filename'] = self.filename[1]
        if self.tab_name:
            od['tab_name'] = self.tab_name
        else:
            od['tab_name'] = "Unnamed Tag"
        if self.status:
            od['status'] = self.status
        if self.chart_properties:
            od['chart_properties'] = self.chart_properties.to_dict()
        else:
            raise WebTabExc
        return od

    def combine_tables(self, out_dir, **kwargs):
        """Combines files from R1 and R2 directory of the same name into a single file written
        into the parent directory.

        Args:
            out_dir (str): the base output directory for a uid

        Kwargs:
            anything to pass to pandas.DataFrame
        """
        dfa = pd.read_csv(os.path.join(out_dir, self.filename[0][1]),
                          header=0, names=[self.chart_properties.x_value, 'R1'],
                          index_col=self.chart_properties.x_value)
        dfb = pd.read_csv(os.path.join(out_dir, self.filename[1][1]),
                          header=0, names=[self.chart_properties.x_value, 'R2'],
                          index_col=self.chart_properties.x_value)
        merged = pd.merge(dfa, dfb, how='outer', left_index=True, right_index=True)
        merged.to_csv(os.path.join(out_dir, os.path.basename(self.filename[0][1])), na_rep="0", **kwargs)
        # gets converted to string later
        self.filename = ['R1', os.path.basename(self.filename[0][1])]
