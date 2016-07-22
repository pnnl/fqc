FASTQ QA/QC Dashboard
=====================

Quality assurance largely utilizing existing tools like FastQC, while
being extensible to include new data sources. Plots have been revamped
to include the use of modern tools and take advantage of interactivity
where applicable.

Requires
========

Python3
-------

::

    conda install python

FastQC
------

The expectation is that there's an executable in your ``$PATH`` named
``fastqc``, which can easily be satisfied by installing via ``conda``:

::

    conda install -c bioconda fastqc

Install
=======

::

    git clone https://brow015@stash.pnnl.gov/scm/~brow015/fqcdb.git
    cd fqcdb
    python setup.py install
    # testing requires `nose`
    nosetests

Run
===

::

    $ fqcdb qc test_1 test_r1.fastq.gz test_r2.fastq.gz
    [2016-04-08 13:02] Writing data to: ./plot_data/test_1
    [2016-04-08 13:02] Running FastQC.
    [2016-04-08 13:02] Extracting data from FastQC archives
    [2016-04-08 13:02] Processing complete.

To the output folder, this writes a directory tree of:

::

    plot_data/
    ├── runs.json
    ├── test_1
    │   ├── Per_base_N_content.csv
    │   ├── Per_sequence_GC_content.csv
    │   ├── Per_sequence_quality_scores.csv
    │   ├── R1
    │   │   ├── Adapter_Content.csv
    ...
    │   │   └── Sequence_Length_Distribution.csv
    │   ├── R2
    │   │   ├── Adapter_Content.csv
    ...
    │   │   └── Sequence_Length_Distribution.csv
    │   ├── Sequence_Length_Distribution.csv
    │   └── config.json
    └── test_2
        ├── Per_base_N_content.csv
        ├── Per_sequence_GC_content.csv
        ├── Per_sequence_quality_scores.csv
        ├── R1
        │   ├── Adapter_Content.csv
    ...
        │   └── Sequence_Length_Distribution.csv
        ├── R2
        │   ├── Adapter_Content.csv
    ...
        │   └── Sequence_Length_Distribution.csv
        ├── Sequence_Length_Distribution.csv
        └── config.json

Files
=====

runs.json
---------

Saves metadata for each run outside of the run folder:

::

    [
        {
            "run_id": "test_1",
            "data_folder": "test_1"
        },
        {
            "run_id": "test_2",
            "data_folder": "test_2"
        }
    ]

``run_id`` is used as the ID in the dropdown.

``data_folder`` is used as the path to ``config.json``.

config.json
-----------

Holds metadata for each run inside the run folder.

Each entry must have a ``tab_name``, ``filename``, and
``chart_properties``. See examples below.

Table
~~~~~

::

    {
        "filename": [
            [
                "R1",
                "R1/Overrepresented_sequences.csv"
            ],
            [
                "R2",
                "R2/Overrepresented_sequences.csv"
            ]
        ],
        "tab_name": "Overrepresented Sequences",
        "chart_properties": {
            "type": "table"
        },
        "status": "fail"
    }

Heatmap
~~~~~~~

``label`` is an optional outline per data point being plotted. The
legend value corresponds to the value in the row under column ``label``.

::

    {
        "filename": [
            [
                "R1",                                       # subplot label
                "R1/Per_tile_sequence_quality.csv"          # path to file
            ],
            [
                "R2",                                       # subplot label
                "R2/Per_tile_sequence_quality.csv"          # path to file
            ]
        ],
        "tab_name": "Quality by Tile",
        "chart_properties": {
            "y_value": "Tile",
            "x_label": "Position",
            "value": "Mean",
            "y_label": "Tile",
            "shape": "square",
            "subtitle": "Mean quality per tile",
            "x_value": "Base",
            "type": "heatmap"
        },
        "status": "pass"
    }

Line
~~~~

When multiple y-values are passed, line labels are header values.

::

    {
        "filename": [
            [
                "R1",
                "R1/Per_base_sequence_content.csv"
            ],
            [
                "R2",
                "R2/Per_base_sequence_content.csv"
            ]
        ],
        "tab_name": "Sequence Content",
        "chart_properties": {
            "y_value": [
                "G",
                "A",
                "T",
                "C"
            ],
            "x_label": "Position",
            "y_label": "Percent",
            "subtitle": "Sequence content across all bases",
            "x_value": "Base",
            "type": "line"
        },
        "status": "fail"
    }

Boxplot
~~~~~~~

::

    {
        "filename": [
            [
                "R1",
                "R1/Per_base_sequence_quality.csv"
            ],
            [
                "R2",
                "R2/Per_base_sequence_quality.csv"
            ]
        ],
        "tab_name": "Quality by Position",
        "chart_properties": {
            "median": "Median",
            "lower_percentile": "10th Percentile",
            "x_label": "Position",
            "upper_quartile": "Upper Quartile",
            "upper_percentile": "90th Percentile",
            "lower_quartile": "Lower Quartile",
            "subtitle": "",
            "x_value": "Base",
            "type": "boxplot"
        },
        "status": "pass"
    }

Adding Plots
============

Plot data can be added manually to the UID directory then edit the
appropriate configuration file. If you're adding a new run, you will
have to add it to ``run.json``, but if the run exists, you can add the
plot metadata into that UIDs ``config.json``.

There's also a convenience method that will copy data and update
``config.json`` with a valid JSON entry for the plot type being added.

::

    fqcdb add --x-value WELL_COL \
        --y-value WELL_ROW \
        --shape circle \
        --value TOTAL_PAIRED_READS \
        --subplot-label PRIMER_PLATE_NUMBER \
        --label "LABEL"
        qc/plot_data/test_1/config.json \
        counts.csv \
        heatmap \
        "Reads by Plate"

This appends the following JSON entry onto
``qc/plot_data/test_1/config.json``:

::

    {
        "filename": [
            [
                "Plate 1",
                "counts.csv"
            ],
            [
                "Plate 2",
                "counts.csv"
            ],
            [
                "Plate 3",
                "counts.csv"
            ],
            [
                "Plate 4",
                "counts.csv"
            ]
        ],
        "tab_name": "Reads by Plate",
        "status": "",
        "chart_properties": {
            "type": "heatmap",
            "subtitle": "",
            "x_value": "WELL_COL",
            "y_value": "WELL_ROW",
            "x_label": "",
            "y_label": "",
            "shape": "circle",
            "value": "TOTAL_PAIRED_READS",
            "label": "LABEL"
        }
    }
