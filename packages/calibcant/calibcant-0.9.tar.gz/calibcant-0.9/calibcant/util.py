# Copyright (C) 2012-2013 W. Trevor King <wking@tremily.us>
#
# This file is part of calibcant.
#
# calibcant is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# calibcant is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# calibcant.  If not, see <http://www.gnu.org/licenses/>.

"""Useful utilites not related to calibration.

Currently just a framework for consistently saving/loading calibration
data.
"""

import h5py as _h5py

from h5config.storage.hdf5 import HDF5_Storage as _HDF5_Storage
from h5config.storage.hdf5 import h5_create_group as _h5_create_group


from . import LOG as _LOG


class SaveSpec (object):
    def __init__(self, item=None, relpath='/', key=None, config=False,
                 array=False, units=None, deviation=None):
        self.item = item
        self.relpath = relpath
        self.key = key
        self.config = config
        self.array = array
        self.units = units
        self.deviation = deviation

def save(filename=None, group='/', specs=tuple()):
    f = None
    storage = _HDF5_Storage()
    try:
        if isinstance(group, str):
            f = _h5py.File(filename, 'a')
            group = _h5_create_group(f, group)
        for spec in specs:
            if spec.item is None:
                continue
            cwg = _h5_create_group(group, spec.relpath)
            if spec.config:
                storage.save(config=spec.item, group=cwg)
                continue
            assert spec.units, spec.item
            for k in ['data', 'units', 'standard-deviation']:
                try:
                    del cwg[k]
                except KeyError:
                    pass
            cwg['data'] = spec.item
            cwg['units'] = spec.units
            if spec.deviation is not None:
                cwg['standard-deviation'] = spec.deviation
    finally:
        if f:
            f.close()

def load(filename=None, group='/', specs=tuple()):
    data = {}
    f = None
    storage = _HDF5_Storage()
    try:
        if isinstance(group, str):
            f = _h5py.File(filename, 'a')
            group = _h5_create_group(f, group)
        for spec in specs:
            try:
                cwg = group[spec.relpath]
            except KeyError:
                continue
            d = data
            for n in spec.key[:-1]:
                if n not in d:
                    d[n] = {}
                d = d[n]
            if spec.config:
                d[spec.key[-1]] = spec.config(storage=_HDF5_Storage(group=cwg))
                d[spec.key[-1]].load()
                continue
            assert spec.units, spec.key
            try:
                if spec.array:
                    d[spec.key[-1]] = cwg['data'][...]
                else:
                    d[spec.key[-1]] = float(cwg['data'][...])
            except KeyError:
                continue
            except TypeError, e:
                _LOG.warn('while loading {} from {}: {}'.format(
                        spec.key, cwg['data'], e))
                raise
            if spec.key[-1] in d:
                units_ = cwg['units'][...]
                assert units_ == spec.units, (units_, spec.units)
                if spec.deviation is not None:
                    try:
                        d[spec.deviation] = float(
                            cwg['standard-deviation'][...])
                    except KeyError:
                        pass
    finally:
        if f:
            f.close()
    return data
