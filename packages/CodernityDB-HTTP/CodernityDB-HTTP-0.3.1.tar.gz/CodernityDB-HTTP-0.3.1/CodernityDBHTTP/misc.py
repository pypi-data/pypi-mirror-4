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

from functools import wraps
from base64 import b64decode
from os import path as os_path
from os import access as os_access
from os import R_OK
import sys
from all_exceptions import DBHTTPException, HTTPDatabaseException, HTTPNotFoundException, HTTPConflictException, DBIsNotOpened
from types import FunctionType, MethodType, GeneratorType
from CodernityDB.database import RevConflict, RecordDeleted, RecordNotFound
import httplib


import traceback

content_types = {
    'js': 'text/javascript',
    'py': 'text/x-python',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'gif': 'image/gif',
    'txt': 'text/plain',
    'html': 'text/html',
    'css': 'text/css',
    'default': 'text/plain'
}


ERRORS_TABLE = {
    'RevConflict': 409,
    'IndexConflict': 409,
    'DatabaseConflict': 409,
    'IndexNotFoundException': 404,
    'PreconditionsException': 400,
    'IndexPreconditionsException': 400,
    'DocIdNotFound': 404,
    'ElemNotFound': 404,
    'RecordNotFound': 404,
    'RecordDeleted': 404,
    'DatabasePathException': 409,
    'DatabaseIsNotOpened': 409,
    'TryReindexException': 409,
    'ReindexException': 409
}


# class HandleErrors(type):

#     @staticmethod
#     def wrapper(f):
#         @wraps(f)
#         def _inner(*args, **kwargs):
#             try:
#                 return f(*args, **kwargs)
#             except UpdateConflict:
#                 raise HTTPConflictException()
#             except (RecordNotFound, RecordDeleted) as ex:
#                 raise HTTPNotFoundException(ex)
#             except Exception as ex:
#                 database = args[0]
#                 # if database is not opened maybe that's issue
#                 if not database.opened and not f.__name__ in ['close', 'create', 'initialize', 'open']:
#                 #if not database.opened:
#                     raise DBIsNotOpened()
#                 raise
#         return _inner

#     def __new__(cls, classname, bases, attr):
#         new_attr = {}
#         for base in bases:
#             for b_attr in dir(base):
#                 a = getattr(base, b_attr, None)

#                 if isinstance(a, MethodType) and not b_attr.startswith('_'):
#                     setattr(base, b_attr, HandleErrors.wrapper(a))
#         for attr_name, attr_value in attr.iteritems():
#             if isinstance(attr_value, FunctionType) and not attr_name.startswith('_'):
#                 attr_value = HandleErrors.wrapper(attr_value)
#             new_attr[attr_name] = attr_value
#         return type.__new__(cls, classname, bases, new_attr)


# def dummy_auth(user, password):
#     if user == password:
#         return user
#     return False


def fixed_user_pass(def_user, def_password):
    def _fixed_user_pass(user, password):
        return user == def_user and def_password == password
    return _fixed_user_pass


def with_basic_auth(function, realm='Protected', auth_function=fixed_user_pass):

    @wraps(function)
    def _inner(env, start_response, in_f, out_f, inc_type, *args, **kwargs):
        auth = env.get("HTTP_AUTHORIZATION")
        if auth:
            try:
                data = auth.split(" ", 1)
                user, password = b64decode(data[1]).split(':', 1)
            except:
                start_response("401 Unauthorized", [("WWW-Authenticate",
                                                     "Basic realm=\"%s\"" % realm)])
                return ["You're not authorized to access this address"]
            else:
                user_login = auth_function(user, password)
                if user_login:
                    env['USER'] = user_login
                    try:
                        res = function(*args, **kwargs)
                    except Exception:
                        return handle_exception(start_response, out_f, inc_type)
                    else:
                        start_response("200 Ok", [('Content-Type', inc_type)])
                        return out_f(res)
        start_response("401 Unauthorized", [("WWW-Authenticate",
                                             "Basic realm=\"%s\"" % realm)])
        return ["You're not authorized to access this address"]

    return _inner


def default_method(function):

    @wraps(function)
    def _inner(env, start_response, inf_f, out_f, inc_type, *args, **kwargs):
        try:
            res = function(*args, **kwargs)
        # except DBHTTPException as ex:
        #     start_response(ex.status, [('Content-Type', inc_type)])
        #     return out_f(format_exception(code=ex.code))
        except Exception as ex:
            return handle_exception(start_response, out_f, inc_type)
        else:
            start_response("200 Ok", [('Content-Type', inc_type)])
            try:
                return out_f(res)
            except TypeError:
                if isinstance(res, GeneratorType):  # not memory optimized though
                    return out_f(tuple(res))
                else:
                    raise
    return _inner


def static_file(root, path, env, start_response):
    f_path = os_path.join(root, *path[1:])
    if os_path.isdir(f_path):
        # it's directory let's serve index.html if exists
        f_path = os_path.join(f_path, 'index.html')
    if not os_path.exists(f_path) or not os_path.isfile(f_path):
        start_response("404 Not Found", [('Content-Type', 'text/plain')])
        yield ""
    else:
        abs_path = os_path.abspath(f_path)
        if not os_access(f_path, R_OK) or not abs_path.startswith(root):
            start_response("403 Forbidden", [('Content-Type', 'text/plain')])
            yield ""
        else:
            try:
                content_type = content_types.get(f_path.rsplit(
                    '.', 1)[1], content_types['default'])
            except:
                content_type = content_types['default']
            with open(f_path, 'rb') as fp:
                start_response("200 OK", [('Content-Type', content_type)])
                chunk = fp.read(4096)
                while chunk:
                    yield chunk
                    chunk = fp.read(4096)


def normal_static_file(root, function):

    abs_root = os_path.abspath(root)

    @wraps(function)
    def _inner(*args, **kwargs):
        return function(abs_root, *args, **kwargs)
    return _inner


def auth_static_file(root, function, realm="Protected", auth_function=fixed_user_pass):

    abs_root = os_path.abspath(root)

    @wraps(function)
    def _inner(path, env, start_response):
        auth = env.get("HTTP_AUTHORIZATION")
        if auth:
            try:
                data = auth.split(" ", 1)
                user, password = b64decode(data[1]).split(':', 1)
            except:
                start_response("401 Unauthorized", [("WWW-Authenticate",
                                                     "Basic realm=\"%s\"" % realm)])
                return ["You're not authorized to access this address"]
            else:
                user_login = auth_function(user, password)
                if user_login:
                    env['USER'] = user_login
                    return function(abs_root, path, env, start_response)
                else:
                    start_response("401 Unauthorized", [("WWW-Authenticate",
                                                         "Basic realm=\"%s\"" % realm)])
                    return ["You're not authorized to access this address"]
        else:
            start_response("401 Unauthorized", [("WWW-Authenticate",
                                                 "Basic realm=\"%s\"" % realm)])
            return ["You're not authorized to access this address"]
    return _inner


def tuple_funct(function):

    @wraps(function)
    def _inner(*args, **kwargs):
        return tuple(function(*args, **kwargs))
    return _inner


def make_one_item_iter(function):

    @wraps(function)
    def _inner(*args, **kwargs):
        return [function(*args, **kwargs)]
    return _inner


def convert_values_to_base(v):
    if isinstance(v, (int, basestring, unicode, long)):
        v = v
    elif isinstance(v, list):
        l = []
        for curr in v:
            l.append(convert_values_to_base(curr))
        v = l
    elif isinstance(v, tuple):
        l = ()
        for curr in v:
            l += (convert_values_to_base(curr), )
        v = l
    elif isinstance(v, dict):
        _d = {}
        for key, value in v.iteritems():
            _d[key] = convert_values_to_base(value)
        v = _d
    elif v is None:
        v = v
    else:
        v = str(v)
    return v


def values_to_base(function):

    @wraps(function)
    def _inner(*args, **kwargs):
        v = function(*args, **kwargs)
        return convert_values_to_base(v)
    return _inner


def handle_exception(start_response, out_f, content_type, code=None, reason=None):
    exc_type, exc_value, exc_traceback = sys.exc_info()

    if reason:
        pass
    # elif hasattr(exc_value, 'content'):
    #     reason = exc_value.content
    else:
        reason = str(exc_value)
        if not reason:
            reason = exc_type.__name__

    exc_code = ERRORS_TABLE.get(exc_type.__name__)
    with_traceback = False
    if exc_code:
        code = exc_code
    if code:
        error = "%s %s" % (code, httplib.responses[code])
        if code == 500:
            with_traceback = True
    elif hasattr(exc_value, 'exc_value'):
        error = exc_value.exc_value
    else:
        error = "%s %s" % (500, httplib.responses[500])
        with_traceback = True
    exception_output = {'exception': exc_type.__name__,
                        'reason': reason,
                        'error': error}
    if with_traceback:
        tb = traceback.format_exception(exc_type, exc_value, exc_traceback)
        exception_output['traceback'] = ''.join(tb)
        sys.stderr.writelines(tb)  # print the traceback to console
    start_response(error, [('Content-Type', content_type), ])
    return out_f(exception_output)
