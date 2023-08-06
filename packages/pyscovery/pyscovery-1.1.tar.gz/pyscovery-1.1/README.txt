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
    for plugin in pyscovery.find(Plugin, True, False):
        print plugin

Recursion in the filesystem is off by default, since that's the way people are
used to.  If there is enough demand, I will make it the default.

If you want to create instances of all the classes found instead of just
getting the class it self, you can use the following:

    for plugin in pyscovery.find(Plugin, True, True):
        print plugin

