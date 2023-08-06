#! /usr/bin/env python
"""
Reader and writer for Wave Watch III data stored in a Matlab file.
"""

import scipy

from cmt.grids import RectilinearField
from cmt.nc import field_tofile

from cmt_convert.decorator import ReaderPlugin, WriterPlugin


@ReaderPlugin()
def ww3(name):
    """
    Read a MATLAB file that describes some Wave Watch III output.

    Data contained within the Matlab file includes:
        - sea_water__depth
        - sea_surface_wave__significant_height
        - sea_surface_wave__max_over_time_of_period
        - model_grid_cell_center__latitude
        - model_grid_cell_center__longitude
        - time

    :name: Name of Matlab file containing WWIII data
    """
    var_map = dict(
        h='sea_water__depth',
        Hs='sea_surface_wave__significant_height',
        Ptop='sea_surface_wave__max_over_time_of_period',
        lat_grid='model_grid_cell_center__latitude',
        lon_grid='model_grid_cell_center__longitude',
        timestamp='time',
    )

    data = scipy.io.loadmat(name)
    for (key, value) in var_map.items():
        data[value] = data.pop(key)

    lat = data['model_grid_cell_center__latitude']
    lon = data['model_grid_cell_center__longitude']

    attrs = dict(description=data['README'], version=data['__version__'])

    grid = RectilinearField(lat[:, 0], lon[0, :], indexing='ij', attrs=attrs,
                            units=('degrees_north', 'degrees_east'))
    grid.add_field('sea_water__depth', data['sea_water__depth'],
                    centering='point', units='m')
    grids = [(0., grid)]

    for (i, time) in enumerate(data['time'][1:]):
        grid = RectilinearField(lat[:, 0], lon[0, :], indexing='ij',
                                 attrs=attrs, units=('degrees_north',
                                                     'degrees_east'))
        for (var, units) in [('sea_surface_wave__significant_height',
                              'm'),
                             ('sea_surface_wave__max_over_time_of_period',
                              's')]:
            grid.add_field(var, data[var][i, :, :], centering='point',
                            units=units)
        grids.append((time, grid))

    return grids


@WriterPlugin('ww3')
def write_ww3(name, grids):
    """
    Write Wave Watch III data as a NetCDF file.

    :name: NetCDF file to write to
    :grids: List of grids to write
    """
    field_tofile(grids[0][1], name, append='append', time_units='days',
                 time=grids[0][0],
                 long_name=dict(x='model_grid_cell_center__latitude',
                                y='model_grid_cell_center__longitude'))

    for (time, grid) in grids[1:]:
        field_tofile(grid, name, append=True, time=time,
                      long_name=dict(x='model_grid_cell_center__latitude',
                                     y='model_grid_cell_center__longitude'))
