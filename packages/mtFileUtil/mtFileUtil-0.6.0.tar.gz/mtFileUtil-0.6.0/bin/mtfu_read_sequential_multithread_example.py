#!/usr/bin/env python

import sys
from threading import Thread
from mtfileutil import reader


class TestThread(Thread):
    def __init__(self, iterations, name):
        Thread.__init__(self, name=name)
        self.iterations = iterations
        
    def run(self):
        print "Starting thread %s, reading %d times" % (self.getName(), self.iterations)
        for i in range(0, self.iterations):
            line = reader.getNextLine(queue_name)
            print "Thread %s: %s" % (self.getName(), line)
    


if len(sys.argv) != 4:
    print "usage: mtfu_read_sequential_multithread_example.py <data file> <# of lines to read> <# threads>"
    sys.exit(1)
data_file = sys.argv[1]
times = int(sys.argv[2])
queue_name = "test-queue"

reader.startSequentialReader(data_file, queue_name)
thread_count = int(sys.argv[3])
threads = []
for i in range (0, thread_count):
    th = TestThread(times, "th %d" %i)
    threads.append(th)
    th.start()

# wait for completion
for th in threads:
    th.join()

# this part is important.  Without it, future invocations
# will not seek to the correct location in the file.
reader.stopSequentialReader(queue_name)
print "Test complete"

