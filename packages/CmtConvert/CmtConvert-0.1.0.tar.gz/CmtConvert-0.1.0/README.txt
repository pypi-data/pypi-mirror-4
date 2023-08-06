====
CSDMS File Conversion Utilities
====

package name: cmt_convert
version: 0.1
release date: 2013-03-09

The CSDMS File Conversion provides utilities for converting various data
file formats.

    #! /usr/bin/env python

    from cmt_convert import (READERS, WRITERS)

    print 'Valid readers: %s' % READERS.keys ()
    print 'Valid writers: %s' % WRITERS.keys ()

Install
=======

    easy_install cmt_convert

Author
======

author: Eric Hutton
email: eric.hutton@colorado.edu

