#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""A python module for fetching Collectd CSV data from a CollectD data 
directory matching a specified time interval and regular expressions.
(c) Petteri Tolonen (petteri.tolonen@gmail.com), 2012
This code is licensed under the FreeBSD license. See LICENSE.txt for the 
full license text.
"""

import os
import re
import glob
import time
from datetime import date,timedelta
from collections import OrderedDict

#import all the plugins. Use with plugins.<plugin name>.function
import plugins

#The maximum number of CSV files to read, so that it won't take too
#long to fetch the data.
MAX_DATAFILES = 10000

class MyError(Exception): pass

def readEpochLines(filename, header, epoch_start, epoch_end):
    """
    Read lines from collectd CSV file and return
    a list containing the lines that match the given time interval
    Arguments:
        filename: The path and name to the data file to be read
        header: Boolean describing if header should be included in the result
        epoch_start: The start epoch (timestamp) of the wanted timeframe
        epoch_end: The end epoch (timestamp) of the wanted timeframe
    Returns:
        a list containing the lines between the start and end epoch. 
    """
    line = ""
    output = list()
    with open(filename, "r") as infile:
	#Read the header if wanted, otherwise throw it away
        if header:
            output.append(infile.readline()[:-1])
        else:
            infile.readline()
           
        #This hack makes the reading faster, when there are a lot of 
        #measurements. it tries to calculate the starting line and read until
        #that faster. It assumes, that the data lines in CSV are the same 
        #length, and that the measurement 
        #interval (step) doesn't change in the file. If you are sure these 
        #assumptions are true for you, then it should be safe to uncomment this.
        """   
        line1 = infile.readline()
        line2 = infile.readline()
        epoch1 = float(line1.split(",", 1)[0])
        epoch2 = float(line2.split(",", 1)[0])
        step = (epoch2 - epoch1)
        epochdiff = epoch_start - epoch1
        if epochdiff > 0:
            infile.readlines(int(len(line1)*(epochdiff/(step + 1))))
        """
	#Read the lines until we get out of desired range or there are
        #no more lines
        while True:
            line = infile.readline()
            if len(line) == 0:
                break
            #remove the newline
            line = line[:-1]
            current_epoch = float(line.split(",", 1)[0])
            if current_epoch > epoch_end:
                break
            elif current_epoch >= epoch_start:
                output.append(line)

    return output

def storeResourceData(resourcename, datastrlist, targetpath, datadict):
    """Store the one resource data for later usage. Use targetpath
    and resourcename to write the data in a file, unless targetpath 
    is None. In the latter case, save the data in datadict.
    Arguments:
        resourcename: The name of the data file without the ending
        datastrlist: The lines to be saved
        targetpath: The path to the directory, where the data file 
                    is to be written. None, if the data is to be
                    returned in a dictionary.
        datadict: Ordered dictionary, where key is the resource name
                  and and value is a list containing the data for that
                  resource.
    Returns:
        Was some data saved?
    """

    #If the resource name is given and there is more than just the header
    if resourcename and len(datastrlist) > 1:
        
        plugin_name = resourcename.split("__")[-1].split("_",1)[-1] 
        
        #transform output with a plugin if available
        try:
            plugin = getattr(plugins, plugin_name)
            datastrlist = plugin.convert(datastrlist)
        except Exception as e:
            pass

        if targetpath == None:
            datadict[resourcename] = datastrlist
        else:
            with open(targetpath + resourcename + ".dat", "w+") as outfile:
                outfile.write("\n".join(datastrlist))
        return True
    return False

def fetchData(epoch_start, epoch_end, regexps, csvdatadir, destdir):
    """
    Fetch the data from the given timeframe matching at least one of the given
    regexps. Additionally Generate the plots with gnuplot if wanted.
    The output identifiers (filenames without ending, when writing to disk 
    or dict keys otherwise.) are in format: hostname__resource_measurement
    Arguments:
        epoch_start: The starting epoch (seconds from 1970-01-01 00:00:00 UTC)
        epoch_end: The ending epoch
        regexps: a list containing regexps (strings).
        csvdatadir: a collectd-style CSV data directory root
        destdir: The directory in which the data and plots shall be written.
                 If 'None' then the data is returned in an ordered dictionary.
    Returns:
        If destdir is None, then ordered dict containing the data. (Keys are
        output identifiers, values are lists containing the data by resource.)
        Otherwise returns nothing.
    """

    if epoch_start < 0:
        raise MyError("Negative epoch start timestamp: " + epoch_start)
    if epoch_end < 0:
        raise MyError("Negative epoch end timestamp: " + epoch_end)
    if len(regexps) == 0:
        raise MyError("At least one regexp has to be given!")

    if not os.path.isdir(csvdatadir):
        raise MyError("'"+csvdatadir+"' is not a directory.")
    if not os.access(csvdatadir, os.R_OK):
        raise MyError("'"+csvdatadir+"' is not readable.")
    if destdir != None:
        if not os.path.isdir(destdir):
            raise MyError("'"+destdir+"' is not a directory.")
        if not os.access(destdir, os.W_OK):
            raise MyError("'"+destdir+"' is not writable.")
        destdir = os.path.abspath(destdir) + os.sep

    date_start = date.fromtimestamp(epoch_start)
    date_end = date.fromtimestamp(epoch_end)
   
    #How many days (files) is the data from the timeframe saved
    daycount = (date_end - date_start).days + 1
    #Get the ISO date strings ("YYYY-MM-DD") for the date range
    isodaylist = [(date_start + timedelta(n)).isoformat() 
                  for n in range(daycount)]

    datadict = OrderedDict()
    resourcename = ""
    datastrlist = list()
    paths = list()

    for f in glob.iglob(csvdatadir+(os.sep+"*")*3):
       
        #if any of the requested dates exists in the filename and if the i
        #filename matches the regular expression given in the command line
        ftail = f.split(csvdatadir+os.sep)[-1]
        for d in isodaylist:
            if d in ftail:
                for r in regexps:
                    if re.search(r, ftail):
                        paths.append(f)
		        #the file matched one regexp, so will choose that. 
                        #No need to check further regexps
                        break

    if len(paths) > MAX_DATAFILES:
        raise MyError("The data you are trying to fetch is spread across " + 
                      str(len(paths)) + " CSV files. Reading data from this \
                      many files will probably take several minutes. Please \
                      adjust the time interval and regexp(s). If you are \
                      sure you want to do this, you can set the value of \
                      MAX_DATAFILES higher in CollectdCSV.py.".strip("\n"))

    #glob doesn't guarantee the order of the filenames to be alphabetical. 
    #Need this so can assume that if certain part of the path changes, 
    #no measurements from the same set will appear.
    paths.sort()
    for path in paths:
       
        #Resource name is the end of the path without the iso date stamp
        resource = path.rsplit("-", 3)[0].split(csvdatadir + os.sep, 1)[-1]
        newresourcename = resource.replace(os.sep, "__", 1)

        #If saving to a file, the resource mustn't contain directory separators
        if destdir != None:
            newresourcename = newresourcename.replace(os.sep, "_")
      
        #another file from the same set (measurement)
        if resourcename == newresourcename: 
           
            #if this is not the last file in the set, just read all of it
            if isodaylist[-1] not in path:
                with open(path, "r") as infile:
                    infile.readline()
                    datastrlist.extend(infile.read().split("\n"))
            #otherwise read line by line and check
            else:
                datastrlist.extend(readEpochLines(path, False, 
                                   epoch_start, epoch_end))

        #The last measurement in set / New measurement
        else:
            #Store the old resource data
            dataexists = storeResourceData(resourcename, datastrlist, 
                                           destdir, datadict)
            #Read the new measurement
            #here the file might be cut from both ends (just want a small 
            #timeframe from the middle of a file)
            datastrlist = readEpochLines(path, True, epoch_start, epoch_end)
            resourcename = newresourcename
 
    #The last resource data is not stored in loop, so do it now
    dataexists = storeResourceData(resourcename, datastrlist, destdir,
                                   datadict)

    if not dataexists:
        raise MyError("No data in the given time interval with the given\
regexps.")
    if destdir == None:
        return datadict
