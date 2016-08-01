import json
import logging
import os
import re
import shutil
import string
import sys
from stat import ST_ATIME, ST_MTIME


def parser_file_exists(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file <%s> does not exist!" % arg)
    return arg


def import_json(json_file):
    """Imports a JSON into a python object.

    Args:
        json_file (str): file path to json file

    Returns:
        object: imported json data object or empty list if file does not exist

    Raises:
        json.decoder.JSONDecoderError
    """
    data = []
    if os.path.exists(json_file):
        with open(json_file) as fh:
            try:
                data = json.load(fh)
            except json.decoder.JSONDecoderError:
                logging.critical("%s was not in valid JSON format" % json_file)
                raise
    else:
        return data
    return data


def fastqs_from_dir(input_dir):
    """
    Grabs single-end or paired-end FASTQ file pairs from a directory with basic assumptions in
    naming convention. Files are assumed to contain the extension .fq or .fastq and can be
    compressed. Paired files are assumed to have <sample>_R1.fastq and <sample>_R2.fastq. The
    read index (_R1, _R2) is required and should closely precede the file extension.

    Args:
        input_dir (str): directory containing fastq files

    Returns:
        dict of sample id to file path or list of file paths
    """
    exts = ['.fastq', '.fq']
    input_dir = os.path.abspath(input_dir)
    if not os.path.isdir(input_dir):
        logging.debug("Changing input dir from %s to %s" % (input_dir, os.path.dirname(input_dir)))
        input_dir = os.path.dirname(input_dir)
    if not os.path.exists(input_dir):
        return {}
    pairs = {}
    # sample name for files without _r1 or _r2 in the name
    split_pattern = re.compile('(\\%s)' % '|\\'.join(exts))
    # split file name based on _r1 and _r2
    pattern = re.compile(r'((?:_[rR][12][^_]*))$')

    for f in os.listdir(input_dir):
        if not any(ext in f for ext in exts): continue
        toks = pattern.split(f)
        sample_id = toks[0] if len(toks) > 1 else split_pattern.split(f)[0]
        if sample_id in pairs:
            if isinstance(pairs[sample_id], list):
                logging.warning("%s has more than 2 paired fastqs in %s" % (sample_id, input_dir))
                continue
            pairs[sample_id] = [pairs[sample_id], os.path.join(input_dir, f)]
        else:
            pairs[sample_id] = os.path.join(input_dir, f)
    logging.info("Found %d unique samples in %s" % (len(pairs), input_dir))
    return pairs


def copy_file(src, dst):
    if not os.path.exists(dst):
        logging.info("Copying %s to %s" % (src, dst))
        shutil.copy(src, dst)
        # update the modified time of this file
        st = os.stat(dst)
        os.utime(dst, (st[ST_ATIME], st[ST_MTIME] + 5))


def add_csv_input(csv, dst):
    """
    Parses CLI argument `csv` for `fqc add` and returns the filename string or filename list
    with tab names.

    Args:
        csv (list): list of CSV files or <tab name>,<csv file> pairs
        dst (str): directory in which to copy input CSV files

    Returns:
        file path or list of tab name, file paths suitable for WebTab.filename
    """
    if len(csv) > 1:
        filename = []
        # 'Plate 1',plate_1_counts.csv 'Plate 2',plate_2_counts.csv
        for i in csv:
            if "," in i:
                name, filepath = i.split(",")
            # just use the filename for the subplot label
            else:
                name = string.capwords(os.path.basename(i).rpartition(".")[0].replace("_", " "))
                filepath = i
            filepath = os.path.abspath(os.path.expanduser(filepath))
            if not os.path.exists(filepath):
                sys.exit("Input file does not exist: %s" % filepath)
            copy_file(filepath, os.path.join(dst, os.path.basename(filepath)))
            filename.append([name, os.path.basename(filepath)])
    # no subplots
    else:
        if "," in csv[0]:
            filename = os.path.abspath(csv[0].partition(",")[-1])
        else:
            filename = os.path.abspath(csv[0])
        if not os.path.exists(filename):
            sys.exit("Input file does not exist: %s" % filename)
        copy_file(filename, os.path.join(dst, os.path.basename(filename)))
        filename = os.path.basename(filename)
    return filename
