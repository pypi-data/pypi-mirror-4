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


import os
import re
import sqlite3
from contextlib import closing, contextmanager
import datetime
import warnings
import itertools

from .utils.iterutils import nonempty
from .utils.sqlconstructor import SQLConstructor
from .model import CommandRecord, SessionRecord, VersionRecord, EnvironRecord

schema_version = '0.1'


def convert_ts(ts):
    """
    Convert timestamp (ts)

    :type ts: int or str or None
    :arg  ts: Unix timestamp
    :rtype: datetime.datetime or str or None

    """
    if ts is None:
        return None
    try:
        return datetime.datetime.utcfromtimestamp(ts)
    except TypeError:
        pass
    return ts


def normalize_directory(path):
    """
    Append "/" to `path` if needed.
    """
    if path is None:
        return None
    if path.endswith(os.path.sep):
        return path
    else:
        return path + os.path.sep


def sql_regexp_func(expr, item):
    return re.match(expr, item) is not None


def sql_program_name_func(command):
    """
    Extract program name from `command`.

    >>> sql_program_name_func('ls')
    'ls'
    >>> sql_program_name_func('git status')
    'git'
    >>> sql_program_name_func('EMACS=emacs make')
    'make'

    :type command: str

    """
    args = command.split(' ')
    for prog in args:
        if '=' not in prog:
            return prog
    return args[0]


class DataBase(object):

    schemapath = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'schema.sql')

    def __init__(self, dbpath):
        self.dbpath = dbpath
        if not os.path.exists(dbpath):
            self._init_db()
        self.update_version_records()

    def _get_db(self):
        """Returns a new connection to the database."""
        return closing(sqlite3.connect(self.dbpath))

    def _init_db(self):
        """Creates the database tables."""
        with self._get_db() as db:
            with open(self.schemapath) as f:
                db.cursor().executescript(f.read())
            db.commit()

    @contextmanager
    def connection(self, commit=False):
        """
        Context manager to keep around DB connection.

        :rtype: sqlite3.Connection

        SOMEDAY: Get rid of this function.  Keeping connection around as
        an argument to the method using this context manager is
        probably better as it is more explicit.
        Also, holding "global state" as instance attribute is bad for
        supporting threaded search, which is required for more fluent
        percol integration.

        """
        if commit:
            self._need_commit = True
        if self._db:
            yield self._db
        else:
            try:
                with self._get_db() as db:
                    self._db = db
                    db.create_function("REGEXP", 2, sql_regexp_func)
                    db.create_function("PROGRAM_NAME", 1,
                                       sql_program_name_func)
                    yield self._db
                    if self._need_commit:
                        db.commit()
            finally:
                self._db = None
                self._need_commit = False
    _db = None
    _need_commit = False

    def close_connection(self):
        """
        Close connection kept by :meth:`connection`.

        If commit is needed, :meth:`sqlite3.Connection.commit`
        is called first and then :meth:`sqlite3.Connection.interrupt`
        is called.

        A few methods/generators support :meth:`close_connection`:

        - :meth:`search_command_record`
        - :meth:`select_by_command_record`

        """
        if self._db:
            db = self._db
            try:
                if self._need_commit:
                    db.commit()
            finally:
                db.interrupt()
                self._db = None
                self._need_commit = False

    def _executing(self, sql, params=[]):
        """
        Execute and yield rows in a way to support :meth:`close_connection`.
        """
        with self.connection() as connection:
            for row in connection.execute(sql, params):
                yield row
                if not self._db:
                    return

    def _select_rows(self, rowclass, keys, sql, params):
        return (rowclass(**dict(zip(keys, row)))
                for row in self._executing(sql, params))

    def get_version_records(self):
        """
        Yield RASH version information stored in DB. Latest first.

        :rtype: [VersionRecord]

        """
        keys = ['id', 'rash_version', 'schema_version', 'updated']
        sql = """
        SELECT id, rash_version, schema_version, updated
        FROM rash_info
        ORDER BY id DESC
        """
        with self.connection() as connection:
            for row in connection.execute(sql):
                yield VersionRecord(**dict(zip(keys, row)))

    def update_version_records(self):
        """
        Update rash_info table if necessary.
        """
        from .__init__ import __version__ as version
        with self.connection(commit=True) as connection:
            for vrec in self.get_version_records():
                if (vrec.rash_version == version and
                    vrec.schema_version == schema_version):
                    return  # no need to insert the new one!
            connection.execute(
                'INSERT INTO rash_info (rash_version, schema_version) '
                'VALUES (?, ?)',
                [version, schema_version])

    def import_json(self, json_path, **kwds):
        import json
        with open(json_path) as fp:
            try:
                dct = json.load(fp)
            except ValueError:
                warnings.warn(
                    'Ignoring invalid JSON file at: {0}'.format(json_path))
                return
        self.import_dict(dct, **kwds)

    def import_dict(self, dct, check_duplicate=True):
        crec = CommandRecord(**dct)
        if check_duplicate and nonempty(self.select_by_command_record(crec)):
            return
        with self.connection(commit=True) as connection:
            db = connection.cursor()
            ch_id = self._insert_command_history(db, crec)
            self._isnert_command_environment(db, ch_id, crec.environ)
            self._insert_pipe_status(db, ch_id, crec.pipestatus)

    def _insert_command_history(self, db, crec):
        command_id = self._get_maybe_new_command_id(db, crec.command)
        session_id = self._get_maybe_new_session_id(db, crec.session_id)
        directory_id = self._get_maybe_new_directory_id(db, crec.cwd)
        terminal_id = self._get_maybe_new_terminal_id(db, crec.terminal)
        db.execute(
            '''
            INSERT INTO command_history
                (command_id, session_id, directory_id, terminal_id,
                 start_time, stop_time, exit_code)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            [command_id, session_id, directory_id, terminal_id,
             convert_ts(crec.start), convert_ts(crec.stop), crec.exit_code])
        return db.lastrowid

    def _isnert_command_environment(self, db, ch_id, environ):
        self._insert_environ(db, 'command_environment_map', 'ch_id', ch_id,
                             environ)

    def _insert_environ(self, db, table, id_name, ch_id, environ):
        if not environ:
            return
        for (name, value) in environ.items():
            if name is None or value is None:
                continue
            ev_id = self._get_maybe_new_id(
                db, 'environment_variable',
                {'variable_name': name, 'variable_value': value})
            db.execute(
                '''
                INSERT INTO {0}
                    ({1}, ev_id)
                VALUES (?, ?)
                '''.format(table, id_name),
                [ch_id, ev_id])

    def _insert_pipe_status(self, db, ch_id, pipe_status):
        if not pipe_status:
            return
        for (i, code) in enumerate(pipe_status):
            db.execute(
                '''
                INSERT INTO pipe_status_map
                    (ch_id, program_position, exit_code)
                VALUES (?, ?, ?)
                ''',
                [ch_id, i, code])

    def _get_maybe_new_command_id(self, db, command):
        if command is None:
            return None
        return self._get_maybe_new_id(
            db, 'command_list', {'command': command})

    def _get_maybe_new_session_id(self, db, session_long_id):
        if session_long_id is None:
            return None
        return self._get_maybe_new_id(
            db, 'session_history', {'session_long_id': session_long_id})

    def _get_maybe_new_directory_id(self, db, directory):
        if directory is None:
            return None
        directory = normalize_directory(directory)
        return self._get_maybe_new_id(
            db, 'directory_list', {'directory': directory})

    def _get_maybe_new_terminal_id(self, db, terminal):
        if terminal is None:
            return None
        return self._get_maybe_new_id(
            db, 'terminal_list', {'terminal': terminal})

    def _get_maybe_new_id(self, db, table, columns):
        kvlist = list(columns.items())
        values = [v for (_, v) in kvlist]
        sql_select = 'SELECT id FROM "{0}" WHERE {1}'.format(
            table,
            ' AND '.join(map('"{0[0]}" = ?'.format, kvlist)),
        )
        for (id_val,) in db.execute(sql_select, values):
            return id_val
        sql_insert = 'INSERT INTO "{0}" ({1}) VALUES ({2})'.format(
            table,
            ', '.join(map('"{0[0]}"'.format, kvlist)),
            ', '.join('?' for _ in kvlist),
        )
        db.execute(sql_insert, values)
        return db.lastrowid

    def select_by_command_record(self, crec):
        """
        Yield records that matches to `crec`.

        All attributes of `crec` except for `environ` are concerned.

        """
        keys = ['command_history_id', 'command', 'session_history_id',
                'cwd', 'terminal',
                'start', 'stop', 'exit_code']
        sql = """
        SELECT
            command_history.id, CL.command, session_id,
            DL.directory, TL.terminal,
            start_time, stop_time, exit_code
        FROM command_history
        LEFT JOIN command_list AS CL ON command_id = CL.id
        LEFT JOIN directory_list AS DL ON directory_id = DL.id
        LEFT JOIN terminal_list AS TL ON terminal_id = TL.id
        WHERE
            (CL.command   = ? OR (CL.command   IS NULL AND ? IS NULL)) AND
            (DL.directory = ? OR (DL.directory IS NULL AND ? IS NULL)) AND
            (TL.terminal  = ? OR (TL.terminal  IS NULL AND ? IS NULL)) AND
            (start_time   = ? OR (start_time   IS NULL AND ? IS NULL)) AND
            (stop_time    = ? OR (stop_time    IS NULL AND ? IS NULL)) AND
            (exit_code    = ? OR (exit_code    IS NULL AND ? IS NULL))
        """
        desired_row = [
            crec.command, normalize_directory(crec.cwd), crec.terminal,
            convert_ts(crec.start), convert_ts(crec.stop), crec.exit_code]
        params = list(itertools.chain(*zip(desired_row, desired_row)))
        return self._select_rows(CommandRecord, keys, sql, params)

    def search_command_record(self, **kwds):
        """
        Search command history.

        :rtype: [CommandRecord]

        """
        (sql, params, keys) = self._compile_sql_search_command_record(**kwds)
        return self._select_rows(CommandRecord, keys, sql, params)

    def _compile_sql_search_command_record(
            cls, limit, unique,
            match_pattern, include_pattern, exclude_pattern,
            match_regexp, include_regexp, exclude_regexp,
            cwd, cwd_glob, cwd_under,
            time_after, time_before, duration_longer_than, duration_less_than,
            include_exit_code, exclude_exit_code,
            include_session_history_id, exclude_session_history_id,
            match_environ_pattern, include_environ_pattern,
            exclude_environ_pattern,
            match_environ_regexp, include_environ_regexp,
            exclude_environ_regexp,
            reverse, sort_by,
            ignore_case,
            additional_columns=[],
            **_):  # SOMEDAY: don't ignore unused kwds to search_command_record
        keys = ['command_history_id', 'command', 'session_history_id',
                'cwd', 'terminal',
                'start', 'stop', 'exit_code']
        columns = ['command_history.id', 'CL.command', 'session_id',
                   'DL.directory', 'TL.terminal',
                   'start_time', 'stop_time', 'exit_code']
        source = (
            'command_history '
            'LEFT JOIN command_list AS CL ON command_id = CL.id '
            'LEFT JOIN directory_list AS DL ON directory_id = DL.id '
            'LEFT JOIN terminal_list AS TL ON terminal_id = TL.id')

        if cwd_under:
            cwd_glob.extend(os.path.join(os.path.abspath(p), "*")
                            for p in cwd_under)

        if ignore_case:
            glob = "glob(lower({1}), lower({0}))".format
        else:
            glob = "glob({1}, {0})".format
        regexp = "regexp({1}, {0})"
        eq = '{0} = {1}'

        if not unique and sort_by == 'command_count':
            # When not using "GROUP BY", `COUNT(*)` yields just one
            # row.  As unique is True by default, `unique=False`
            # should mean to ignore ``sort_by='command_count'``.
            sort_by = None

        sc = SQLConstructor(source, columns, keys,
                            order_by=sort_by or 'start_time',
                            reverse=reverse, limit=limit)
        sc.add_matches(glob, 'CL.command',
                       match_pattern, include_pattern, exclude_pattern)
        sc.add_matches(regexp, 'CL.command',
                       match_regexp, include_regexp, exclude_regexp)
        sc.add_or_matches(glob, 'DL.directory', cwd_glob)
        sc.add_or_matches(
            eq, 'DL.directory',
            [normalize_directory(os.path.abspath(p)) for p in cwd])
        sc.add_and_matches('DATETIME({0}) >= {1}', 'start_time', time_after)
        sc.add_and_matches('DATETIME({0}) <= {1}', 'start_time', time_before)
        comdura = (
            '(JULIANDAY(stop_time) - JULIANDAY(start_time)) * 60 * 60 * 24')
        sc.add_and_matches('({0} >= {1})', comdura, duration_longer_than)
        sc.add_and_matches('({0} <= {1})', comdura, duration_less_than)
        sc.add_matches(eq, 'exit_code',
                       [], include_exit_code, exclude_exit_code)
        sc.add_matches(eq, 'session_id', [],
                       include_session_history_id, exclude_session_history_id)

        if match_environ_pattern or include_environ_pattern or \
           exclude_environ_pattern or match_environ_regexp or \
           include_environ_regexp:
            evsc = cls._sc_matched_environment_variable(
                match_environ_pattern, include_environ_pattern,
                exclude_environ_pattern,
                match_environ_regexp, include_environ_regexp,
                exclude_environ_regexp,
                table_alias='EV')
            cesc = SQLConstructor('command_environment_map',
                                  ['ch_id', 'ev_id'], table_alias='CEMap')
            cesc.join(evsc, op='INNER JOIN', on='ev_id = EV.id')
            sesc = SQLConstructor('session_environment_map',
                                  ['sh_id', 'ev_id'], table_alias='SEMap')
            sesc.join(evsc, op='INNER JOIN', on='ev_id = EV.id')
            sc.join(cesc, on='command_history.id = CEMap.ch_id')
            sc.join(sesc, on='session_id = SEMap.sh_id')
            sc.conditions.append(
                '(CEMap.ev_id IS NOT NULL OR SEMap.ev_id IS NOT NULL)')

        if unique:
            sc.uniquify_by('CL.command', 'start_time')

        need = lambda *x: (sort_by in x or set(x) & set(additional_columns))
        if need('command_count'):
            sc.add_column('COUNT(*) as command_count', 'command_count')
        if need('success_count', 'success_ratio'):
            sc.join(cls._sc_success_count(),
                    on='command_id = success_command.id')
            sc.add_column('success_count')
            sc.add_column('(success_count * 1.0 / COUNT(*)) AS success_ratio',
                          'success_ratio')
        if need('program_count'):
            sc.join(cls._sc_program_count(),
                    on='PROGRAM_NAME(CL.command) = command_program.program')
            sc.add_column('program_count')

        return sc.compile()

    @staticmethod
    def _sc_success_count(table_alias='success_command'):
        count = ('COUNT(CASE WHEN exit_code = 0 THEN 1 ELSE NULL END)'
                 ' AS success_count')
        return SQLConstructor(
            'command_history',
            ['command_id AS id', count],
            ['command_id', 'success_count'],
            group_by=['command_id'], table_alias=table_alias)

    @staticmethod
    def _sc_program_count(table_alias='command_program'):
        return SQLConstructor(
            'command_history '
            'LEFT JOIN command_list AS CL ON command_id = CL.id',
            ['PROGRAM_NAME(CL.command) AS program',
             'COUNT(*) AS program_count'],
            ['program', 'program_count'],
            group_by=['program'], table_alias=table_alias)

    @staticmethod
    def _sc_matched_environment_variable(
            match_pattern=[], include_pattern=[], exclude_pattern=[],
            match_regexp=[], include_regexp=[], exclude_regexp=[],
            table_alias='matched_environment_variable'):
        glob = "({0[0]} = {1} AND glob({2}, {0[1]}))".format
        regexp = "({0[0]} = {1} AND regexp({2}, {0[1]}))".format
        sc = SQLConstructor(
            'environment_variable',
            ['id', 'variable_name', 'variable_value'],
            ['environment_variable_id', 'variable_name', 'variable_value'],
            table_alias=table_alias)
        sc.add_matches(glob, ['variable_name', 'variable_value'],
                       match_pattern, include_pattern, exclude_pattern, numq=2)
        sc.add_matches(regexp, ['variable_name', 'variable_value'],
                       match_regexp, include_regexp, exclude_regexp, numq=2)
        return sc

    def search_environ_record(self, **kwds):
        sc = self._sc_matched_environment_variable(**kwds)
        (sql, params, keys) = sc.compile()
        return self._select_rows(EnvironRecord, keys, sql, params)

    def import_init_dict(self, dct, overwrite=True):
        long_id = dct['session_id']
        srec = SessionRecord(**dct)
        with self.connection(commit=True) as connection:
            db = connection.cursor()
            records = list(self.select_session_by_long_id(long_id))
            if records:
                assert len(records) == 1
                oldrec = records[0]
                if oldrec.start is not None and not overwrite:
                    return
                oldrec.start = srec.start
                sh_id = self._update_session_history(db, oldrec)
            else:
                sh_id = self._insert_session_history(db, srec)
            self._update_session_environ(db, sh_id, srec.environ)

    def import_exit_dict(self, dct, overwrite=True):
        long_id = dct['session_id']
        srec = SessionRecord(**dct)
        with self.connection(commit=True) as connection:
            db = connection.cursor()
            records = list(self.select_session_by_long_id(long_id))
            if records:
                assert len(records) == 1
                oldrec = records[0]
                if oldrec.stop is not None and not overwrite:
                    return
                oldrec.stop = srec.stop
                self._update_session_history(db, oldrec)
            else:
                self._insert_session_history(db, srec)

    def _insert_session_history(self, db, srec):
        db.execute(
            '''
            INSERT INTO session_history
                (session_long_id, start_time, stop_time)
            VALUES (?, ?, ?)
            ''',
            [srec.session_id, convert_ts(srec.start), convert_ts(srec.stop)])
        return db.lastrowid

    def _update_session_history(self, db, srec):
        assert srec.session_history_id is not None
        db.execute(
            '''
            UPDATE session_history
            SET session_long_id=?, start_time=?, stop_time=?
            WHERE id=?
            ''',
            [srec.session_id, convert_ts(srec.start), convert_ts(srec.stop),
             srec.session_history_id])
        return srec.session_history_id

    def _update_session_environ(self, db, sh_id, environ):
        if not environ:
            return
        db.execute('DELETE FROM session_environment_map WHERE sh_id=?',
                   [sh_id])
        self._insert_session_environ(db, sh_id, environ)

    def _insert_session_environ(self, db, sh_id, environ):
        self._insert_environ(db, 'session_environment_map', 'sh_id', sh_id,
                             environ)

    def select_session_by_long_id(self, long_id):
        keys = ['session_history_id', 'session_id', 'start', 'stop']
        sql = """
        SELECT id, session_long_id, start_time, stop_time
        FROM session_history
        WHERE session_long_id = ?
        """
        params = [long_id]
        with self.connection() as connection:
            for row in connection.execute(sql, params):
                yield SessionRecord(**dict(zip(keys, row)))

    def search_session_record(self, session_id):
        return self.select_session_by_long_id(session_id)

    def get_full_command_record(self, command_history_id,
                                merge_session_environ=True):
        """
        Get fully retrieved :class:`CommandRecord` instance by ID.

        By "fully", it means that complex slots such as `environ` and
        `pipestatus` are available.

        :type    command_history_id: int
        :type merge_session_environ: bool

        """
        with self.connection() as db:
            crec = self._select_command_record(db, command_history_id)
            crec.pipestatus = self._get_pipestatus(db, command_history_id)
            # Set environment variables
            cenv = self._select_environ(db, 'command', command_history_id)
            crec.environ.update(cenv)
            if merge_session_environ:
                senv = self._select_environ(
                    db, 'session', crec.session_history_id)
                crec.environ.update(senv)
        return crec

    def _select_command_record(self, db, command_history_id):
        keys = ['session_history_id', 'command', 'cwd', 'terminal',
                'start', 'stop', 'exit_code']
        sql = """
        SELECT
            session_id, CL.command, DL.directory, TL.terminal,
            start_time, stop_time, exit_code
        FROM command_history
        LEFT JOIN command_list AS CL ON command_id = CL.id
        LEFT JOIN directory_list AS DL ON directory_id = DL.id
        LEFT JOIN terminal_list AS TL ON terminal_id = TL.id
        WHERE command_history.id = ?
        """
        params = [command_history_id]
        for row in db.execute(sql, params):
            crec = CommandRecord(**dict(zip(keys, row)))
            crec.command_history_id = command_history_id
            return crec
        raise ValueError("Command record of id={0} is not found"
                         .format(command_history_id))

    def _get_pipestatus(self, db, command_history_id):
        sql = """
        SELECT program_position, exit_code
        FROM pipe_status_map
        WHERE ch_id = ?
        """
        params = [command_history_id]
        records = list(db.execute(sql, params))
        length = max(r[0] for r in records) + 1
        pipestatus = [None] * length
        for (i, s) in records:
            pipestatus[i] = s
        return pipestatus

    def _select_environ(self, db, recname, recid):
        sql = """
        SELECT
            EVar.variable_name, EVar.variable_value
        FROM {recname}_environment_map as EMap
        LEFT JOIN environment_variable AS EVar ON EMap.ev_id = EVar.id
        WHERE EMap.{hist_id} = ?
        """.format(
            recname=recname,
            hist_id='ch_id' if recname == 'command' else 'sh_id',
        )
        params = [recid]
        return db.execute(sql, params)
