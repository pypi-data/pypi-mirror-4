#!/usr/bin/env python

from mtfileutil import reverse
import sys

if len(sys.argv) != 3:
    print "usage: tail.py <data file> <# of lines to read>"
    sys.exit(1)

filename=sys.argv[1]
lines=sys.argv[2]
for line in reverse.tail(filename, lines):
    print line