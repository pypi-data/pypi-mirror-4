#!/usr/bin/env python
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

"""Run a cantilever calibration using the default AFM
(``pyafm.storage.load_afm()``).
"""

import argparse as _argparse
import time as _time

import h5py as _h5py
from pyafm.storage import load_afm as _load_afm

from calibcant.calibrate import Calibrator as _Calibrator
import calibcant.config as _config


_module_doc = __doc__

def main(args):
    parser = _argparse.ArgumentParser(description=_module_doc)
    parser.add_argument(
        '--num-bumps', type=int,
        help='Number of surface bumps')
    parser.add_argument(
        '--num-temperatures', type=int,
        help='Number of temperature measurements')
    parser.add_argument(
        '--num-vibrations', type=int,
        help='Number of thermal vibration measurements')

    args = parser.parse_args(args)

    timestamp = '{0}-{1:02d}-{2:02d}T{3:02d}-{4:02d}-{5:02d}'.format(
        *_time.localtime())
    filename = '{}-calibcant-data.h5'.format(timestamp)
    config = _config.CalibrateConfig()
    config['bump'] = _config.BumpConfig()
    config['bump'].update(
        {'model':_config.Linear, 'initial-position':-150e-9})
    config['temperature'] = _config.TemperatureConfig()
    config['vibration'] = _config.VibrationConfig()
    if args.num_bumps is None:
        args.num_bumps = config['num-bumps']
    else:
        config['num-bumps'] = args.num_bumps
    if args.num_temperatures is None:
        args.num_temperatures = config['num-temperatures']
    else:
        config['num-temperatures'] = args.num_temperatures
    if args.num_vibrations is None:
        args.num_vibrations = config['num-vibrations']
    else:
        config['num-vibrations'] = args.num_vibrations
    insufficient_calibration_data = 0 in [
        args.num_bumps, args.num_temperatures, args.num_vibrations]
    devices = []
    try:
        afm = _load_afm()
        afm.load_from_config(devices=devices)
        calibrator = _Calibrator(config=config, afm=afm)
        calibrator.setup_config()
        deflection = afm.piezo.read_deflection()
        try:
            position,deflection = afm.stepper_approach(
                target_deflection=deflection + 1e3, record_data=True)
            with _h5py.File(filename) as f:
                f['/approach/position'] = position
                f['/approach/deflection'] = deflection
            if insufficient_calibration_data:
                data = calibrator.acquire(filename=filename)
            else:
                k,k_s,data = calibrator.calibrate(filename=filename)
        except:
            afm.move_away_from_surface()
            afm.piezo.zero()
            raise
    finally:
        for device in devices:
            device.close()
    if insufficient_calibration_data:
        for count,field,label in [
            (args.num_bumps, 'bump', 'photodiode sensitivity (V/m)'),
            (args.num_temperatures, 'temperature', 'temperature (K)'),
            (args.num_vibrations, 'vibration', 'variance (V**2)')]:
            if count:
                d = data[field]
                print('{}: {:g} +/- {:g}'.format(label, d.mean(), d.std()))
    else:
        print('k: {:g} +/- {:g}'.format(k, k_s))
    return 0

if __name__ == '__main__':
    import sys

    sys.exit(main(sys.argv[1:]))
