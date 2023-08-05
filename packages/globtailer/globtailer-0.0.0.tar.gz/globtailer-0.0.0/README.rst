python-globtailer
=================

.. image:: https://secure.travis-ci.org/msabramo/python-globtailer.png
   :target: http://travis-ci.org/msabramo/python-globtailer

A generator that yields lines from the most recently modified file matching a glob pattern

Example::

    tailer = TailMostRecentlyModifiedFileMatchingGlobPatternGenerator("/path/to/log*")

    for line in tailer:
        print(line)
