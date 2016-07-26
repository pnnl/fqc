#!/usr/bin/env python
# coding=utf-8
"""
Subcommands to process FASTQs through FastQC and generate supporting configuration files as well
as to append additional data, like tables or heatmap counts, into UID pages.
"""
import argparse
import json
import logging
import os
import pandas as pd
import shutil
from bisect import insort_left
from collections import OrderedDict
from fqc import __version__
from fqc.fastqc import Fastqc
from fqc.utils import add_csv_input, fastqs_from_dir, import_json, parser_file_exists
from fqc.tabs import WebTab, ChartProperties


def run_qc(gid, uid, r1, r2=None, adapter=None, contaminants=None, exclude=[], kmers=8, out_dir=".", threads=1):
    """Creates output directory tree, handles JSON creation and updating when running QC, and
    executes FastQC.

    Args:
        gid (str): group, batch, or experiment ID
        uid (str): unique ID to this group, e.g. run ID or sample ID
        r1 (str): file path to R1 FASTQ file
        r2 (Optional[str]): file path to R2 FASTQ file
        adapter (Optional[str]): file path to optional adapters FASTA
        contaminants (Optional[str]): file path to optional contaminants FASTA
        exclude (Optional[list]): tab name list to exclude from JSON
        kmers (Optional[int]): the length of kmer for which to look
        out_dir (Optional[str]): parent directory of server; holds 'plot_data' and child folders
        threads (Optional[str]): number of threads to use
    """
    qc_obj = Fastqc(gid, uid, r1, r2=r2, out_dir=out_dir)
    logging.info("Running FastQC")
    # executes fastqc and writes data tables
    qc_obj.run(adapter=adapter, contaminants=contaminants, kmers=kmers, threads=threads)
    # exclude user requested tabs
    tabs = []
    for filename, web_tab in qc_obj.tabs.items():
        if exclude and web_tab.tab_name in exclude:
            logging.info("Omitting tab '%s'" % web_tab.tab_name)
        else:
            tabs.append(web_tab.to_dict())
    # writes config for this uid
    with open(os.path.join(qc_obj.out_dir, "config.json"), 'w') as fh:
        print(json.dumps(tabs, indent=4), file=fh)
    # update groups json
    group_config = os.path.join(qc_obj.out_dir.partition(gid)[0], "groups.json")
    logging.debug("Updating Group config: %s" % group_config)
    group_data = import_json(group_config)
    # if existing group
    if gid in [i['group_id'] for i in group_data]:
        for i in range(len(group_data)):
            if group_data[i]['group_id'] == gid:
                if uid not in group_data[i]['uids']:
                    # update UID list
                    insort_left(group_data[i]['uids'], uid)
    else:
        group_data.insert(0, {'group_id': gid, 'uids': [uid]})
    with open(group_config, 'w') as fh:
        print(json.dumps(group_data, indent=4, sort_keys=True), file=fh)
    logging.info("Processing of %s complete" % uid)


def run_batch_qc(gid, input_dir, adapter=None, contaminants=None, exclude=[], kmers=8, out_dir=".", threads=1):
    """Builds group directory tree which holds individual sample QCs.

    Args:
        gid (str): unique ID, e.g. experiment ID
        input_dir (str): path of directory containing FASTQ files
        adapter (Optional[str]): file path to optional adapters FASTA
        contaminants (Optional[str]): file path to optional contaminants FASTA
        exclude (Optional[list]): tab name list to exclude from JSON
        kmers (Optional[int]): the length of kmer for which to look
        out_dir (Optional[str]): parent directory of server; holds 'plot_data' and child folders
        threads (Optional[str]): number of threads to use
    """
    fastqs = fastqs_from_dir(input_dir)
    if not fastqs:
        logging.warning("No FASTQS were found in %s" % os.path.abspath(input_dir))
    else:
        for sample, file_path in fastqs.items():
            if isinstance(file_path, list):
                run_qc(gid, sample, file_path[0], r2=file_path[1], adapter=adapter,
                       contaminants=contaminants, exclude=exclude, kmers=kmers, out_dir=out_dir,
                       threads=threads)
            else:
                run_qc(gid, sample, file_path, adapter=adapter, contaminants=contaminants,
                       exclude=exclude, kmers=kmers, out_dir=out_dir, threads=threads)
    logging.info("Batch processing is complete.")


def run_add(config, name, plot_type, csv, status=None, x_value=None, y_value=None, x_label=None,
    y_label=None, subtitle=None, lower_quartile=None, upper_quartile=None, mean=None, shape=None,
    value=None, label=None):
    """Copies the CSV into the directory containing the config file if it does not already exist
    there, then either appends an appropriate entry onto the existing config JSON or creates a new
    file.

    Args:
        config (str): file path to config.json
        name (str): name being used in the tab on the dashboard
        plot_type (str): type of chart being created ['line', 'table', 'heatmap', 'plateheatmap', 'arearange']
        csv (str): file path to data file being added to dashboard
        status (Optional[str]): image icon to be displayed on tab [None, 'warn', 'pass', 'fail']
        x_value (Optional[str]): header label in CSV containing the x-values
        y_value (Optional[str]): header label in CSV containing the y-values
        x_label (Optional[str]): x-label to be drawn on dashboard; defaults to `x_value`
        y_label (Optional[str]): y-label to be drawn on dashboard; defaults to `y_value`
        subtitle (Optional[str]): subtitle to be drawn on dashboard
        lower_quartile (Optional[str]): arearange specific option; header label in CSV for lower
            quartile value
        upper_quartile (Optional[str]): arearange specific option; header label in CSV for upper
            quartile value
        mean (Optional[str]): arearange specific option; header label in CSV for mean value
        shape (Optional[str]): internal plateheatmap shape; either square or circle
        value (Optional[str]): value label in CSV to be plotted in heatmap
        label (Optional[str]): optional heatmap label header to mark individual coordinates
    """
    filename = add_csv_input(csv, os.path.dirname(config))
    web_tab = WebTab(filename, name, status,
                     ChartProperties(plot_type, subtitle, x_label, x_value, y_label, y_value,
                                     lower_quartile, upper_quartile, mean, shape, value,
                                     label))
    # append onto configuration file
    if os.path.exists(config):
        shutil.copy(config, config + '.bak')
        logging.info("Saving backup: %s" % config + '.bak')
        tab_data = import_json(config)
        tab_data.append(web_tab.to_dict())
        try:
            with open(config, 'w') as fh:
                print(json.dumps(tab_data, indent=4), file=fh)
        except Exception:
            shutil.move(config + '.bak', config)
            logging.exception("The backup config has been restored.")
            raise
    # create new
    else:
        with open(config, 'w') as fh:
            print(json.dumps([entry], indent=4), file=fh)
    logging.info("Added entry into %s\n%s" % (config, json.dumps(web_tab.to_dict(), indent=4)))


def main():
    p = argparse.ArgumentParser(description=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('--version', action='version',
        version='%(prog)s {version}'.format(version=__version__))

    sp = p.add_subparsers(dest="subparser_name", title="commands")
    qc_p = sp.add_parser('qc', formatter_class=argparse.ArgumentDefaultsHelpFormatter,
               description=("Builds output directory structure based on `ID`, adding new entries "
                            "for each unique `ID`. Runs QC across pair-end reads and generates or "
                            "appends server configuration files."),
               help="run QC across PE reads and setup or update configuration")
    bqc_p = sp.add_parser('batch-qc', formatter_class=argparse.ArgumentDefaultsHelpFormatter,
               description=("Run `qc` over all FASTQ files within a directory. Files are assumed "
                            "to contain the extension .fq or .fastq and can be compressed. Paired "
                            "files are assumed to have <sample>_R1.fastq and <sample>_R2.fastq. "
                            "The read index (_R1, _R2) is required and should closely precede the "
                            "file extension."),
               help="Run `qc` over all FASTQ files within a directory")
    add_p = sp.add_parser('add', formatter_class=argparse.ArgumentDefaultsHelpFormatter,
               description=("Appends JSON entries onto existing config JSON or creates a new "
                            "configuration file for a dashboard tab"),
               help="add JSON entry for new dashboard data")

    # qc
    qc_p.add_argument("gid", metavar="GROUP-ID",
        help="group ID or experiment ID for this FASTQ batch")
    qc_p.add_argument("uid", metavar="SAMPLE-ID",
        help=("unique, sample ID or some other ID unique to this read pair; IDs within a group "
              "should be unique or the underlying data will be overwritten with most recent read "
              "pair"))
    qc_p.add_argument("r1", metavar="R1", type=lambda x: parser_file_exists(p, x),
        help="path to R1 FASTQ file")
    qc_p.add_argument("--r2", metavar="R2", type=lambda x: parser_file_exists(p, x),
        help="path to R2 FASTQ file")
    qc_p.add_argument("-a", "--adapter", metavar="STR",
        help=("a non-default file containing a list of adapter sequences which will be explicity "
              "searched against the library -- must contain sets of named adapters in the form "
              "name[tab]sequence {prefix lines with # to ignore}"))
    qc_p.add_argument("-c", "--contaminants", metavar="STR",
        help=("a non-default file containing a list of contaminants to screen overrepresented "
              "sequences against -- must contain sets of named contaminants in the form "
              "name[tab]sequence {prefix lines with # to ignore}"))
    qc_p.add_argument("-e", "--exclude", action="append",
        help=("Exclude default plots of FastQC from being displayed by specifying its name; use "
              "flag for each exclusion -- 'Basic Statistics', 'Quality by Position', 'Quality by "
              "Tile', 'Sequence Content', 'Duplication Levels', 'Overrepresented Sequences', "
              "'Adapter Content', 'Kmer Content', 'Count by Quality', 'Count by GC', "
              "'N by Position', 'Count by Length'"))
    qc_p.add_argument("-k", "--kmers", metavar="INT", type=int, default=8,
        choices=range(2,10), help="the length of kmer for which to look")
    qc_p.add_argument("-o", "--out-dir", metavar="STR", default=".",
        help="parent directory of server; holds 'plot_data' and child folders")
    qc_p.add_argument("-t", "--threads", metavar="INT", type=int, default=0,
        help="number of threads to use; 0 for 'all'")

    # batch qc
    bqc_p.add_argument("gid", metavar="GROUP-ID",
        help="group ID or experiment ID for this FASTQ batch")
    bqc_p.add_argument("input_dir", metavar="FASTQ-DIR",
        help="directory containing input FASTQ files")
    bqc_p.add_argument("-a", "--adapter", metavar="STR",
        help=("a non-default file containing a list of adapter sequences which will be explicity "
              "searched against the library -- must contain sets of named adapters in the form "
              "name[tab]sequence {prefix lines with # to ignore}"))
    bqc_p.add_argument("-c", "--contaminants", metavar="STR",
        help=("a non-default file containing a list of contaminants to screen overrepresented "
              "sequences against -- must contain sets of named contaminants in the form "
              "name[tab]sequence {prefix lines with # to ignore}"))
    bqc_p.add_argument("-e", "--exclude", action="append",
        help=("Exclude default plots of FastQC from being displayed by specifying its name; use "
              "flag for each exclusion -- 'Basic Statistics', 'Quality by Position', 'Quality by "
              "Tile', 'Sequence Content', 'Duplication Levels', 'Overrepresented Sequences', "
              "'Adapter Content', 'Kmer Content', 'Count by Quality', 'Count by GC', "
              "'N by Position', 'Count by Length'"))
    bqc_p.add_argument("-k", "--kmers", metavar="INT", type=int, default=8,
        choices=range(2,10), help="the length of kmer for which to look")
    bqc_p.add_argument("-o", "--out-dir", metavar="STR", default=".",
        help="parent directory of server; holds 'plot_data' and child folders")
    bqc_p.add_argument("-t", "--threads", metavar="INT", type=int, default=0,
        help="number of threads to use; 0 for 'all'")

    # add plots
    add_p.add_argument("config", metavar="JSON", help="config onto which we're appending or creating")
    add_p.add_argument("name", metavar="STR", help="chart tab name")
    add_p.add_argument("plot_type", choices=['arearange', 'heatmap', 'plateheatmap', 'line', 'table'])
    add_p.add_argument("csv", metavar="CSV", nargs="+",
        help=("CSV data file that is being added; if more than one is being plotted as subplots, "
              "use name,file.csv convention, e.g. 'Plate 1',pla1.cnt.csv 'Plate 2',pla2.cnt.csv"))
    add_p.add_argument("--status", choices=['pass', 'fail', 'warn'], help="tab status indicator")

    data_props = add_p.add_argument_group("data properties")
    data_props.add_argument("--x-value", metavar="STR",
        help="header label in CSV representing x-value")
    data_props.add_argument("--y-value", metavar="STR", action="append",
        help="header label in CSV representing y-value; can be specified more than one time for line plot")

    chart_props = add_p.add_argument_group("chart properties")
    chart_props.add_argument("--x-label", metavar="STR", help="default is x-value")
    chart_props.add_argument("--y-label", metavar="STR", help="default is y-value")
    chart_props.add_argument("--subtitle", metavar="STR", help="chart subtitle")

    arearange = add_p.add_argument_group("arearange")
    arearange.add_argument("--lower-quartile", metavar="STR",
        help="header label of lower quartile value")
    arearange.add_argument("--upper-quartile", metavar="STR",
        help="header label of upper quartile value")
    arearange.add_argument("--mean", metavar="STR", help="header label of mean value")

    heatmap = add_p.add_argument_group("heatmap")
    heatmap.add_argument("--shape", choices=['circle', 'square'], default='square',
        help="shape applied to colors inside the heatmap")
    heatmap.add_argument("--value", metavar="STR", help="header label of plot value")

    # plateheatmap
    heatmap.add_argument("--label", metavar="STR", help="optional header label for coordinate highlights within the heatmap")

    args = p.parse_args()

    logging.basicConfig(level=logging.INFO, datefmt="%Y-%m-%d %H:%M",
        format="[%(asctime)s %(levelname)s] %(message)s")

    if "threads" in args and args.threads == 0:
        import multiprocessing
        args.threads = multiprocessing.cpu_count()

    if args.subparser_name == "qc":
        run_qc(args.gid, args.uid, args.r1, r2=args.r2, adapter=args.adapter,
            contaminants=args.contaminants, exclude=args.exclude, kmers=args.kmers,
            out_dir=args.out_dir, threads=args.threads)
    elif args.subparser_name == "batch-qc":
        run_batch_qc(args.gid, args.input_dir, adapter=args.adapter, contaminants=args.contaminants,
            exclude=args.exclude, kmers=args.kmers, out_dir=args.out_dir, threads=args.threads)
    elif args.subparser_name == "add":
        run_add(args.config, args.name, args.plot_type, args.csv, status=args.status,
            x_value=args.x_value, y_value=args.y_value, x_label=args.x_label, y_label=args.y_label,
            subtitle=args.subtitle, lower_quartile=args.lower_quartile,
            upper_quartile=args.upper_quartile, shape=args.shape, value=args.value,
            label=args.label)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
