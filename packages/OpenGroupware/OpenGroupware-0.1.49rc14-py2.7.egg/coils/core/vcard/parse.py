#
# Copyright (c) 2010, 2011, 2012 
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
import logging, vobject
from coils.core  import *
from parse_vcard import parse_vcard

class Parser(object):

    @staticmethod
    def _fix_card(data):
        data = data.strip()
        card = [ ]
        for line in data.splitlines():
            if (line[0:8] == 'PROFILE:'):
                continue
            else:
                card.append(line)
        return '\r\n'.join(card)

    @staticmethod
    def Parse(data, ctx, **params):
        log = logging.getLogger('parse')
        result = []
        #TODO: log duration of render at debug level
        if data is None:
            raise CoilsException('Attempt to parse a None')
        elif isinstance(data, basestring):
            try:
                data = Parser._fix_card(data)
                log.debug('VCARD DATA:\n\n{{{0}}}\n\n'.format(data))
                card = vobject.readOne( data )
                result.append(parse_vcard(card, ctx, log, **params))
            except Exception, e:
                log.exception(e)
                log.warn('Unable to parse vcard data into components.')
                raise e
        else:
            raise CoilsException('Non-text data received by vcard parser.')
        return result
        
    @staticmethod
    def ParseAll(data, ctx, **params):
        log = logging.getLogger('parse')
        result = []
        #TODO: log duration of render at debug level
        if data is None:
            raise CoilsException('Attempt to parse a None')
        elif isinstance(data, basestring):
            try:
                data = Parser._fix_card(data)
                #log.debug('VCARD DATA:\n\n{{{0}}}\n\n'.format(data))
                cards = vobject.readComponents( data )
                for card in cards:
                    om = parse_vcard(card, ctx, log, **params)
                    result.append( om )
            except Exception, e:
                log.exception(e)
                log.warn('Unable to parse vcard data into components.')
                raise e
        else:
            raise CoilsException('Non-text data received by vcard parser.')
        return result        
        
