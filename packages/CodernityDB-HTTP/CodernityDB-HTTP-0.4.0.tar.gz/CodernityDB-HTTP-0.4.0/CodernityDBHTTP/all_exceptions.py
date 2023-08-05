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

from CodernityDB.database import DatabaseException
import httplib


class HTTPDatabaseException(DatabaseException):
    pass


class DBHTTPException(Exception):

    def __init__(self, code, conflict):
        if not isinstance(conflict, basestring):
            conflict = str(conflict)
        self.code = code
        self.status = "%s %s" % (self.code, httplib.responses[self.code])
        self.content = conflict
        Exception.__init__(self)

    def __str__(self):
        return "%s: %s" % (repr(self.status), repr(self.content))


class HTTPConflictException(DBHTTPException):

    def __init__(self, ex="Conflict"):
        DBHTTPException.__init__(self, 409, ex)


class HTTPNotFoundException(DBHTTPException):

    def __init__(self, ex="Not found"):
        DBHTTPException.__init__(self, 404, ex)


class DBIsNotOpened(DBHTTPException):
    def __init__(self, ex="Database is not opened, try to open it first"):
        DBHTTPException.__init__(self, '500', ex)
