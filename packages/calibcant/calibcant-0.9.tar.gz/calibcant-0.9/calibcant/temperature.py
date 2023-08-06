"""Temperature measurement tools

Fairly stubby, since a one shot temperature measurement is a common
thing.  We just wrap that to provide a consistent interface.
"""

from . import LOG as _LOG
from .temperature_analyze import analyze as _analyze
from .temperature_analyze import save as _save


def acquire(get=None):
    """Measure the current temperature of the sample, 
    """
    if get:
        _LOG.info('measure temperature')
        temperature = get()
    else:
        temperature = None
    return temperature

def run(get, config, filename, group='/'):
    """Wrapper around acquire(), analyze(), save().

    >>> import os
    >>> import tempfile
    >>> from h5config.storage.hdf5 import HDF5_Storage, pprint_HDF5
    >>> from .config import TemperatureConfig

    >>> fd,filename = tempfile.mkstemp(suffix='.h5', prefix='calibcant-')
    >>> os.close(fd)

    >>> config = TemperatureConfig()
    >>> def get():
    ...     return 19.2
    >>> t = run(
    ...     get=get, config=config, filename=filename, group='/')
    >>> pprint_HDF5(filename)  # doctest: +ELLIPSIS, +REPORT_UDIFF
    /
      /config
        /config/temperature
          <HDF5 dataset "sleep": shape (), type "<i4">
            1
      /processed
        <HDF5 dataset "data": shape (), type "<f8">
          19.2
        <HDF5 dataset "units": shape (), type "|S1">
          K
      /raw
        <HDF5 dataset "data": shape (), type "<f8">
          19.2
        <HDF5 dataset "units": shape (), type "|S1">
          K

    Cleanup our temporary config file.

    >>> os.remove(filename)
    """
    raw = acquire(get)
    _LOG.debug('got temperature: {} K'.format(raw))
    processed = _analyze(config=config, temperature=raw)
    _save(filename=filename, group=group, config=config, raw=raw,
          processed=processed)
    return processed
