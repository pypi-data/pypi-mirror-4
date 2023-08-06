#! /usr/bin/env python
"""
Convert from one file format to another.
"""

from cmt_convert import (READERS, WRITERS)
from cmt_convert._utils import _get_next_name_in_sequence


def main():
    """
    Read a data file from one format and write it to another.

    =============
    Typical Usage
    =============

    ww3 Reader
    ----------

    Read Wave Watch III data from a Matlab file and write it as NetCDF
    
        convert data.mat data.nc --reader=ww3

    ESRI ASCII Raster File Reader
    -----------------------------

    Read Wave Watch III data from a Matlab file and write it as NetCDF
    
        convert data.asc data.nc --reader=asc
    """
    import argparse

    valid_readers = READERS.keys()
    valid_writers = WRITERS.keys()

    parser = argparse.ArgumentParser(description='Convert Matlab to netCDF')
    parser.add_argument('infile', type=argparse.FileType('r'))
    parser.add_argument('ncfile', default=None)
    parser.add_argument('--stdout', help='Print to stdout',
                         action='store_true', default=False)
    parser.add_argument('--clobber', help='Overwrite existing files',
                         action='store_true', default=False)
    parser.add_argument('--exist-action',
                        help='Action to take if file exists',
                        choices=['clobber', 'append', 'rename'],
                        default='clobber')
    if len(valid_readers) > 0:
        parser.add_argument('--reader', help='Input file reader',
                            choices=valid_readers,
                            default=valid_readers[0])
    if len(valid_writers) > 0:
        parser.add_argument('--writer', help='Input file writer',
                            choices=valid_writers,
                            default=valid_writers[0])

    args = parser.parse_args()

    if args.exist_action == 'clobber':
        name = args.ncfile
        #append = False
    elif args.exist_action == 'append':
        name = args.ncfile
        #append = True
    elif args.exist_action == 'rename':
        name = _get_next_name_in_sequence(args.ncfile)
        #append = False

    grids = READERS[args.reader](args.infile)

    WRITERS[args.writer](name, grids)

    return

if __name__ == '__main__':
    main()
