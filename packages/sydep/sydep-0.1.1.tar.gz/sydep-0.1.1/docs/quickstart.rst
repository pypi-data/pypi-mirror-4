Quickstart
==========

Preparation
-----------
First check if you have installed ``python 2.7``. Current ``sydep`` doesn't work with
``python3`` or older pythons. You must have ``pip``, too.

Installation
------------

If you want to install ``sydep`` for all users, you have to log in as root. Then
you run this command:

.. code-block:: bash

    pip install sydep

Now you can start with using.


Using
-----

Run init in your project root directory.

.. code-block:: bash

    sydep init

This command will create file ``sydep.cfg`` with settings of your deployment. It
looks like this:

.. code-block:: ini

    [server]
    # remote SSH server
    server = login@server

    # remote path (optional)
    remote = .

    # local path (optional)
    local = .

Edit this file, set your login information and paths. Now you can download and
upload your files.

Upload to server
****************

.. code-block:: bash

    sydep push


Download from server
********************

.. code-block:: bash

    sydeb pull

This command doesn't download all files from remote server! It downloads only
these, which are existing in your local folders. If you want to download new
file, you ought to create it first ``touch my_new_file``.


Set up ignored files
--------------------

In file ``.sydebignore`` you can set, which file you want to ignore. You can use
wildcards.

Example
*******

.. code-block:: bash

    tmp/*       # ignore all files from tmp directory
    *~          # ignore backup files
    *.pyc       # ignore all compiled python files
