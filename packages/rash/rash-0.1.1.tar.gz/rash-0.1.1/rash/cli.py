"""
Command line interface.
"""

import argparse
import textwrap

EPILOG = """
# Copyright (C) 2013-  Takafumi Arakaki

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


class Formatter(argparse.RawDescriptionHelpFormatter,
                argparse.ArgumentDefaultsHelpFormatter):
    pass


def get_parser(commands):
    """
    Generate argument parser given a list of subcommand specifications.

    :type commands: list of (str, function, function)
    :arg  commands:
        Each element must be a tuple ``(name, adder, runner)``.

        :param   name: subcommand
        :param  adder: a function takes one object which is an instance
                       of :class:`argparse.ArgumentParser` and add
                       arguments to it
        :param runner: a function takes keyword arguments which must be
                       specified by the arguments parsed by the parser
                       defined by `adder`.  Docstring of this function
                       will be the description of the subcommand.

    """
    parser = argparse.ArgumentParser(
        formatter_class=Formatter,
        description=__doc__,
        epilog=EPILOG,
    )
    subparsers = parser.add_subparsers()

    for (name, adder, runner) in commands:
        subp = subparsers.add_parser(
            name,
            formatter_class=Formatter,
            description=runner.__doc__ and textwrap.dedent(runner.__doc__))
        adder(subp)
        subp.set_defaults(func=runner)

    return parser


def main(args=None):
    from . import init
    from . import record
    from . import daemon
    from . import search
    from . import show
    from . import index
    from . import isearch
    # from . import MODULE
    parser = get_parser(
        init.commands
        + record.commands
        + daemon.commands
        + search.commands
        + show.commands
        + index.commands
        + isearch.commands
        # + MODULE.commands
        + misc_commands
    )
    ns = parser.parse_args(args=args)
    applyargs = lambda func, **kwds: func(**kwds)
    applyargs(**vars(ns))


def version_run():
    """Print version number."""
    from .__init__ import __version__
    print(__version__)


def version_add_arguments(parser):
    pass


misc_commands = [
    ('version', version_add_arguments, version_run),
]


if __name__ == '__main__':
    main()
