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

"calibcant: tools for thermally calibrating AFM cantilevers"

package_name = 'calibcant'
classifiers = """\
Development Status :: 2 - Pre-Alpha
Intended Audience :: Developers
Intended Audience :: Science/Research
Operating System :: POSIX
Operating System :: Unix
License :: OSI Approved :: GNU General Public License (GPL)
Programming Language :: Python
Topic :: Scientific/Engineering
Topic :: Software Development :: Libraries :: Python Modules
"""

from distutils.core import setup
from os import walk, listdir
import os.path

from calibcant import __version__


def find_packages(root='calibcant'):
    packages = []
    prefix = '.'+os.path.sep
    for dirpath,dirnames,filenames in walk(root):
        if '__init__.py' in filenames:
            if dirpath.startswith(prefix):
                dirpath = dirpath[len(prefix):]
            packages.append(dirpath.replace(os.path.sep, '.'))
    return packages

packages = find_packages()
scripts = [os.path.join('bin', f) for f in sorted(os.listdir('bin'))]

setup(name=package_name,
      version=__version__,
      maintainer='W. Trevor King',
      maintainer_email='wking@tremily.us',
      url='http://blog.tremily.us/posts/%s/' % package_name,
      download_url='http://git.tremily.us/?p=calibcant.git;a=snapshot;h={};sf=tgz'.format(__version__),
      license='GNU General Public License (GPL)',
      platforms=['all'],
      description=__doc__,
      long_description=open('README', 'r').read(),
      classifiers=filter(None, classifiers.split('\n')),
      packages=packages,
      scripts=scripts,
      provides=['calibcant (%s)' % __version__],
      requires=['pypiezo (>= 0.5)'],
      )
