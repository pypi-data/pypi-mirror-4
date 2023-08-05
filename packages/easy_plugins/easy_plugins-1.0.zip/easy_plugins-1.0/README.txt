===========
Easy Plugins
===========

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

You can find this project on the bitbucket:
* https://bitbucket.org/prost87/easyplugins

Continuous integration is provided by the drone.io:
* https://drone.io/prost87/EasyPlugins