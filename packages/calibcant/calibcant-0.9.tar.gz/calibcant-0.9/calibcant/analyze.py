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

"""Calculate `k` from arrays of bumps, temperatures, and vibrations.

Separate the more general `analyze()` from the other calibration
functions in calibcant.

The relevent physical quantities are :
  Vzp_out  Output z-piezo voltage (what we generate)
  Vzp      Applied z-piezo voltage (after external ZPGAIN)
  Zp       The z-piezo position
  Zcant    The cantilever vertical deflection
  Vphoto   The photodiode vertical deflection voltage (what we measure)
  Fcant    The force on the cantilever
  T        The temperature of the cantilever and surrounding solution
           (another thing we measure)
  k_b      Boltzmann's constant

Which are related by the parameters:
  zp_gain           Vzp_out / Vzp
  zp_sensitivity    Zp / Vzp
  photo_sensitivity Vphoto / Zcant
  k_cant            Fcant / Zcant


>>> import numpy
>>> from .config import CalibrateConfig

>>> config = CalibrateConfig()
>>> bumps = numpy.array((15.9e6, 16.9e6, 16.3e6))
>>> temperatures = numpy.array((295, 295.2, 294.8))
>>> vibrations = numpy.array((2.20e-5, 2.22e-5, 2.21e-5))

>>> k,k_s = analyze(bumps=bumps, temperatures=temperatures,
...     vibrations=vibrations)
>>> (k, k_s)  # doctest: +ELLIPSIS
(0.0493..., 0.00248...)

Most of the error in this example comes from uncertainty in the
photodiode sensitivity (bumps).

>>> k_s/k  # doctest: +ELLIPSIS
0.0503...
>>> bumps.std()/bumps.mean()  # doctest: +ELLIPSIS
0.0251...
>>> temperatures.std()/temperatures.mean()  # doctest: +ELLIPSIS
0.000553...
>>> vibrations.std()/vibrations.mean()  # doctest: +ELLIPSIS
0.00369...
"""

import h5py as _h5py
import numpy as _numpy
try:
    from scipy.constants import Boltzmann as _kB  # in J/K
except ImportError:
    from scipy.constants import Bolzmann as _kB  # in J/K
# Bolzmann -> Boltzmann patch submitted:
#   http://projects.scipy.org/scipy/ticket/1417
# Fixed in scipy commit 4716d91, Apr 2, 2011, during work after v0.9.0rc5.

try:
    import matplotlib as _matplotlib
    import matplotlib.pyplot as _matplotlib_pyplot
    import time as _time  # for timestamping lines on plots
except (ImportError, RuntimeError), e:
    _matplotlib = None
    _matplotlib_import_error = e

from h5config.storage.hdf5 import h5_create_group as _h5_create_group
from pypiezo.base import get_axis_name as _get_axis_name

from . import LOG as _LOG
from . import package_config as _package_config

from .bump_analyze import analyze as _bump_analyze
from .bump_analyze import save as _bump_save
from .temperature_analyze import analyze as _temperature_analyze
from .temperature_analyze import save as _temperature_save
from .vibration_analyze import analyze as _vibration_analyze
from .vibration_analyze import save as _vibration_save
from .util import SaveSpec as _SaveSpec
from .util import save as _save


def analyze(bumps, temperatures, vibrations):
    """Analyze data from `get_calibration_data()`

    Inputs (all are arrays of recorded data):
      bumps measured (V_photodiode / nm_tip) proportionality constant
      temperatures    measured temperature (K)
      vibrations  measured V_photodiode variance in free solution (V**2)
    Outputs:
      k    cantilever spring constant (in N/m, or equivalently nN/nm)
      k_s  standard deviation in our estimate of k

    Notes:

    We're assuming vib is mostly from thermal cantilever vibrations
    (and then only from vibrations in the single vertical degree of
    freedom), and not from other noise sources.

    If the error is large, check the relative errors
    (`x.std()/x.mean()`)of your input arrays.  If one of them is
    small, don't bother repeating that measurment too often.  If one
    is large, try repeating that measurement more.  Remember that you
    need enough samples to have a valid error estimate in the first
    place, and that none of this addresses any systematic errors.
    """
    ps_m = bumps.mean()  # ps for photo-sensitivity
    ps_s = bumps.std()
    T_m = temperatures.mean()
    T_s = temperatures.std()
    v2_m = vibrations.mean()  # average voltage variance
    v2_s = vibrations.std()

    if ps_m == 0:
        raise ValueError('invalid bumps: {}'.format(bumps))
    if T_m == 0:
        raise ValueError('invalid temperatures: {}'.format(temperatures))
    if v2_m == 0:
        raise ValueError('invalid vibrations: {}'.format(vibrations))

    # Vphoto / photo_sensitivity = x
    # k = kB T / <x**2> = kB T photo_sensitivity**2 / Vphoto_var
    #
    # units,  photo_sensitivity =  Vphoto/(Zcant in m),
    # so Vphoto/photo_sensitivity = Zcant in m
    # so k = J/K * K / m^2 = J / m^2 = N/m
    k  = _kB * T_m * ps_m**2 / v2_m

    # propogation of errors
    # dk/dT = k/T
    dk_T = k/T_m * T_s
    # dk/dps = 2k/ps
    dk_ps = 2*k/ps_m * ps_s
    # dk/dv2 = -k/v2
    dk_v = -k/v2_m * v2_s

    k_s = _numpy.sqrt(dk_T**2 + dk_ps**2 + dk_v**2)

    _LOG.info('variable (units)         : '
              'mean +/- std. dev. (relative error)')
    _LOG.info('cantilever k (N/m)       : %g +/- %g (%g)' % (k, k_s, k_s/k))
    _LOG.info('photo sensitivity (V/m)  : %g +/- %g (%g)'
              % (ps_m, ps_s, ps_s/ps_m))
    _LOG.info('T (K)                    : %g +/- %g (%g)'
              % (T_m, T_s, T_s/T_m))
    _LOG.info('vibration variance (V^2) : %g +/- %g (%g)'
              % (v2_m, v2_s, v2_s/v2_m))

    if _package_config['matplotlib']:
        plot(bumps, temperatures, vibrations)

    return (k, k_s)


def plot(bumps, temperatures, vibrations):
    if not _matplotlib:
        raise _matplotlib_import_error
    figure = _matplotlib_pyplot.figure()

    bump_axes = figure.add_subplot(3, 1, 1)
    T_axes = figure.add_subplot(3, 1, 2)
    vib_axes = figure.add_subplot(3, 1, 3)

    timestamp = _time.strftime('%H%M%S')
    bump_axes.set_title('cantilever calibration %s' % timestamp)

    bump_axes.autoscale(tight=True)
    bump_axes.plot(bumps, 'g.-')
    bump_axes.set_ylabel('photodiode sensitivity (V/m)')
    T_axes.autoscale(tight=True)
    T_axes.plot(temperatures, 'r.-')
    T_axes.set_ylabel('temperature (K)')
    vib_axes.autoscale(tight=True)
    vib_axes.plot(vibrations, 'b.-')
    vib_axes.set_ylabel('thermal deflection variance (V^2)')

    if hasattr(figure, 'show'):
        figure.show()
    return figure
_plot = plot  # alternative name for use inside analyze_all()

def save_results(filename=None, group='/', bump=None,
                 temperature=None, vibration=None, spring_constant=None,
                 spring_constant_deviation=None):
    specs = [
        _SaveSpec(item=bump, relpath='raw/photodiode-sensitivity',
                  array=True, units='V/m'),
        _SaveSpec(item=temperature, relpath='raw/temperature',
                  array=True, units='K'),
        _SaveSpec(item=vibration, relpath='raw/vibration',
                  array=True, units='V^2/Hz'),
        _SaveSpec(item=spring_constant, relpath='processed/spring-constant',
                  units='N/m', deviation=spring_constant_deviation),
        ]
    _save(filename=filename, group=group, specs=specs)

def analyze_all(config, data, raw_data, maximum_relative_error=1e-5,
                filename=None, group=None, plot=False, dry_run=False):
    "(Re)analyze (and possibly plot) all data from a `calib()` run."
    if not data.get('bump', None):
        data['bump'] = _numpy.zeros((config['num-bumps'],), dtype=float)
    if not data.get('temperature', None):
        data['temperature'] = _numpy.zeros(
            (config['num-temperatures'],), dtype=float)
    if not data.get('vibrations', None):
        data['vibration'] = _numpy.zeros(
                (config['num-vibrations'],), dtype=float)
    if 'raw' not in data:
        data['raw'] = {}
    if 'bump' not in data['raw']:
        data['raw']['bump'] = _numpy.zeros((config['num-bumps'],), dtype=float)
    if 'temperature' not in data['raw']:
        data['raw']['temperature'] = _numpy.zeros(
        (config['num-temperatures'],), dtype=float)
    if 'vibration' not in data['raw']:
        data['raw']['vibration'] = _numpy.zeros(
        (config['num-vibrations'],), dtype=float)
    axis_config = config['afm']['piezo'].select_config(
        setting_name='axes',
        attribute_value=config['afm']['main-axis'],
        get_attribute=_get_axis_name)
    input_config = config['afm']['piezo'].select_config(
        setting_name='inputs', attribute_value='deflection')
    calibration_group = None
    if not isinstance(group, _h5py.Group) and not dry_run:
        f = _h5py.File(filename, mode='a')
        group = _h5_create_group(f, group)
    else:
        f = None
    try:
        bumps_changed = len(data['raw']['bump']) != len(data['bump'])
        for i,bump in enumerate(raw_data.get('bump', [])):  # compare values
            data['bump'][i],changed = check_bump(
                index=i, bump=bump, config=config, z_axis_config=axis_config,
                deflection_channel_config=input_config, plot=plot,
                maximum_relative_error=maximum_relative_error)
            if changed and not dry_run:
                bumps_changed = True
                bump_group = _h5_create_group(group, 'bump/{}'.format(i))
                _bump_save(group=bump_group, processed=data['bump'][i])
        temperatures_changed = len(data['raw']['temperature']) != len(
            data['temperature'])
        for i,temperature in enumerate(raw_data.get('temperature', [])):
            data['temperature'][i],changed = check_temperature(
                index=i, temperature=temperature, config=config,
                maximum_relative_error=maximum_relative_error)
            if changed and not dry_run:
                temperatures_changed = True
                temperature_group = _h5_create_group(
                    group, 'temperature/{}'.format(i))
                _temperature_save(
                    group=temperature_group, processed=data['temperature'][i])
        vibrations_changed = len(data['raw']['vibration']) != len(
            data['vibration'])
        for i,vibration in enumerate(raw_data.get('vibration', [])):
            data['vibration'][i],changed = check_vibration(
                    index=i, vibration=vibration, config=config,
                    deflection_channel_config=input_config, plot=plot,
                    maximum_relative_error=maximum_relative_error)
            if changed and not dry_run:
                vibrations_changed = True
                vibration_group = _h5_create_group(
                    group, 'vibration/{}'.format(i))
                _vibration_save(
                    group=vibration_group, processed=data['vibration'][i])
        if (bumps_changed or temperatures_changed or vibrations_changed
            ) and not dry_run:
            calibration_group = _h5_create_group(group, 'calibration')
            if bumps_changed:
                save_results(
                    group=calibration_group, bump=data['bump'])
            if temperatures_changed:
                save_results(
                    group=calibration_group, temperature=data['temperature'])
            if vibrations_changed:
                save_results(
                    group=calibration_group, vibration=data['vibration'])
        if len(raw_data.get('bump', [])) != len(data['bump']):
            raise ValueError(
                'not enough raw bump data: {} of {}'.format(
                    len(raw_data.get('bump', [])), len(data['bump'])))
        if len(raw_data.get('temperature', [])) != len(data['temperature']):
            raise ValueError(
                'not enough raw temperature data: {} of {}'.format(
                    len(raw_data.get('temperature', [])),
                    len(data['temperature'])))
        if len(raw_data['vibration']) != len(data['vibration']):
            raise ValueError(
                'not enough raw vibration data: {} of {}'.format(
                    len(raw_data.get('vibration', [])),
                    len(data['vibration'])))
        k,k_s,changed = check_calibration(
            k=data.get('processed', {}).get('spring_constant', None),
            k_s=data.get('processed', {}).get(
                'spring_constant_deviation', None),
            bumps=data['bump'],
            temperatures=data['temperature'], vibrations=data['vibration'],
            maximum_relative_error=maximum_relative_error)
        if changed and not dry_run:
            if calibration_group is None:
                calibration_group = _h5_create_group(group, 'calibration')
            save_results(
                group=calibration_group,
                spring_constant=k, spring_constant_deviation=k_s)
    finally:
        if f:
            f.close()
    if plot:
        _plot(bumps=data['bump'],
              temperatures=data['temperature'],
              vibrations=data['vibration'])
    return (k, k_s)

def check_bump(index, bump, config=None, maximum_relative_error=0, **kwargs):
    changed = False
    try:
        bump_config = bump['config']['bump']
    except KeyError:
        bump_config = config['bump']
    sensitivity = _bump_analyze(
        config=bump_config, data=bump['raw'], **kwargs)
    if bump.get('processed', None) is None:
        changed = True            
        _LOG.warn('new analysis for bump {}: {}'.format(index, sensitivity))
    else:
        rel_error = abs(sensitivity - bump['processed'])/bump['processed']
        if rel_error > maximum_relative_error:
            changed = True
            _LOG.warn(("new analysis doesn't match for bump {}: {} -> {} "
                       "(difference: {}, relative error: {})").format(
                    index, bump['processed'], sensitivity,
                    sensitivity-bump['processed'], rel_error))
    return (sensitivity, changed)

def check_temperature(index, temperature, config=None,
                      maximum_relative_error=0, **kwargs):
    changed = False
    try:
        temp_config = temperature['config']['temperature']
    except KeyError:
        temp_config = config['temperature']
    temp = _temperature_analyze(
        config=temp_config,
        temperature=temperature['raw'], **kwargs)
    if temperature.get('processed', None) is None:
        changed = True            
        _LOG.warn('new analysis for temperature {}: {}'.format(index, temp))
    else:
        rel_error = abs(temp - temperature['processed']
                        )/temperature['processed']
        if rel_error > maximum_relative_error:
            changed = True
            _LOG.warn(("new analysis doesn't match for temperature "
                       "{} -> {} (difference: {}, relative error: {})"
                       ).format(
                    index, temperature['processed'], temp,
                    temp-temperature['processed'], rel_error))
    return (temp, changed)

def check_vibration(index, vibration, config=None, maximum_relative_error=0,
                    **kwargs):
    changed = False
    try:
        vib_config = vibration['config']['vibration']
    except KeyError:
        vib_config = config['vibration']
    variance = _vibration_analyze(
        config=vib_config, deflection=vibration['raw'], **kwargs)
    if vibration.get('processed', None) is None:
        changed = True
        _LOG.warn('new analysis for vibration {}: {}'.format(
                index, variance))
    else:
        rel_error = abs(variance-vibration['processed'])/vibration['processed']
        if rel_error > maximum_relative_error:
            _LOG.warn(("new analysis doesn't match for vibration {}: {} != {} "
                       "(difference: {}, relative error: {})").format(
                    index, variance, vibration['processed'],
                    variance-vibration['processed'], rel_error))
    return (variance, changed)

def check_calibration(k, k_s, maximum_relative_error, **kwargs):
    changed = False
    new_k,new_k_s = analyze(**kwargs)
    if k is None:
        changed = True
        _LOG.warn('new analysis for the spring constant: {}'.format(new_k))
    else:
        rel_error = abs(new_k-k)/k
        if rel_error > maximum_relative_error:
            changed = True
            _LOG.warn(("new analysis doesn't match for the spring constant: "
                       "{} != {} (difference: {}, relative error: {})").format(
                    new_k, k, new_k-k, rel_error))
    if k_s is None:
        changed = True
        _LOG.warn('new analysis for the spring constant deviation: {}'.format(
                new_k_s))
    else:
        rel_error = abs(new_k_s-k_s)/k_s
        if rel_error > maximum_relative_error:
            changed = True
            _LOG.warn(
                ("new analysis doesn't match for the spring constant deviation"
                 ": {} != {} (difference: {}, relative error: {})").format(
                    new_k_s, k_s, new_k_s-k_s, rel_error))
    return (new_k, new_k_s, changed)
