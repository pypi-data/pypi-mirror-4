#!/usr/bin/env python

from mtfileutil.reverse import reverseSeek
import sys

if len(sys.argv) != 3:
    print "usage: reverse_seek.py <data file> <search target>"
    sys.exit(1)

filename=sys.argv[1]
target=sys.argv[2]
for line in reverseSeek(filename, target):
    print line