# FASTQ QA/QC Dashboard

![dashboard](http://i.imgur.com/df51TBN.png)

Quality assurance largely utilizing existing tools like FastQC, while being
extensible to include new data sources. Plots have been revamped to include
the use of modern tools and take advantage of interactivity where applicable.

# TODO

+ [ ] plateheatmap height appears much larger than other plots
+ [ ] change the name of boxplot to something like iqrplot
+ [ ] change color theme
+ [ ] fastqc plot order
+ [ ] conda packaging
+ [ ] move to github with license

# Requires

Parsing the table and running `FastQC` is performed with code written for
Python 3. We recommend using [Anaconda](https://www.continuum.io/downloads) to
install `fqc` and its dependencies. To install:

```
conda install -c bioconda python fastqc fqc
```

# Run

```
$ fqc qc test_id test_r1.fastq.gz test_r2.fastq.gz
[2016-04-08 13:02] Writing data to: ./plot_data/test_id
[2016-04-08 13:02] Running FastQC.
[2016-04-08 13:02] Extracting data from FastQC archives
[2016-04-08 13:02] Processing complete.
```

If we run over successive test runs named test_1 and test_2, the output folder
directory tree of:

```
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
```

# Deploy Site

**This needs to be adapted for `conda install`**

Start a local server and navigate to `localhost:8000`:

```
python -m http.server
```

This will show the test data QC as determined by the data directory in
`js/fqc.js`:

```
var filePath = "/fqc/tests/data/qc/plot_data/"
```

# Files

## runs.json

Located within the `plot_data` directory, this holds metadata for each run:

```
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
```

+ `run_id` is used as the ID in the dropdown
+ `data_folder` is used as the path to `config.json`

`fqc` will write the same value for each, but if the user chooses to change
what is displayed in the browser versus where the data is stored in the
filesystem.

## config.json

Holds metadata for each run inside the run folder, set tab names, and backing
data. Each entry must have a `tab_name`, `filename`, and `chart_properties`.

### Status

Possible values:

+ pass
+ fail
+ warn

### Table

```
{
    "status": "",
    "filename": [
        [
            "R1",
            "R1/Basic_Statistics.csv"
        ],
        [
            "R2",
            "R2/Basic_Statistics.csv"
        ]
    ],
    "tab_name": "Basic Statistics",
    "chart_properties": {
        "type": "table"
    }
}
```

![basic statistics](http://i.imgur.com/IBkzOT7.png)

### Heatmap

```
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
        "min": -10,
        "max": 10,
        "min_color": "",
        "mid_color": "",
        "max_color": "",
        "type": "heatmap"
    },
    "status": "pass"
}
```

![heatmap](http://i.imgur.com/2XWjpar.png)

### Plate Heatmap

A nicely spaced heatmap specifically for showing trends over sample plates.

### Line

When multiple y-values are passed, line labels are header values.

```
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
```


![multiple line plot](http://i.imgur.com/JDePntm.png)

### Area Range

```
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
        "mean": "",
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
```

![area range](http://i.imgur.com/tM7bgO0.png)

# Adding Plots

Plot data can be added manually to the UID directory then edit the appropriate
configuration file. If you're adding a new run, you will have to add it to
`run.json`, but if the run exists, you can add the plot metadata into that
UIDs `config.json`.

There's also a convenience method that will copy data and update `config.json`
with a valid JSON entry for the plot type being added.

```
fqc add --x-value WELL_COL \
    --y-value WELL_ROW  \
    --shape circle \
    --value TOTAL_PAIRED_READS \
    --label "LABEL" \
    qc/plot_data/test_add_heatmap/config.json \
    "Reads by Plate" \
    heatmap \
    "Plate 1",plt1_counts.csv "Plate 2",plt2_counts.csv
```

This appends the following JSON entry onto `qc/plot_data/test_1/config.json`:

```
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
```

# Testing

We've run...

```
fqc qc -o qc test_qc test_r1.fastq.gz test_r2.fastq.gz
fqc qc -e 'Basic Statistics' -e 'Count by Length' -o qc test_omit_basic_count_by_length test_r1.fastq.gz test_r2.fastq.gz
fqc qc -e 'Basic Statistics' -e 'Count by Length' -o qc test_add_heatmap test_r1.fastq.gz test_r2.fastq.gz
fqc add --x-value WELL_COL --y-value WELL_ROW --shape circle --value TOTAL_PAIRED_READS --label "LABEL" qc/plot_data/test_add_heatmap/config.json "Reads by Plate" plateheatmap "Plate 1",plt1_counts.csv "Plate 2",plt2_counts.csv
```

After we've verified the output by hand we can then run future tests against that using simply `nosetests` from the main project directory.
