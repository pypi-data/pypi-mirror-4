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


from wsgiref.simple_server import make_server
from database_threads import HTTPThreadSafeDatabase
from app import get_app

from CodernityDB import __version__ as __db__version__


# class CodernityDBWsgirefServer(WSGIServer):
#     """
#     It's not intended to be fully REST application,
#     it 'just' maps the url to python methods, everything via GET/POST.
#     """

#     server_software = 'CodernityDB(%s) @ wsgiref' % __db__version__

#     def __init__(self, *args, **kwargs):
#         #super(CodernityDBWsgirefServer, self).__init__(*args, **kwargs)
#         WSGIServer.__init__(self, *args, **kwargs)

#         #self.base_env['SERVER_SOFTWARE'] = 'CodernityDB(%s) @ wsgiref' % __db__version__

def create_server(bind, port, db_path, cfg, **kwargs):
    app = get_app(HTTPThreadSafeDatabase, db_path, cfg)
    s = make_server(bind, port, app)
    return s
