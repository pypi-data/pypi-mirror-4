# -*- coding: utf-8 -*-

# Copyright (c) 2009, 2010, 2011, 2012 Jack Kaliko <efrim@azylum.org>
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

import sys
from argparse import (ArgumentParser, ArgumentError, Action, SUPPRESS)

#from os import devnull
from os import (access, getcwd, W_OK, R_OK)
from os.path import (dirname, isabs, join, normpath, exists, isdir, isfile)


USAGE = """USAGE:  %prog [--help] [options]"""
DESCRIPTION = """
MPD_sima automagicaly queue new tracks in MPD playlist.
All command line options will override their equivalent in configuration
file.
"""


# ArgParse Callbacks
class Obsolete(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        raise ArgumentError(self, 'obsolete argument')

class FileAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        self._file = normalize_path(values)
        self._dir = dirname(self._file)
        self.parser = parser
        self.checks()
        setattr(namespace, self.dest, self._file)

    def checks(self):
        pass


class Wfile(FileAction):
    def checks(self):
        if not exists(self._dir):
            #raise ArgumentError(self, '"{0}" does not exist'.format(self._dir))
            self.parser.error('file does not exist: {0}'.format(self._dir))
        if not exists(self._file):
            # Is parent directory writable then
            if not access(self._dir, W_OK):
                self.parser.error('no write access to "{0}"'.format(self._dir))
        else:
            if not access(self._file, W_OK):
                self.parser.error('no write access to "{0}"'.format(self._file))

class Rfile(FileAction):
    def checks(self):
        if not exists(self._file):
            self.parser.error('file does not exist: {0}'.format(self._file))
        if not isfile(self._file):
            self.parser.error('not a file: {0}'.format(self._file))
        if not access(self._file, R_OK):
            self.parser.error('no read access to "{0}"'.format(self._file))

class Wdir(FileAction):
    def checks(self):
        if not exists(self._file):
            self.parser.error('directory does not exist: {0}'.format(self._file))
        if not isdir(self._file):
            self.parser.error('not a directory: {0}'.format(self._file))
        if not access(self._file, W_OK):
            self.parser.error('no write access to "{0}"'.format(self._file))


def normalize_path(path):
    """
    """
    if not isabs(path):
        return normpath(join(getcwd(), path))
    return path

def clean_dict(to_clean):
    """Remove items which values are set to None/False"""
    for k in list(to_clean.keys()):
        if not to_clean.get(k):
            to_clean.pop(k)


# OPTIONS LIST
# pop out 'sw' value before creating Parser object.
# PAY ATTENTION:
#   If an option has to override its dual in conf file, the destination
#   identifier "dest" is to be named after that option in the conf file.
#   The supersedes_config_with_cmd_line_options method in ConfMan() (config.py)
#   is looking for command line option names identical to config file option
#   name it is meant to override.
OPTS = [
    {
        'sw':['-l', '--log'],
        'type': str,
        'dest':'logfile',
        'action': Wfile,
        'help': 'file to log message to, default is stdout/stderr'},
    {
        'sw': ['-p', '--pid'],
        'dest': 'pidfile',
        'action': Wfile,
        'help': 'file to save PID to, default is not to store pid'},
    {
        'sw': ['-d', '--daemon'],
        'dest': 'daemon',
        'action': 'store_true',
        'help': 'Daemonize process.'},
    {
        'sw': ['--hostname'],
        'dest': 'host',
        'action': Obsolete,
        #'help': '[OBSOLETE] Hostname MPD in running on'
        'help': SUPPRESS},
    {
        'sw': ['-S', '--host'],
        'dest': 'host',
        'help': 'Host MPD in running on (IP or FQDN)'},
    {
        'sw': ['-P', '--port'],
        'type': int,
        'dest': 'port',
        'help': 'Port MPD in listening on'},
    {
        'sw':['-c', '--config'],
        'dest': 'conf_file',
        'action': Rfile,
        'help': 'Configuration file to load'},
    {
        'sw':['--var_dir'],
        'dest': 'var_dir',
        'action': Wdir,
        'help': 'Directory to store var content (ie. database)'},
    {
        'sw': ['--create-db'],
        'action': 'store_true',
        'dest': 'create_db',
        'help': '''Create database and exit, use destination
                   specified in --var_dir or standard location.'''},
    {
        'sw': ['--new-version'],
        'action': 'store_true',
        'dest': 'check_new_version',
        'help': 'Check and log for new version (issue a warning)'},
    {
        'sw':['--queue-mode', '-q'],
        'dest': 'queue_mode',
        'choices': ['track', 'top', 'album'],
        'help': SUPPRESS,
        #'help': 'Queue mode in [track, top, album]',
    },
    {
        'sw':['--purge_history'],
        'action': 'store_true',
        'dest': 'do_purge_history',
        'help': SUPPRESS},]


class StartOpt(object):
    """Command line management.
    """

    def __init__(self, script_info,):
        self.info = dict(script_info)
        self.options = dict()
        self.main()

    def declare_opts(self):
        """
        Declare options in OptionParser object.
        """
        version = 'MPD_sima v{version}'.format(**self.info)
        self.parser = ArgumentParser(description=DESCRIPTION,
                                   usage='%(prog)s [options]',
                                   prog='mpd_sima',
                                   epilog='Happy Listening',
                                   version=version,
                )

        # Add all options declare in OPTS
        for opt in OPTS:
            opt_names = opt.pop('sw')
            self.parser.add_argument(*opt_names, **opt)

    def main(self):
        """
        Look for env. var and parse command line.
        """
        self.declare_opts()
        options = vars(self.parser.parse_args())
        # Set log file to os.devnull in daemon mode to avoid logging to
        # std(out|err).
        # TODO: Probably useless. To be checked
        #if options.__dict__.get('daemon', False) and \
        #        not options.__dict__.get('logfile', False):
        #    options.__dict__['logfile'] = devnull
        self.options.update(options)
        clean_dict(self.options)


if __name__ == '__main__':
    __version__ = '0.11.0'
    __revison__ = '0.1234566'
    __date__  = 'samedi 20 avril 2013, 09:29:48 (UTC+0200)'
    info = dict({'version': __version__, 'revision': __revison__,
                 'date': __date__})
    sopt = StartOpt(info,)
    sys.exit(0)

# VIM MODLINE
# vim: ai ts=4 sw=4 sts=4 expandtab
