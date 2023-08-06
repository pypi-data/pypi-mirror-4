#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#
# Transform interface octet and packet counts to speeds
#

def convert(oldlist):
    newlist = list()
    header = oldlist[0].split(",")
    header[1] = "out"
    header[2] = "in"
    newlist.append(",".join(header))

    previous_value = [float(value) for value in oldlist[1].split(",")]
    for line in oldlist[2:]:
        current_value = [float(value) for value in line.split(",")]
        duration = current_value[0] - previous_value[0]
        sentSpeed = ( current_value[1] - previous_value[1] ) / duration
        receiveSpeed = ( current_value[2] - previous_value[2] ) / duration
        newlist.append( str(current_value[0])+","+str(int(sentSpeed))+","+str(int(receiveSpeed)) )

        previous_value = current_value

    return newlist

