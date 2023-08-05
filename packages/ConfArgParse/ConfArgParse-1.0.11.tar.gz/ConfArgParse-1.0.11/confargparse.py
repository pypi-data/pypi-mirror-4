"""
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
files), just add the --conf-file option.

    python prog.py --conf-file conf.ini

It is easy to write out a configuration file by applying all the options you
want, and then adding the --export-conf-file option.

    python prog.py -n --export-conf-file > conf.ini

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

Feel free to contact me. I am findable online with a google search:
S. Joshua Swamidass.

Please send bug fixes as pull requests to the bitbucket repository
(`https://bitbucket.org/swamidass/confargparse
<https://bitbucket.org/swamidass/confargparse>`_). Please keep pull
requests clean, so I can easily figure out if it should be
merged into the main line.
"""

import argparse
import ConfigParser
import sys
from types import MethodType


def _repr(obj):
    class AtomRepr:
        def __init__(self, f):
            if type(f) == file:
                if f.name == "<stdin>":
                    self.s = "sys.stdin"
                elif f.name == "<stdout>":
                    self.s = "sys.stdout"
                else:
                    self.s = "file('%s','%s')" % (f.name, f.mode)
            else:
                self.s = repr(f)

        def __repr__(self):
            return self.s

    if type(obj) == file:
        return repr(AtomRepr(obj))
    if type(obj) == list:
        return repr([AtomRepr(o) for o in obj])
    return repr(obj)


def _add_argument(self, *args, **kwargs):
        chars = self.prefix_chars
        if not args or len(args) == 1 and args[0][0] not in chars:
            my_kwargs = self._get_positional_kwargs(*args, **kwargs)
            positional = True
        else:
            my_kwargs = self._get_optional_kwargs(*args, **kwargs)
            positional = False

        dest = my_kwargs["dest"]

        section = my_kwargs.get("section", None)
        name = my_kwargs.get("name", dest)
        exclude = my_kwargs.get("conf_exclude", False)

        if not positional:
            if "section" in kwargs:
                del kwargs["section"]
            if "name" in kwargs:
                del kwargs["name"]
            if "conf_exclude" in kwargs:
                del kwargs["conf_exclude"]
        else:
            exclude = True

        action = argparse._ActionsContainer.add_argument(self, *args, **kwargs)

        action.section = section
        action.name = name
        action.parent = self
        action.exclude = exclude

        return action


def _add_parser(self, *args, **kwargs):
    section = kwargs.get("section", None)
    if "section" in kwargs:
        del kwargs["section"]
    parser = _prior_add_parser(self, *args, **kwargs)
    parser.section = section
    return parser


_prior_add_parser = argparse._SubParsersAction.add_parser
argparse._SubParsersAction.add_parser = _add_parser


class ConfArgParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        self.section = kwargs.get("section", "defaults")
        if "section" in kwargs:
            del kwargs["section"]

        ckwargs = dict(kwargs)
        ckwargs["add_help"] = False
        self.conf_parser = argparse.ArgumentParser(*args, **ckwargs)
        group = self.conf_parser.add_argument_group(
                "configuration file options")
        group.add_argument("-c", "--conf-file",
                help="specify config files", nargs="+", metavar="FILE")
        group.add_argument("--export-conf-file",
                help="translate arguments into a config file",
                metavar="FILE", const=sys.stdout, default=None,
                nargs="?", type=argparse.FileType('w'))

        self._added_config_args = False
        kwargs["formatter_class"] = argparse.RawDescriptionHelpFormatter

        self.config_mapping = {}
        self.dest_mapping = {}

        argparse.ArgumentParser.__init__(self, *args, **kwargs)

    add_argument = _add_argument

    def add_argument_group(self, *args, **kwargs):
        section = kwargs.get("section", "defaults")
        if "section" in kwargs:
            del kwargs["section"]
        group = argparse.ArgumentParser.add_argument_group(self,
                *args, **kwargs)
        group.add_argument = MethodType(_add_argument, group, group.__class__)
        group.section = section
        return group

    def add_subparsers(self, *args, **kwargs):
        parser = argparse.ArgumentParser.add_subparsers(self, *args, **kwargs)
        return parser

    def add_mutually_exclusive_groupi(self, *args, **kwargs):
        section = kwargs.get("section", "defaults")
        if "section" in kwargs:
            del kwargs["section"]
        group = argparse.ArgumentParser.add_mutually_exclusive_group(self,
                *args, **kwargs)
        group.add_argument = MethodType(_add_argument, group, group.__class__)
        group.section = section
        return group

    def add_mappings(self, warn=True):
        self.config_mapping = {}
        self.dest_mapping = {}
        actions = self._actions

        for a in actions:
            try:
                assert(not a.exclude)
            except:
                continue

            name = a.name.lower()

            section = a.section
            if section == None:
                section = a.parent.section
            if section == None:
                section = self.section
            if section == None:
                section = "defaults"
            section = section.lower()
            dest = a.dest

            if warn and (section, name) in self.dest_mapping:
                d, t = self.dest_mapping[(section, name)]
                if d != dest:
                    raise ValueError(
                            "Changing destination of this config address!")
            if warn and dest in self.config_mapping:
                s, n, t = self.config_mapping[dest]
                if s != section or n != name:
                    raise ValueError(
                            "Changing config address of this destination!")

            self.config_mapping[dest] = (section, name)
            self.dest_mapping[(section, name)] = (dest)

    def config2dest(self, config):
        args = {}
        for dest, (section, name) in self.config_mapping.items():
            try:
                val = eval(config.get(section, name))
            except:
                continue
            args[dest] = val
        return args

    def args2config(self, args=sys.argv[1:]):
        args = argparse.ArgumentParser.parse_args(self, args)
        config = ConfigParser.RawConfigParser()
        sections = set()
        defaults_added = False
        for dest, (section, name) in self.config_mapping.items():
            try:
                a = args.__getattribute__(dest)
            except:
                continue

            if section not in sections and section.lower() != "defaults":
                config.add_section(section)
                sections.add(section)
            if section.lower() == "defaults" and not defaults_added:
                defaults_added = True
                config.add_section("defaults")

            if a == None:
                config.set(section, name, "")
            else:
                config.set(section, name, _repr(a))

        return config

    def _add_config_args(self):
        if not self._added_config_args:
            self._added_config_args = True
            if self._subparsers == None:
                self._add_container_actions(self.conf_parser)

    def _parse_config(self, args):
        args, remaining_argv = self.conf_parser.parse_known_args(args)

        self.add_mappings()

        if args.conf_file:
            config = ConfigParser.SafeConfigParser()
            config.read(args.conf_file)
            config_options = self.config2dest(config)
            self.set_defaults(**config_options)
        if args.export_conf_file:
            self.args2config(remaining_argv).write(args.export_conf_file)
            sys.exit(0)
        return remaining_argv

    def parse_known_args(self, args=sys.argv[1:], namespace=None):
        self._add_config_args()
        if not self._subparsers:
            args = self._parse_config(args)
        return argparse.ArgumentParser.parse_known_args(self, args, namespace)

    def parse_args(self, args=sys.argv[1:], namespace=None):
        self._add_config_args()
        if not self._subparsers:
            args = self._parse_config(args)
        return argparse.ArgumentParser.parse_args(self, args, namespace)
