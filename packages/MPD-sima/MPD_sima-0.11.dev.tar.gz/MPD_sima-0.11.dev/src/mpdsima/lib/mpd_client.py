# -*- coding: utf-8 -*-
#
# Copyright (C) 2008-2010  J. Alexander Treuman <jat@spatialrift.net>
# Copyright (c) 2011-2013 Jack Kaliko <efrim@azylum.org>
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

from select import select


from .musicpd import (MPDClient, MPDError, CommandError)
from .track import Track


class PlayerError(Exception):
    """Fatal error in poller."""

class PlayerCommandError(PlayerError):
    """Command error"""


class Player(object):
    """
    From python-mpd:
        _fetch_nothing  …
        _fetch_item     single str
        _fetch_object   single dict
        _fetch_list     list of str
        _fetch_playlist list of str
        _fetch_changes  list of dict
        _fetch_database list of dict
        _fetch_songs    list of dict, especially tracks
        _fetch_plugins,

    TODO: handle exception in command not going through _client_wrapper() (ie.
          find_aa, remove…)
    """
    def __init__(self, host="localhost", port="6600", password=None):
        self._host = host
        self._port = port
        self.track_format = False
        self._password = password
        self._client = MPDClient()
        self._client.iterate = True

    def __getattr__(self, attr):
        command = attr
        wrapper = self._execute
        return lambda *args: wrapper(command, args)

    def _execute(self, command, args):
        self._write_command(command, args)
        return self._client_wrapper()

    def _write_command(self, command, args=[]):
        self._comm = command
        self._args = list()
        for arg in args:
            self._args.append(arg)

    def _client_wrapper(self):
        func = self._client.__getattr__(self._comm)
        try:
            ans = func(*self._args)
        # WARNING: MPDError is an ancestor class of # CommandError
        except CommandError as err:
            raise PlayerCommandError('MPD command error: %s' % err)
        except (MPDError, IOError) as err:
            raise PlayerError(err)
        return self._track_format(ans)

    def _track_format(self, ans):
        # TODO: ain't working for "sticker find" and "sticker list"
        tracks_listing = ["playlistfind", "playlistid", "playlistinfo",
                "playlistsearch", "plchanges", "listplaylistinfo", "find",
                "search", "sticker find",]
        track_obj = ['currentsong']
        unicode_obj = ["idle", "listplaylist", "list", "sticker list",
                "commands", "notcommands", "tagtypes", "urlhandlers",]
        if self.track_format:
            if self._comm in tracks_listing:
                return [Track(**track) for track in ans]
            if self._comm in track_obj:
                return Track(**ans)
        return ans

    def find_aa(self, artist, album):
        """
        Special wrapper around album search:
        Album lookup is made through AlbumArtist/Album instead of Artist/Album
        """
        alb_art_search = self.find('albumartist', artist,
            'album', album)
        if alb_art_search:
            return alb_art_search
        return self.find('artist', artist, 'album', album)

    def idle(self):
        try:
            self._client.send_idle('database', 'playlist', 'player', 'options')
            select([self._client], [], [], 60)
            return self._client.fetch_idle()
        except (MPDError, IOError) as err:
            raise PlayerError("Couldn't init idle: %s" % err)

    def remove(self, position=0):
        self._client.delete(position)

    def state(self):
        return str(self._client.status().get('state'))

    def playlist(self):
        """
        Override deprecated MPD playlist command
        """
        return self.playlistinfo()

    def connect(self):
        self.disconnect()
        try:
            self._client.connect(self._host, self._port)

        # Catch socket errors
        except IOError as err:
            raise PlayerError('Could not connect to "%s:%s": %s' %
                              (self._host, self._port, err.strerror))

        # Catch all other possible errors
        # ConnectionError and ProtocolError are always fatal.  Others may not
        # be, but we don't know how to handle them here, so treat them as if
        # they are instead of ignoring them.
        except MPDError as err:
            raise PlayerError('Could not connect to "%s:%s": %s' %
                              (self._host, self._port, err))

        if self._password:
            try:
                self._client.password(self._password)

            # Catch errors with the password command (e.g., wrong password)
            except CommandError as err:
                raise PlayerError("Could not connect to '%s': "
                                  "password command failed: %s" %
                                  (self._host, err))

            # Catch all other possible errors
            except (MPDError, IOError) as err:
                raise PlayerError("Could not connect to '%s': "
                                  "error with password command: %s" %
                                  (self._host, err))
        # Controls we have sufficient rights for MPD_sima
        needed_cmds = ['status', 'stats', 'add', 'find', \
                       'search', 'currentsong', 'ping']

        available_cmd = self._client.commands()
        for nddcmd in needed_cmds:
            if nddcmd not in available_cmd:
                self.disconnect()
                raise PlayerError('Could connect to "%s", '
                                  'but command "%s" not available' %
                                  (self._host, nddcmd))

    def disconnect(self):
        # Try to tell MPD we're closing the connection first
        try:
            self._client.close()
        # If that fails, don't worry, just ignore it and disconnect
        except (MPDError, IOError):
            pass

        try:
            self._client.disconnect()
        # Disconnecting failed, so use a new client object instead
        # This should never happen.  If it does, something is seriously broken,
        # and the client object shouldn't be trusted to be re-used.
        except (MPDError, IOError):
            self._client = MPDClient()

# VIM MODLINE
# vim: ai ts=4 sw=3 sts=4 expandtab
