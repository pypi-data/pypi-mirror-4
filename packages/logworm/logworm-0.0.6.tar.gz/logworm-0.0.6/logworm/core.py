# Copyright 2013 Fredrik Brannbacka
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

import os
import sys
import threading
import logworm
import re


class LogWorm(object):
    class LogPipe(threading.Thread):
        def __init__(self, parent, parsers):
            threading.Thread.__init__(self)
            self.parent = parent
            self.parsers = parsers
            self.daemon = False
            self.fdRead, self.fdWrite = os.pipe()
            self.pipeReader, self.pipeWriter = os.fdopen(self.fdRead, 'r', 0), os.fdopen(self.fdWrite, 'w', 0)
            self.start()

        def fileno(self):
            """Return the write file descriptor of the pipe
            """
            return self.fdWrite

        def run(self):
            """Run the thread, logging everything.
            """
            for line in iter(self.pipeReader.readline, ''):
                for parser in self.parsers:
                    for parser_name in parser.keys():
                        for key, value in parser[parser_name].iteritems():
                            val = value['regex'].search(line)
                            if val and val.groups:
                                for group in val.groups(key):
                                    self.parent._callback({parser_name: {key: group}}, value['mode'])
                self.parent._handler(line.strip('\n'))
                sys.stdout.flush()
            self.pipeReader.close()


    def __init__(self, parsers, match_callback, line_handler):
        self.parsers = [self.setupRE(logworm.WORMS[parser], parser)
                        for parser in parsers if parser in logworm.WORMS.keys()]
        self._callback = match_callback
        self._handler = line_handler
        self.logpipe = self.LogPipe(self, self.parsers)

    def setupRE(self, parser, name):
        re_parser = {}
        re_parser[name] = {}
        for key, value in parser.iteritems():
            re_parser[name][key] = {}
            re_parser[name][key]['regex'] = re.compile(value['regex'])
            re_parser[name][key]['mode'] = value['mode']
        return re_parser
