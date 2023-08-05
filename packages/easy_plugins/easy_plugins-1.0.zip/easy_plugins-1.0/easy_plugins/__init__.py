#!/usr/bin/env python
# -*- coding: utf-8 -*-

# path, modules
import sys
# listdir
import os

__author__ = 'prost'

# import alias for testing
_import = __import__

"""
Module EasyPlugins provides easy way to manage plugins.

I was searching for some easy yet powerful plugin framework, but no
nothing suitable found. They are complicated, require implementation
of some weird interface or they are ugly in other way. This is way
I have decided to reinvent the wheel and create this module (well,
it's just one class and a few tests).

What does it do? It scans your python path and try to load anything that
looks like a python stuff with prefix you specify. That's all.

Let's show you some example. Let's say I have a python application called
image_resizer. Core functionality is in this package. Then I have some
plugins that know something about image formats and each is using some very
clever algorithm. These plugins are called with prefix 'image_resizer_',
so in regexp speech they match  '^image_resizer_.*'. For example
image_resizer_png, image_resizer_jpg and image_resizer_gif.

In the described situation, one might use:

    extensions = {}
    plugins = EasyPlugins('image_resizer_')

    # plugins are now lazy initialized, next time you
    # call iteration, it will immediately return
    # an iterator of plugin modules
    for name, plugin in plugins:
        extension = plugin.extension
        resizer_class = plugin.Resizer
        extensions[extension] = resizer_class

So in general usage is following:

    plugins = EasyPlugins('desired_prefix_')

    for name, plugin in plugins:
        # do whatever you need with the module
        # we have a duct typing, use it!
        expected_class = plugin.Class
        expected_function = plugin.function
        custom_terminal_options = plugin.options

Actually you can provide multiple plugin names, for example
for backward compatibility:

    plugins = EasyPlugins(['archiver_', 'archiver_plugin_'])

If you would like to add plugins from directory that is not on the path
for some reason, you could still use them by setting the additional path.
This situation usually happens during development of the plugins.

    PYTHONPATH=/path/to/plugins /path/to/your/application.py
"""

class EasyPlugins(object):
    """
    EasyPlugins class is the main class and the only class of this package.

    Searching of plugins is not done in constructor, class uses
    lazy initialization.
    """
    EXTENSIONS = ["py", "pyc", "pyo"]
    def __init__(self, plugin_prefixes):
        """
        Creates instances and sets prefixes. Plugins are searched
        during iteration.

        plugin_prefixes -- string or an iterable
        """
        if hasattr(plugin_prefixes, '__iter__'):
            self._plugin_prefixes = plugin_prefixes
        # plugin_prefixes is only one string? then make it list
        else:
            self._plugin_prefixes = [plugin_prefixes]
        # no plugins yet, they are lazily initialized
        self._plugins = None

    def _plugin_corresponds_to_prefix(self, plugin):
        """
        Check that plugin name corresponds to desired prefix (or more prefixes).
        Complexity is O(n).

        plugin -- plugin's name
        """
        for prefix in self._plugin_prefixes:
            if plugin.startswith(prefix) is True:
                return True
        return False

    def _get_module_name_from_filename(self, path, filename):
        """
        Returns None if the filename does not represent a module.

        path -- root path
        filename -- possible module
        """
        values = filename.split('.')
        # first pop first name
        name = values.pop(0)
        if len(values) == 0:
            full_filename = os.path.join(path, filename)
            if os.path.isdir(full_filename) is False:
                return None
        if len(values) > 1:
            return None
        if len(values) == 1:
            extension = values.pop()
            if extension not in self.EXTENSIONS:
                return None
        return name

    def _from_path(self):
        """
        Implementation of __iter__.
        """
        self._plugins = {}
        reversed_path_iterator = reversed(sys.path)
        # for path in paths
        for path in reversed_path_iterator:
            try:
                #TODO: it might be a trap! (zip file)
                entries = os.listdir(path)
                for entry in entries:
                    if self._plugin_corresponds_to_prefix(entry) is False:
                        continue
                    name = self._get_module_name_from_filename(path, entry)
                    # it's not a module or already registered
                    if name is None or name in self._plugins:
                        continue
                    module = _import(name)
                    self._plugins[name] = module
                    yield name, module
            # for some reason path might not be iterable
            except OSError:
                continue

    def __iter__(self):
        """
        Iterates over plugins- Returns
        """
        # lazy load
        if self._plugins is None:
            # return generator
            return self._from_path()
        # return listiterator
        return self._plugins.iteritems()
