import os
import pandas as pd
from collections import OrderedDict


class WebTabExc(Exception):
    def __init__(self):
        Exception.__init__(self, "Invalid tab; missing chart properties")


class ChartProperties(object):
    """
    """
    def __init__(self, plot_type="", subtitle="", x_label="", x_value="",
        y_label="", y_value="", lower_quartile="", upper_quartile="", mean="",
        value="", label="", minimum="", maximum="", min_color="", mid_color="",
        max_color="", step=10, zones=[], label_color=""):
        self.type = plot_type
        self.subtitle = subtitle
        self.x_label = x_label
        self.x_value = x_value
        self.y_label = y_label
        self.y_value = y_value
        self.lower_quartile = lower_quartile
        self.upper_quartile = upper_quartile
        self.mean = mean
        self.value = value
        self.label = label
        self.min = minimum
        self.max = maximum
        self.min_color = min_color
        self.mid_color = mid_color
        self.max_color = max_color
        self.step = step
        self.zones = zones
        self.label_color = label_color

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
        od["type"] = self.type
        if self.subtitle:
            od["subtitle"] = self.subtitle
        if self.x_label:
            od["x_label"] = self.x_label
        if self.x_value:
            od["x_value"] = self.x_value
            if not self.x_label:
                od["x_label"] = self.x_value
        if self.y_label:
            od["y_label"] = self.y_label
        if self.y_value:
            od["y_value"] = self.y_value
            if not self.y_label:
                od["y_label"] = self.y_value[0]
        if self.lower_quartile:
            od["lower_quartile"] = self.lower_quartile
        if self.upper_quartile:
            od["upper_quartile"] = self.upper_quartile
        if self.mean:
            od["mean"] = self.mean
        if self.value:
            od["value"] = self.value
        if self.label:
            od["label"] = self.label
        if self.min:
            od["min"] = self.min
        if self.max:
            od["max"] = self.max
        if self.min_color:
            od["min_color"] = self.min_color
        if self.mid_color:
            od["mid_color"] = self.mid_color
        if self.max_color:
            od["max_color"] = self.max_color
        if self.step:
            if self.type == "histogram":
                od["step"] = self.step
        if self.zones:
            if self.type == "arearange":
                od["zones"] = self.zones
        if self.label_color:
            od["label_color"] = self.label_color
        return od


class WebTab(object):
    def __init__(self, filename, tab_name="", status="", chart_properties=None):
        """The object defining a tab in the left pane of the dashboard.

        Args:
            filename (list): the read index and read index + basename of each file
            tab_name (Optional[str]): the string displayed in the left tab on the web page
            status (Optional[str]): tab status -- pass, fail, or warn
            chart_properties (Optional[str]): ChartProperties object for this tab
        """
        self.filename = filename
        self.tab_name = tab_name
        self.status = status
        if chart_properties is None:
            self.chart_properties = ChartProperties()
        else:
            self.chart_properties = chart_properties

    def update_status(self, status):
        """Updates status to worse condition of either R1 and R2."""
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
        # list as filename
        if isinstance(self.filename, list):
            # paired-end
            if isinstance(self.filename[0], list):
                od["filename"] = self.filename
            # single-end; just need the filename
            else:
                od["filename"] = self.filename[1]
        # string as filename
        else:
            od["filename"] = self.filename
        if self.tab_name:
            od["tab_name"] = self.tab_name
        else:
            od["tab_name"] = "Unnamed Tag"
        if self.status:
            od["status"] = self.status
        if self.chart_properties:
            od["chart_properties"] = self.chart_properties.to_dict()
        else:
            raise WebTabExc
        return od

    def combine_tables(self, out_dir, **kwargs):
        """Combines files from R1 and R2 directory of the same name into a single file written
        into the parent directory.

        Args:
            out_dir (str): the base output directory for a uid

        Kwargs:
            pandas.DataFrame.to_csv kwargs
        """
        dfa = pd.read_csv(os.path.join(out_dir, self.filename[0][1]),
                          header=0, names=[self.chart_properties.x_value, "R1"],
                          index_col=self.chart_properties.x_value)
        dfb = pd.read_csv(os.path.join(out_dir, self.filename[1][1]),
                          header=0, names=[self.chart_properties.x_value, "R2"],
                          index_col=self.chart_properties.x_value)
        merged = pd.merge(dfa, dfb, how="outer", left_index=True, right_index=True)
        # output is malformed when users have short, non-grouped R1 read lengths and grouped R2 read lengths
        merged.to_csv(os.path.join(out_dir, os.path.basename(self.filename[0][1])), na_rep="0", **kwargs)
        # gets converted to string later
        self.filename = ["R1", os.path.basename(self.filename[0][1])]
