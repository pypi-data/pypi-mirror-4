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

"""Load a calibration file and (re)analyze from the raw data.
"""

from optparse import OptionParser

from calibcant.calibrate import load_all
from calibcant.analyze import analyze_all


def main(args):
    usage = '%prog [options] filename'
    p = OptionParser(usage)

    p.add_option('-g', '--group', dest='group', default='/',
                 help='HDF5 group containing calibration data (%default).')
    p.add_option('-d', '--dry-run', dest='dry_run', action='store_true',
                 help="Don't change the original file.")

    options,args = p.parse_args(args)
    filename = args[0]

    calibrator,data,raw_data = load_all(filename=filename, group=options.group)
    k,k_s = analyze_all(
        config=calibrator.config, data=data, raw_data=raw_data,
        filename=filename, group=options.group, plot=False,
        dry_run=options.dry_run)
    print "New spring constant:"
    print "%g +/- %g N/m" % (k, k_s)


if __name__ == '__main__':
    import sys

    sys.exit(main(sys.argv[1:]))
