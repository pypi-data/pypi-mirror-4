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


import logging


def loglevel(level):
    """
    Convert any representation of `level` to an int appropriately.

    :type level: int or str
    :rtype: int

    >>> loglevel('DEBUG') == logging.DEBUG
    True
    >>> loglevel(10)
    10
    >>> loglevel(None)
    Traceback (most recent call last):
      ...
    ValueError: None is not a proper log level.

    """
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    elif isinstance(level, int):
        pass
    else:
        raise ValueError('{0!r} is not a proper log level.'.format(level))
    return level


logger = logging.getLogger('rash')


def setup_daemon_log_file(conf):
    """
    Attach file handler to RASH logger.

    :type conf: rash.config.ConfigStore

    """
    level = loglevel(conf.daemon_log_level)
    handler = logging.FileHandler(filename=conf.daemon_log_path)
    handler.setLevel(level)
    logger.setLevel(level)
    logger.addHandler(handler)
