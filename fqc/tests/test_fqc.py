import fqc
import json
import shutil
import os
import pandas as pd
import tempfile


DATA = os.path.join(os.path.dirname(__file__), "data")


def compare_output_dirs(data_dir, temp_dir, gid, uid):
    for k_root, k_dirs, k_files in os.walk(data_dir):
        for k_file in k_files:
            if uid not in k_root:
                continue

            test_result_file = os.path.join(temp_dir, "plot_data", k_root.partition("plot_data/")[2], k_file)

            if 'config.json' in k_file:
                # the whole thing is a 1-item list
                target = fqc.import_json(os.path.join(k_root, k_file))[0]
                query = fqc.import_json(os.path.join(temp_dir, "plot_data", uid, k_file))[0]
                assert target == query

            elif k_file.endswith('csv'):
                known_df = pd.read_csv(os.path.join(k_root, k_file))
                unknown_df = pd.read_csv(test_result_file)
                assert known_df.equals(unknown_df)

    run_json = fqc.import_json(os.path.join(temp_dir, "plot_data", "runs.json"))
    assert run_json[0]['data_folder'] == uid
    assert run_json[0]['run_id'] == uid


def test_qc():
    r1 = os.path.join(DATA, 'test_r1.fastq.gz')
    r2 = os.path.join(DATA, 'test_r2.fastq.gz')
    outd = tempfile.mkdtemp()
    gid = 'group_test_qc'
    uid = 'test_qc'
    fqc.run_qc(gid, uid, r1, r2=r2, out_dir=outd)
    compare_output_dirs(os.path.join(DATA, 'qc'), outd, gid, uid)
    shutil.rmtree(outd, ignore_errors=True)


def test_qc_omit_tables():
    r1 = os.path.join(DATA, 'test_r1.fastq.gz')
    r2 = os.path.join(DATA, 'test_r2.fastq.gz')
    outd = tempfile.mkdtemp()
    uid = 'test_omit_basic_count_by_length'
    fqc.run_qc(uid, r1, r2, out_dir=outd, exclude=['Basic Statistics', 'Count by Length'])
    compare_output_dirs(os.path.join(DATA, 'qc'), outd, uid)
    shutil.rmtree(outd, ignore_errors=True)


def test_add_heatmap():
    csv = ["Plate 1,%s" % os.path.join(DATA, 'plt1_counts.csv'),
            "Plate 2,%s" % os.path.join(DATA, 'plt2_counts.csv')]
    config = tempfile.mktemp()
    result = {"filename": [["Plate 1", "plt1_counts.csv"], ["Plate 2", "plt2_counts.csv"]],
              "tab_name": "Reads by Plate",
              "status": "",
              "chart_properties": {"type": "heatmap", "subtitle": "plot subtitle",
                                   "x_value": "WELL_COL", "y_value": "WELL_ROW",
                                   "x_label": "x-label", "y_label": "y-label",
                                   "shape": "circle", "value": "TOTAL_PAIRED_READS",
                                   "label": "LABEL"}}

    fqc.run_add(config, "Reads by Plate", "heatmap", csv, x_value="WELL_COL", y_value="WELL_ROW",
        shape="circle", value="TOTAL_PAIRED_READS", label="LABEL", x_label="x-label",
        y_label="y-label", subtitle="plot subtitle")

    test_result = fqc.import_json(config)[0]

    for k, v in result.items():
        # chart properties
        if isinstance(v, dict):
            for kk, vv in v.items():
                assert test_result[k][kk] == vv
        else:
            assert test_result[k] == v
