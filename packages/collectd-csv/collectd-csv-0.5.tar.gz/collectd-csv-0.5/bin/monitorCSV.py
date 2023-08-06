#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""A simple command line tool for monitoring recent CollectD CSV data.
Calculates minimum, maximum and average of wanted measurements in the last 
XX minutes for the specified host. Prints results in a tabulated "pretty"
format for human reading, or CSV format for file output.
This tool is part of CollectD-CSV package. It uses CollectD_CSV-module
for fetching the data.
"""

import CollectD_CSV
import sys
import glob
import time
import os
import argparse
from collections import OrderedDict

class MyParser(argparse.ArgumentParser):
    """Argument parser doesn't print help text when it errors."""
    def error(self, message):
        sys.stderr.write("Error: %s\n\n" % message)
        self.print_help()
        sys.exit(2)

def listNodes(datadir):
    """
    Lists hosts that have data in the datadir directory. 
    Basically just does "ls" in datadir and puts the results in a list.
    Arguments:
        datadir: Full path to collectd data directory (without the last slash)
    """
    nodelist = list()
    for g in glob.iglob(datadir + os.sep + "*"):
        if os.path.isdir(g):
            nodelist.append(os.path.split(g)[-1])
    return sorted(nodelist)

def parseData(data):
    """
    Parses the Collectd CSV data into a more convenient dictionary format.
    Arguments:
        data: Ordered dict containing the data from fetchData()
    Returns:
        Ordered dict. 
    """
    parseddict = OrderedDict()
    for key, resourcedata in data.items():
        newkey = key.split("__", 1)[-1]
        parseddict[newkey] = [[] for k in range(len(resourcedata[0].split(",")))]
        parseddict[newkey][0] = resourcedata[0].split(",")[1:]
        for l in resourcedata[1:]:
            linedata = l.split(",")
            linedatalength = len(linedata)
            for x in range(1, linedatalength):
                try:
                    parseddict[newkey][x].append(float(linedata[x]))
                except ValueError as e:
                    #if it isn't a number, then it can't be used
                    pass
                
    return parseddict

def printReport(parsedData, formatting):
    """
    Prints the minimum, maximum and average of every measurement in the data
    Arguments:
        parsedData: The
        formatting: The output format of the report. "pretty" or "csv"
    """

    if formatting == "pretty":
        colwidths = [50,17,17,17]
        separator = "\t"
    elif formatting == "csv":
        colwidths = [0,0,0,0]
        separator = ","

    #print headers line
    print("measurement".ljust(colwidths[0]) + separator + 
          "min".ljust(colwidths[1]) + separator + 
          "average".ljust(colwidths[2]) + separator + 
          "max".ljust(colwidths[3]))
    if formatting == "pretty":
        print("-"*120)
    for resource, data in parsedData.items():
        datalength = len(data)
        for i in range(1, datalength):
            biggest = -1e+40
            smallest = 1e+40
            average = 0
            for n in data[i]:
                if n > biggest:
                    biggest = n
                if n < smallest:
                    smallest = n
                average += n
            average /= len(data[i])
            if data[0][i-1] != "value":
                line = resource + "-" + data[0][i-1]
            else:
                line = resource
            print(line.ljust(colwidths[0]) + separator + 
                  str(smallest).ljust(colwidths[1]) + separator + 
                  str(average).ljust(colwidths[2]) + separator + 
                  str(biggest).ljust(colwidths[3]))

            
if __name__ == "__main__":
    
    parser = MyParser(description="""Collectd CSV data monitoring tool.
    Calculates some characteristics (min, avg, max) from specified resources 
    of one host using recent CollectD CSV data.""")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-l", action="store_true", dest="listing", 
                       default=False, 
                       help="List the hosts available in the data directory")
    group.add_argument("-n", action="store", dest="hostname", 
                       help="The hostname of the host to monitor")

    parser.add_argument("-m", action="store", dest="minutes", type=int, 
                        default=10, 
                        help="""Get data from the last MINUTES minutes. 
                             Default: 10""")
    parser.add_argument("-d", action="store", dest="datadir", 
                        default="/var/lib/collectd", 
                        help="""The CSV data directory
                             Default: /var/lib/collectd""")
    parser.add_argument("-r", action="store", dest="regexp", nargs="*", 
                        default=[".*"], 
                        help="""Selection of the desired resources as regexps. 
                             You can give as many regexps as you wish. 
                             Default: .* (all)""")
    parser.add_argument("-f", action="store", dest="format",  
                        choices=["pretty","csv"], default="pretty", 
                        help="""Format used for printing the report. 
                             Default: pretty""")
    
    params =  parser.parse_args()
    nodelist = listNodes(params.datadir)
    params.datadir = os.path.abspath(params.datadir)

    try:
        if params.listing:
            if len(nodelist) == 0:
                raise CollectD_CSV.MyError("No readable host data in '" + 
                                          params.datadir + "'")
            print("In '"+params.datadir+"' there seems to be data from hosts:")
            for i in nodelist:
                print(i)
            sys.exit(0)
        if params.hostname not in nodelist:
            raise CollectD_CSV.MyError("'" + params.hostname + 
                                      "' is not a valid hostname in '" + 
                                      params.datadir + "'")
        if params.minutes < 0:
            raise CollectD_CSV.MyError("Invalid negative minutes: '" + 
                                      params.minutes + "'")
        
        epoch_end = int(time.time())
        epoch_start = epoch_end - params.minutes*60
        hostsinregexps = ["^"+params.hostname+"/.*"+x for x in params.regexp] 
        data = CollectD_CSV.fetchData(epoch_start, epoch_end, hostsinregexps,
                                     params.datadir, destdir=None)
        parsed = parseData(data)
        printReport(parsed, params.format)
    except CollectD_CSV.MyError as e:
        parser.error(str(e))
   

