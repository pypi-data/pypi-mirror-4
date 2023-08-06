#! /usr/bin/env python
"""
Reader for raster data contained in an ESRI ASCII file.
"""
import os
import types

import numpy as np

from cmt_convert.decorator import ReaderPlugin
from cmt.grids import RasterField


STANDARD_NAME = {
    'RCKv': 'sea_floor_exposed_rock__area_percent',
    'GVLv': 'sea_floor_sediment_gravel__volume_percent',
    'SNDv': 'sea_floor_sediment_sand__volume_percent',
    'MUDv': 'sea_floor_sediment_mud__volume_percent',
    'GRZv': 'sea_floor_sediment__krumbein_phi_diameter',
    'SRTv': 'sea_floor_sediment__grain_sorting',
    'CRBv': 'sea_floor_sediment_carbonate__volume_percent',
    'RCKu': 'sea_floor_exposed_rock__uncertainty_of_area_percent',
    'GVLu': 'sea_floor_sediment_gravel__uncertainty_of_volume_percent',
    'SNDu': 'sea_floor_sediment_sand__uncertainty_of_volume_percent',
    'MUDu': 'sea_floor_sediment_mud__uncertainty_of_volume_percent',
    'GRZu': 'sea_floor_sediment__uncertainty_of_krumbein_phi_diameter',
    'SRTu': 'sea_floor_sediment__uncertainty_of_grain_sorting',
    'CRBu': 'sea_floor_sediment_carbonate__uncertainty_of_volume_percent',
}

STANDARD_UNITS = {
    'RCKv': 'percent',
    'GVLv': 'percent',
    'SNDv': 'percent',
    'MUDv': 'percent',
    'GRZv': '1',
    'SRTv': '1',
    'CRBv': 'percent',
    'RCKu': 'percent',
    'GVLu': 'percent',
    'SNDu': 'percent',
    'MUDu': 'percent',
    'GRZu': '1',
    'SRTu': '1',
    'CRBu': 'percent',
}

def _quantity_name_from_file_name(file_name):
    """
    Get a short quantity name from a file name. This plugin reads ESRI ASCII files
    whose names are of the form <prefix>_<short_name>.asc, where <prefix> is
    any string and <short_name> is a four letter key indicating the quantity
    described by the file.

    :file_name: Name of an ESRI ASCII file

    :returns: A string of the short name
    """
    (base, _) = os.path.splitext(file_name)
    return base.split('_')[-1]

def _standard_name_from_file_name(file_name):
    """
    Make a standard name from a file name.

    :file_name: Name of an ESRI ASCII file

    :returns: A string of the standard name
    """
    short_name = _quantity_name_from_file_name(file_name)
    return STANDARD_NAME[short_name]

def _standard_units_from_file_name(file_name):
    """
    Make a standard units string from a file name.

    :file_name: Name of an ESRI ASCII file

    :returns: A string of the standard units
    """
    short_name = _quantity_name_from_file_name(file_name)
    return STANDARD_UNITS[short_name]

def _read_asc_header(name):
    """
    Read header information from an ESRI ASCII raster file.

    The header contains the following,
        :ncols: Number of columns
        :nrows: Number of rows
        :xllcorner: X (columne) coordinate of lower-left coordinate of grid
        :yllcorner: Y (row) coordinate of lower-left coordinate of grid
        :cellsize: Grid spacing between rows and columns
        :nodata_value: No-data value

    TODO:
        - nodata_value is optional
        - xllcorner or xllcenter
        - yllcorner or yllcenter
    """
    from itertools import islice

    required_keys = set(['ncols', 'nrows', 'xllcorner', 'yllcorner',
                          'cellsize', 'NODATA_value'])

    header = {}
    for line in list(islice(name, len(required_keys))):
        items = line.split()
        if items[0] in required_keys:
            header[items[0]] = items[1]
        else:
            raise KeyError(items[0])

    return header


def _read_asc_data(asc_file):
    """
    Read gridded data from an ESRI ESCII data file.

    :asc_file: File-like object of the data file pointing to the start of the
               data

    Note
    ----

    Row 1 of the data is at the top of the raster, row 2 is just under row 1,
    and so on.
    """
    return np.genfromtxt(asc_file)


@ReaderPlugin('esri')
def asc(asc_file):
    """
    Read data from an ESRI_ ASCII file into a RasterField.

    :asc_file: Name of the ESRI ASCII file or a file-like object

    .. _ESRI: http://resources.esri.com/help/9.3/arcgisengine/java/GP_ToolRef/spatial_analyst_tools/esri_ascii_raster_format.htm
    """
    if isinstance(asc_file, types.StringTypes):
        file_name = asc_file
        with open(file_name, 'r') as asc_file:
            header = _read_asc_header(asc_file)
            data = _read_asc_data(asc_file)
    else:
        file_name = asc_file.name
        header = _read_asc_header(asc_file)
        data = _read_asc_data(asc_file)

    standard_name = _standard_name_from_file_name(file_name)
    standard_units = _standard_units_from_file_name(file_name)

    shape = (int(header['nrows']), int(header['ncols']))
    spacing = (float(header['cellsize']), float(header['cellsize']))
    origin = (float(header['xllcorner']), float(header['yllcorner']))

    grid = RasterField(shape, spacing, origin, indexing='ij')
    grid.add_field(standard_name, data, centering='point', units=standard_units)

    return [(0, grid)]
