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


from CodernityDB.database_thread_safe import ThreadSafeDatabase
from all_exceptions import HTTPDatabaseException

#from misc import HandleErrors


class HTTPThreadSafeDatabase(ThreadSafeDatabase):
    """
    A database that works with Threads
    """

    #__metaclass__ = HandleErrors

    def __init__(self, *args, **kwargs):
        super(HTTPThreadSafeDatabase, self).__init__(*args, **kwargs)

    def count(self, method, *args, **kwargs):
        func = getattr(super(HTTPThreadSafeDatabase, self), method)
        return super(HTTPThreadSafeDatabase, self).count(func, *args, **kwargs)

    def insert(self, data):
        res = super(HTTPThreadSafeDatabase, self).insert(data)
        if res:
            #return {"_id": data['_id'], '_rev': data['_rev']}
            return res
        else:
            raise HTTPDatabaseException("Invalid return data from Database")

    def update(self, data):
        res = super(HTTPThreadSafeDatabase, self).update(data)
        if res:
            #return {"_id": data['_id'], '_rev': data['_rev']}
            return res
        else:
            raise HTTPDatabaseException("Invalid return data from Database")

    def delete(self, data):
        res = super(HTTPThreadSafeDatabase, self).delete(data)
        return res

    def get_many(self, *args, **kwargs):
        return super(HTTPThreadSafeDatabase, self).get_many(*args, **kwargs)

    def all(self, *args, **kwargs):
        return super(HTTPThreadSafeDatabase, self).all(*args, **kwargs)
