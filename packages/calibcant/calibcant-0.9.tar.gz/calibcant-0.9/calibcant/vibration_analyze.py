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

"""Thermal vibration analysis.

Separate the more general `analyze()` from the other `vibration`
functions in calibcant.

The relevent physical quantities are :
  Vphoto   The photodiode vertical deflection voltage (what we measure)

>>> import os
>>> from pprint import pprint
>>> import random
>>> import tempfile
>>> import numpy
>>> from .config import VibrationConfig
>>> from h5config.storage.hdf5 import pprint_HDF5
>>> from pypiezo.test import get_piezo_config
>>> from pypiezo.base import convert_volts_to_bits

>>> fd,filename = tempfile.mkstemp(suffix='.h5', prefix='calibcant-')
>>> os.close(fd)

>>> piezo_config = get_piezo_config()
>>> config = VibrationConfig()
>>> config['frequency'] = 50e3

We'll be generating a test vibration time series with the following
parameters.  Make sure these are all floats to avoid accidental
integer division in later steps.

>>> m = 5e-11       # kg
>>> gamma = 1.6e-6  # N*s/m
>>> k = 0.05        # N/m
>>> T = 1/config['frequency']
>>> T  # doctest: +ELLIPSIS
2...e-05
>>> N = int(2**15)  # count
>>> F_sigma = 1e3   # N

where `T` is the sampling period, `N` is the number of samples, and
`F_sigma` is the standard deviation of the white-noise external force.
Note that the resonant frequency is less than the Nyquist frequency so
we don't have to worry too much about aliasing.

>>> w0 = numpy.sqrt(k/m)
>>> f0 = w0/(2*numpy.pi)
>>> f0  # doctest: +ELLIPSIS
5032.9...
>>> f_nyquist = config['frequency']/2
>>> f_nyquist  # doctest: +ELLIPSIS
25000.0...

The damping ratio is

>>> damping = gamma / (2*m*w0)
>>> damping  # doctest: +ELLIPSIS
0.505...

The quality factor is 

>>> Q = m*w0 / gamma
>>> Q  # doctest: +ELLIPSIS
0.988...
>>> (1 / (2*damping)) / Q  # doctest: +ELLIPSIS
1.000...

We expect the white-noise power spectral density (PSD) to be a flat
line at

>>> F0 = F_sigma**2 * 2 * T

because the integral from `0` `1/2T` should be `F_sigma**2`.

The expected time series PSD parameters are

>>> A = f0
>>> B = gamma/(m*2*numpy.pi)
>>> C = F0/(m**2*(2*numpy.pi)**4)

Simulate a time series with the proper PSD using center-differencing.

  m\ddot{x} + \gamma \dot{x} + kx = F

  m \frac{x_{i+1} - 2x_i + x_{i-1}}{T**2}
    + \gamma \frac{x_{i+1}-x_{i-1}}{T}
    + kx_i = F_i

  a x_{i+1} + b x_{i} + c x_{i-1} = F_i

where `T` is the sampling period, `i=t/T` is the measurement index,
`a=m/T**2+gamma/2T`, `b=-2m/T**2+k`, and `c=m/T**2-gamma/2T`.
Rearranging and shifting to `j=i-1`

  x_j = \frac{F_{i-1} - bx_{i-1} - cx_{i-2}}{a}

>>> a = m/T**2 + gamma/(2*T)
>>> b = -2*m/T**2 + k
>>> c = m/T**2 - gamma/(2*T)
>>> x = numpy.zeros((N+2,), dtype=numpy.float)  # two extra initial points
>>> F = numpy.zeros((N,), dtype=numpy.float)
>>> for i in range(2, x.size):
...     Fp = random.gauss(mu=0, sigma=F_sigma)
...     F[i-2] = Fp
...     xp = x[i-1]
...     xpp = x[i-2]
...     x[i] = (Fp - b*xp - c*xpp)/a
>>> x = x[2:]  # drop the initial points

Convert the simulated data to bits.

>>> deflection = x
>>> deflection_bits = convert_volts_to_bits(
...     piezo_config.select_config('inputs', 'deflection'), x)

Analyze the simulated data.

>>> naive = analyze_naive(deflection)
>>> naive  # doctest: +SKIP
136871517.43486854
>>> abs(naive / 136.9e6 - 1) < 0.1
True

>>> processed = analyze(
...     deflection_bits, config,
...     piezo_config.select_config('inputs', 'deflection'))
>>> processed  # doctest: +SKIP
136457906.25574699

>>> plot(deflection=deflection_bits, config=config)
>>> save(filename=filename, group='/vibration/',
...     raw=deflection_bits, config=config,
...     deflection_channel_config=piezo_config.select_config(
...         'inputs', 'deflection'),
...     processed=processed)

>>> pprint_HDF5(filename)  # doctest: +ELLIPSIS, +REPORT_UDIFF
/
  /vibration
    /vibration/config
      /vibration/config/deflection
        <HDF5 dataset "analog-reference": shape (), type "|S6">
          ground
        <HDF5 dataset "channel": shape (), type "<i4">
          0
        <HDF5 dataset "conversion-coefficients": shape (2,), type "<i4">
          [0 1]
        <HDF5 dataset "conversion-origin": shape (), type "<i4">
          0
        <HDF5 dataset "device": shape (), type "|S12">
          /dev/comedi0
        <HDF5 dataset "inverse-conversion-coefficients": shape (2,), type "<i4">
          [0 1]
        <HDF5 dataset "inverse-conversion-origin": shape (), type "<i4">
          0
        <HDF5 dataset "maxdata": shape (), type "<i4">
          100
        <HDF5 dataset "name": shape (), type "|S10">
          deflection
        <HDF5 dataset "range": shape (), type "<i4">
          0
        <HDF5 dataset "subdevice": shape (), type "<i4">
          -1
      /vibration/config/vibration
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
    /vibration/processed
      <HDF5 dataset "data": shape (), type "<f8">
        ...
      <HDF5 dataset "units": shape (), type "|S6">
        V^2/Hz
    /vibration/raw
      <HDF5 dataset "data": shape (32768,), type "<f8">
        [...]
      <HDF5 dataset "units": shape (), type "|S4">
        bits

>>> data = load(filename=filename, group='/vibration/')

>>> pprint(data)  # doctest: +ELLIPSIS
{'config': {'vibration': <InputChannelConfig ...>},
 'processed': ...,
 'raw': array([...])}
>>> data['processed']  # doctest: +SKIP
136457906.25574699
>>> abs(data['processed'] / 136.5e6 - 1) < 0.1
True

>>> os.remove(filename)
"""

import os as _os
import time as _time

import h5py as _h5py
import numpy as _numpy
from scipy.optimize import leastsq as _leastsq

try:
    import matplotlib as _matplotlib
    import matplotlib.pyplot as _matplotlib_pyplot
    import time as _time  # for timestamping lines on plots
except (ImportError, RuntimeError), e:
    _matplotlib = None
    _matplotlib_import_error = e

from h5config.storage.hdf5 import HDF5_Storage as _HDF5_Storage
from h5config.storage.hdf5 import h5_create_group as _h5_create_group
import FFT_tools as _FFT_tools
from pypiezo.base import convert_bits_to_volts as _convert_bits_to_volts
from pypiezo.config import InputChannelConfig as _InputChannelConfig

from . import LOG as _LOG
from . import package_config as _package_config
from .config import Variance as _Variance
from .config import BreitWigner as _BreitWigner
from .config import OffsetBreitWigner as _OffsetBreitWigner
from .config import VibrationConfig as _VibrationConfig
from .util import SaveSpec as _SaveSpec
from .util import save as _save
from .util import load as _load


def analyze_naive(deflection):
    """Calculate the deflection variance in Volts**2.

    This method is simple and easy to understand, but it highly
    succeptible to noise, drift, etc.
    
    Inputs
      deflection : numpy array with deflection timeseries in Volts.
    """
    std = deflection.std()
    var = std**2
    _LOG.debug('naive deflection variance: %g V**2' % var)
    return var

def analyze(deflection, config, deflection_channel_config,
            plot=False):
    """Calculate the deflection variance in Volts**2.

    Improves on `analyze_naive()` by first converting `Vphoto(t)`
    to frequency space, and fitting a Breit-Wigner in the relevant
    frequency range (see cantilever_calib.pdf for derivation).
    However, there may be cases where the fit is thrown off by noise
    spikes in frequency space.  To protect from errors, the fitted
    variance is compared to the naive variance (where all noise is
    included), and the minimum variance is returned.

    Inputs:
      deflection        Vphoto deflection input in bits.
      config            `.config.VibrationConfig` instance
      deflection_channel_config
                        deflection `pypiezo.config.ChannelConfig` instance
      plot              boolean overriding matplotlib config setting.

    The conversion to frequency space generates an average power
    spectrum by breaking the data into windowed chunks and averaging
    the power spectrums for the chunks together. See
    `FFT_tools.unitary_avg_power_spectrum()` for details.
    """
    # convert the data from bits to volts
    deflection_v = _convert_bits_to_volts(
        deflection_channel_config, deflection)
    mean = deflection_v.mean()
    _LOG.debug('average thermal deflection (Volts): %g' % mean)

    naive_variance = analyze_naive(deflection_v)
    if config['model'] == _Variance:
        return naive_variance
    
    # Compute the average power spectral density per unit time (in uV**2/Hz)
    _LOG.debug('compute the averaged power spectral density in uV**2/Hz')
    freq_axis,power = _FFT_tools.unitary_avg_power_spectrum(
        (deflection_v - mean)*1e6, config['frequency'],
        config['chunk-size'], config['overlap'],
        config['window'])

    if config['smooth-window'] and config['smooth-length']:
        n = config['smooth-length']
        smooth_window = config['smooth-window'](length=n)
        smooth_window /= smooth_window.sum()
    else:
        smooth_window = None
    A,B,C,D = fit_psd(
        freq_axis, power,
        min_frequency=config['minimum-fit-frequency'],
        max_frequency=config['maximum-fit-frequency'],
        smooth_window=smooth_window,
        offset=config['model'] == _OffsetBreitWigner)

    _LOG.debug('fit PSD(f) = C / ((A**2-f**2)**2 + (f*B)**2) with '
               'A = %g, B = %g, C = %g, D = %g' % (A, B, C, D))

    if plot or _package_config['matplotlib']:
        _plot(deflection, freq_axis, power, A, B, C, D, config=config)

    # Our A is in uV**2, so convert back to Volts**2
    fitted_variance = breit_wigner_area(A,B,C) * 1e-12

    _LOG.debug('fitted deflection variance: %g V**2' % fitted_variance)

    return min(fitted_variance, naive_variance)

def breit_wigner(f, A, B, C, D=0):
    """Breit-Wigner (sortof).

    Inputs
      f  Frequency
      A  Resonant frequency
      B  Quality Q = A/B
      C  Scaling factor
      D  Optional white-noise offset

    All parameters must be postive.
    """
    return abs(C) / ((A**2-f**2)**2 + (B*f)**2) + abs(D)

def fit_psd(freq_axis, psd_data, min_frequency=500, max_frequency=25000,
            smooth_window=_FFT_tools.window_hann(10), offset=False):
    """Fit the FFTed vibration data to a Breit-Wigner.

    Inputs
      freq_axis      array of frequencies in Hz
      psd_data       array of PSD amplitudes for the frequencies in freq_axis
      min_frequency  lower bound of Breit-Wigner fitting region
      max_frequency  upper bound of Breit-Wigner fitting region
      smooth_window  array for smoothing the PSD before guessing params
      offset         add a white-noise offset to the Breit-Wigner model
    Output
      Breit-Wigner model fit parameters `A`, `B`, `C`, and `D`.
    """
    # cut out the relevent frequency range
    _LOG.debug('cut the frequency range %g to %g Hz'
               % (min_frequency, max_frequency))
    imin = 0
    while freq_axis[imin] < min_frequency : imin += 1
    imax = imin
    while freq_axis[imax] < max_frequency : imax += 1
    assert imax >= imin + 10 , 'less than 10 points in freq range (%g,%g)' % (
        min_frequency, max_frequency)

    # generate guesses for Breit-Wigner parameters A, B, C, and D
    if hasattr(smooth_window, '__len__'):
        smooth_psd_data = _numpy.convolve(psd_data, smooth_window, mode='same')
    else:
        smooth_psd_data = psd_data
    max_psd_index = _numpy.argmax(smooth_psd_data[imin:imax]) + imin
    max_psd = psd_data[max_psd_index]
    res_freq = freq_axis[max_psd_index]

    # Breit-Wigner L(x) = C / ((A**2-x**2)**2 + (B*x)**2)
    # is expected power spectrum for
    # x'' + B x' + A^2 x'' = F_external(t)/m
    # (A = omega_0)
    # C = (2 k_B T B) / (pi m)
    # 
    # A = resonant frequency
    # peak at  x_res = sqrt(A^2 - B^2/2)  (by differentiating)
    #  which could be complex if there isn't a peak (overdamped)
    # peak height    = C / (3 x_res^4 + A^4)
    #
    # Q = A/B
    #
    # Guessing Q = 1 is pretty safe.

    Q_guess = 1

    # so x_res^2 = B^2 Q^2 - B^2/2 = (Q^2-1/2)B^2 
    #    B = x_res / sqrt(Q^2-1/2)
    B_guess = res_freq / _numpy.sqrt(Q_guess**2-0.5)
    A_guess = Q_guess*B_guess
    C_guess = max_psd * (-res_freq**4 + A_guess**4)
    if offset:
        D_guess = psd_data[-1]
        C_guess -= D_guess
    else:
        D_guess = 0
    _LOG.debug(('guessed params: resonant freq %g, max psd %g, Q %g, A %g, '
                'B %g, C %g, D %g') % (
            res_freq, max_psd, Q_guess, A_guess, B_guess, C_guess, D_guess))
    # Half width w on lower side when L(a-w) = L(a)/2
    #  (a**2 - (a-w)**2)**2 + (b*(a-w))**2 = 2*(b*a)**2
    # Let W=(a-w)**2, A=a**2, and B=b**2
    #  (A - W)**2 + BW = 2*AB
    #  W**2 - 2AW + A**2 + BW = 2AB
    #  W**2 + (B-2A)W + (A**2-2AB) = 0
    #  W = (2A-B)/2 * [1 +/- sqrt(1 - 4(A**2-2AB)/(B-2A)**2]
    #    = (2A-B)/2 * [1 +/- sqrt(1 - 4A(A-2B)/(B-2A)**2]
    #  (a-w)**2 = (2A-B)/2 * [1 +/- sqrt(1 - 4A(A-2B)/(B-2A)**2]
    #  so w is a disaster ;)
    # For some values of A and B (non-underdamped), W is imaginary or negative.
    #
    # The mass m is given by m = k_B T / (pi A)
    # The spring constant k is given by k = m (omega_0)**2
    # The quality factor Q is given by Q = omega_0 m / gamma

    # Fitting the PSD of V = photoSensitivity*x just rescales the parameters

    # fit Breit-Wigner using scipy.optimize.leastsq
    def residual(p, y, x):
        return breit_wigner(x, *p) - y
    if offset:
        guess = _numpy.array((A_guess, B_guess, C_guess, D_guess))
    else:
        guess = _numpy.array((A_guess, B_guess, C_guess))

    p,cov,info,mesg,ier = _leastsq(
        residual, guess,
        args=(psd_data[imin:imax], freq_axis[imin:imax]),
        full_output=True, maxfev=10000)
    _LOG.debug('fitted params: %s' % p)
    _LOG.debug('covariance matrix: %s' % cov)
    #_LOG.debug('info: %s' % info)
    _LOG.debug('message: %s' % mesg)
    if ier == 1:
        _LOG.debug('solution converged')
    else:
        _LOG.debug('solution did not converge')
    if offset:
        A,B,C,D = p
    else:
        A,B,C = p
        D = 0
    A=abs(A) # A and B only show up as squares in f(x)
    B=abs(B) # so ensure we get positive values.
    C=abs(C) # Only abs(C) is used in breit_wigner().
    return (A, B, C, D)

def breit_wigner_area(A, B, C):
    # Integrating the the power spectral density per unit time (power) over the
    # frequency axis [0, fN] returns the total signal power per unit time
    #  int_0^fN power(f)df = 1/T int_0^T |x(t)**2| dt
    #                      = <V(t)**2>, the variance for our AC signal.
    # The variance from our fitted Breit-Wigner is the area under the Breit-Wigner
    #  <V(t)**2> = (pi*C) / (2*B*A**2)
    return (_numpy.pi * C) / (2 * B * A**2)

def breit_wigner_resonant_frequency(A, B):
    if (B**2 >= 2*A**2):
        return 0  # over- or critically-damped
    return _numpy.sqrt(A**2 - B**2/2)

def save(filename=None, group='/', raw=None, config=None,
         deflection_channel_config=None, processed=None):
    specs = [
        _SaveSpec(item=config, relpath='config/vibration',
                  config=_VibrationConfig),
        _SaveSpec(item=deflection_channel_config,
                  relpath='config/deflection',
                  config=_InputChannelConfig),
        _SaveSpec(item=raw, relpath='raw', units='bits'),
        _SaveSpec(item=processed, relpath='processed', units='V^2/Hz'),
        ]
    _save(filename=filename, group=group, specs=specs)

def load(filename=None, group='/'):
    specs = [
        _SaveSpec(key=('config', 'vibration'), relpath='config/vibration',
                  config=_VibrationConfig),
        _SaveSpec(key=('config', 'deflection'), relpath='config/deflection',
                  config=_InputChannelConfig),
        _SaveSpec(key=('raw',), relpath='raw', array=True, units='bits'),
        _SaveSpec(key=('processed',), relpath='processed', units='V^2/Hz'),
        ]
    return _load(filename=filename, group=group, specs=specs)

def plot(deflection=None, freq_axis=None, power=None, A=None, B=None,
         C=None, D=0, config=None, analyze=False):
    """Plot 3 subfigures displaying vibration data and analysis.

     Time series (Vphoto vs sample index) (show any major drift events),
     A histogram of Vphoto, with a gaussian fit (demonstrate randomness), and
     FFTed Vphoto data (Vphoto vs Frequency) (show major noise components).
    """
    if not _matplotlib:
        raise _matplotlib_import_error
    figure = _matplotlib_pyplot.figure()

    if power is None:
        assert deflection != None, (
            'must set at least one of `deflection` or `power`.')
        time_axes = figure.add_subplot(2, 1, 1)
        hist_axes = figure.add_subplot(2, 1, 2)
        freq_axes = None
    elif deflection is None:
        time_axes = hist_axes = None
        freq_axes = figure.add_subplot(1, 1, 1)
    else:
        time_axes = figure.add_subplot(3, 1, 1)
        hist_axes = figure.add_subplot(3, 1, 2)
        freq_axes = figure.add_subplot(3, 1, 3)
        
    timestamp = _time.strftime('%H%M%S')

    if deflection is not None:
        time_axes.plot(deflection, 'r.')
        time_axes.autoscale(tight=True)
        time_axes.set_title('free oscillation')

        # plot histogram distribution and gaussian fit
        hist_axes.hold(True)
        n,bins,patches = hist_axes.hist(
            deflection, bins=30, normed=True, align='mid')
        gauss = _numpy.zeros((len(bins),), dtype=_numpy.float)
        mean = deflection.mean()
        std = deflection.std()
        pi = _numpy.pi
        exp = _numpy.exp
        gauss = exp(-0.5*((bins-mean)/std)**2) / (_numpy.sqrt(2*pi) * std)
        # Matplotlib's normed histogram uses bin heights of n/(len(x)*dbin)
        hist_axes.plot(bins, gauss, 'r-')
        hist_axes.autoscale(tight=True)
    if power is not None:
        freq_axes.hold(True)
        freq_axes.set_yscale('log')
        freq_axes.plot(freq_axis, power, 'r.-')
        freq_axes.autoscale(tight=True)
        xmin,xmax = freq_axes.get_xbound()
        ymin,ymax = freq_axes.get_ybound()

        # highlight the region we're fitting
        if config:
            freq_axes.axvspan(
                config['minimum-fit-frequency'],
                config['maximum-fit-frequency'],
                facecolor='g', alpha=0.1, zorder=-2)

        if A is not None:
            fitdata = breit_wigner(freq_axis, A, B, C, D)
            freq_axes.plot(freq_axis, fitdata, 'b-')
            noisefloor = D + 0*freq_axis;
            freq_axes.plot(freq_axis, noisefloor)
            res_freq = breit_wigner_resonant_frequency(A=A, B=B)
            if res_freq > 0:
                freq_axes.axvline(res_freq, color='b', zorder=-1)

        freq_axes.set_title('power spectral density %s' % timestamp)
        freq_axes.axis([xmin,xmax,ymin,ymax])
        freq_axes.set_xlabel('frequency (Hz)')
        freq_axes.set_ylabel('PSD')
    if hasattr(figure, 'show'):
        figure.show()
    return figure
_plot = plot  # alternative name for use inside analyze()
