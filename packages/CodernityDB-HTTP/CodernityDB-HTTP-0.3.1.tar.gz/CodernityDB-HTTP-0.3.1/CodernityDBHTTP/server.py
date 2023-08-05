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

import sys

try:
    import simplejson as json
except ImportError:
    try:
        import json
    except ImportError:
        import sys
        print "You need json to parse config file"
        sys.exit(0)


def get_config(path):
    with open(path, 'r') as f:
        cfg = json.loads(f.read())
    bind = cfg.get('bind', "0.0.0.0")
    port = cfg.get('port', 9876)
    db_path = cfg.get('db_path', '/tmp/db')
    server = cfg.get('server', 'gevent')

    if server == 'auto':
        server = 'wsgiref'
        try:
            import gevent
        except ImportError:
            pass
        else:
            del gevent
            server = 'gevent'
            cfg['server'] = server
    if server == 'gevent':
        from server_gevent import create_server
    elif server == 'wsgiref':
        from server_wsgiref import create_server
    else:
        raise NotImplemented("Not supported server method")
    s = create_server(bind, port, db_path, cfg)
    del create_server
    cfg['port'] = s.server_port
    return s, cfg


def run():
    import sys
    if len(sys.argv) != 2:
        sys.stderr.write("No config file specified!")
        sys.exit(1)
    s, cfg = get_config(sys.argv[1])
    #cfg['host'] = s.server_host
    sys.stdout.write("Got server: " + s.__class__.__name__ + "\n")
    sys.stdout.write("Got server config:\n")
    sys.stdout.write(json.dumps(cfg) + "\n")
    sys.stdout.flush()
    s.serve_forever()

if __name__ == '__main__':
    run()
