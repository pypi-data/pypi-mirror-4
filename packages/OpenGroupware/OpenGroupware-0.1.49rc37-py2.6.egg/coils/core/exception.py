#!/usr/bin/python
# Copyright (c) 2009, 2013
#   Adam Tauno Williams <awilliam@whitemice.org>
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

class CoilsException(Exception):
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return '<CoilsException msg="{0]" code={1}/>'.format( self.error_text(), self.error_code( ) )

    def __str__(self):
        return self.text

    def error_text(self):
        return self.text

    def error_code(self):
        return 500


class CoilsDateFormatException(CoilsException):
    '''
    Exception raised when the server cannot parse a non-date/non-datetime
    type as a datetime value; for example, when attempting to convert a
    string value to a datetime.
    '''

    def __repr__(self):
        return '<CoilsDateFormatException msg="{0}" code={1}>/>'.format( self.error_text(), self.error_code( ) )


class InsufficientParametersException(CoilsException):
    '''
    Exception raised by OpenGroupware Logic commands when insufficient parameters have
    been provided to prepare the Command class for operation.
    '''

    def error_code(self):
        return 400

    def __repr__(self):
        return '<InsufficientInputException msg="{0}" code={1}>'.format( self.error_text( ), self.error_code( ) )


class AuthenticationException(CoilsException):
    '''
    Exception raised when an authentication attempt fails
    '''
    def error_code(self):
        return 401

    def __str__(self):
        return self.text


class AccessForbiddenException(CoilsException):
    '''
    Exception raised when an operation attempts to use an object in a manner for
    which it has insufficient privileges.
    '''
    def error_code(self):
        return 403

    def __str__(self):
        return self.text


class NoSuchPathException(CoilsException):
    '''
    Exception raised when an operation attempts to access an object at a path
    and the target of the path cannot be discovered.
    '''
    def error_code(self):
        return 404

    def __str__(self):
        return self.text


class NotImplementedException(CoilsException):
    '''
    Exception raised when an operation attempts to perform some action or
    sub-action which has not yet been implemented. This exception differs
    from NotSupportedException as this exception indicates a deficiency
    in the server's implementation;  a NotImplementedException should only
    be raised in the case where it is a RoadMap target to implement the
    feature or a standards document specifies a feature as explicitly
    option, but it would be possible to implement that feature on top of
    the OpenGroupware data model.
    '''
    def error_code(self):
        return 501

    def __str__(self):
        return self.text

class NotSupportedException(CoilsException):
    '''
    Exception raised when an operation attempts to perform some action or
    sub-action which is not supported;  this differs from the
    NotImplementedException in that this exception implies the lack
    of implementation of the requested operation is intentional, it may
    not be desirable or possible given the server's mode, configuration,
    or data model.
    '''

    def error_code(self):
        return 501

    def __str__(self):
        return self.text


class CoilsBusException(CoilsException):
    '''
    Exception raised when a AMQ communication error occurs in the inter-
    communication of OpenGroupware Coils service components.
    '''
    def error_code(self):
        return 500

    def __str__(self):
        return self.text
