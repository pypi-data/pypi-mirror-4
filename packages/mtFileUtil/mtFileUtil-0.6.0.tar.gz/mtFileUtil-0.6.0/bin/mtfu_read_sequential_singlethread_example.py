#!/usr/bin/env python

import sys
from threading import Thread
from mtfileutil import reader

if len(sys.argv) != 3:
    print "usage: mtfu_read_sequential_multithread_example.py <data file> <# of lines to read> <# threads>"
    sys.exit(1)
data_file = sys.argv[1]
times = int(sys.argv[2])
queue_name = "test-queue"


reader.startSequentialReader(data_file, queue_name)
for i in range(0,times):
    print reader.getNextLine(queue_name)

# this part is important.  Without it, future invocations
# will not seek to the correct location in the file.
reader.stopSequentialReader(queue_name)
print "Test complete"

