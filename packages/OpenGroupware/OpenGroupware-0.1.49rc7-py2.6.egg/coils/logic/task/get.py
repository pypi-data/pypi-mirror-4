#!/usr/bin/env python
# Copyright (c) 2010, 2012
#  Adam Tauno Williams <awilliam@whitemice.org>
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
from sqlalchemy       import *
from coils.foundation import *
from coils.core       import *
from coils.core.logic import *

class GetTask(GetCommand):
    __domain__ = "task"
    __operation__ = "get"

    def parse_parameters(self, **params):
        GetCommand.parse_parameters( self, **params )
        if 'uid' in params or 'href' in params:
            self._uid  = unicode( params.get( 'uid', None ) )
            self._href = unicode( params.get( 'href', None ) )
            if not self._href: self._href = self._uid
            if not self._uid:  self._uid = self._href
            self.set_single_result_mode( )
        else:
            self._uid = None
                
    def run(self, **params):
        db = self._ctx.db_session( )

        query = db.query( Task ).with_labels( )
        if self._uid:
            _or = or_( Task.href == self._href, Task.uid == self._uid )
            if self.object_ids: 
                _or = _or( _or, Task.object_id.in_( self.object_ids ) )
            query = query.filter(_or)
        else:
            query = query.filter( Task.object_id.in_( self.object_ids ) )
        self.set_return_value( query.all( ) )
