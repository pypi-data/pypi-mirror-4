# Copyright (c) 2012 
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

from render_object import as_string, as_integer, as_datetime

def render_lock(entity, detail, ctx, favorite_ids=None):
    """ { 'operations': 'dwx',
          'exclusive': 'YES' | 'NO',
          'objectId': 54720,
          'entityName': 'lock',
          'targetEntityName': 'Contact',
          'token': '' } """
          
    lock = { 'entityName':       'lock',
             'targetObjectId':   as_integer( entity.object_id ),
             'operations':       as_string( entity.operations ),
             'exclusive':        'YES' if entity.exclusive == 'Y' else 'NO',
             'targetEntityName': as_string( ctx.type_manager.get_type( entity.object_id ) ),
             'token':            as_string( entity.token ),
             'granted':          as_integer( entity.granted ),
             'expires':          as_integer( entity.expires ) }
             
    return lock
