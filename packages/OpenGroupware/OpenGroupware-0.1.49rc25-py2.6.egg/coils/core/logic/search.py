#
# Copyright (c) 2009, 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
from datetime         import datetime, timedelta
from dateutil.tz      import gettz
from sqlalchemy       import *
from sqlalchemy.orm   import *
from coils.core       import PropertyManager, Command, ObjectProperty, \
                              CompanyValue, Address, Telephone, \
                              CoilsException
from get              import GetCommand, \
                              RETRIEVAL_MODE_SINGLE, \
                              RETRIEVAL_MODE_MULTIPLE
from keymap      import COILS_ADDRESS_KEYMAP, COILS_TELEPHONE_KEYMAP, COILS_COMPANYVALUE_KEYMAP

class SearchCommand(Command):

    def __init__(self):
        Command.__init__(self)
        self.mode = RETRIEVAL_MODE_MULTIPLE

    def prepare(self, ctx, **params):
        self._result  = [ ]
        self._pr      = [ ]
        self._cv      = { }
        self._revolve = False
        Command.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)

        self._limit = params.get('limit', None)
        if (self._limit is None):
            self._limit = 150
        else:
            self._limit = int(self._limit)
        if ('criteria' in params):
            x = params['criteria']
            if (isinstance(x, dict)):
                x = [ x ]
            self._criteria = x
        else:
            raise CoilsException('Search requested with no criteria.')

        if (str(params.get('revolve', 'NO')).upper() in ['YES', 'TRUE']):
            self._revolve = True

    """
        Keymap Example:     'private':              ['is_private', 'int'],
                            'bossname':             ['boss_name'],
                            'managersname':         ['boss_name'],
                            'managers_name':        ['boss_name'],
                            'sex':                  ['gender'],
                            'deathdate':            ['grave_date', 'date', None],
        This translates the named key into the first value of the corresponding array.  If the
        array has a second value it is: "int" or "date" and the value is translated into the
        corresponding value type.  If the value is None and the array has a third value (a
        "default" value) then the value is replaced with the third value.  Date formats supported
        are "YYYY-MM-DD" and "YYYY-MM-DD HH:mm" where hours are in 0 - 23 not AM/PM.  All dates
        are interpreted as GMT.
    """
    def _translate_key(self, key, value, keymap):
        key = key.lower()
        if (key in keymap):
            x = keymap[key]
            # translate key name
            key = x[0]
            # transform value type
            if (len(x) > 1):
                t = x[1]
                if (t == 'int'):
                    # Make sure value is an integer
                    if (isinstance(value, basestring)):
                        value = value.replace('%', '')
                        value = value.replace('*', '')
                    try:
                        value = int(value)
                    except Exception, e:
                        self.log.exception(e)
                        raise CoilsException('Unable to convert search value to integer.')
                elif (t == 'date'):
                    # Deal with date value
                    if (not (isinstance(value, datetime))):
                        # Translate string to datetime
                        if (isinstance(value, basestring)):
                            if (len(value) == 10):
                                # YYYY-MM-DD
                                value = datetime(int(value[0:4]), int(value[5:7]), int(value[8:10]))
                            elif (len(value) == 16):
                                # YYYY-MM-DD HH:mm [24 hour, no AM/PM crap]
                                value = datetime(int(value[0:4]), int(value[5:7]), int(value[8:10]),
                                                 int(value[11:13]), int(value[14:16]))
                            else:
                                raise CoilsException('Invalid string format for datetime conversion')
                        elif (isinstance(value, int)):
                            value = dateime.utcfromtimestamp(value)
                    # set timezone to UTC
                    value.replace(tzinfo=gettz('UTC'))
            # default value, for None
            if ((len(x) == 3) and (value is None)):
                value = x[2]
        else:
            self.log.debug('key {0} not found in entity keymap'.format(key))
        return (key, value)

    def _form_expression(self, attribute, expression, value):
        if (expression == 'ILIKE'):
            return (attribute.ilike(value))
        elif (expression == 'LIKE'):
            return (attribute.like(value))
        elif (expression == 'NOTEQUALS'):
            return (attribute != value)
        elif (expression == 'GT'):
            return (attribute > value)
        elif (expression == 'LT'):
            return (attribute < value)
        else:
            return (attribute == value)

    def _translate_criterion(self, criterion, entity, keymap):
        """ Translates a criterion in the corresponding ORM components """
        # Returns Entity, Key, Conjunction, Expression
        v = criterion.get('value', None)
        try:
            k = criterion['key'].split('.')
        except KeyError:
            raise CoilsException('Critia does not specify a key: {0}'.format(criterion))
        # Everything after the first "." needs to be reassembled as the
        # second element, at most we should see a two element list.
        # Property names possibly [ likely ] contain "." characters.
        if (len(k) > 1):
            k[1] = '.'.join(k[1:])
            k = k[0:2]
        c = criterion.get('conjunction', 'AND').upper()
        e = criterion.get('expression', 'EQUALS').upper()
        if (e not in ('EQUALS', 'ILIKE', 'LIKE', 'NOTEQUALS', 'GT', 'LT')):
            return (None, None, None, None, None)
        if (len(k) == 1):
            k = k[0]
            (k, v) = self._translate_key(k, v, keymap)
            if (hasattr(entity, k)):
                return (entity, k, v, c, e)
            elif (hasattr(entity, 'company_values')):
                # company value
                return (CompanyValue, k, v, c, e)
        elif (len(k) == 2):
                # address or telephone
                if (hasattr(entity, 'addresses') and (k[0].lower() in ['address'])):
                    k = k[1]
                    (k, v) = self._translate_key(k, v, COILS_ADDRESS_KEYMAP)
                    if (k is not None):
                        return (Address, k, v, c, e)
                elif (hasattr(entity, 'telephones') and (k[0].lower() in ['phone', 'telephone'])):
                    k = k[1]
                    (k, v) = self._translate_key(k, v, COILS_TELEPHONE_KEYMAP)
                    if (k is not None):
                        return (Telephone, k, v, c, e)
                elif (k[0].lower() in ['property']):
                    if (hasattr(entity, 'properties')):
                        return (ObjectProperty, k[1], v, c, e)
                    else:
                        self.log.warn('Client issued property search criteria on entity {0} '\
                                      'that does not support properties.'\
                            .format(entity))
                        return (None, None, None, None, None)
        # TODO: Provide a default to raise an exception in this case
        self.log.warn('Client issued unknown key {0} in search criteria; discarding.'.format('.'.join(k)))
        return (None, None, None, None, None)

    def _aggregate_criterion(self, aggregation, criterion, entity, keymap):
        # entity, key, value, conjunction, expression
        (E, k, v, c, e) = self._translate_criterion(criterion, entity, keymap)
        if (E is not None):
            if (E not in aggregation):
                aggregation[E] = { }
            if (k not in aggregation[E]):
                aggregation[E][k] = { 'AND': [], 'OR': [] }
            # If the value is an integer and the user attempted a LIKE / ILIKE
            # expression we turn the expression into an EQUALS to avoid an error
            # Also change to equals if it is a GT or LT comparison and the value is not-numeirc
            if (isinstance(v, int) and e in ('LIKE', 'ILIKE')):
                self.log.warn('Client attempted LIKE/ILIKE on numeric attribute "{0}", changing to EQUALS'.format(k))
                e = 'EQUALS'
            elif ((not ((isinstance(v, int)) or isinstance(v, float))) and e in ('GT', 'LT')):
                self.log.warn('Client attempted GT/LT on non-numeric attribute "{0}", changing to EQUALS'.format(k))
                e = 'EQUALS'
            aggregation[E][k][c].append((e, v))
        else:
            self.log.warn('Client search criteria invalid & discarded.')
        return aggregation

    def _parse_criteria(self, criteria, entity, keymap):
        """ Compiles criteria in an ORM query """
        #TODO: Support object properties
        aggregate = { }
        # Compile the criteria
        if not isinstance(criteria, list):
            raise CoilsException('Criteria specification of type "{0}" is not understood.'.format(type(criteria)))
        for criterion in criteria:
            # Entity, key, value, conjunction, expression
            if 'clause' in criterion:
                sub_aggregate = { }
                for clause in criterion['clause']:
                    sub_aggregate = self._aggregate_criterion(sub_aggregate, clause,  entity, keymap)
            else:
                aggregate = self._aggregate_criterion(aggregate, criterion,  entity, keymap)
        db = self._ctx.db_session()
        query = db.query( entity ).with_labels( )
        _and = and_( )
        _or  = or_( )
        # TODO [URGENT!] - Support 'clause' structures
        for E in aggregate:
            if (E == entity):
                for k in aggregate[E]:
                    for e, v in aggregate[E][k]['AND']:
                        _and.append(self._form_expression(getattr(entity, k), e, v))
                    for e, v in aggregate[E][k]['OR']:
                        _or.append(self._form_expression(getattr(entity, k), e, v))
            elif (E == CompanyValue):
                # Join for ObjectProperty criteria
                for k in aggregate[E]:
                    t = aliased(CompanyValue)
                    inner_and = and_()
                    inner_and.append(t.name == k)
                    inner_or  = or_()
                    for e, v in aggregate[E][k]['AND']:
                        inner_and.append(self._form_expression(t.string_value, e, v))
                    for e, v in aggregate[E][k]['OR']:
                        inner_or.append(self._form_expression(t.string_value, e, v))
                    if (len(inner_or) > 0):
                         inner_and.append(inner_or)
                    _and.append(inner_and)
                    query = query.join(t)
            elif (E == ObjectProperty):
                # Join for ObjectProperty criteria
                for k in aggregate[E]:
                    (namespace, name) = PropertyManager.Parse_Property_Name(k)
                    t = aliased(ObjectProperty)
                    inner_and = and_()
                    inner_and.append(t.name == name)
                    inner_and.append(t.namespace == namespace)
                    inner_or  = or_()
                    for e, v in aggregate[E][k]['AND']:
                        if (isinstance(v, int)):
                            inner_and.append(self._form_expression(t._integer_value, e, v))
                        else:
                            inner_and.append(self._form_expression(t._string_value, e, v))
                    for e, v in aggregate[E][k]['OR']:
                        if (isinstance(v, int)):
                            inner_or.append(self._form_expression(t._integer_value, e, v))
                        else:
                            inner_or.append(self._form_expression(t._string_value, e, v))
                    if (len(inner_or) > 0):
                         inner_and.append(inner_or)
                    _and.append(inner_and)
                    query = query.join(t)
            else:
                for k in aggregate[E]:
                    for e, v in aggregate[E][k]['AND']:
                        _and.append(self._form_expression(getattr(E, k), e, v))
                    for e, v in aggregate[E][k]['OR']:
                         _or.append(self._form_expression(getattr(E, k), e, v))
                query = query.join(E)
        if (len(_or) > 0):
            if (len(_and) > 0):
                _or.append(_and)
            query = query.filter(_or)
        elif (len(_and) > 0):
            query = query.filter(_and)
        #query = query.limit(self._limit)
        # Log query
        self.log.debug('SQL: {0}'.format(query.statement))
        return query

    def do_revolve(self):
        return [ ]

    def set_return_value(self, data):
        if (isinstance(data, list)):
            if (self.access_check):
                data = self._ctx.access_manager.filter_by_access('r', data, contexts=self.context_ids)
            if (len(data) > 0):
                if (self.mode == RETRIEVAL_MODE_SINGLE):
                    self._result = data[0]
                else:
                    if (len(data) > self._limit):
                        data = data[0:self._limit]
                    self._result = data
                    if (self._revolve):
                        self._result.extend(self.do_revolve())
            elif (self.mode == RETRIEVAL_MODE_MULTIPLE):
                self._result = [ ]
            elif (self.mode == RETRIEVAL_MODE_SINGLE):
                self._result = None
            else:
                raise CoilsException('Unknown mode value')
            return
        raise CoilsException('Data for Get result is not a list')
        self._result = None
