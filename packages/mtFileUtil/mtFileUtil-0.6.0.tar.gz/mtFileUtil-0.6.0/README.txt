=============
MT File Utils
=============


Overview
========

MT File Utils provides a simple API for common I/O tasks on text
files.

 * **Tail**: performs like the linux 'tail' command.
 * **Reverse Seek**:  Starting at the end of a file, returns all the
   lines until a specific target is found
 * **Reader**: High-performance API for reading lines from a text file.
   Most useful when you need fast concurrent access to very large data
   sets that don't fit in memory.  Supports multithreaded access,
   random or sequential reads.


Compatibility
=============

MT File Utils has been tested in cpython (2.7) and jython (2.5).


Use
===

For each example below, assume a file named 'data.txt' with one number per line::

    1
    2
    3
    ...
    9999


tail
----

Functions like the standard unix tail command.  ("follow" or "-f" not supported.)
Pass in the file name, and the max number of lines you want returned::

    >>> from mtfileutil.reverse import tail
    >>> tail('data.txt', 5)
    ['9995', '9996', '9997', '9998', '9999']
    
    
reverse_seek
------------

Searches backward from the end of a file for target text.  Returns a list of each line
between the end of the file and the target::

    >>> from mtfileutil.reverse import reverseSeek
    >>> reverseSeek('data.txt', '994')
    '994' found after searching back 6 lines.
    ['9994', '9995', '9996', '9997', '9998', '9999']

You can specify how far back to seek.  The default limit is 3000 lines::

    >>> from mtfileutil.reverse import reverseSeek
    >>> reverseSeek('data.txt', 'loot')
    'loot' not found in final 3000 lines of data.txt
    >>> reverseSeek('data.txt', '9993', max=5)
    '9993' not found in final 5 lines of data.txt
    []
    >>> reverseSeek('data.txt', '9993', max=10)
    '9993' found after searching back 7 lines.
    ['9993', '9994', '9995', '9996', '9997', '9998', '9999']
    
    
    
read random
-----------
The random reader selects a random line from a given text file
every time it is invoked.  

*CAUTION:  The random nature of these reads typically defeats the 
page caching strategies used by your OS, so for large text files that
don't fit entirely in memory, it's easy to saturate your disk 
I/O capacity with this reader.*

The typical pattern is to start a reader by assigning it a text file
to read and a queue name to use, use the reader as desired, then stop
the reader::

    >>> from mtfileutil import reader
    >>> reader.startRandomReader('data.txt', 'rand_queue')
    Initializing random line queues[rand_queue](100)
    Initializing random line reader thread (data.txt)
    Data reader thread starting against file 'data.txt', size 48887
    Populating random queue
    >>> reader.getRandomLine('rand_queue')
    '7276'
    >>> reader.getRandomLine('rand_queue')
    '8452'
    >>> reader.getRandomLine('rand_queue')
    '640'
    >>> reader.stopRandomReader('rand_queue')
    Data reader received signal to end
    
    



read sequential
---------------
For large files that don't fit in memory, this is much friendlier on
your disk I/O because the data can be read and used in entire blocks.
Makes a "best effort" to remember (bookmark) your location between reads,
that will typically be off by the maximum queue size.  For text files with
many millions of lines this is probably not a big deal, but may be
a consideration when using repeatedly with smaller files.

As with the random reader, the typical pattern is to start a reader,
use the reader, then stop the reader.  The bookmark is not saved until
you stop the reader, so this step is required if you want the reader to
bookmark its location between runs::

    >>> from mtfileutil import reader
    >>> reader.startSequentialReader('./data.txt', 'seq_queue')
    Initializing sequential line queue[seq_queue](100)
    Initializing sequential line reader thread[seq_queue] (./data.txt)
    Data reader thread starting against file './data.txt', size 48887
    Reading data file './data.txt' from 0
    >>> reader.getNextLine('seq_queue')
    '1'
    >>> reader.getNextLine('seq_queue')
    '2'
    >>> reader.getNextLine('seq_queue')
    '3'
    >>> reader.stopSequentialReader('seq_queue')
    Data reader received signal to end
    Writing seek position 312 to temp file ./data.txt.seek
    Sequential data reader thread ending normally

Subsequent invocations will remember the approximate location of the
last line you read.  A subsequent python shell might look like this::

    >>> from mtfileutil import reader
    >>> reader.startSequentialReader('./data.txt', 'seq_queue')
    Initializing sequential line queue[seq_queue](100)
    Initializing sequential line reader thread[seq_queue] (./data.txt)
    Data reader thread starting against file './data.txt', size 48887
    >>> Reading data file './data.txt' from 312
    >>> reader.getNextLine('seq_queue')
    '106'
    >>> reader.getNextLine('seq_queue')
    '107'
    >>> reader.getNextLine('seq_queue')
    '108'
    >>> reader.stopSequentialReader('seq_queue')
    Data reader received signal to end
    Waiting for sequential line reader 'seq_queue' to end
    Writing seek position 732 to temp file ./data.txt.seek
    Sequential data reader thread ending normally

As you can see, the bookmarked location is about 100 lines ahead of
the last line read.  The amount of variance depends on the size of
the read-ahead queue, which is sized at 100 by default.

If you want to start reading the file from the beginning each time, the
bookmark feature can be disabled.::

    >>> from mtfileutil import reader
    >>> reader.startSequentialReader('./data.txt', 'seq_queue', start_at_last_read_location=False)
    Initializing sequential line queue[seq_queue](100)
    Initializing sequential line reader thread[seq_queue] (./data.txt)
    Data reader thread starting against file './data.txt', size 48887
    Reading data file './data.txt' from 0
    >>> reader.getNextLine('seq_queue')
    '1'



Examples
========
        
Example scripts are included in the package:

 * mtfu_read_random_example.py
 * mtfu_read_sequential_multithread_example.py
 * mtfu_read_sequential_singlethread_example.py
 * mtfu_reverse_seek_example.py
 * mtfu_tail_example.py


Source
======

Source code and additional detail available here:
https://bitbucket.org/travis_bear/file_util

Patches accepted.
