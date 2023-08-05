#
# Copyright (c) 2009, 2011, 2012
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
#

ASSOCIATIVE_KEYS = { '_ADDRESSES':     'type',
                     '_COMPANYVALUES': 'attribute',
                     '_PHONES':        'type',
                     '_PROPERTIES':    'propertyName' }

def disassociate_omphalos_representation(data):
    ''' Receive an Omphalos representation, or list of representations, and dissacociate the
        associated keys of the value of that key is a dictionary rather than a list. '''

    def _disassociate_representation(_data):
        ''' For an associative user-agent these keys are turned into dictionaries,
            when we get data back from such a client we need to make sure we
            flatten the values back to an unassociated value (a list)'''
        if not isinstance( _data, dict ):
            return _data
        tmp = { }
        for key in _data:
            if key in ASSOCIATIVE_KEYS:
                if isinstance( _data[key], dict ):
                    tmp[ key ] = _data[ key ].values( )
                else:
                    tmp[ key ] = _data[ key ]
            else:
                tmp[ key ] = _data[ key ]
        return tmp

    if isinstance( data, list ) or isinstance( data, tuple ):
        return [ _disassociate_representation( x ) for x in data ]
    if isinstance( data, dict ):
        return _disassociate_representation( data )
    else:
        return data

def associate_omphalos_representation(data):
    ''' Receive an Omphalos representation, or list of representations, and associate the
        associate-able keys of the value turning the list into a dictionary '''

    def _associate_representation( _data ):
        if not isinstance( _data, dict ):
            return _data
        tmp = { }
        for key in _data:
            if key in ASSOCIATIVE_KEYS:
                tmp[ key ] = { }
                for sub in _data[ key ]:
                    tmp[ key ][ sub[ ASSOCIATIVE_KEYS[ key ] ] ] = sub
            else:
                tmp[ key ] = _data[ key ]
        return tmp

    if isinstance( data, list ):
        return [ _associate_representation( x ) for x in data ]
    if isinstance( data, dict ):
        return _associate_representation( data )
    else:
        return data
