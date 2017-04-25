Processing a FASTQ
==================

The first time this is run, it will build the entire backend of the site.
Additional FASTQs being written to the same output directory are added to
the backend according to Group ID and UID.

Single-end FASTQ
````````````````

::

    $ fqc qc group_2016 sample1 test_r1.fastq.gz
    [2016-07-26 13:24 INFO] Writing data to: plot_data/group_2016/sample1
    [2016-07-26 13:24 INFO] Running FastQC
    [2016-07-26 13:27 INFO] Extracting data from FastQC archives
    [2016-07-26 13:27 INFO] Processing of sample1 complete


Paired-end FASTQs
`````````````````

::

    fqc qc --r2 test_r2.fastq.gz group_2016 sample2 test_r1.fastq.gz


Adding Custom Plot
``````````````````

::

    fqc add --x-value WELL_COL \
        --y-value WELL_ROW  \
        --shape circle \
        --value TOTAL_PAIRED_READS \
        --label "LABEL" \
        plot_data/group_00/test_00/config.json \
        "Reads by Plate" \
        plateheatmap \
        "Plate 1",plt1_counts.csv "Plate 2",plt2_counts.csv

This copies data into the necessary local folders and appends the following
JSON entry onto `plot_data/group_00/test_00/config.json`::

    {
        "filename": [
            [
                "Plate 1",
                "plt1_counts.csv"
            ],
            [
                "Plate 2",
                "plt2_counts.csv"
            ]
        ],
        "tab_name": "Reads by Plate",
        "chart_properties": {
            "type": "plateheatmap",
            "x_value": "WELL_COL",
            "y_value": [
                "WELL_ROW"
            ],
            "shape": "circle",
            "value": "TOTAL_PAIRED_READS",
            "label": "LABEL"
        }
    }
