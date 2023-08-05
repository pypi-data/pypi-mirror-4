
============
ConfArgParse
============

This module adds a config file parsing capability to argparse.


Usage
-----

Start by importing the module and initializing the parser::

    import confargparse
    parser = confargparse.ConfArgParser()

The usage is identical to the argparse module::

    parser.add_argument("-n", type=int)
    group = parser.add_argument_group("my group")
    group.add_argument("-g")

Now, to use a configuration file (or list of sequentially read configuration
files), just add the --conf_file option.

    python prog.py --conf_file conf.ini

It is easy to write out a configuration file by applying all the options you
want, and then adding the --export_conf_file option.

    python prog.py -n --export_conf_file > conf.ini

API Changes
-----------

All argparse code should be compatible by just drapping in the new object. This
package adds a few important options to the API to figure out how to map
namespace dests to configuration sections/names.

The key concepts to note:

1. Parameters in configuration files map to specific section/name pairs.
2. Configuration file sections and names ignore case.

Specifiying the Name
====================

By default all configuration names are the lowercase dest from argparse. Care
must be taken to make sure that there are no name clashes from dests with
different capitalizations.

The default name can be changed by using the "name" keyword to add_argument::

    parser.add_argument("-n", type=int, name="my_n")

This targets the argument to "my_n" instead of "n" in the configuration file.

Specifying the Section
======================

By default, all configurations go to the [defaults] section.  Argument 
groups and subparsers inherit from the parser that initialized them.

The add_argument_group, add_argument, add_subparsers, and ConfArgParser
initialization all include the "section" optional keyword argument. Specifying
this section sets the section in the configuration the option will be targeted
to. If the value is None, the object will inherit up as expected::

    parser = ConfArgParser(section = "main")
    parser.add_argument("-n", type=int)
    group = parser.add_argument_group("my group", section="group")
    group.add_argument("-g")
    group.add_argument("-t", section="section2")

In this example, the first argument targets to "n" name in the [main] section.
The second argument targets to the "g" name in the [group] section. The third
argument targets to the "t" name in the [section2] section.

Excluding Arguments
===================

Currently, positional arguments cannot be sent to the configuration file.

If you would like to exclude additional arguments, just use the exclude keyword
argument to add_arguments::

    parser.add_argument("-n", type=int, exclude=True)


Suggestions or BugFixes?
========================

Feel free to contact me. I am findable online with a google search: S. Joshua Swamidass.
