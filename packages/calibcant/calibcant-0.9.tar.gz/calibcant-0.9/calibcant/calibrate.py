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

"""Acquire and analyze cantilever calibration data.

The relevent physical quantities are:

* Vzp_out  Output z-piezo voltage (what we generate)
* Vzp      Applied z-piezo voltage (after external ZPGAIN)
* Zp       The z-piezo position
* Zcant    The cantilever vertical deflection
* Vphoto   The photodiode vertical deflection voltage (what we measure)
* Fcant    The force on the cantilever
* T        The temperature of the cantilever and surrounding solution
           (another thing we measure or guess)
* k_b      Boltzmann's constant

Which are related by the parameters:

* zpGain           Vzp_out / Vzp
* zpSensitivity    Zp / Vzp
* photoSensitivity Vphoto / Zcant
* k_cant           Fcant / Zcant

Cantilever calibration assumes a pre-calibrated z-piezo
(zpSensitivity) and a amplifier (zpGain).  In our lab, the z-piezo is
calibrated by imaging a calibration sample, which has features with
well defined sizes, and the gain is set with a knob on the Nanoscope.

photoSensitivity is measured by bumping the cantilever against the
surface, where Zp = Zcant (see bump_acquire() and the bump_analyze
submodule).

k_cant is measured by watching the cantilever vibrate in free solution
(see the vib_acquire() and the vib_analyze submodule).  The average
energy of the cantilever in the vertical direction is given by the
equipartition theorem.

.. math::  \frac{1}{2} k_b T = \frac{1}{2} k_cant <Zcant**2>

so

.. math::   k_cant = \frac{k_b T}{Zcant**2}

but

.. math::   Zcant = \frac{Vphoto}{photoSensitivity}

so

.. math:: k_cant = \frac{k_b T * photoSensitivty^2}{<Vphoto**2>}

We measured photoSensitivity with the surface bumps.  We can either
measure T using an external function (see temperature.py), or just
estimate it (see T_acquire() and the T_analyze submodule).  Guessing
room temp ~22 deg C is actually fairly reasonable.  Assuming the
actual fluid temperature is within +/- 5 deg, the error in the spring
constant k_cant is within 5/273.15 ~= 2%.  A time series of Vphoto
while we're far from the surface and not changing Vzp_out will give us
the average variance <Vphoto**2>.

We do all these measurements a few times to estimate statistical
errors.
"""

from time import sleep as _sleep

from numpy import zeros as _zeros
from numpy import float as _float

import h5py as _h5py
from pyafm.afm import AFM as _AFM
from h5config.storage.hdf5 import HDF5_Storage as _HDF5_Storage

from . import LOG as _LOG
from .config import CalibrateConfig as _CalibrateConfig
from .bump import run as _bump
from .bump_analyze import load as _bump_load
from .temperature import run as _temperature
from .temperature_analyze import load as _temperature_load
from .vibration import run as _vibration
from .vibration_analyze import load as _vibration_load
from .analyze import analyze as _analyze
from .analyze import save_results as _save_results
from .util import SaveSpec as _SaveSpec
from .util import load as _load


def load(filename=None, group='/'):
    config = _CalibrateConfig(storage=_HDF5_Storage(
            filename=filename, group=group))
    config.load()
    return Calibrator(config=config)

def load_all(filename=None, group='/', raw=True):
    "Load all data from a `Calibration.calibrate()` run."
    assert group.endswith('/'), group
    calibrator = load(
        filename=filename, group='{}config/'.format(group))
    data = calibrator.load_results(
        filename=filename, group='{}calibration/'.format(group))
    if raw:
        raw_data = calibrator.load_raw(filename=filename, group=group)
    else:
        raw_data = None
    return (calibrator, data, raw_data)


class Calibrator (object):
    """Calibrate a cantilever spring constant using the thermal tune method.

    >>> import os
    >>> from pprint import pprint
    >>> import tempfile
    >>> from h5config.storage.hdf5 import pprint_HDF5
    >>> from pyafm.storage import load_afm
    >>> from .config import (CalibrateConfig, BumpConfig,
    ...     TemperatureConfig, VibrationConfig)

    >>> fd,filename = tempfile.mkstemp(suffix='.h5', prefix='calibcant-')
    >>> os.close(fd)

    >>> devices = []

    >>> afm = load_afm()
    >>> afm.load_from_config(devices=devices)
    >>> if afm.piezo is None:
    ...    raise NotImplementedError('save a better default AFM!')
    >>> config = CalibrateConfig()
    >>> config['bump'] = BumpConfig()
    >>> config['temperature'] = TemperatureConfig()
    >>> config['vibration'] = VibrationConfig()
    >>> c = Calibrator(config=config, afm=afm)
    >>> c.setup_config()
    >>> k,k_s,data = c.calibrate(filename=filename)
    >>> k  # doctest: +SKIP
    0.058402262154840491
    >>> k_s  # doctest: +SKIP
    0.0010609833397949553
    >>> pprint(data)  # doctest: +ELLIPSIS, +REPORT_UDIFF
    {'bump': array([...]),
     'temperature': array([...]),
     'vibration': array([...])}
    >>> pprint_HDF5(filename)  # doctest: +ELLIPSIS, +REPORT_UDIFF
    /
      /bump
        /bump/0
          /bump/0/config
            /bump/0/config/bump
              <HDF5 dataset "far-steps": shape (), type "<i4">
                200
              <HDF5 dataset "initial-position": shape (), type "<f8">
                -5e-08
              ...
          /bump/0/processed
            <HDF5 dataset "data": shape (), type "<f8">
              ...
            <HDF5 dataset "units": shape (), type "|S3">
              V/m
          /bump/0/raw
            /bump/0/raw/deflection
              <HDF5 dataset "data": shape (2048,), type "<u2">
                [...]
              <HDF5 dataset "units": shape (), type "|S4">
                bits
            /bump/0/raw/z
              <HDF5 dataset "data": shape (2048,), type "<u2">
                [...]
              <HDF5 dataset "units": shape (), type "|S4">
                bits
        /bump/1
        ...
      /config
        /config/afm
          <HDF5 dataset "fallback-temperature": shape (), type "<f8">
            295.15
          <HDF5 dataset "far": shape (), type "<f8">
            3e-05
          <HDF5 dataset "main-axis": shape (), type "|S1">
            z
          <HDF5 dataset "name": shape (), type "|S5">
            1B3D9
          /config/afm/piezo
            /config/afm/piezo/axes
              /config/afm/piezo/axes/0
                /config/afm/piezo/axes/0/channel
                  <HDF5 dataset "analog-reference": shape (), type "|S6">
                    ground
                  <HDF5 dataset "channel": shape (), type "<i4">
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
                  <HDF5 dataset "maxdata": shape (), type "<i8">
                    65535
                  <HDF5 dataset "name": shape (), type "|S1">
                    z
                  <HDF5 dataset "range": shape (), type "<i4">
                    0
                  <HDF5 dataset "subdevice": shape (), type "<i4">
                    1
                <HDF5 dataset "gain": shape (), type "<f8">
                  20.0
                <HDF5 dataset "maximum": shape (), type "<f8">
                  9.0
                <HDF5 dataset "minimum": shape (), type "<f8">
                  -9.0
                <HDF5 dataset "monitor": shape (), type "|S1">
    <BLANKLINE>
                <HDF5 dataset "sensitivity": shape (), type "<f8">
                  8.8e-09
              /config/afm/piezo/axes/1
                /config/afm/piezo/axes/1/channel
                  <HDF5 dataset "analog-reference": shape (), type "|S6">
                    ground
                  <HDF5 dataset "channel": shape (), type "<i4">
                    1
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
                  <HDF5 dataset "maxdata": shape (), type "<i8">
                    65535
                  <HDF5 dataset "name": shape (), type "|S1">
                    x
                  <HDF5 dataset "range": shape (), type "<i4">
                    0
                  <HDF5 dataset "subdevice": shape (), type "<i4">
                    1
                <HDF5 dataset "gain": shape (), type "<f8">
                  20.0
                <HDF5 dataset "maximum": shape (), type "<f8">
                  8.0
                <HDF5 dataset "minimum": shape (), type "<f8">
                  -8.0
                <HDF5 dataset "monitor": shape (), type "|S1">
    <BLANKLINE>
                <HDF5 dataset "sensitivity": shape (), type "<f8">
                  4.16e-09
            /config/afm/piezo/inputs
              /config/afm/piezo/inputs/0
                <HDF5 dataset "analog-reference": shape (), type "|S4">
                  diff
                <HDF5 dataset "channel": shape (), type "<i4">
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
                <HDF5 dataset "maxdata": shape (), type "<i8">
                  65535
                <HDF5 dataset "name": shape (), type "|S10">
                  deflection
                <HDF5 dataset "range": shape (), type "<i4">
                  0
                <HDF5 dataset "subdevice": shape (), type "<i4">
                  0
            <HDF5 dataset "name": shape (), type "|S5">
              2253E
          /config/afm/stepper
            <HDF5 dataset "backlash": shape (), type "<i4">
              100
            <HDF5 dataset "delay": shape (), type "<f8">
              0.01
            <HDF5 dataset "full-step": shape (), type "|b1">
              True
            <HDF5 dataset "logic": shape (), type "|b1">
              True
            <HDF5 dataset "name": shape (), type "|S9">
              z-stepper
            /config/afm/stepper/port
              <HDF5 dataset "channels": shape (4,), type "<i4">
                [0 1 2 3]
              <HDF5 dataset "device": shape (), type "|S12">
                /dev/comedi0
              <HDF5 dataset "direction": shape (), type "|S6">
                output
              <HDF5 dataset "name": shape (), type "|S12">
                stepper DB-9
              <HDF5 dataset "subdevice": shape (), type "<i4">
                2
              <HDF5 dataset "subdevice-type": shape (), type "|S3">
                dio
            <HDF5 dataset "step-size": shape (), type "<f8">
              1.7e-07
          /config/afm/temperature
            <HDF5 dataset "baudrate": shape (), type "<i4">
              9600
            <HDF5 dataset "controller": shape (), type "<i4">
              1
            <HDF5 dataset "device": shape (), type "|S10">
              /dev/ttyS0
            <HDF5 dataset "max-current": shape (), type "<f8">
              0.0
            <HDF5 dataset "name": shape (), type "|S14">
              room (ambient)
            <HDF5 dataset "units": shape (), type "|S7">
              Celsius
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
        <HDF5 dataset "num-bumps": shape (), type "<i4">
          10
        <HDF5 dataset "num-temperatures": shape (), type "<i4">
          10
        <HDF5 dataset "num-vibrations": shape (), type "<i4">
          20
        /config/temperature
          <HDF5 dataset "sleep": shape (), type "<i4">
            1
        /config/vibration
          <HDF5 dataset "chunk-size": shape (), type "<i4">
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
          <HDF5 dataset "sample-time": shape (), type "<i4">
            1
          <HDF5 dataset "window": shape (), type "|S4">
            Hann
        <HDF5 dataset "vibration-spacing": shape (), type "<f8">
          5e-05
      /temperature
        /temperature/0
          /temperature/0/config
            /temperature/0/config/temperature
              <HDF5 dataset "sleep": shape (), type "<i4">
                1
          /temperature/0/processed
            <HDF5 dataset "data": shape (), type "<f8">
              ...
            <HDF5 dataset "units": shape (), type "|S1">
              K
          /temperature/0/raw
            <HDF5 dataset "data": shape (), type "<f8">
              ...
            <HDF5 dataset "units": shape (), type "|S1">
              K
        /temperature/1
        ...
      /vibration
        /vibration/0
          /vibration/0/config
            /vibration/0/config/deflection
              ...
            /vibration/0/config/vibration
              <HDF5 dataset "chunk-size": shape (), type "<i4">
                2048
              <HDF5 dataset "frequency": shape (), type "<f8">
                50000.0
              ...
          /vibration/0/processed
            <HDF5 dataset "data": shape (), type "<f8">
              ...
            <HDF5 dataset "units": shape (), type "|S6">
              V^2/Hz
          /vibration/0/raw
            <HDF5 dataset "data": shape (65536,), type "<u2">
              [...]
            <HDF5 dataset "units": shape (), type "|S4">
              bits
        ...

    >>> calibrator,data,raw_data = load_all(filename=filename)
    >>> calibrator.load_from_config(devices=devices)
    >>> print(calibrator.config.dump())  # doctest: +ELLIPSIS, +REPORT_UDIFF
    afm:
      name: 1B3D9
      main-axis: z
      piezo:
        name: 2253E
    ...
    >>> pprint(data)  # doctest: +ELLIPSIS, +REPORT_UDIFF
    {'processed': {'spring_constant': ...
                   'spring_constant_deviation': ...},
     'raw': {'bump': array([...]),
             'temperature': array([...]),
             'vibration': array([...])}}

    >>> pprint(raw_data)  # doctest: +ELLIPSIS, +REPORT_UDIFF
    {'bump': [{'config': {'bump': <BumpConfig ...>},
               'processed': ...,
               'raw': {'deflection': array([...], dtype=uint16),
                       'z': array([...], dtype=uint16)}},
              {...},
              ...],
     'temperature': [{'config': {'temperature': <TemperatureConfig ...>},
                      'processed': ...,
                      'raw': ...},
                     {...},
                     ...],
     'vibration': [{'config': {'vibration': <InputChannelConfig ...>},
                    'processed': ...
                    'raw': array([...], dtype=uint16)},
                   {...},
                   ...]}

    Close the Comedi devices.

    >>> for device in devices:
    ...     device.close()

    Cleanup our temporary config file.

    >>> os.remove(filename)
    """
    def __init__(self, config, afm=None):
        self.config = config
        self.afm = afm

    def load_from_config(self, devices):
        if self.afm is None:
            self.afm = _AFM(config=self.config['afm'])
            self.afm.load_from_config(devices=devices)

    def setup_config(self):
        if self.afm:
            self.afm.setup_config()
            self.config['afm'] = self.afm.config

    def calibrate(self, filename=None, group='/'):
        """Main calibration method.

        Outputs:
        k    cantilever spring constant (in N/m, or equivalently nN/nm)
        k_s  standard deviation in our estimate of k
        data the data used to determine k
        """
        data = self.acquire(filename=filename, group=group)
        k = k_s = bumps = temperatures = vibrations = None
        bumps = data.get('bump', None)
        temperatures = data.get('temperature', None)
        vibrations = data.get('vibration', None)
        if None not in [bumps, temperatures, vibrations]:
            k,k_s = _analyze(
                bumps=bumps, temperatures=temperatures, vibrations=vibrations)
        if filename is not None:
            self.save_results(
                filename=filename, group='{}calibration/'.format(group),
                spring_constant=k, spring_constant_deviation=k_s, **data)
        return (k, k_s, data)

    def acquire(self, filename=None, group='/'):
        """Acquire data for calibrating a cantilever in one function.

        Outputs a dict of `action` -> `data_array` pairs, for each
        action (bump, temperature, vibration) that is actually
        configured.  For example, if you wanted to skip the surface
        approach, bumping, and retraction, you could just set
        `.config['bump']` to `None`.

        The temperatures are collected after moving far from the
        surface but before and vibrations are measured to give
        everything time to settle after the big move.

        Because theres a fair amount of data coming in during a
        calibration, we save the data as it comes in.  So the
        procedure is bump-0, save-bump-0, bump-1, save-bump-0, etc.
        To disable the saving, just set `filename` to `None`.
        """
        if filename is not None:
            assert group.endswith('/'), group
            self.save(filename=filename, group='{}config/'.format(group))
        data = {}
        if self.config['bump'] and self.config['num-bumps'] > 0:
            data['bump'] = _zeros((self.config['num-bumps'],), dtype=_float)
            for i in range(self.config['num-bumps']):
                _LOG.info('acquire bump {} of {}'.format(
                        i, self.config['num-bumps']))
                data['bump'][i] = _bump(
                    afm=self.afm, config=self.config['bump'],
                    filename=filename, group='{}bump/{}/'.format(group, i))
            _LOG.debug('bumps: {}'.format(data['bump']))
        self.afm.move_away_from_surface(
            distance=self.config['vibration-spacing'])
        if self.config['temperature'] and self.config['num-temperatures'] > 0:
            data['temperature'] = _zeros(
                (self.config['num-temperatures'],), dtype=_float)
            for i in range(self.config['num-temperatures']):
                _LOG.info('acquire temperature {} of {}'.format(
                        i, self.config['num-temperatures']))
                data['temperature'][i] = _temperature(
                    get=self.afm.get_temperature,
                    config=self.config['temperature'],
                    filename=filename,
                    group='{}temperature/{}/'.format(group, i))
                _sleep(self.config['temperature']['sleep'])
            _LOG.debug('temperatures: {}'.format(data['temperature']))
        if self.config['vibration'] and self.config['num-vibrations'] > 0:
            data['vibration'] = _zeros(
                (self.config['num-vibrations'],), dtype=_float)
            for i in range(self.config['num-vibrations']):
                data['vibration'][i] = _vibration(
                    piezo=self.afm.piezo, config=self.config['vibration'],
                    filename=filename,
                    group='{}vibration/{}/'.format(group, i))
            _LOG.debug('vibrations: {}'.format(data['vibration']))
        return data

    def save(self, filename=None, group='/'):
        storage = _HDF5_Storage(filename=filename, group=group)
        storage.save(config=self.config)

    @staticmethod
    def load_results(filename, group='/'):
        """Load results saved with `.save_results()`."""
        specs = [
            _SaveSpec(key=('raw', 'bump'),
                      relpath='raw/photodiode-sensitivity',
                      array=True, units='V/m'),
            _SaveSpec(key=('raw', 'temperature'), relpath='raw/temperature',
                      array=True, units='K'),
            _SaveSpec(key=('raw', 'vibration'),
                      relpath='raw/vibration',
                      array=True, units='V^2/Hz'),
            _SaveSpec(key=('processed', 'spring_constant'),
                      relpath='processed/spring-constant',
                      units='N/m', deviation='spring_constant_deviation'),
            ]
        return _load(filename=filename, group=group, specs=specs)

    def load_raw(self, filename=None, group='/'):
        """Load results saved during `.acquire()` by bumps, etc."""
        data = {}
        with _h5py.File(filename, 'r') as f:
            for name,loader in [('bump',_bump_load),
                                ('temperature', _temperature_load),
                                ('vibration', _vibration_load),
                                ]:
                n = self.config['num-{}s'.format(name)]
                if n > 0:
                    data[name] = []
                    for i in range(n):
                        try:
                            cwg = f['{}{}/{}/'.format(group, name, i)]
                        except KeyError:
                            pass
                        else:
                            data[name].append(loader(group=cwg))
        return data

Calibrator.save_results = staticmethod(_save_results)
