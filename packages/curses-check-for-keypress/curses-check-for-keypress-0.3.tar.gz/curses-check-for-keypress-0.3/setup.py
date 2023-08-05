# Copyright (C) 2009-2012 W. Trevor King <wking@tremily.us>
#
# This file is part of curses-check-for-keypress.
#
# curses-check-for-keypress is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# curses-check-for-keypress is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# curses-check-for-keypress.  If not, see <http://www.gnu.org/licenses/>.

"curses_check_for_keypress: loop until user presses a key."

from distutils.core import setup
import os.path

from curses_check_for_keypress import __version__


package_name = 'curses-check-for-keypress'
_this_dir = os.path.dirname(__file__)

setup(name=package_name,
      version=__version__,
      maintainer='W. Trevor King',
      maintainer_email='wking@tremily.us',
      url = 'http://blog.tremily.us/post/{}/'.format(package_name),
      download_url = 'http://git.tremily.us/?p={}.git/a=snapshot;h=v{};sf=tgz'.format(
        package_name, __version__),
      license = 'GNU GPL v3+',
      platforms = ['all'],
      description = __doc__,
      long_description = open(os.path.join(_this_dir, 'README'), 'r').read(),
      classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      py_modules = ['curses_check_for_keypress'],
      )
