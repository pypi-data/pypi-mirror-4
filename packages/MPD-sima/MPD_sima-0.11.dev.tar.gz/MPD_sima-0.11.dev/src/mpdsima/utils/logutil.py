# -*- coding: utf-8 -*-

# Copyright (c) 2009, 2010 Jack Kaliko <efrim@azylum.org>
#
#  This file is part of MPD_sima
#
#  MPD_sima is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MPD_sima is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MPD_sima.  If not, see <http://www.gnu.org/licenses/>.
#
#

"""
Logging facility for MPD_sima.
"""

import logging
import sys

#CONSTANT

LEVELS = {'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL}

LOG_FORMAT = '%(asctime)s - %(levelname)-9s %(message)s'
#LOG_FORMAT = '%(lineno)d:%(funcName)s - %(levelname)-9s %(message)s'
#LOG_FORMAT = '%(asctime)s : %(lineno)d - %(levelname)-9s %(message)s'

LOG_FORMATS = {'debug': '%(asctime)s : %(levelname)-9s %(message)s',
        'info': '%(levelname)-9s: %(message)s'}
DATE_FMT = "%Y-%m-%d %H:%M:%S"


class LevelFilter(logging.Filter):# Logging facility 
    """
    Enable logging between two log level by filtering everything < level.
    """

    def __init__(self, filt_level):
        logging.Filter.__init__(self)
        self.level = filt_level

    def filter(self, record):
        """Defines loglevel"""
        return record.levelno <= self.level


def logger(log_level='info', log_file=None, name='simaLogger'):
    """
    TODO: Add different log format for info / debug
    """

    user_log_level = LEVELS.get(log_level, logging.INFO)
    logg = logging.getLogger(name)
    formatter = logging.Formatter(LOG_FORMAT, DATE_FMT)
    logg.setLevel(user_log_level)
    if log_file:
        # create file handler
        fileh = logging.FileHandler(log_file)
        #fileh.setLevel(user_log_level)
        fileh.setFormatter(formatter)
        logg.addHandler(fileh)
    else:
        # create console handler with a specified log level (STDOUT)
        couth = logging.StreamHandler(sys.stdout)
        #couth.setLevel(user_log_level)
        couth.addFilter(LevelFilter(logging.WARNING))

        # create console handler with warning log level (STDERR)
        cerrh = logging.StreamHandler(sys.stderr)
        #cerrh.setLevel(logging.WARNING)
        cerrh.setLevel(logging.ERROR)

        # add formatter to the handlers
        cerrh.setFormatter(formatter)
        couth.setFormatter(formatter)

        # add the handlers to SIMA_LOGGER
        logg.addHandler(couth)
        logg.addHandler(cerrh)

    return logg


# VIM MODLINE
# vim: ai ts=4 sw=4 sts=4 expandtab
