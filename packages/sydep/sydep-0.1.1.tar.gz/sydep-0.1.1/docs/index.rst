.. sydep documentation master file, created by
   sphinx-quickstart on Sat Mar 23 12:27:08 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

sydep 0.1
=================================

Sydep is a tool for easy deployment with rsync.

Requirements
------------

* `python 2.7` with `pip`
* `rsync`

Installation
------------

Stable
******

.. code-block:: bash

    pip install sydep


From sources
************

.. code-block:: bash

    pip install -e git+https://github.com/yetty/sydep.git#egg=sydep




Usage
-----

.. code-block:: bash

    sydep - tool for deployment over rsync

    Usage: sydep [-q] (-h|init|pull|push)

    -h --help               show this help
    -q --quiet              no output

    init                    create new sydep.cfg
    pull                    download files from server
    push                    uplod files to remote server



Contents
--------

.. toctree::
    :maxdepth: 2

    quickstart
    sydep





Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

