# -*- coding: utf-8 -*-

# Copyright (c) 2010, 2011, 2013 Jack Kaliko <efrim@azylum.org>
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


from os import environ

def get_mpd_environ():
    """
    Retrieve MPD env. var.
    """
    passwd = host = port = None
    mpd_host_env = environ.get('MPD_HOST')
    if mpd_host_env:
        # If password is set:
        # mpd_host_env = ['pass', 'host'] because MPD_HOST=pass@host
        mpd_host_env = mpd_host_env.split('@')
        mpd_host_env.reverse()
        host = mpd_host_env[0]
        if len(mpd_host_env) > 1 and mpd_host_env[1]:
            passwd = mpd_host_env[1]
    return (host, environ.get('MPD_PORT', None), passwd)

# VIM MODLINE
# vim: ai ts=4 sw=4 sts=4 expandtab
