============
CollectD-CSV
============

CollectD-CSV is a small project providing utilities for analyzing CollectD 
CSV data locally. 

CollectD_CSV module provides functions for fetching data with a specified 
time interval and regular expressions matching the end of the path excluding
the datestamp. The fetched data can be saved into files or returned as an 
ordered dictionary.

fetchCSV.py script can be used to fetch the data matching the given parameters
and save to files in a specified directory.

monitorCSV.py script calculates the minimum, average and maximum values of 
specified resources on one host from the last XX minutes.

Typical usage of the module looks like this::

    #!/usr/bin/env python

    import CollectD_CSV
    from collections import OrderedDict

    regexps = ["myhost/load.*", "myotherhost/memory.*"]

    #fetch the data into an ordered dictionary
    resultdirct = CollectD_CSV.fetchData(123456789, 123498765, regexps, 
                                         "/var/lib/collectd", destdir=None)


See more information about the usage in the comments of CollectD_CSV.py.
For complete usage examples, see bin/fetchCSV.py and bin/monitorCSV.py.
For help in using the scripts use the "-h" command line option.


