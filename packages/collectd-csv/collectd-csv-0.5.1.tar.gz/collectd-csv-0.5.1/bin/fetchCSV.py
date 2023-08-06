#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""A simple command line tool for fetching CollectD CSV data from a
specified time interval and matching given regular expressions.
The data is saved in .dat-files in a specified directory.
This tool is part of CollectD-CSV package. It uses CollectD_CSV-module
for fetching the data.
(c) Petteri Tolonen (petteri.tolonen@gmail.com), 2012
This code is licensed under the FreeBSD license. See LICENSE.txt for the 
full license text.
"""

import CollectD_CSV
import argparse
import time
import sys
import os

#The default argparser doesn't print the help when there's an error
class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write("Error: %s\n\n" % message)
        self.print_help()
        sys.exit(2)

if __name__ == "__main__":
    
    desc = """Collectd CSV data fetching tool. Fetch data from the given 
            interval that match with at least one of the given regexps."""
    parser = MyParser(description=desc)

    #The time interval must be given
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-e", action="store", dest="epoch", nargs=2, type=int,
                       help="""Select data from a time interval specified as 
                            epoch timestamps.""")
    group.add_argument("-m", action="store", dest="minutes", type=int,
                       help="Select data from the last MINUTES minutes")

    parser.add_argument("-d", action="store", dest="datadir", 
                        default="/var/lib/collectd", 
                        help="""The CSV data directory. 
                             Default: /var/lib/collectd""") 
    parser.add_argument("-r", action="store", dest="regexp", nargs="*", 
                        default=[".*"], 
                        help="""Selection of the desired
                             resources as regexps. You can give as many
                             regexps as you wish. Default: .* (all)""")
    parser.add_argument("-o", action="store", dest="outdir", default="./",
                        help="""The directory where to save the fetched data
                             files. Default: ./""")
    
    params =  parser.parse_args()
 
    #If there's no epochs given, then time has to be minutes!
    #Epochs and minutes already limited to ints, by argparser
    if params.epoch == None:
        epoch_end = int(time.time())
        epoch_start = epoch_end - params.minutes*60
    else:
        epoch_start = params.epoch[0]
        epoch_end = params.epoch[1]

    #get absolute input and output paths from command line parameters
    #this also makes the path representations uniform (removes trailing slash)
    params.datadir = os.path.abspath(params.datadir)
    params.outdir = os.path.abspath(params.outdir)

    try:
        if params.minutes < 0:
            raise CollectD_CSV.MyError("Invalid negative minutes: '" + 
                                      params.minutes + "'")
        print("Writing data to: '" + params.outdir + "'") 
        CollectD_CSV.fetchData(epoch_start, epoch_end, params.regexp, 
            params.datadir, params.outdir)
        print("Done!")
    except CollectD_CSV.MyError as e:
        parser.error(str(e))
   

