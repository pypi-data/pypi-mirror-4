python-globtailer
=================

.. image:: https://secure.travis-ci.org/msabramo/python-globtailer.png
   :target: http://travis-ci.org/msabramo/python-globtailer

The main class is ``FileTailer``, a generator that yields lines from the most
recently modified file matching a glob pattern.

Example::

    from globtailer import FileTailer

    tailer = FileTailer("/path/to/*.log")

    for line in tailer:
        print(line)
