#!/usr/bin/env python

import sys
from mtfileutil import reader

if len(sys.argv) != 3:
    print "usage: mtfu_read_random_example.py <data file> <# of lines to read>"
    sys.exit(1)
data_file = sys.argv[1]
times = int(sys.argv[2])

print "reading %d lines from %s" %(times, data_file)
queue_name="test-queue"
reader.startRandomReader(data_file, queue_name)
for i in range (0,times):
    print reader.getRandomLine(queue_name)
