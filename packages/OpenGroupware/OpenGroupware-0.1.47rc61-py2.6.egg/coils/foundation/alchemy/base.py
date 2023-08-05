#
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
import pprint
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, date
from pytz import timezone

Base = declarative_base()

class CoilsORMKVCException(Exception):
    pass

class KVC(object):

    def take_values(self, values, keymap):
        if (values is None):
            raise 'Cannot take values from None'
        if (not(isinstance(values, dict))):
            values = values.__dict__
        #if (keymap is None):
        #    self.log.warn('No keymap provided to KVC')
        for key in values:
            #key = key.lower()
            (k, v) = self.translate_key(key, values[key], keymap)
            if k is not None:
                if hasattr(self, k):
                    try:
                        setattr(self, k, v)
                    except AttributeError, e:
                        raise CoilsORMKVCException('Unable to set attribute "{0}" on entity {1}'.format(k, self))

    @staticmethod
    def translate_key(key, value, keymap):
        if (keymap is None):
            return (key, value)
        key = key.lower()
        if (key in keymap):
            x = keymap[key]
            if (x is None):
                return (None, None)
            # translate key name
            key = x[0]
            # transform value type
            if (len(x) > 1):
                t = x[1]
                if (t == 'int'):
                    # Make sure value is an integer
                    if value:
                        value = int(str(value))
                    else:
                        value = None
                elif (t == 'date'):
                    # Deal with date value
                    if (value is None):
                        value = None
                    elif (isinstance(value, datetime)):
                        value = value.replace(tzinfo=timezone('UTC'))
                    elif (isinstance(value, date)):
                        value = value
                    elif (isinstance(value, basestring)):
                        if (len(value) == 0):
                            value = None
                        elif (len(value) == 10):
                            # YYYY-MM-DD
                            value = datetime(int(value[0:4]), int(value[5:7]), int(value[8:10]), tzinfo=timezone('UTC'))
                        elif ((len(value) == 16) or (len(value) == 19)):
                            # YYYY-MM-DD HH:mm [24 hour, no AM/PM crap]
                            value = datetime(int(value[0:4]), int(value[5:7]), int(value[8:10]),
                                             int(value[11:13]), int(value[14:16]), tzinfo=timezone('UTC'))
                        else:
                            raise Exception('Invalid string format for datetime conversion')
                    elif (isinstance(value, int)):
                            value = datetime.utcfromtimestamp(value)
                    else:
                        raise Exception('Unable to translate date/time value: {0}'.format(value))
                elif (t == 'csv'):
                    if (isinstance(value, list)):
                        pass
                    elif (isinstance(value, basestring)):
                        value = value.split(x[2])
                    else:
                        raise Exception('Cannot transform type to CSV value')
                    value = unicode(x[2]).join([unicode(o.strip()) for o in value])
            # default value, for None
            if (value is None):
                if (len(x) == 3):
                    value = x[2]
        return (key, value)

    @staticmethod
    def translate_dict(values, keymap):
        # TODO: Throw exception if values is not dict
        result = {}
        #pprint.pprint(values)
        for key in values:
            #print '--------------------'
            #print 'KEY: {0} {1}'.format(key, values[key])
            (k, v) = KVC.translate_key(key, values[key], keymap)
            if (k is not None):
                result[k] = v
        return result

    @staticmethod
    def subvalues_for_key(values, keys, default=[]):
        for key in keys:
            if (key in values):
                x = values[key]
                break
        else:
            x = default
        return x

    @staticmethod
    def keyed_values(values_list, key_value):
        if (not isinstance(values_list, list)):
            raise Exception('Provided values is not a list')
        elif (len(values_list) == 0):
            return { }
        else:
            # key_value may be a list, if so we pick as our key the first key
            # from the list that exists in the first entry of the list
            first = values_list[0]
            if (isinstance(key_value, list)):
                for candidate in key_value:
                    if (candidate in first):
                        key_value = candidate
                        break
                else:
                    key_value = None
            else:
                if (key_value not in first):
                    key_value = None
            if (key_value is None):
                raise Exception('No specified key value present in values')
            values = { }
            for value in values_list:
                if (key_value in value):
                    values[value[key_value]] = value
            return values
