Install
=======

Requires
````````

Parsing the table and running ``FastQC`` is performed with code written for
Python 3. We recommend using Anaconda (https://www.continuum.io/downloads) to
install the FastQC dependency::

    conda install -c bioconda fastqc


Install
```````

The dashboard reads local files, so install where you will eventually be
serving the site::

    git clone https://github.com/pnnl/fqc.git
    cd fqc
    python setup.py install


This installs ``fqc`` command-line tool to process FASTQs and create the
dashboard.

Then to deploy a local copy from within the ``fqc`` directory, you can run::

    python -m http.server --bind localhost 8000


And navigate to ``localhost:8000`` in your browser.

By default, this will show the test data QC as determined by the data
directory in ``js/fqc.js``::

    var filePath = "/example/plot_data/"

Edit ``fqc.js`` to your local path **within** the ``fqc`` directory tree.
