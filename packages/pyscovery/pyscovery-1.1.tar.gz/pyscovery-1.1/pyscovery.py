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
"""

import fnmatch
import importlib
import inspect
import os

# we use a list since it is a mutable sequence type.  Meaning we can add to it
# while iterating.
MODULES = []


__version__ = '1.1'

def add_module(module):
    """Adds a module to search for plugins under
    
    :param module: The module to add to the search paths
    :type module: string
    """

    global MODULES # pylint:disable-msg=W0602

    if not module in MODULES:
        MODULES.append(module)
        

def remove_module(module):
    """Removes a module to search for plugins under
    
    :param module: The module to remove
    :type module: string
    """

    global MODULES # pylint:disable-msg=W0602

    if module in MODULES:
        MODULES.remove(module)

        
def get_modules():
    """Returns the list of all module to search under
    
    :returns: A list of the current modules used for searching
    """

    return MODULES


def clear_modules():
    """Clears all search modules
    """
    
    MODULES[:] = []


def find(cls, recurse, create, *args, **kwargs):
    """Find all plugins that are subclasses of cls in the current search paths
    
    :param cls: The class whose subclasses to find.
    :type cls: class
    :param recurse: Whether or not to recurse into packages.
    :type recurse: bool
    :param create: return instances rather than just return their class.
    :type create: bool
    :param args: Additional arguments to pass to each constructor.  Ignored if
                 create is False.
    :type args: arguments
    :param kwargs: Additional keyword arguements to pass to each constructor.
                   Ignored if create is False.
    :type kwargs: kwargs
    :returns: Generator of subclasses of cls
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
            
            if not issubclass(symbol, cls):
                continue

            if create:
                yield symbol(*args, **kwargs)
            else:
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


#__all__ = [add_module, remove_module, get_modules, clear_modules, find]

