# Copyright (C) 2012 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import socket
import logging
import cmd
from gevent.server import StreamServer


class RyuCli(cmd.Cmd):
    prompt = "Ryu> "
    use_rawinput = False

    def do_log(self, args):
        args = args.split()
        if len(args) > 0:
            if args[0] == 'show':
                self.log_show()
            elif args[0] == 'set':
                self.log_set(args)
            else:
                self.log_help()

    def log_help(self):
        self.stdout.write('log show|set\n')

    def log_show(self):
        for name, l in logging.Logger.manager.loggerDict.iteritems():
            if name.startswith('ryu.') and isinstance(l, logging.Logger):
                self.stdout.write('%s\t%s\n' %
                                  (name, logging.getLevelName(l.level)))

    def log_set(self, args):
        if len(args) != 3:
            return

        if not isinstance(logging.getLevelName(args[2]), int):
            return

        if args[1] in logging.Logger.manager.loggerDict:
            log = logging.getLogger(args[1])
            log.setLevel(args[2])
            self.stdout.write('set %s loglevel to %s\n' % (args[1], args[2]))

    def do_exit(self, args):
        return True


def client_factory(socket, address):
    f = socket.makefile("rb")
    try:
        RyuCli(stdin=f, stdout=f).cmdloop()
    except:
        pass


class CliController(object):
    def __init__(self):
        super(CliController, self).__init__()

    def __call__(self):
        server = StreamServer(('', 2525),
                              client_factory)
        server.serve_forever()
