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
import psycopg2
from sql_connection import SQLConnection

class PostgresConnection(SQLConnection):

    def __init__(self, params):
        self._db = psycopg2.connect(database = params.get('database', None),
                                    host     = params.get('hostname', '127.0.0.1'),
                                    user     = params.get('username', ''),
                                    password = params.get('password', ''))

    def connect(self):
        return self._db

    def cursor(self):
        return self._db.cursor()

    def bind_param(self, offset):
        return '%s'

    def get_type_from_code(string, code):
        if (code == psycopg2.STRING):
            return 'string'
        elif (code == psycopg2.BINARY):
            return 'binary'
        elif (code == psycopg2.DATETIME):
            return 'datetime'
        elif (code == psycopg2.extensions.DATE):
            return 'date'
        elif (code == psycopg2.extensions.FLOAT):
            return 'float'
        elif (code == psycopg2.extensions.INTEGER):
            return 'integer'
        elif (code == psycopg2.extensions.UNICODE):
            return 'string'
        else:
            return 'unknown'
