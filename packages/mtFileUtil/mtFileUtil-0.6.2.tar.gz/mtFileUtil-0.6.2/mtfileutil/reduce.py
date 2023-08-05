
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

DEFAULT_FACTOR=25

def thin(source_file, dest_file, interval=DEFAULT_FACTOR):
    """
    Take a large text file, keeps every n lines, strips out the rest.
    
    params:
        source_file    The file to read.  This file is not changed.

        dest_file      The file to create.  This will be a smaller
                       version of the original.

        interval       the interval between lines that are kept.  If
                       factor == 10, 9 lines will be discarded for
                       every line that is kept.

    May throw various I/O exceptions if the specified files cannot be
    read or written.  Handling these is the responsibility of the
    caller.
    """
    print "Writing every %d lines of %s to %s" %(interval, source_file, dest_file)
    in_stream = open(source_file)
    out_stream = open(dest_file, 'w')
    line_number = -1
    for line in in_stream:
        line_number += 1
        if line_number % interval == 0:
            out_stream.write(line)
    in_stream.close()
    out_stream.close()

