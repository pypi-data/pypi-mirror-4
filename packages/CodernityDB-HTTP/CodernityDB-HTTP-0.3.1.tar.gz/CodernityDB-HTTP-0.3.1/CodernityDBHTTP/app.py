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

from urlparse import parse_qs
try:
    import msgpack
except ImportError:
    has_msgpack = False
else:
    has_msgpack = True

try:
    import ujson as json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        try:
            import json
        except ImportError:
            # rly ?
            has_json = False
    else:
        has_json = True
else:
    has_json = True

from misc import with_basic_auth, default_method, static_file, auth_static_file, tuple_funct, fixed_user_pass, make_one_item_iter, values_to_base, handle_exception
from all_exceptions import *
from CodernityDB.database import header_for_indexes
from CodernityDB import __version__ as __db__version__
import os

try:
    from CodernityDBHTTP import __version__ as __srv__version__
except ImportError:
    from __init__ import __version__ as __srv__version__


content_types = {
    'application/json': (json.loads, make_one_item_iter(json.dumps)),
}

if has_msgpack:
    content_types['application/msgpack'] = (
        msgpack.unpackb, make_one_item_iter(msgpack.packb))

content_types['json'] = content_types['application/json']
if has_msgpack:
    content_types['msgpack'] = content_types['application/msgpack']

#content_types['text/plain'] = content_types['application/json']

default_content_type = 'application/json'


class CodernityDBApp(object):
    """
    It's not intended to be fully REST application,
    it 'just' maps the url to python methods, everything via GET/POST.

    Also it's not using webob/werkzeug (request/response etc) because not needed (YET?)
    """

    def __init__(self, routes, static_routes):
        self.routes = routes
        self.static_routes = static_routes

    def codernitydb_app(self, env, start_response):
        path = env['PATH_INFO'].split('/')[1:]
        try:
            db_method = self.routes[path[0]]
        except KeyError:
            try:
                static_method = self.static_routes[path[0]]
            except KeyError:
                start_response("404 Not Found", [(
                    'Content-Type', 'text/plain')])
                return ["Not found"]
            else:
                return static_method(path, env, start_response)
        else:
            inc_type = env.get('CONTENT_TYPE', default_content_type)
            inc_type = inc_type.split(';')[0]
            try:
                input_f, output_f = content_types[inc_type]
            except KeyError:
                inc_type = default_content_type
                input_f, output_f = content_types[inc_type]
                # traceback.print_exc()
                # start_response("415 Unsupported Media Type", [('Content-Type', 'text/plain')])
                # return ["You have to specify one of %s" % ', '.join(sorted(content_types.keys()))]
            # if inc_type.startswith('text'):
            #     inc_type = default_content_type
            # inc_type = '%s; charset=utf-8' % inc_type
            args = path[1:]
            if len(args) > 1:
                try:
                    args[1:] = map(input_f, args[1:])
                                   # mostly for 'run' and 'count' for *args
                except Exception:
                    return handle_exception(start_response, output_f, inc_type, 400, "Invalid encoded data in GET parameters")
            http_method = env.get("REQUEST_METHOD", "GET")
            if http_method == "POST":
                try:
                    l = int(env.get('CONTENT_LENGTH', 0))
                except ValueError:
                    return handle_exception(start_response, output_f, inc_type, 400, 'You have to specify body')
                else:
                    if l != 0:
                        inp = env.get('wsgi.input')
                        try:
                            body = inp.read(l)
                            kwargs = input_f(body)
                        except Exception:
                            return handle_exception(start_response, output_f, inc_type)
                    else:
                        kwargs = {}
            elif http_method == 'GET':
                kwargs = {}
            else:
                return handle_exception(start_response, output_f, inc_type, 405, "Method Not Allowed")
            query_string = env.get('QUERY_STRING')
            if query_string:
                try:
                    # hack start
                    # because:
                    # ->> parse_qs('/a&b=1')
                    # {'b': ['1']}
                    # this fix it to:
                    # {'b': '1'}
                    qs = parse_qs(query_string)
                    if qs:
                        v = qs.iteritems()
                        fx_qs = dict(map(lambda item: (item[0],
                                                       input_f(item[1][0])), v))
                        kwargs.update(fx_qs)
                except Exception:
                    return handle_exception(start_response, output_f, inc_type)
            try:
                return db_method(env, start_response, input_f, output_f, inc_type, *args, **kwargs)
            except:
                return handle_exception(start_response, output_f, inc_type)


def get_app(db_class, db_path, cfg):

    def auth_function(target, realm="Admin"):
        return with_basic_auth(target, realm, fixed_user_pass('admin', cfg.get('admin_pass')))

    db = db_class(db_path)
    try:
        db.open()
    except:
        pass

    routes = {
        'get': default_method(db.get),
        'insert': default_method(db.insert),
        'update': default_method(db.update),
        'delete': default_method(db.delete),
        'all': default_method(tuple_funct(db.all)),
        'get_many': default_method(tuple_funct(db.get_many)),
        'count': default_method(db.count),
        'run': default_method(db.run),
        'add_index': auth_function(db.add_index),
        'edit_index': auth_function(db.edit_index),
        'destroy_index': auth_function(db.destroy_index),
        'compact': auth_function(db.compact),
        'compact_index': auth_function(db.compact_index),
        'reindex': auth_function(db.reindex),
        'reindex_index': auth_function(db.reindex_index),
        'open': auth_function(db.open),
        'opened': auth_function(lambda: db.opened),
        'destroy': auth_function(db.destroy),
        'exists': auth_function(db.exists),
        'close': auth_function(db.close),
        'flush': auth_function(db.flush),
        'fsync': auth_function(db.fsync),
        'initialize': auth_function(db.initialize),
        'create': auth_function(db.create),
        'get_indexes_names': auth_function(lambda: db.indexes_names.keys()),
        'get_index_code': auth_function(db.get_index_code),
        'get_index_details': auth_function(values_to_base(db.get_index_details)),
        'get_db_details': auth_function(values_to_base(db.get_db_details)),
        'get_version': default_method(lambda: dict(db_version=__db__version__,
                                                   srv_version=__srv__version__)),
        'get_index_header': auth_function(lambda: header_for_indexes("__REPLACE_NAME__", "__REPLACE_CLASS__"))
    }

    _ui_path = os.path.join(__file__, '..', 'interface')
    static_routes = {
        '_ui': auth_static_file(os.path.abspath(_ui_path), static_file)
    }

    return CodernityDBApp(routes, static_routes).codernitydb_app
