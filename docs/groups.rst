Groups
======

Located within the ``plot_data`` directory, this holds metadata for each group
and samples within the groups::


    [
        {
            "group_id": "group_01",
            "uids": [
                "test_01"
            ]
        },
        {
            "group_id": "group_00",
            "uids": [
                "test_00"
            ]
        }
    ]


Renders as:

.. image:: _static/groups_json_example.png

The sample ID and group ID must match the underlying directory tree that is
built by ``fqc qc`` and maintained when using ``fqc batch-qc`` and ``fqc add``.

The directory tree of this simple example::

    plot_data/
    ├── group_00
    │   └── test_00
    │       ├── R1
    │       ├── R2
    │       └── config.json
    ├── group_01
    │   └── test_01
    │       ├── R1
    │       ├── R2
    │       └── config.json
    └── groups.json

For a more detailed example, see the groups.json file located in the example
data directory.
