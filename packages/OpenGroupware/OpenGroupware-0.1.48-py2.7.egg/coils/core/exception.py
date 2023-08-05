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
import sys, traceback

class CoilsException(Exception):
    def __init__(self, text):
        self.text = text
        #print 'CoilsException(%s)' % self.text
        #traceback.print_exc(file=sys.stdout)

    def __repr__(self):
        return '<CoilsException msg="%s" code=%d>' % (self.error_text(), self.error_code())

    def __str__(self):
        return self.text

    def error_text(self):
        return self.text

    def error_code(self):
        return 500

  #def stack_trace(self):
  #  return self.trace

  #def build_trace(self):
  #  return ''
  #return traceback.print_exc()

class AuthenticationException(CoilsException):
    def error_code(self):
        return 401

    def __str__(self):
        return self.text


class AccessForbiddenException(CoilsException):
    def error_code(self):
        return 403

    def __str__(self):
        return self.text


class NoSuchPathException(CoilsException):
    def error_code(self):
        return 404

    def __str__(self):
        return self.text


class NotImplementedException(CoilsException):
    def error_code(self):
        return 500

    def __str__(self):
        return self.text

class NotSupportedException(CoilsException):
    def error_code(self):
        return 501

    def __str__(self):
        return self.text
