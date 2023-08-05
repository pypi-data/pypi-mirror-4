#
# Copyright (c) 2010 Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import multiprocessing, os
from time        import time
from server      import CoilsHTTPServer
from handler     import CoilsRequestHandler
from root        import RootFolder
from coils.core  import *
import logging, logging.config

def serve_forever(server, silent=False):
    try:
        server.run(silent=silent)
    except KeyboardInterrupt:
        pass


class HTTPService(Service):
    __service__ = 'coils.http.manager'
    __auto_dispatch__ = True
    __is_worker__     = True

    def prepare(self):
        self._last_time = time()
        self._workers = { }
        Service.prepare(self)
        RootFolder.load_protocols(self.log)
        sd = ServerDefaultsManager()
        HTTP_HOST = sd.string_for_default('CoilsListenAddress', '127.0.0.1')
        HTTP_PORT = sd.integer_for_default('CoilsListenPort', 8080)
        self.log.info("Starting Server @ %s:%d" % (HTTP_HOST, HTTP_PORT))
        self._httpd = CoilsHTTPServer((HTTP_HOST, HTTP_PORT), CoilsRequestHandler)
        for i in range(15):
            pid = self.start_worker()
        try:
            self.send(Packet('coils.http/__null',
                             'coils.master/__status',
                             'HTTP/201 ONLINE'))
        except Exception, e:
            self.log.exception(e)
            sys.exit(1)

    def start_worker(self):
            p = multiprocessing.Process(target=serve_forever,
                                        args=(self._httpd,))
            p.start()
            self._workers[p.pid] = p
            self.log.info('Started HTTP worker PID#{0}'.format(p.pid))
            return p.pid

    def work(self):
        # TODO: Component check should be a time-based, not iteration based, component
        if ((time() - self._last_time) > 15):
            self._last_time = time()
            drop = [ ]
            for pid in self._workers:
                worker = self._workers[pid]
                worker.join(0.1)
                if (worker.is_alive()):
                    # TODO: provide a config option to perform a log mark for living components
                    pass
                else:
                    self.log.debug('HTTP workerId#{0} has failed'.format(pid))
                    drop.append(pid)
            if (len(drop) > 0):
                for pid in drop:
                    del self._workers[pid]
                    new_pid = self.start_worker()
                    message='HTTP workerId#{0} has failed, new workerId#{1} has been created.'.format(pid, new_pid)
                    self.log.info(message)
