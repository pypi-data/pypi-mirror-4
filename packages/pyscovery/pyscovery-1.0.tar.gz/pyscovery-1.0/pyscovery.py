# pyscovery - A python plugin finder
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
pyscovery is a Python plugin loader that will search for classes based from a
list of modules and optionally use the file system to recurse into packages.

This is different from pkg_resources and friends since it doesn't require you
to add every module that might have packages, it will discover it for you.

I wrote this because none of the existing solutions fit my need of being able
to logically group similar plugins in the filesystem.

Say you have the following structure in your project:

    module/
      __init__.py
      plugin.py
    plugins/
      __init__.py
      plugin1/
        __init__.py
      plugin2/
        __init__.py
      plugin3.py

With pyscovery, the following code will find plugins 1, 2, and 3 for you:

    import pyscovery
  
    from plugin import Plugin
  
    pyscovery.add_module('plugins')
    for plugin in pyscovery.find(Plugin, recurse=True):
        print plugin
        
Recursion in the filesystem is off by default, since that's the way people are
used to.  If there is enough demand, I will make it the default.
"""


import fnmatch
import importlib
import inspect
import os

# we use a list since it is a mutable sequence type.  Meaning we can add to it
# while iterating.
MODULES = []


__version__ = '1.0'

def add_module(module):
    """
    Adds a module to search for plugins under
    """

    global MODULES # pylint:disable-msg=W0602

    if not module in MODULES:
        MODULES.append(module)
        

def remove_module(module):
    """
    Removes a module to search for plugins under
    """

    global MODULES # pylint:disable-msg=W0602

    if module in MODULES:
        MODULES.remove(module)

        
def get_modules():
    """
    Returns the list of all module to search under
    """

    return MODULES


def clear_modules():
    """
    Clears all search modules
    """
    
    MODULES[:] = []


def find(cls, recurse=False):
    """
    Find all plugins that are subclasses of cls in the current search paths
    """

    if not inspect.isclass(cls):
        raise TypeError('{} is not a class instance')

    cls_name = cls.__name__

    for module in MODULES:
        mod = importlib.import_module(module)
        
        if recurse and _is_package(mod):
            _recurse(mod)
        
        for symbol_name in dir(mod):
            if symbol_name == cls_name:
                continue
            
            symbol = getattr(mod, symbol_name, None)
            
            if not inspect.isclass(symbol):
                continue
            
            if inspect.isabstract(symbol):
                continue

            yield symbol


def _is_package(module):
    """
    Returns true if the module's name is __init__, false otherwise
    """

    filename = os.path.basename(module.__file__)
    base, _ = os.path.splitext(filename)
    
    return base == '__init__'


def _recurse(module):
    """
    Adds additional modules from a package
    """

    dirname = os.path.dirname(module.__file__)

    make_module = lambda name: '.'.join((module.__name__, name))

    for name in os.listdir(dirname):
        base, _ = os.path.splitext(name)
        
        if base == '__init__':
            continue

        filename = os.path.join(dirname, name)
        
        if os.path.isdir(filename):
            add_module(make_module(base))
        elif os.path.isfile(filename):
            if fnmatch.fnmatch(name, '*.py') or \
               fnmatch.fnmatch(name, '*.py[co]'):
                add_module(make_module(base))


__all__ = [add_module, remove_module, get_modules, clear_modules, find]

