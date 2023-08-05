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
#
import informixdb
from sql_connection import SQLConnection

class InformixConnection(SQLConnection):

    def __init__(self, params):
        self._db = informixdb.connect(params.get('url'),
                                      params.get('username'),
                                      params.get('password'))

    def connect(self):
        return self._db

    def cursor(self):
        return self._db.cursor()

    def get_type_from_code(string, code):
        if (code == 'serial'):
            return 'integer'
        elif (code == 'string'):
            return 'string'
        elif (code == 'integer'):
            return 'integer'
        elif (code == 'float'):
            return 'float'
        elif (code == 'decimal'):
            return 'decimal'
        elif (code == 'smallint'):
            return 'integer'
        elif (code == 'char'):
            return 'string'
        elif (code == 'varchar'):
            return 'string'
        elif (code == 'date'):
            return 'date'
        elif (code == 'datetime'):
            return 'datetime'
        else:
            return 'unknown'