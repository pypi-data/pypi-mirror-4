# calibcant - tools for thermally calibrating AFM cantilevers
#
# Copyright (C) 2008-2013 W. Trevor King <wking@tremily.us>
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

"""Acquire, save, and load cantilever calibration bump data.

For measuring photodiode sensitivity.

The relevent physical quantities are:
  Vzp_out  Output z-piezo voltage (what we generate)
  Vzp      Applied z-piezo voltage (after external ZPGAIN)
  Zp       The z-piezo position
  Zcant    The cantilever vertical deflection
  Vphoto   The photodiode vertical deflection voltage (what we measure)

Which are related by the parameters:
  zp_gain           Vzp_out / Vzp
  zp_sensitivity    Zp / Vzp
  photo_sensitivity Vphoto / Zcant

Cantilever calibration assumes a pre-calibrated z-piezo
(zp_sensitivity) and amplifier (zp_gain).  In our lab, the z-piezo is
calibrated by imaging a calibration sample, which has features with
well defined sizes, and the gain is set with a knob on our modified
NanoScope.

Photo-sensitivity is measured by bumping the cantilever against the
surface, where `Zp = Zcant`.  The measured slope Vphoto/Vout is
converted to photo-sensitivity via::

  Vphoto/Vzp_out * Vzp_out/Vzp  * Vzp/Zp   *    Zp/Zcant =    Vphoto/Zcant
   (measured)      (1/zp_gain) (1/zp_sensitivity)  (1)    (photo_sensitivity)

We do all these measurements a few times to estimate statistical
errors.
"""

import numpy as _numpy

from pypiezo.base import convert_meters_to_bits as _convert_meters_to_bits
from pypiezo.base import convert_bits_to_meters as _convert_bits_to_meters

from . import LOG as _LOG
from .bump_analyze import analyze as _analyze
from .bump_analyze import save as _save


def acquire(afm, config):
    """Ramps `push_depth` closer and returns to the original position.

    Inputs:
      afm     a pyafm.AFM instance
      config  a .config._BumpConfig instance

    Returns the acquired ramp data dictionary, with data in DAC/ADC bits.
    """
    afm.move_just_onto_surface(
        depth=config['initial-position'], far=config['far-steps'],
        setpoint=config['setpoint'],
        min_slope_ratio=config['min-slope-ratio'])
    #afm.piezo.jump('z', 32000)

    _LOG.info(
        'bump the surface to a depth of {} m with a setpoint of {} V'.format(
            config['push-depth'], config['setpoint']))

    axis = afm.piezo.axis_by_name(afm.config['main-axis'])

    start_pos = afm.piezo.last_output[afm.config['main-axis']]
    start_pos_m = _convert_bits_to_meters(axis.config, start_pos)
    close_pos_m = start_pos_m + config['push-depth']
    close_pos = _convert_meters_to_bits(axis.config, close_pos_m)

    dtype = afm.piezo.channel_dtype(
        afm.config['main-axis'], direction='output')
    appr = _numpy.linspace(
        start_pos, close_pos, config['samples']).astype(dtype)
    # switch numpy.append to numpy.concatenate with version 2.0+
    out = _numpy.append(appr, appr[::-1])
    out = out.reshape((len(out), 1))

    # (samples) / (meters) * (meters/second) = (samples/second)
    freq = (config['samples'] / config['push-depth']
            * config['push-speed'])

    data = afm.piezo.ramp(out, freq, output_names=[afm.config['main-axis']],
                          input_names=['deflection'])

    out = out.reshape((len(out),))
    data = data.reshape((data.size,))
    return {afm.config['main-axis']: out, 'deflection': data}

def run(afm, config, filename, group='/'):
    """Wrapper around acquire(), analyze(), save().

    >>> import os
    >>> import tempfile
    >>> from h5config.storage.hdf5 import pprint_HDF5
    >>> from pyafm.storage import load_afm
    >>> from .config import BumpConfig

    >>> fd,filename = tempfile.mkstemp(suffix='.h5', prefix='calibcant-')
    >>> os.close(fd)

    >>> devices = []
    >>> afm = load_afm()
    >>> afm.load_from_config(devices=devices)

    Test a bump:

    >>> config = BumpConfig()
    >>> output = run(afm=afm, config=config, filename=filename, group='/')
    >>> output  # doctest: +SKIP
    23265462.3047795
    >>> pprint_HDF5(filename)  # doctest: +ELLIPSIS, +REPORT_UDIFF
    /
      /config
        /config/bump
          <HDF5 dataset "far-steps": shape (), type "<i4">
            200
          <HDF5 dataset "initial-position": shape (), type "<f8">
            -5e-08
          <HDF5 dataset "min-slope-ratio": shape (), type "<f8">
            10.0
          <HDF5 dataset "model": shape (), type "|S9">
            quadratic
          <HDF5 dataset "push-depth": shape (), type "<f8">
            2e-07
          <HDF5 dataset "push-speed": shape (), type "<f8">
            1e-06
          <HDF5 dataset "samples": shape (), type "<i4">
            1024
          <HDF5 dataset "setpoint": shape (), type "<f8">
            2.0
      /processed
        <HDF5 dataset "data": shape (), type "<f8">
          ...
        <HDF5 dataset "units": shape (), type "|S3">
          V/m
      /raw
        /raw/deflection
          <HDF5 dataset "data": shape (2048,), type "<u2">
            [...]
          <HDF5 dataset "units": shape (), type "|S4">
            bits
        /raw/z
          <HDF5 dataset "data": shape (2048,), type "<u2">
            [...]
          <HDF5 dataset "units": shape (), type "|S4">
            bits

    Close the Comedi devices.

    >>> for device in devices:
    ...     device.close()

    Cleanup our temporary config file.

    >>> os.remove(filename)
    """
    deflection_channel = afm.piezo.input_channel_by_name('deflection')
    axis = afm.piezo.axis_by_name(afm.config['main-axis'])

    raw = acquire(afm, config)
    photo_sensitivity = _analyze(
        config=config, data=raw, z_axis_config=axis.config,
        deflection_channel_config=deflection_channel.config)
    _save(filename=filename, group=group, config=config,
          raw=raw, processed=photo_sensitivity)
    return photo_sensitivity
