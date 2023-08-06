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


import re
import shlex

try:
    from percol.finder import FinderMultiQueryString
    assert FinderMultiQueryString  # fool pyflakes
except ImportError:
    # Dummy class for making this module importable:
    FinderMultiQueryString = object

from argparse import ArgumentParser
from .search import search_add_arguments, preprocess_kwds


def strip_glob(string, split_str=' '):
    """
    Strip glob portion in `string`.

    >>> strip_glob('*glob*like')
    'glob like'
    >>> strip_glob('glob?')
    'glo'
    >>> strip_glob('glob[seq]')
    'glob'
    >>> strip_glob('glob[!seq]')
    'glob'

    :type string: str
    :rtype: str

    """
    string = _GLOB_PORTION_RE.sub(split_str, string)
    return string.strip()

_GLOB_PORTION_RE = re.compile(r'\*|.\?|\[[^\]]+\]')


class SafeArgumentParser(ArgumentParser):

    def exit(self, *_, **__):
        raise ValueError

    def print_usage(self, *_):
        pass

    print_help = print_version = print_usage


class RashFinder(FinderMultiQueryString):

    base_query = []

    def __init__(self, *args, **kwds):
        super(RashFinder, self).__init__(*args, **kwds)

        self.__parser = parser = SafeArgumentParser()
        search_add_arguments(parser)

    # Generator should be terminated in order to close connection to
    # sqlite.  Otherwise, sqlite3 modules raise an error saying that
    # it doesn't support multi-threading access.
    lazy_finding = False

    def find(self, query, collection=None):
        try:
            # shlex < 2.7.3 does not work with unicode:
            args = self.base_query + shlex.split(query.encode())
            ns = self.__parser.parse_args(args)
            kwds = preprocess_kwds(vars(ns))
        except (ValueError, SyntaxError):
            return super(RashFinder, self).find(query, collection)

        # SOMEDAY: get rid of this hard-coded search limit by making
        # `search_command_record` thread-safe and setting
        # `lazy_finding = True`.
        kwds['limit'] = 50 if kwds['match_pattern'] else 1000

        records = self.db.search_command_record(**kwds)
        self.collection = collection = (r.command for r in records)

        # There will be no filtering in the super class.
        # I am using it for highlighting matches.
        subquery = self.split_str.join(strip_glob(q, self.split_str)
                                       for q in kwds['match_pattern'])
        return super(RashFinder, self).find(subquery, collection)


def load_rc(percol, path=None, encoding=None):
    import os
    from percol import debug
    if path is None:
        path = os.path.expanduser("~/.percol.d/rc.py")
    try:
        with open(path, 'r') as rc:
            exec(rc.read().decode(encoding or 'utf-8'), locals())
    except Exception as e:
        debug.log("exception", e)


def launch_isearch(conf, rcfile=None, input_encoding=None, base_query=[],
                   **kwds):
    from percol import Percol
    from percol import tty
    import percol.actions as actions

    from .database import DataBase

    # Pass db instance to finder.  Not clean but works and no harm.
    RashFinder.db = DataBase(conf.db_path)
    RashFinder.base_query = base_query

    ttyname = tty.get_ttyname()
    with open(ttyname, "r+w") as tty_f:
        with Percol(descriptors=tty.reconnect_descriptors(tty_f),
                    finder=RashFinder,
                    actions=(actions.output_to_stdout,),
                    # This will be used if the first call for RashFinder.find
                    # fails to fetch collections from DB.
                    candidates=[],
                    **kwds) as percol:
            load_rc(percol, rcfile, input_encoding)
            exit_code = percol.loop()

    exit(exit_code)
