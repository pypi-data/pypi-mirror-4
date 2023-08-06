# calibcant - tools for thermally calibrating AFM cantilevers
#
# Copyright (C) 2011-2013 W. Trevor King <wking@tremily.us>
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

"""Acquire, save, and load cantilever thermal vibration data.

For measuring the cantilever's spring constant.

The relevent physical quantity is:
  Vphoto   The photodiode vertical deflection voltage (what we measure)
"""

from numpy import zeros as _zeros
from FFT_tools import ceil_pow_of_two as _ceil_pow_of_two
from pycomedi.constant import TRIG_SRC as _TRIG_SRC
from pycomedi.utility import inttrig_insn as _inttrig_insn
from pycomedi.utility import Reader as _Reader

from . import LOG as _LOG
from .vibration_analyze import analyze as _analyze
from .vibration_analyze import save as _save


def acquire(piezo, config):
    """Record thermal vibration data for `piezo` at its current position.

    Inputs:
      piezo             a pypiezo.afm.AFMPiezo instance
      config  a .config.Config instance
    """
    _LOG.debug('prepare vibration aquisition command')

    # round up to the nearest power of two, for efficient FFT-ing
    n_samps = _ceil_pow_of_two(
        config['sample-time']*config['frequency'])
    time = n_samps / config['frequency']
    scan_period_ns = int(1e9 / config['frequency'])

    input_channel = piezo.input_channel_by_name('deflection')
    channel = input_channel.channel

    channels = [channel]

    dtype = piezo.deflection_dtype()
    data = _zeros((n_samps, len(channels)), dtype=dtype)

    cmd = channel.subdevice.get_cmd_generic_timed(
        len(channels), scan_period_ns)
    cmd.start_src = _TRIG_SRC.int
    cmd.start_arg = 0
    cmd.stop_src = _TRIG_SRC.count
    cmd.stop_arg = n_samps
    cmd.chanlist = channels
    channel.subdevice.cmd = cmd
    for i in range(3):
        rc = channel.subdevice.command_test()
        if rc == None: break
        _LOG.debug('command test %d: %s' % (i,rc))

    _LOG.info('get %g seconds of vibration data at %g Hz'
              % (config['sample-time'],
                 config['frequency']))
    channel.subdevice.command()
    reader = _Reader(channel.subdevice, data)
    reader.start()
    channel.subdevice.device.do_insn(_inttrig_insn(channel.subdevice))
    reader.join()
    data = data.reshape((data.size,))
    return data

def run(piezo, config, filename, group='/'):
    """Wrapper around acquire(), analyze(), save().

    >>> import os
    >>> import tempfile
    >>> from h5config.storage.hdf5 import pprint_HDF5
    >>> from pyafm.storage import load_afm
    >>> from .config import VibrationConfig

    >>> fd,filename = tempfile.mkstemp(suffix='.h5', prefix='calibcant-')
    >>> os.close(fd)

    >>> devices = []
    >>> afm = load_afm(devices=devices)
    >>> afm.load_from_config()

    Test a vibration:

    >>> config = VibrationConfig()
    >>> output = run(piezo=afm.piezo, config=config, filename=filename,
    ...     group='/vibration')
    >>> output  # doctest: +SKIP
    4.1589771694838657e-05
    >>> pprint_HDF5(filename)  # doctest: +ELLIPSIS, +REPORT_UDIFF
    /
      /vibration
        /vibration/config
          /vibration/config/deflection
            <HDF5 dataset "analog-reference": shape (), type "|S4">
              diff
            <HDF5 dataset "channel": shape (), type "<i...">
              0
            <HDF5 dataset "conversion-coefficients": shape (2,), type "<f8">
              [ -1.00000000e+01   3.05180438e-04]
            <HDF5 dataset "conversion-origin": shape (), type "<f8">
              0.0
            <HDF5 dataset "device": shape (), type "|S12">
              /dev/comedi0
            <HDF5 dataset "inverse-conversion-coefficients": shape (2,), type "<f8">
              [    0.    3276.75]
            <HDF5 dataset "inverse-conversion-origin": shape (), type "<f8">
              -10.0
            <HDF5 dataset "maxdata": shape (), type "<i...">
              65535
            <HDF5 dataset "name": shape (), type "|S10">
              deflection
            <HDF5 dataset "range": shape (), type "<i...">
              0
            <HDF5 dataset "subdevice": shape (), type "<i...">
              0
          /vibration/config/vibration
            <HDF5 dataset "chunk-size": shape (), type "<i...">
              2048
            <HDF5 dataset "frequency": shape (), type "<f8">
              50000.0
            <HDF5 dataset "maximum-fit-frequency": shape (), type "<f8">
              25000.0
            <HDF5 dataset "minimum-fit-frequency": shape (), type "<f8">
              500.0
            <HDF5 dataset "model": shape (), type "|S12">
              Breit-Wigner
            <HDF5 dataset "overlap": shape (), type "|b1">
              False
            <HDF5 dataset "sample-time": shape (), type "<i...">
              1
            <HDF5 dataset "window": shape (), type "|S4">
              Hann
        /vibration/processed
          <HDF5 dataset "data": shape (), type "<f8">
            ...
          <HDF5 dataset "units": shape (), type "|S6">
            V^2/Hz
        /vibration/raw
          <HDF5 dataset "data": shape (65536,), type "<u2">
            [...]
          <HDF5 dataset "units": shape (), type "|S4">
            bits

    Close the Comedi devices.

    >>> for device in devices:
    ...     device.close()

    Cleanup our temporary config file.

    >>> os.remove(filename)
    """
    deflection_input_channel = piezo.input_channel_by_name('deflection')
    
    deflection_channel_config = deflection_input_channel.config

    deflection = acquire(piezo, config)
    variance = _analyze(
        deflection, config, deflection_channel_config)
    _save(
        filename=filename, group=group, raw=deflection, config=config,
        deflection_channel_config=deflection_channel_config,
        processed=variance)
    return variance
