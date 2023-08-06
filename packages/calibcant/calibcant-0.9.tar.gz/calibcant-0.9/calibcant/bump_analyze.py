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

"""Surface bump analysis (measures photodiode sensitivity).

Separate the more general `analyze()` from the other `bump_*()`
functions in calibcant.

The relevant physical quantities are:

* `Vzp_out`  Output z-piezo voltage (what we generate)
* `Vzp`      Applied z-piezo voltage (after external amplification)
* `Zp`       The z-piezo position
* `Zcant`    The cantilever vertical deflection
* `Vphoto`   The photodiode vertical deflection voltage (what we measure)

Which are related by the parameters:

* `zp_gain`           Vzp_out / Vzp
* `zp_sensitivity`    Zp / Vzp
* `photo_sensitivity` Vphoto / Zcant

`photo_sensitivity` is measured by bumping the cantilever against the
surface, where `Zp = Zcant` (see `calibrate.bump_acquire()`).  The
measured slope `Vphoto/Vout` is converted to `photo_sensitivity` with
`analyze()`.

>>> import os
>>> from pprint import pprint
>>> import tempfile
>>> import numpy
>>> from h5config.storage.hdf5 import pprint_HDF5
>>> from pypiezo.config import ChannelConfig, AxisConfig
>>> from .config import BumpConfig

>>> fd,filename = tempfile.mkstemp(suffix='.h5', prefix='calibcant-')
>>> os.close(fd)

>>> config = BumpConfig()
>>> z_channel_config = ChannelConfig()
>>> z_channel_config['name'] = 'z'
>>> z_channel_config['maxdata'] = 200
>>> z_channel_config['conversion-coefficients'] = (0,1)
>>> z_channel_config['conversion-origin'] = 0
>>> z_axis_config = AxisConfig()
>>> z_axis_config['channel'] = z_channel_config
>>> deflection_channel_config = ChannelConfig()
>>> deflection_channel_config['name'] = 'deflection'
>>> deflection_channel_config['maxdata'] = 200
>>> deflection_channel_config['conversion-coefficients'] = (0,1)
>>> deflection_channel_config['conversion-origin'] = 0

>>> raw = {
...     'z': numpy.arange(100, dtype=numpy.uint16),
...     'deflection': numpy.arange(100, dtype=numpy.uint16),
...     }
>>> raw['deflection'][:50] = 50
>>> processed = analyze(
...     config=config, data=raw, z_axis_config=z_axis_config,
...     deflection_channel_config=deflection_channel_config)
>>> plot(data=raw)  # TODO: convert to V and m
>>> save(filename=filename, group='/bump/',
...     config=config, raw=raw, processed=processed)

>>> pprint_HDF5(filename)  # doctest: +ELLIPSIS, +REPORT_UDIFF
/
  /bump
    /bump/config
      /bump/config/bump
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
    /bump/processed
      <HDF5 dataset "data": shape (), type "<f8">
        1.00...
      <HDF5 dataset "units": shape (), type "|S3">
        V/m
    /bump/raw
      /bump/raw/deflection
        <HDF5 dataset "data": shape (100,), type "<u2">
          [50 50 ... 50 51 52 ... 97 98 99]
        <HDF5 dataset "units": shape (), type "|S4">
          bits
      /bump/raw/z
        <HDF5 dataset "data": shape (100,), type "<u2">
          [ 0  1  2  3  ... 97 98 99]
        <HDF5 dataset "units": shape (), type "|S4">
          bits

>>> data = load(filename=filename, group='/bump/')

>>> pprint(data)  # doctest: +ELLIPSIS, +REPORT_UDIFF
{'config': {'bump': <BumpConfig ...>},
 'processed': 1.00...,
 'raw': {'deflection': array([50, 50, ..., 52, 53, ..., 98, 99], dtype=uint16),
         'z': array([ 0,  1,  2,  ..., 97, 98, 99], dtype=uint16)}}

>>> os.remove(filename)
"""

import numpy as _numpy
from scipy.optimize import leastsq as _leastsq

try:
    import matplotlib as _matplotlib
    import matplotlib.pyplot as _matplotlib_pyplot
    import time as _time  # for timestamping lines on plots
except (ImportError, RuntimeError), e:
    _matplotlib = None
    _matplotlib_import_error = e

from pypiezo.base import convert_bits_to_volts as _convert_bits_to_volts
from pypiezo.base import convert_bits_to_meters as _convert_bits_to_meters
from pypiezo.config import AxisConfig as _AxisConfig
from pypiezo.config import InputChannelConfig as _InputChannelConfig

from . import LOG as _LOG
from . import package_config as _package_config
from .config import Linear as _Linear
from .config import Quadratic as _Quadratic
from .config import BumpConfig as _BumpConfig
from .util import SaveSpec as _SaveSpec
from .util import save as _save
from .util import load as _load


def analyze(config, data, z_axis_config,
            deflection_channel_config, plot=False):
    """Return the slope of the bump.

    Inputs:
      data              dictionary of data in DAC/ADC bits
      config            `.config._BumpConfig` instance
      z_axis_config     z `pypiezo.config.AxisConfig` instance
      deflection_channel_config
                        deflection `pypiezo.config.InputChannelConfig` instance
      plot              boolean overriding matplotlib config setting.
    Returns:
      photo_sensitivity (Vphoto/Zcant) in Volts/m

    Checks for strong correlation (r-value) and low randomness chance
    (p-value).
    """
    z = _convert_bits_to_meters(z_axis_config, data['z'])
    deflection = _convert_bits_to_volts(
        deflection_channel_config, data['deflection'])
    high_voltage_rail = _convert_bits_to_volts(
        deflection_channel_config, deflection_channel_config['maxdata'])
    if config['model'] == _Linear:
        kwargs = {
            'param_guesser': limited_linear_param_guess,
            'model': limited_linear,
            'sensitivity_from_fit_params': limited_linear_sensitivity,
            }
    else:  # _Quadratic
        kwargs = {
            'param_guesser': limited_quadratic_param_guess,
            'model': limited_quadratic,
            'sensitivity_from_fit_params': limited_quadratic_sensitivity,
            }
    photo_sensitivity = fit(
        z, deflection, high_voltage_rail=high_voltage_rail, plot=plot,
        **kwargs)
    return photo_sensitivity

def limited_linear(x, params, high_voltage_rail):
    """
    Model the bump as:
      flat region (off-surface)
      linear region (in-contact)
      flat region (high-voltage-rail)
    Parameters:
      x_contact (x value for the surface-contact kink)
      y_contact (y value for the surface-contact kink)
      slope (dy/dx at the surface-contact kink)
    """
    x_contact,y_contact,slope = params
    off_surface_mask = x <= x_contact
    on_surface_mask = x > x_contact
    y = (off_surface_mask * y_contact +
         on_surface_mask * (y_contact + slope*(x-x_contact)))
    y = _numpy.clip(y, y_contact, high_voltage_rail)
    return y

def limited_linear_param_guess(x, y):
    """
    Guess rough parameters for a limited_linear model.  Assumes the
    bump approaches (raising the deflection as it does so) first.
    Retracting after the approach is optional.  Approximates the contact
    position and an on-surface (high) position by finding first crossings
    of thresholds 0.3 and 0.7 of the y value's total range.  Not the
    most efficient algorithm, but it seems fairly robust.
    """
    y_contact = float(y.min())
    y_max = float(y.max())
    i = 0
    y_low  = y_contact + 0.3 * (y_max-y_contact)
    y_high = y_contact + 0.7 * (y_max-y_contact)
    while y[i] < y_low:
        i += 1
    i_low = i
    while y[i] < y_high:
        i += 1
    i_high = i
    x_contact = float(x[i_low])
    x_high = float(x[i_high])
    if x_high == x_contact:  # things must be pretty flat
        x_contact = (x_contact + x[0]) / 2
    if x_high == x_contact:
        x_high = x[1]
    slope = (y_high - y_contact) / (x_high - x_contact)
    return (x_contact, y_contact, slope)

def limited_linear_sensitivity(params):
    """
    Return the estimated sensitivity to small deflections according to
    limited_linear fit parameters.
    """
    slope = params[2]
    return slope

def limited_quadratic(x, params, high_voltage_rail):
    """
    Model the bump as:
      flat region (off-surface)
      quadratic region (in-contact)
      flat region (high-voltage-rail)
    Parameters:
      x_contact (x value for the surface-contact kink)
      y_contact (y value for the surface-contact kink)
      slope (dy/dx at the surface-contact kink)
      quad (d**2 y / dx**2, allow decreasing sensitivity with increased x)
    """
    x_contact,y_contact,slope,quad = params
    off_surface_mask = x <= x_contact
    on_surface_mask = x > x_contact
    y = (off_surface_mask * y_contact +
         on_surface_mask * (
            y_contact + slope*(x-x_contact) + quad*(x-x_contact)**2))
    y = _numpy.clip(y, y_contact, high_voltage_rail)
    return y

def limited_quadratic_param_guess(x, y):
    """
    Guess rough parameters for a limited_quadratic model.  Assumes the
    bump approaches (raising the deflection as it does so) first.
    Retracting after the approach is optional.  Approximates the contact
    position and an on-surface (high) position by finding first crossings
    of thresholds 0.3 and 0.7 of the y value's total range.  Not the
    most efficient algorithm, but it seems fairly robust.
    """
    x_contact,y_contact,linear_slope = limited_linear_param_guess(x,y)
    contact_depth = x.max() - x_contact
    slope = linear_slope / 2
    quad = slope / contact_depth
    # The above slope and quad were chosen so
    #   x = contact_depth
    #   x*slope + x**2 * slope == x * linear_slope
    return (x_contact, y_contact, slope, quad)

def limited_quadratic_sensitivity(params):
    """
    Return the estimated sensitivity to small deflections according to
    limited_quadratic fit parameters.
    """
    slope = params[2]
    return slope

def fit(z, deflection, high_voltage_rail,
        param_guesser=limited_quadratic_param_guess,
        model=limited_quadratic,
        sensitivity_from_fit_params=limited_quadratic_sensitivity,
        plot=False):
    """Fit a aurface bump and return the photodiode sensitivitiy.

    Parameters:
      z              piezo position in meters
      deflection     photodiode deflection in volts
      param_guesser  function that guesses initial model parameters
      model          parametric model of deflection vs. z
      sensitivity_from_fit_params  given fit params, return the sensitivity
      plot              boolean overriding matplotlib config setting.
    Returns:
      photodiode_sensitivity  photodiode volts per piezo meter
    """
    _LOG.debug('fit bump data with model %s' % model)
    def residual(p, deflection, z):
        return model(z, p, high_voltage_rail=high_voltage_rail) - deflection
    param_guess = param_guesser(z, deflection)
    try:
        p,cov,info,mesg,ier = _leastsq(
            residual, param_guess, args=(deflection, z), full_output=True,
            maxfev=int(10e3))
    except ValueError:
        zd = _numpy.ndarray(list(z.shape) + [2], dtype=z.dtype)
        zd[:,0] = z
        zd[:,1] = deflection
        _numpy.savetxt('/tmp/z-deflection.dat', zd, delimiter='\t')
        raise
    _LOG.debug('fitted params: %s' % p)
    _LOG.debug('covariance matrix: %s' % cov)
    #_LOG.debug('info: %s' % info)
    _LOG.debug('message: %s' % mesg)
    if ier == 1:
        _LOG.debug('solution converged')
    else:
        _LOG.debug('solution did not converge')
    if plot or _package_config['matplotlib']:
        yguess = model(z, param_guess, high_voltage_rail=high_voltage_rail)
        yfit = model(z, p, high_voltage_rail=high_voltage_rail)
        _plot({'z': z, 'deflection': deflection}, yguess=yguess, yfit=yfit)
    return sensitivity_from_fit_params(p)

def save(filename=None, group='/', config=None, z_axis_config=None,
         deflection_channel_config=None, raw=None, processed=None):
    specs = [
        _SaveSpec(item=config, relpath='config/bump', config=_BumpConfig),
        _SaveSpec(item=z_axis_config, relpath='config/z', config=_AxisConfig),
        _SaveSpec(item=deflection_channel_config, relpath='config/deflection',
                  config=_InputChannelConfig),
        _SaveSpec(item=processed, relpath='processed', units='V/m'),
        ]
    if raw is not None:
        for key in raw.keys():
            specs.append(_SaveSpec(
                    item=raw[key], relpath='raw/{}'.format(key), array=True,
                    units='bits'))
    _save(filename=filename, group=group, specs=specs)

def load(filename=None, group='/'):
    specs = [
        _SaveSpec(key=('config', 'bump'), relpath='config/bump',
                  config=_BumpConfig),
        _SaveSpec(key=('config', 'z_axis_config'), relpath='config/z',
                  config=_AxisConfig),
        _SaveSpec(key=('config', 'deflection_channel_config'),
                  relpath='config/deflection', config=_InputChannelConfig),
        _SaveSpec(key=('raw', 'z'), relpath='raw/z', array=True, units='bits'),
        _SaveSpec(key=('raw', 'deflection'), relpath='raw/deflection',
                  array=True, units='bits'),
        _SaveSpec(key=('processed',), relpath='processed', units='V/m'),
        ]
    return _load(filename=filename, group=group, specs=specs)

def plot(data, yguess=None, yfit=None):
    "Plot the bump (Vphoto vs Vzp)"
    if not _matplotlib:
        raise _matplotlib_import_error
    figure = _matplotlib_pyplot.figure()
    if yfit is None:
        axes = figure.add_subplot(1, 1, 1)
    else:
        axes = figure.add_subplot(2, 1, 1)
        residual_axes = figure.add_subplot(2, 1, 2)
    timestamp = _time.strftime('%H%M%S')

    axes.hold(True)
    axes.plot(data['z'], data['deflection'], '.', label='bump')
    if yguess != None:
        axes.plot(data['z'], yguess, 'g-', label='guess')
    if yfit != None:
        axes.plot(data['z'], yfit, 'r-', label='fit')

    axes.autoscale(tight=True)
    axes.set_title('bump surface %s' % timestamp)
    #axes.legend(loc='upper left')
    axes.set_xlabel('Z piezo (meters)')
    axes.set_ylabel('Photodiode (Volts)')
    if yfit is not None:
        # second subplot for residual
        residual_axes.plot(data['z'], data['deflection'] - yfit,
                           'r-', label='residual')
        residual_axes.autoscale(tight=True)
        #residual_axes.legend(loc='upper right')
        residual_axes.set_xlabel('Z piezo (meters)')
        residual_axes.set_ylabel('Photodiode (Volts)')
    if hasattr(figure, 'show'):
        figure.show()
    return figure
_plot = plot  # alternative name for use inside fit()
