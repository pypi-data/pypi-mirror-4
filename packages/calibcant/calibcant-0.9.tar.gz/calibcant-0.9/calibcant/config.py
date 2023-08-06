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

"""h5config support, so we can easily save what we did and load it later.
"""

import sys as _sys

from FFT_tools import window_hann as _window_hann
import h5config.config as _config
import h5config.tools as _h5config_tools
from pyafm.config import AFMConfig as _AFMConfig


class PackageConfig (_h5config_tools.PackageConfig):
    "Configure `calibcant` module operation"
    settings = _h5config_tools.PackageConfig.settings + [
        _config.BooleanSetting(
            name='matplotlib',
            help='Plot piezo motion using `matplotlib`.',
            default=False),
        ]


class _BumpModel (object):
    pass
class Linear (_BumpModel):
    pass
class Quadratic (_BumpModel):
    pass

class BumpConfig (_config.Config):
    "Configure `calibcant` bump operation"
    settings = [
        _config.FloatSetting(
            name='initial-position',
            help=('Position relative to surface for start of bump in meters.  '
                  'Should be less than zero to ensure non-contact region '
                  'before you hit the surface.'),
            default=-50e-9),
        _config.FloatSetting(
            name='setpoint',
            help=('Maximum deflection in volts in case of stepper positioning '
                  'to achieve the initial position.'),
            default=2.0),
        _config.FloatSetting(
            name='min-slope-ratio',
            help=('Set the minimum ratio between the deflection/displacement '
                  'of the contact and the non-contact regions for bumps '
                  'seeking the surface.  Bumps without sufficient difference '
                  'assume they need to move closer to find the surface.'),
            default=10.0),
        _config.IntegerSetting(
            name='far-steps',
            help=('Number of stepper steps to move "far" away from the '
                  'surface.  For possible stepper adjustments while initially '
                  'locating the surface.'),
            default=200),
        _config.FloatSetting(
            name='push-depth',
            help='Distance to approach in meters.',
            default=200e-9),
        _config.FloatSetting(
            name='push-speed',
            help='Approach/retract speed in meters/second.',
            default=1e-6),
        _config.FloatSetting(
            name='samples',
            help='Number of samples during approach and during retreat.',
            default=1024),
        _config.ChoiceSetting(
            name='model',
            help='Bump deflection model.',
            default=Quadratic,
            choices=[
                ('linear', Linear),
                ('quadratic', Quadratic),
                ]),
        ]


class TemperatureConfig (_config.Config):
    "Configure `calibcant` temperature operation"
    settings = [
        _config.FloatSetting(
            name='sleep',
            help=('Time between temperature measurements (in seconds) to get '
                  'independent measurements when reading from slow sensors.'),
            default=1),
        ]


class _VibrationModel (object):
    pass
class Variance (_VibrationModel):
    pass
class BreitWigner (_VibrationModel):
    pass
class OffsetBreitWigner (_VibrationModel):
    pass

class VibrationConfig (_config.Config):
    "Configure `calibcant` vibration operation"
    settings = [
        _config.FloatSetting(
            name='frequency',
            help='Sampling frequency in Hz.',
            default=50e3),
        _config.FloatSetting(
            name='sample-time',
            help=('Aquisition time in seconds.  This is rounded up as required '
                  'so the number of samples will be an integer power of two.'),
            default=1),
        _config.ChoiceSetting(
            name='model',
            help='Vibration model.',
            default=BreitWigner,
            choices=[
                ('variance', Variance),
                ('Breit-Wigner', BreitWigner),
                ('offset Breit-Wigner', OffsetBreitWigner),
                ]),
        _config.IntegerSetting(
            name='chunk-size',
            help='FFT chunk size (for PSD fits).',
            default=2048),
        _config.BooleanSetting(
            name='overlap',
            help='Overlap FFT chunks (for PSD fits).'),
        _config.ChoiceSetting(
            name='window',
            help='FFT chunk window (for PSD fits).',
            default=_window_hann,
            choices=[
                ('Hann', _window_hann),
                ]),
        _config.FloatSetting(
            name='minimum-fit-frequency',
            help='Lower bound of Lorentzian fitting region.',
            default=500.),
        _config.FloatSetting(
            name='maximum-fit-frequency',
            help='Upper bound of Lorentzian fitting region.',
            default=25e3),
        _config.ChoiceSetting(
            name='smooth-window',
            help='Smoothing window type (for guessing PSD parameters).',
            default=_window_hann,
            choices=[
                ('Hann', _window_hann),
                ]),
        _config.FloatSetting(
            name='smooth-length',
            help='Size of the smoothing window (in points).',
            default=10),
        ]


class CalibrateConfig (_config.Config):
    "Configure a full `calibcant` calibration run"
    settings = [
        _config.ConfigSetting(
            name='afm',
            help='Configure the AFM used to carry out the calibration',
            config_class=_AFMConfig),
        _config.ConfigSetting(
            name='bump',
            help='Configure the surface bumps',
            config_class=BumpConfig),
        _config.IntegerSetting(
            name='num-bumps',
            help='Number of surface bumps.',
            default=10),
        _config.ConfigSetting(
            name='temperature',
            help='Configure the temperature measurements',
            config_class=TemperatureConfig),
        _config.IntegerSetting(
            name='num-temperatures',
            help='Number of temperature measurements.',
            default=10),
        _config.ConfigSetting(
            name='vibration',
            help='Configure the temperature measurements',
            config_class=VibrationConfig),
        _config.IntegerSetting(
            name='num-vibrations',
            help='Number of thermal vibration measurements.',
            default=20),
        _config.FloatSetting(
            name='vibration-spacing',
            help=('Approximate distance from the surface in meters for the '
                  'vibration measurements.  This should be large enough that '
                  'surface effects are negligable.'),
            default=50e-6),
        ]
