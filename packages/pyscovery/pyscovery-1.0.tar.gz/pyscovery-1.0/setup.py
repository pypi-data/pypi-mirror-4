# pyplugin - A python plugin finder
# Copyright (C) 2013 Gary Kramlich <grim@reaperworld.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This module contains the setuptools bootstrap for packaging
"""

from setuptools import setup

from pyscovery import __version__

DESC = """
A Python plugin loader that will search for classes based from a list of
modules and optionally use the file system to recurse into packages.
"""

def main():
    """ Main function to create our package """

    setup(
        name='pyscovery',
        version=__version__,
        description=DESC,
        py_modules=['pyscovery'],
        zip_safe=True,
        test_suite='tests',
        author='Gary Kramlich',
        author_email='grim@reaperworld.com',
        url='http://www.bitbucket.org/rw_grim/pyplugin',
    )
    

if __name__ == '__main__':
    main()
    
    