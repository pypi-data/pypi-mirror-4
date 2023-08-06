#! /usr/bin/env python
"""
Regrid data stored in a NetCDF file based on a mesh provided by another
file.
"""

import numpy as np

from cmt.nc import field_tofile, fromfile
from cmt.mappers import NearestVal, RadialBasisFunction
from cmt.mappers import EsmpPointToPoint as Bilinear
from cmt.mappers import RectBivariateSpline as SplineMapper

from cmt_convert._utils import _get_next_name_in_sequence


def main():
    """
    Regrid data in a NetCDF file based on the mesh of another.

    =============
    Typical Usage
    =============

    Regrid
    ------

    Regrid data contained on the mesh described in src.nc NetCDF file to the
    grid described in dest.nc. Print the result as a NetCDF file to stdout.
    
        map src.nc dest.nc --stdout
    """
    import argparse

    parser = argparse.ArgumentParser(description='Remap grids')
    parser.add_argument(
        'src', help='NetCDF file describing source grid and field values')
    parser.add_argument('dst', help='NetCDF file describing destination grid')
    parser.add_argument('outfile', help='NetCDF file of remapped values')
    parser.add_argument('--mapper', help='Mapper to use for regridding',
                        choices=['csdms', 'esmp', 'spline', 'rbf'],
                        default='csdms')
    parser.add_argument('--stdout', help='Print to stdout',
                        action='store_true', default=False)
    parser.add_argument('--exist-action',
                        help='Action to take if file exists',
                        choices=['clobber', 'append', 'rename'],
                        default='clobber')

    args = parser.parse_args()

    if args.exist_action == 'clobber':
        name = args.outfile
        append = False
    elif args.exist_action == 'append':
        name = args.outfile
        append = True
    elif args.exist_action == 'rename':
        name = _get_next_name_in_sequence(args.outfile)
        append = False

    print 'Reading source grid'
    src_fields = fromfile(args.src)
    print 'Reading destination grid'
    dst_field = fromfile(args.dst, just_grid=True)

    mapper_name = args.mapper.upper()
    if mapper_name == 'ESMP':
        import ESMP
        ESMP.ESMP_Initialize()

        mapper = Bilinear()
        mapper.initialize(dst_field, src_fields[0][1],
                          method=ESMP.ESMP_REGRIDMETHOD_BILINEAR,
                          unmapped=ESMP.ESMP_UNMAPPEDACTION_IGNORE)
    elif mapper_name == 'RBF':
        print 'Create mapper'
        mapper = RadialBasisFunction()
        print 'Init mapper'
        mapper.initialize(dst_field, src_fields[0][1], function='linear')
    elif mapper_name == 'SPLINE':
        print 'Create spline mapper'
        mapper = SplineMapper()
        print 'Init mapper'
        mapper.initialize(dst_field, src_fields[0][1])
    else:
        mapper = NearestVal()
        mapper.initialize(dst_field, src_fields[0][1])

    print 'Run mapper'
    time, field = src_fields[0]
    for field_name in field.keys():
        src = field.get_field(field_name)
        print 'Masking NaNs with 0.'
        src[np.isnan(src)] = 0.
        dst_value = mapper.run(field.get_field(field_name))
        dst_field.add_field(field_name, dst_value,
                            centering='point', units='m')
    field_tofile(dst_field, name, append=append, time_units='days', time=time)

if __name__ == '__main__':
    main()
