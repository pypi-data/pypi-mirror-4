#!/usr/bin/env python
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

"""Load a calibration file and plot everything interesting.
"""

from optparse import OptionParser

import h5py as _h5py
from matplotlib.pyplot import close, get_fignums, figure, show

from calibcant.calibrate import load_all
from calibcant.analyze import analyze_all


def main(args):
    usage = '%prog [options] filename'
    p = OptionParser(usage)

    p.add_option('-g', '--group', dest='group', default='/',
                 help='HDF5 group containing calibration data (%default).')
    p.add_option('-b', '--no-bumps', dest='bumps', default=True,
                 action='store_false',
                 help="Don't display bump details.")
    p.add_option('-v', '--no-vibrations', dest='vibrations', default=True,
                 action='store_false',
                 help="Don't display vibration details.")
    p.add_option('-s', '--save-figures', dest='save', action='store_true',
                 help="Save plots (instead of displaying them.")

    options,args = p.parse_args(args)
    filename = args[0]

    with _h5py.File(filename) as f:
        if options.group in f:
            g = f[options.group]
            if 'approach' in g:
                position = g['approach/position'][...]
                deflection = g['approach/deflection'][...]
                fig = figure()
                axes = fig.add_subplot(1, 1, 1)
                axes.plot(position, deflection)
                axes.set_title('Stepper approach')
                axes.set_xlabel('position (steps)')
                axes.set_ylabel('deflection (bits)')
    calibrator,data,raw_data = load_all(filename=filename, group=options.group)
    if not options.bumps:
        raw_data['bump'] = []
    if not options.vibrations:
        raw_data['vibration'] = []
    analyze_all(config=calibrator.config, data=data, raw_data=raw_data,
                plot=True, dry_run=True)
    if options.save:
        for i in get_fignums():
            fig = figure(i)
            fig.savefig('%i.png' % i, dpi=300)
            close(i)
    else:
        show()


if __name__ == '__main__':
    import sys

    sys.exit(main(sys.argv[1:]))
