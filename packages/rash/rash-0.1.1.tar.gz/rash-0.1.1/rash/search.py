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


SORT_KEY_SYNONYMS = {
    'count': 'command_count',
    'success_count': 'success_count',
    'success_ratio': 'success_ratio',
    'program_count': 'program_count',
    'time': 'start_time',
    'start': 'start_time',
    'stop': 'stop_time',
    'code': 'exit_code',
}


def search_run(output, format, with_command_id, with_session_id, format_level,
               **kwds):
    """
    Search command history.

    """
    from .config import ConfigStore
    from .database import DataBase

    if format_level >= 3:
        format = ("{session_history_id:>5}  "
                  "{command_history_id:>5}  "
                  "{command_count:>4}  {command}\n")
    elif format_level == 2 or with_command_id and with_session_id:
        format = ("{session_history_id:>5}  "
                  "{command_history_id:>5}  {command}\n")
    elif format_level == 1 or with_command_id:
        format = "{command_history_id:>5}  {command}\n"
    elif with_session_id:
        format = "{session_history_id:>5}  {command}\n"
    else:
        format = format.decode('string_escape')

    fmtkeys = formatter_keys(format)
    candidates = set([
        'command_count', 'success_count', 'success_ratio', 'program_count'])
    kwds['additional_columns'] = candidates & set(fmtkeys)

    db = DataBase(ConfigStore().db_path)
    for crec in db.search_command_record(**preprocess_kwds(kwds)):
        output.write(format.format(**crec.__dict__))


def formatter_keys(format_string):
    """
    Return required fields in `format_string`.

    >>> sorted(formatter_keys('{1} {key}'))
    ['1', 'key']

    """
    from string import Formatter
    return (tp[1] for tp in Formatter().parse(format_string))


def preprocess_kwds(kwds):
    """
    Preprocess keyword arguments for `DataBase.search_command_record`.
    """
    from .utils.timeutils import parse_datetime, parse_duration

    for key in ['output', 'format', 'with_command_id', 'with_session_id']:
        kwds.pop(key, None)

    for key in ['time_after', 'time_before']:
        val = kwds[key]
        if val:
            dt = parse_datetime(val)
            if dt:
                kwds[key] = dt

    for key in ['duration_longer_than', 'duration_less_than']:
        val = kwds[key]
        if val:
            dt = parse_duration(val)
            if dt:
                kwds[key] = dt

    # interpret "pattern" (currently just copying to --include-pattern)
    less_strict_pattern = list(map("*{0}*".format, kwds.pop('pattern', [])))
    kwds['match_pattern'] = kwds['match_pattern'] + less_strict_pattern

    kwds['sort_by'] = SORT_KEY_SYNONYMS[kwds['sort_by']]
    return kwds


def search_add_arguments(parent_parser):
    import argparse
    # Filter
    parser = parent_parser.add_argument_group('Filter')
    parser.add_argument(
        'pattern', nargs='*',
        help="""
        Glob pattern to match substring of command.  It is as same as
        --match-pattern/-m except that the pattern is going to be
        wrapped by `*`s.  If you want to use strict glob pattern
        that matches to entire command, use --match-pattern/-m.
        """)
    parser.add_argument(
        '--match-pattern', '-m', metavar='GLOB', action='append', default=[],
        help="""
        Only commands that match to this glob pattern are listed.
        Unlike --include-pattern/-g, applying this option multiple
        times does AND match.
        """)
    parser.add_argument(
        '--include-pattern', '-g', metavar='GLOB', action='append', default=[],
        help='glob patterns that matches to commands to include.')
    parser.add_argument(
        '--exclude-pattern', '-G', metavar='GLOB', action='append', default=[],
        help='glob patterns that matches to commands to exclude.')
    parser.add_argument(
        '--match-regexp', '-M',
        metavar='REGEXP', action='append', default=[],
        help="""
        Only commands that matches to this grep pattern are listed.
        Unlike --include-regexp/-e, applying this option multiple
        times does AND match.
        """)
    parser.add_argument(
        '--include-regexp', '-e',
        metavar='REGEXP', action='append', default=[],
        help="""
        Regular expression patterns that matches to commands to include.
        """)
    parser.add_argument(
        '--exclude-regexp', '-E',
        metavar='REGEXP', action='append', default=[],
        help="""
        Regular expression patterns that matches to commands to exclude.
        """)
    parser.add_argument(
        '--cwd', '-d', metavar='DIR', action='append', default=[],
        help="""
        The working directory at the time when the command was run.
        When given several times, items that match to one of the
        directory are included in the result.
        """)
    parser.add_argument(
        '--cwd-glob', '-D', metavar='GLOB', action='append', default=[],
        help="""
        Same as --cwd but it accepts glob expression.
        """)
    parser.add_argument(
        '--cwd-under', '-u', metavar='DIR', action='append', default=[],
        help="""
        Same as --cwd but include all subdirectories.
        """)
    parser.add_argument(
        '--time-after', '-t', metavar='TIME',
        help='commands run after the given time')
    parser.add_argument(
        '--time-before', '-T', metavar='TIME',
        help='commands run before the given time')
    parser.add_argument(
        '--duration-longer-than', '-S', metavar='DURATION',
        help='commands that takes longer than the given time')
    parser.add_argument(
        '--duration-less-than', '-s', metavar='DURATION',
        help='commands that takes less than the given time')
    parser.add_argument(
        '--include-exit-code', '-x',
        metavar='CODE', action='append', default=[], type=int,
        help='include command which finished with given exit code.')
    parser.add_argument(
        '--exclude-exit-code', '-X',
        metavar='CODE', action='append', default=[], type=int,
        help='exclude command which finished with given exit code.')
    parser.add_argument(
        '--include-session', '-n', dest='include_session_history_id',
        metavar='ID', action='append', default=[], type=int,
        help="""
        include command which is issued in given session.
        """)
    parser.add_argument(
        '--exclude-session', '-N', dest='exclude_session_history_id',
        metavar='ID', action='append', default=[], type=int,
        help="""
        exclude command which is issued in given session.
        """)
    parser.add_argument(
        '--match-environ-pattern',
        metavar='ENV', action='append', default=[], nargs=2,
        help="""
        [NOT IMPLEMENTED]
        select command which associated with environment variable
        that matches to given glob pattern.""")
    parser.add_argument(
        '--include-environ-pattern', '-v',
        metavar='ENV', action='append', default=[], nargs=2,
        help="""
        [NOT IMPLEMENTED]
        include command which associated with environment variable
        that matches to given glob pattern.""")
    parser.add_argument(
        '--exclude-environ-pattern', '-V',
        metavar='ENV', action='append', default=[], nargs=2,
        help="""
        [NOT IMPLEMENTED]
        exclude command which associated with environment variable
        that matches to given glob pattern.""")
    parser.add_argument(
        '--match-environ-regexp',
        metavar='ENV', action='append', default=[], nargs=2,
        help="""
        [NOT IMPLEMENTED]
        select command which associated with environment variable
        that matches to given glob pattern.""")
    parser.add_argument(
        '--include-environ-regexp', '-w',
        metavar='ENV', action='append', default=[], nargs=2,
        help="""
        [NOT IMPLEMENTED]
        include command which associated with environment variable
        that matches to given glob pattern.""")
    parser.add_argument(
        '--exclude-environ-regexp', '-W',
        metavar='ENV', action='append', default=[], nargs=2,
        help="""
        [NOT IMPLEMENTED]
        exclude command which associated with environment variable
        that matches to given glob pattern.""")
    # "global" filters
    parser.add_argument(
        '--limit', '-l', metavar='NUM', type=int, default=10,
        help='maximum number of history to show. -1 means no limit.')
    parser.add_argument(
        '--no-unique', '-a', dest='unique', action='store_false', default=True,
        help="""
        Include all duplicates.
        """)
    parser.add_argument(
        '--ignore-case', '-i', action='store_true', default=False,
        help="""
        Do case insensitive search.
        """)

    # Sorter
    parser = parent_parser.add_argument_group('Sorter')
    parser.add_argument(
        '--reverse', '-r', action='store_true', default=False,
        help="""
        Reverse order of the result.
        By default, most recent commands are shown.
        """)
    parser.add_argument(
        '--sort-by', default='count',
        choices=sorted(SORT_KEY_SYNONYMS),
        help="""
        Sort keys
        `count`: number of the time command is executed;
        `success_count`: number of the time command is succeeded;
        `program_count`: number of the time *program* is used;
        `start`(=`time`): the time command is executed;
        `stop`: the time command is finished;
        `code`: exit code of the command;
        Note that --sort-by=count cannot be used with --no-unique.
        """)

    # Modifier
    parser = parent_parser.add_argument_group('Modifier')
    parser.add_argument(
        '--after-context', '-A', type=int, metavar='NUM',
        help="""
        [NOT IMPLEMENTED]
        Print NUM commands executed after matching commands.
        """)
    parser.add_argument(
        '--before-context', '-B', type=int, metavar='NUM',
        help="""
        [NOT IMPLEMENTED]
        Print NUM commands executed before matching commands.
        """)
    parser.add_argument(
        '--context', '-C', type=int, metavar='NUM',
        help="""
        [NOT IMPLEMENTED]
        Print NUM commands executed before and after matching commands.
        """)
    parser.add_argument(
        '--context-type', choices=['session', 'time'],
        help="""
        [NOT IMPLEMENTED]
        `session`: commands executed in the same shell session;
        `time`: commands executed around the same time;
        """)

    # Formatter
    parser = parent_parser.add_argument_group('Formatter')
    parser.add_argument(
        '--with-command-id', action='store_true', default=False,
        help="""
        Print command ID number.
        When this is set, --format option has no effect.
        If --with-session-id is also specified, session ID comes
        at the first column then command ID comes the next column.
        """)
    parser.add_argument(
        '--with-session-id', action='store_true', default=False,
        help="""
        Print session ID number.
        When this is set, --format option has no effect.
        See also: --with-command-id
        """)
    parser.add_argument(
        '--format', default=r'{command}\n',
        help="""
        Python string formatter.  Available keys:
        command, exit_code, pipestatus (a list), start, stop, cwd,
        command_history_id, session_history_id.
        See also:
        http://docs.python.org/library/string.html#format-string-syntax
        """)
    parser.add_argument(
        '-f', dest='format_level', action='count', default=0,
        help="""
        Set formatting detail.  This can be given multiple times to
        make more detailed output.  For example, giving it once
        equivalent to passing --with-command-id and one more -f means
        adding --with-session-id.
        """)

    # Misc
    parser = parent_parser.add_argument_group('Misc')
    parser.add_argument(
        '--output', default='-', type=argparse.FileType('w'),
        help="""
        Output file to write the results in. Default is stdout.
        """)


commands = [
    ('search', search_add_arguments, search_run),
]
