#
# reader is a python library supporting multithreaded access to text files
#
# Copyright (C) 2011-2012, Travis Bear
# All rights reserved.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA


import Queue
import os
import sys
import random
from threading import Thread
from threading import Lock

"""

"""

__author__ = "Travis Bear"


DEFAULT_QUEUE_SIZE = 100
JOIN_TIMEOUT = 2.5
SEEK_SUFFIX = "seek"

class AbstractDataReaderThread(Thread):
    fileSize = None
    _continue = None
    data_file = None    
    
    def __init__(self, dataFile):
        Thread.__init__(self)
        self.data_file = dataFile
        self._continue = True
        # handle the case where the file does not exist
        if not os.path.isfile(dataFile):
            print "FATAL: not a file: '" + dataFile + "'.  Aborting."
            sys.exit(1)     
        self.fileSize = os.stat(dataFile)[6] - 1
        if self.fileSize < 1:
            print "FATAL: empty data file '%s'.  Exiting." % dataFile
            sys.exit(1) 
        print "Data reader thread starting against file '%s', size %d" % (dataFile, self.fileSize)
        # TODO -- handle the case where there is no read access on the file
               
    def end(self):
        print "Data reader received signal to end"
        self._continue = False


    def run (self):
        raise NotImplementedError



class SequentialDataReaderThread (AbstractDataReaderThread):
    """
    Log reader thread -- tries to keep the queue full of new requests read from
    the apache log, but blocks when the queue can hold no more.  Expires when
    the log file has been completely processed.
    """
    recycleDataFile = None
    queue_name = None
    
    def __init__(self, data_file, queue_name, repeat, start_at_last_read_location):
        AbstractDataReaderThread.__init__(self, data_file)
        self.setName("Sequential Reader [%s]" % queue_name)
        self.recycleDataFile = repeat
        self.queue_name = queue_name
        self.initial_seek_location = 0
        self.seek_file_name = "%s.%s" %(self.data_file, SEEK_SUFFIX)
        if start_at_last_read_location:
            if not os.path.exists(self.seek_file_name):
                return
            line = open(self.seek_file_name).readline().strip()
            try:
                self.initial_seek_location = int(line)
            except:
                print "WARNING: Corrupted temp file '%s', line: %s" %(self.seek_file_name, line)
                self.initial_seek_location = 0
        
    def _readFile(self, seek_location):
        print "Reading data file '%s' from %d" % (self.data_file, seek_location)
        in_stream = open(self.data_file, 'r')
        in_stream.seek(seek_location)
        line = in_stream.readline().strip()
        while line:
            pos = in_stream.tell()
            if not self._continue:
                return pos
            seqential_line_queues[self.queue_name].put(line)
            line = in_stream.readline().strip()
        print "End of file"
        return 0
            
                    
    def run (self):
        position = self._readFile(self.initial_seek_location)
        while self.recycleDataFile and self._continue:
            #print "Finished reading data file %s.  Repeating." %self.data_file
            position = self._readFile(0)
        print "Writing seek position %d to temp file %s" %(position, self.seek_file_name)
        try:
            stream = open(self.seek_file_name, 'w')
            stream.write("%s\n" %position)
            stream.close()
            print "Sequential data reader thread ending normally"
        except:
            "ERROR: could not write to seek file '%s'.  Next invocation will start from the beginning of %s." %(self.seek_file_name, self.data_file)
        
    def end(self):
        print "Data reader received signal to end"
        self._continue = False
        try:
            # The queue is probably full.  That means this thread is blocked
            # on the call to queue.put(), and is unable to detect that it's
            # been signaled to stop.  Read (and ignore) a single item off the
            # queue to unblock it.
            seqential_line_queues[self.queue_name].get_nowait()
        except:
            print "Burn failed"



class RandomDataReaderThread(AbstractDataReaderThread):
    """
    Extract random lines from a data file.  Put them in a globally-accessible
    queue 
    """
    _input = None
    queue_name = None
    data_file = None
    
    def __init__(self, data_file, queue_name):
        AbstractDataReaderThread.__init__(self, data_file)
        self.data_file = data_file
        self._input = open(self.data_file)
        self.queue_name = queue_name
        
    def _getforwardLineSegment(self, seek_position):
        line_segment = ""
        self._input.seek(seek_position)
        ch = self._input.read(1)
        if not ch:
            return line_segment
        if ch != '\r' and ch != '\n':
            line_segment = line_segment + ch
        while ch != '\n' and seek_position < self.fileSize:
            seek_position += 1
            self._input.seek(seek_position)  
            ch = self._input.read(1)
            if ch != '\r' and ch != '\n':
                line_segment = line_segment + ch
        return line_segment
    
    def _getReverseLineSegment(self, seek_position):
        line_segment = ""
        if not seek_position > 0:
            return line_segment
        self._input.seek(seek_position)
        ch = self._input.read(1)
        if not ch:
            return line_segment
        if ch != '\r' and ch != '\n':
            line_segment = ch + line_segment
        while ch != '\n' and seek_position > 0:
            seek_position -= 1
            self._input.seek(seek_position)
            ch = self._input.read(1)
            if ch != '\r' and ch != '\n':
                line_segment = ch + line_segment
        return line_segment
    
    def getRandomLineFromFile(self):
        retry_count = 0
        max_retry_count = 5
        randomPosition = random.randint(1, self.fileSize)
        line = self._getReverseLineSegment(randomPosition - 1) + self._getforwardLineSegment(randomPosition)
        while line == "" and retry_count < max_retry_count:
            line = self.getRandomLineFromFile()
        return line
    
    def run(self):
        print "Populating random queue"
        while self._continue:
            random_line_queues[self.queue_name].put(self.getRandomLineFromFile())
        print "Random data reader thread shutting down normally."
        self._input.close()



def startRandomReader(data_file, queue_name=None, queue_size=DEFAULT_QUEUE_SIZE):
    """
    Starts a single instance of the random line reader thread.
    Subsequent calls to this function will not start additional
    threads.
    """
    global random_line_queues
    global random_line_threads
    lock.acquire()
    if not random_line_queues.has_key(queue_name):
        print "Initializing random line queues[%s](%d)" % (queue_name, queue_size)
        random_line_queues[queue_name] = Queue.Queue(queue_size)
        print "Initializing random line reader thread (%s)" % data_file
        random_line_threads[queue_name] = RandomDataReaderThread(data_file, queue_name)
        random_line_threads[queue_name].setDaemon(True)
        random_line_threads[queue_name].start()
    else:
        print "Random reader previously started.  No action taken."
    lock.release()
    

def stopRandomReader(queue_name):
    random_line_threads[queue_name].end()
    #del random_line_queues[queue_name]


def getRandomLine(queue_name):
    """
    Returns the next item in the 'random line' queue
    """
    return random_line_queues[queue_name].get()



def startSequentialReader(data_file,
                          queue_name,
                          queue_size=DEFAULT_QUEUE_SIZE,
                          repeatReads=True,
                          start_at_last_read_location=True):
    """
    Starts a single instance of the sequential line reader thread.
    Subsequent calls to this function will not start additional
    threads.
    """
    global seqential_line_queues
    global sequential_line_threads
    lock.acquire()
    if not seqential_line_queues.has_key(queue_name):
        print "Initializing sequential line queue[%s](%d)" % (queue_name, queue_size)
        seqential_line_queues[queue_name] = Queue.Queue(queue_size)
        print "Initializing sequential line reader thread[%s] (%s)" % (queue_name, data_file)
        sequential_line_threads[queue_name] = SequentialDataReaderThread(data_file,
                                                                         queue_name,
                                                                         repeatReads,
                                                                         start_at_last_read_location)
        sequential_line_threads[queue_name].setDaemon(True)
        sequential_line_threads[queue_name].start()
    else:
        print "Random reader previously started.  No action taken."
    lock.release()

def stopSequentialReader(queue_name):
    #global seqential_line_queues
    sequential_line_threads[queue_name].end()
    print "Waiting for sequential line reader '%s' to end" % queue_name
    sequential_line_threads[queue_name].join(JOIN_TIMEOUT)
    if sequential_line_threads[queue_name].isAlive():
        print "ERROR: sequential line reader thread failed to end normally"
    
def getNextLine(queue_name):
    """
    Returns the next item in the 'next line' queue
    """
    line = seqential_line_queues[queue_name].get()
    #print "got '%s' from queue" %line
    return line


random_line_queues = {}
random_line_threads = {}
seqential_line_queues = {}
sequential_line_threads = {}
lock = Lock()
