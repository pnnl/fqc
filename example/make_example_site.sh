#!/usr/bin/env bash

# everything executed in example_workflow.rst
fqc qc -t 8 -e 'Basic Statistics' \
    -e 'Overrepresented Sequences' \
    -e 'Count by Length' \
    -e 'Kmer Content' \
    2016 160912_M03018 data/fastqs/160912_M03018_R1.fastq.gz

fqc add --prepend --x-value FractionOfSamples --y-value Equal \
    --y-value Actual --x-label 'Fraction of Samples' \
    --y-label 'Fraction of On Target Reads' \
    plot_data/2016/160912_M03018/config.json \
    'Read Distribution' \
    line \
    data/tables/160912_lorenz.csv

fqc add --prepend plot_data/2016/160912_M03018/config.json \
    'Run Stats' \
    table data/tables/160912_summary.csv

fqc add --x-value WELL_COL --y-value WELL_ROW --value TOTAL_PAIRED_READS \
    --label LABEL \
    --colors 'UNUSED:#000000' \
    plot_data/2016/160912_M03018/config.json \
    'Abundance by Plate' \
    plateheatmap \
    data/tables/160912_plate_1.csv

fqc add --x-value Barcode --y-value Count \
    plot_data/2016/160912_M03018/config.json \
    "Barcode Counts" \
    bar \
    data/tables/160912_top50barcodes.csv

# finish up the remaining samples
samples="160919_M03018 160923_M03018 170120_M03018 170123_M03018 170129_M03018"

for sample in $samples; do
    year=20${sample:0:2}
    shortsample=${sample/_*}

    fqc qc -t 8 \
        -e 'Basic Statistics' \
        -e 'Overrepresented Sequences' \
        -e 'Count by Length' \
        -e 'Kmer Content' \
        $year \
        $sample \
        data/fastqs/${sample}_R1.fastq.gz

    fqc add --prepend --x-value FractionOfSamples --y-value Equal \
        --y-value Actual --x-label 'Fraction of Samples' \
        --y-label 'Fraction of On Target Reads' \
        plot_data/$year/$sample/config.json \
        'Read Distribution' \
        line \
        data/tables/${shortsample}_lorenz.csv

    fqc add --prepend \
        plot_data/$year/$sample/config.json \
        'Run Stats' \
        table \
        data/tables/${shortsample}_summary.csv

    for (( i = 1; i < 10; i++ )); do
        if [[ -f data/tables/${shortsample}_plate_${i}.csv ]]; then
            fqc add --x-value WELL_COL --y-value WELL_ROW \
                --value TOTAL_PAIRED_READS --label LABEL \
                --colors 'NEG CTRL:#1f77b4,POS CTRL:#d62728,UNUSED:#000000' \
                plot_data/$year/$sample/config.json \
                'Abundance by Plate' \
                plateheatmap \
                data/tables/${shortsample}_plate_*.csv
            fqc add --x-value WELL_COL --y-value WELL_ROW \
                --value TOTAL_CONTAMINATION --label LABEL \
                --colors 'NEG CTRL:#1f77b4,POS CTRL:#d62728,UNUSED:#000000' \
                plot_data/$year/$sample/config.json \
                'Contamination by Plate' \
                plateheatmap \
                data/tables/${shortsample}_plate_*.csv
            break
        fi
    done

    fqc add --x-value Barcode --y-value Count \
        plot_data/2016/160912_M03018/config.json \
        "Barcode Counts" \
        bar \
        data/tables/160912_top50barcodes.csv

done
