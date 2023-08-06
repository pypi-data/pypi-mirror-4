# calibcant - tools for thermally calibrating AFM cantilevers
#
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

"""Temperature analysis.

Separate the more general `temperature.analyze()` from the other
`temperature.*()` functions in calibcant.

The relevant physical quantities are:

* `T` Temperature at which thermal vibration measurements were acquired

>>> import os
>>> from pprint import pprint
>>> import tempfile
>>> import numpy
>>> from .config import TemperatureConfig
>>> from h5config.storage.hdf5 import pprint_HDF5, HDF5_Storage

>>> fd,filename = tempfile.mkstemp(suffix='.h5', prefix='calibcant-')
>>> os.close(fd)

>>> config = TemperatureConfig()

>>> raw = 296.5
>>> processed = analyze(config=config, temperature=raw)
>>> plot(raw=raw, processed=processed)
>>> save(filename=filename, group='/',
...     config=config, raw=raw, processed=processed)

>>> pprint_HDF5(filename)  # doctest: +REPORT_UDIFF
/
  /config
    /config/temperature
      <HDF5 dataset "sleep": shape (), type "<i4">
        1
  /processed
    <HDF5 dataset "data": shape (), type "<f8">
      296.5
    <HDF5 dataset "units": shape (), type "|S1">
      K
  /raw
    <HDF5 dataset "data": shape (), type "<f8">
      296.5
    <HDF5 dataset "units": shape (), type "|S1">
      K

>>> data = load(filename=filename, group='/')

>>> pprint(data)  # doctest: +ELLIPSIS
{'config': {'temperature': <TemperatureConfig ...>},
 'processed': 296.5,
 'raw': 296.5}

>>> print(data['config']['temperature'].dump())
sleep: 1.0
>>> data['raw']
296.5
>>> type(data['raw'])
<type 'float'>
>>> data['processed']
296.5

>>> os.remove(filename)
"""

import h5py as _h5py

try:
    import matplotlib as _matplotlib
    import matplotlib.pyplot as _matplotlib_pyplot
    import time as _time  # for timestamping lines on plots
except (ImportError, RuntimeError), e:
    _matplotlib = None
    _matplotlib_import_error = e

from h5config.storage.hdf5 import HDF5_Storage as _HDF5_Storage
from h5config.storage.hdf5 import h5_create_group as _h5_create_group

from . import LOG as _LOG
from . import package_config as _package_config
from .config import TemperatureConfig as _TemperatureConfig
from .util import SaveSpec as _SaveSpec
from .util import save as _save
from .util import load as _load


def analyze(config, temperature, units='Kelvin'):
    """Convert measured temperature to Kelvin.

    `temperature` should be a numpy ndarray or scalar.  `config`
    should be a `config._temperatureemperatureConfig` instance.

    The `units` option is just for fun.  The AFM's `get_temperature`
    method always returns temperatures in Kelvin.
    """
    if units == 'Kelvin':
        return temperature
    elif units == 'Celsius':
        return _C2K(temperature)
    else:
        raise NotImplementedError()


def save(filename=None, group='/', config=None, raw=None, processed=None):
    specs = [
        _SaveSpec(item=config, relpath='config/temperature',
                  config=_TemperatureConfig),
        _SaveSpec(item=raw, relpath='raw', units='K'),
        _SaveSpec(item=processed, relpath='processed', units='K'),
        ]
    _save(filename=filename, group=group, specs=specs)

def load(filename=None, group='/'):
    specs = [
        _SaveSpec(key=('config', 'temperature',), relpath='config/temperature',
                  config=_TemperatureConfig),
        _SaveSpec(key=('processed',), relpath='processed', units='K'),
        _SaveSpec(key=('raw',), relpath='raw', units='K'),
        ]
    return _load(filename=filename, group=group, specs=specs)

def plot(raw=None, processed=None):
    if not _matplotlib:
        raise _matplotlib_import_error
    figure = _matplotlib_pyplot.figure()
    timestamp = _time.strftime('%H%M%S')
    if raw is None:
        if processed is None:
            return  # nothing to plot
        axes1 = None
        axes2 = figure.add_subplot(1, 1, 1)
    elif processed is None:
        axes1 = figure.add_subplot(1, 1, 1)
        axes2 = None
    else:
        axes1 = figure.add_subplot(2, 1, 1)
        axes2 = figure.add_subplot(2, 1, 2)
    if axes1:
        axes1.set_title('Raw Temperatures %s' % timestamp)
        axes1.plot(raw, label='raw')
    if axes2:
        axes2.set_title('Processed Temperatures %s' % timestamp)
        axes2.plot(processed, label='processed')
    if hasattr(figure, 'show'):
        figure.show()
    return figure
