#
# Copyright (c) 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
#
class PerformanceLog(object):

    def __init__(self):
        self._data = { }

    @property
    def data(self):
        return self._data

    def clear(self):
        self._data = { }

    def insert_record(self, lname, oname, runtime=0.0, error=False):
        runtime = round(runtime, 4)
        if lname not in self.data:
            self.data[lname] = { }
        if oname not in self.data[lname]:
            self.data[lname][oname] = { 'total': runtime,
                                        'counter': 1,
                                        'errors': 0,
                                        'max': runtime,
                                        'min': runtime }
        else:
            self.data[lname][oname]['counter'] += 1
            self.data[lname][oname]['total'] += runtime
            if (error):
                self.data[lname][oname]['errors'] += 1
            elif (runtime > self.data[lname][oname]['max']):
                self.data[lname][oname]['max'] = runtime
            elif (runtime < self.data[lname][oname]['min']):
                self.data[lname][oname]['min'] = runtime
