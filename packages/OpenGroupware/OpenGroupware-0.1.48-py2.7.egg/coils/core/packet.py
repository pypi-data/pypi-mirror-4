#!/usr/bin/python
# Copyright (c) 2009 Adam Tauno Williams <awilliam@whitemice.org>
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
from uuid           import uuid4
from time           import time
from exception      import CoilsException

class Packet(object):
    def __init__(self, source, target, data, qos=None, auth=None, kind=None):
        self._source    = source
        self._target    = target
        self._data      = data
        self._uuid      = '{{{0}}}'.format(str(uuid4()))
        self._reply_to  = None
        self._qos       = None
        self._auth      = None
        self._time      = float(time())
        if (kind is None):
            self._kind = 'application/x-pickle-ascii.python'
        else:
            self._kind = kind

    def __repr__(self):
        return '<Packet source="{0}" target="{1}" UUID="{2}"/>'.format(self.source, self.target, self.uuid)

    @property
    def data(self):
        return self._data

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        self._source = value

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, value):
        self._target = value        

    @property
    def uuid(self):
        return self._uuid

    @property
    def reply_to(self):
        return self._reply_to

    @property
    def time(self):
        return self._time

    @staticmethod
    def Reply(packet, data):
        m = Packet(packet.target, packet.source, data)
        m._reply_to = str(packet.uuid)
        return m

    @staticmethod
    def Service(name):
        if name is None:
            raise CoilsException('Request for service from NULL address')
        return name.split('/')[0].lower()

    @staticmethod
    def Method(name):
        if name is None:
            raise CoilsException('Request for method from NULL address')
        return name.split('/')[1].split(':')[0]

    @staticmethod
    def Parameter(name):
        if name is None:
            raise CoilsException('Request for parameter from NULL address')
        x = name.split('/')[1].split(':')
        if (len(x) > 1):
            return x[1]
        else:
            return None
