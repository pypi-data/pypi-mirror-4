#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2011-2012 Codernity (http://codernity.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from gevent import monkey
monkey.patch_all()


from gevent.pywsgi import WSGIServer
from database_gevent import HTTPGeventDatabase
from app import get_app

from CodernityDB import __version__ as __db__version__


class CodernityDBGeventWSGIServer(WSGIServer):
    """
    It's not intended to be fully REST application,
    it 'just' maps the url to python methods, everything via GET/POST.
    """

    def __init__(self, *args, **kwargs):
        super(CodernityDBGeventWSGIServer, self).__init__(*args, **kwargs)


def create_server(bind, port, db_path, cfg, **kwargs):
    from gevent import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((bind, port))
    backlog = kwargs.get('backlog', 50)
    sock.listen(backlog)
    s = CodernityDBGeventWSGIServer(
        sock, get_app(HTTPGeventDatabase, db_path, cfg))
    return s
