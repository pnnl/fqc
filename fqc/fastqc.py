import io
import logging
import os
import pandas as pd
import shutil
import subprocess
import sys
import tempfile
import zipfile
from collections import OrderedDict
from distutils.spawn import find_executable
from fqc.tabs import WebTab, ChartProperties


FASTQC_EXE = "fastqc"


class Fastqc(object):
    """Runs FastQC across paired-end reads with the intended result being
    to get the QC data generated by FastQC.

    Args:
        uid (str): run ID or other unique identifier
        r1 (str): file path to R1 FASTQ file
        r2 (Optional[str]): file path to R2 FASTQ file
        out_dir (Optional[str]): output path
    """
    def __init__(self, gid, uid, r1, r2=None, out_dir="."):
        self.gid = gid
        self.uid = uid
        self.r1 = r1
        self.r2 = r2
        self.out_dir = os.path.join(os.path.abspath(out_dir), 'plot_data', gid, uid)
        self.tabs = OrderedDict()
        # data directories
        os.makedirs(self.out_dir, exist_ok=True)
        os.makedirs(os.path.join(self.out_dir, 'R1'), exist_ok=True)
        if r2:
            os.makedirs(os.path.join(self.out_dir, 'R2'), exist_ok=True)
        logging.info("Writing data to: %s" % self.out_dir)

    def __iter__(self):
        return iter(self.tabs)

    def out_archive(self, fastq):
        """Determines output file name of Zip archive based on input FASTQ name.

        Args:
            fastq (str): file path to FASTQ file

        Returns:
            str: path of FastQC created output archive
        """
        filename, ext = os.path.splitext(os.path.basename(fastq))
        if ext == ".gz":
            filename, ext = os.path.splitext(filename)
        elif ext == ".zip":
            return os.path.basename(fastq)
        if ext in [".fastq", ".fq"]:
            return filename + "_fastqc.zip"
        else:
            return filename + ext + "_fastqc.zip"

    def get_fastqc_data(self, temp_dir, archive):
        with zipfile.ZipFile(os.path.join(temp_dir, archive)) as zf:
            with zf.open(os.path.join(archive.rstrip(".zip"), "fastqc_data.txt")) as qcdata:
                for line in io.TextIOWrapper(qcdata):
                    yield line.strip()

    def file_and_status_from_metarow(self, name_and_status, read_index):
        """
        ['>>Sequence Length Distribution', 'pass']
        """
        filename = name_and_status[0].replace(" ", "_").strip(">>") + ".csv"
        filehandle = open(os.path.join(self.out_dir, read_index, filename), "w")
        # new tab
        if read_index == "R1":
            web_tab = WebTab([read_index, "R1/%s" % filename], status=name_and_status[1])
        # R2; look up existing tab and add filename
        else:
            assert(read_index == "R2")
            try:
                web_tab = self.tabs[filename]
                # list of lists
                web_tab.filename = [web_tab.filename, ["R2", "R2/%s" % filename]]
                # set status to worse of R1 and R2
                web_tab.update_status(name_and_status[1])
            # R2 has output that is missing from the analysis of R1
            except KeyError:
                # new tab, needs empty R1 plot tab
                web_tab = WebTab([["R1", "R1/%s" % filename], ["R2", "R2/%s" % filename]], status=name_and_status[1])

        return filename, filehandle, web_tab

    def extract_data(self, out_dir):
        """Extracts individual tables from FastQC output and writes tables to `self.out_dir`.
        Also generates the properties list for each individual plot.

        Args:
            out_dir (str): path to folder containing FastQC archive
        """
        logging.info("Extracting data from FastQC archives")

        fastqs = [self.r1, self.r2] if self.r2 else [self.r1]
        indexes = ['R1', 'R2'] if self.r2 else ['R1']

        for fastq, idx in zip(fastqs, indexes):
            logging.debug("Extracting data for FASTQ %s" % fastq)
            for line in self.get_fastqc_data(out_dir, self.out_archive(fastq)):
                # fastqc version info
                if line.startswith("##FastQC"): continue
                # close up the previous file
                if line.startswith(">>END_MODULE"):
                    if filehandle:
                        filehandle.close()
                    continue
                # RNA PCR Primer, Index 37 (95% over 23bp)
                line = line.replace(",", ";")
                # >>Per base sequence quality  pass
                toks = line.strip().split("\t")
                # >>Sequence Length Distribution  pass
                if line.startswith(">>"):
                    filename, filehandle, web_tab = self.file_and_status_from_metarow(toks, idx)
                    continue

                # process the headers
                elif line.startswith("#"):
                    toks[0] = toks[0].strip("#")
                    # Measure, Value
                    if filename == "Basic_Statistics.csv":
                        if "R1" in idx:
                            web_tab.tab_name = "Basic Statistics"
                            web_tab.chart_properties.type = "table"
                    # Base, Mean, Median, Lower Quartile, Upper Quartile, 10th Percentile, 90th Percentile
                    elif filename == "Per_base_sequence_quality.csv":
                        if "R1" in idx:
                            web_tab.tab_name = "Quality by Position"
                            web_tab.chart_properties = ChartProperties("arearange", x_label="Position", x_value=toks[0],
                                y_label="Quality (Phred score)", lower_quartile=toks[3], upper_quartile=toks[4],
                                mean=toks[1], zones=[{"value": 30, "color": "#e5afb0"}, {"value": 34, "color": "#e6d6b1"}, {"color": "#b0e5b1"}])

                    # Quality, Count
                    elif filename == "Per_tile_sequence_quality.csv":
                        if "R1" in idx:
                            web_tab.tab_name = "Quality by Tile"
                            web_tab.chart_properties = ChartProperties("heatmap", subtitle="Per Tile Average Quality Deviation",
                                x_label="Position", x_value=toks[1], y_label="Tile", y_value=toks[0], value=toks[2],
                                minimum="-10", maximum="10", min_color="#36c", mid_color="#ffffff", max_color="#dc3912")
                    # Base, G, A, T, C
                    elif filename == "Per_base_sequence_content.csv":
                        if "R1" in idx:
                            web_tab.tab_name = "Sequence Content"
                            web_tab.chart_properties = ChartProperties("line", subtitle="Sequence content across all bases",
                                x_label="Position", x_value=toks[0], y_label="Percent", y_value=toks[1:])
                    # Total Deduplicated Percentage, 28.416000000000004
                    # Duplication Level, Percentage of deduplicated, Percentage of total
                    elif filename == "Sequence_Duplication_Levels.csv":
                        if line.startswith("#Total Deduplicated Percentage"):
                            if "R1" in idx:
                                web_tab.chart_properties.subtitle = "%s%% remaining after deduplication" % toks[1].partition(".")[0]
                                self.tabs[filename] = web_tab
                            continue
                        else:
                            # affects printed header
                            toks[1] = "Deduplicated"
                            toks[2] = "Total"
                            if "R1" in idx:
                                web_tab = self.tabs[filename]
                                web_tab.tab_name = "Duplication Levels"
                                web_tab.chart_properties.type = "line"
                                web_tab.chart_properties.x_label = toks[0]
                                web_tab.chart_properties.x_value = toks[0]
                                web_tab.chart_properties.y_label = "Percent"
                                web_tab.chart_properties.y_value = toks[1:]
                    # Sequence, Count, Percentage, Possible Source
                    elif filename == "Overrepresented_sequences.csv":
                        if "R1" in idx:
                            web_tab.tab_name = "Overrepresented Sequences"
                            web_tab.chart_properties.type = "table"
                    # Position, Illumina Universal Adapter, Illumina Small RNA Adapter, Nextera Transposase Sequence, SOLID Small RNA Adapter
                    elif filename == "Adapter_Content.csv":
                        # Position, Illumina Universal, Illumina Small RNA, Nextera Transposase, SOLID Small RNA
                        toks = [t.replace("Adapter", "").replace("Sequence", "").strip() for t in toks]
                        if "R1" in idx:
                            web_tab.tab_name = "Adapter Content"
                            web_tab.chart_properties = ChartProperties("line", x_label=toks[0], x_value=toks[0],
                                y_label="Percent", y_value=toks[1:])
                    # Sequence, Count, PValue, Obs/Exp Max, Max Obs/Exp Position
                    elif filename == "Kmer_Content.csv":
                        if "R1" in idx:
                            web_tab.tab_name = "Kmer Content"
                            web_tab.chart_properties.type = "table"
                    # Quality, Count
                    elif filename == "Per_sequence_quality_scores.csv":
                        if "R1" in idx:
                            web_tab.tab_name = "Quality by Count"
                            web_tab.chart_properties = ChartProperties("line", x_value=toks[0],
                                x_label="Mean Sequence Quality", y_label=toks[1])
                    # GC Content, Count
                    elif filename == "Per_sequence_GC_content.csv":
                        if "R1" in idx:
                            web_tab.tab_name = "GC Content"
                            web_tab.chart_properties = ChartProperties("line", x_value=toks[0], x_label=toks[0], y_label=toks[1])
                    # Base, N-Count
                    elif filename == "Per_base_N_content.csv":
                        if "R1" in idx:
                            web_tab.tab_name = "N Content"
                            web_tab.chart_properties = ChartProperties("line", x_value=toks[0], x_label="Position", y_label="Percent N")
                    # Length, Count
                    elif filename == "Sequence_Length_Distribution.csv":
                        if "R1" in idx:
                            web_tab.tab_name = "Count by Length"
                            web_tab.chart_properties = ChartProperties("line", x_value=toks[0], x_label="Length (nt)", y_label=toks[1])
                    else:
                        logging.warn("We're not accounting for file named %s" % filename)
                    # add the tab to the site
                    if idx == "R1":
                        self.tabs[filename] = web_tab
                # print the current line to the open file handle as CSV
                print(*toks, sep=",", file=filehandle)
            if filehandle:
                filehandle.close()
        # combine simple line plots when reads are paired-end
        if self.r2:
            for filename in ["Per_sequence_quality_scores.csv", "Per_sequence_GC_content.csv",
                             "Per_base_N_content.csv", "Sequence_Length_Distribution.csv"]:
                self.tabs[filename].combine_tables(self.out_dir, float_format=None if filename == "Per_sequence_GC_content.csv" else "%g")

    def run(self, keep_tmp=False, **kwargs):
        """Runs FastQC.

        Keyword Args:
            adapter (Optional[str]): path to adapter file
            contaminants (Optional[str]): path to contaminants file
            kmers (Optional[int]): length of kmer for which to look
        """
        if self.r1 and self.r1.endswith(".zip"):
            logging.info("Extracting existing FastQC data from %s" % os.path.dirname(self.r1))
            self.extract_data(os.path.dirname(self.r1))
            return

        if not find_executable(FASTQC_EXE):
            sys.exit("`%s` was not found in your PATH." % FASTQC_EXE)

        tempd = tempfile.mkdtemp()
        if keep_tmp:
            logging.info("Writing temporary files to: %s" % tempd)
        cmd = [FASTQC_EXE, "-q", "-o", tempd]
        for k, v in kwargs.items():
            if v:
                cmd.extend(["--%s" % k, "%s" % str(v)])
        if self.r2:
            cmd.extend([self.r1, self.r2])
        else:
            cmd.extend([self.r1])

        try:
            subprocess.check_call(cmd)
            self.extract_data(tempd)
        except subprocess.CalledProcessError:
            logging.critical("Failed executing FastQC")
            logging.critical("Command was: %s" % " ".join(cmd))
            raise
        finally:
            if not keep_tmp:
                shutil.rmtree(tempd, ignore_errors=True)
