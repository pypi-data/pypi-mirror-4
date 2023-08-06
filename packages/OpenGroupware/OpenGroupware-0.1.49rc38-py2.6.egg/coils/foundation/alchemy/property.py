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
from datetime     import datetime,date,tzinfo
from sqlalchemy   import *
from utcdatetime  import UTCDateTime, UniversalTimeZone
from base         import *


class ObjectProperty(Base):
    """ An OpenGroupware Property Object """
    __tablename__ = 'obj_property'
    __entityName__       = 'objectProperty'
    __internalName__     = 'ObjectProperty'
    object_id       = Column("obj_property_id",
                              Integer,
                              Sequence('key_generator'),
                              primary_key=True)
    parent_id       = Column("obj_id", Integer,
                              ForeignKey('person.company_id'),
                              ForeignKey('enterprise.company_id'),
                              ForeignKey('date_x.date_id'),
                              ForeignKey('job.job_id'),
                              ForeignKey('project.project_id'),
                              ForeignKey('doc.document_id'),
                              ForeignKey('route.route_id'),
                              ForeignKey('process.process_id'),
                              ForeignKey('company_value.company_value_id'),
                              nullable=False)
    namespace      = Column("namespace_prefix", String(255), nullable=False)
    name           = Column("value_key", String(255), nullable=False)
    _string_value  = Column("value_string", String(255))
    _date_value    = Column("value_date", UTCDateTime())
    _integer_value = Column("value_int", Integer)
    _float_value   = Column("value_float", Float)
    _oid_value     = Column("value_oid", String(255))
    _blob_value    = Column("value_blob", Text)
    _blob_size     = Column("blob_size", Integer)
    _data_hint     = Column("preferred_type", String(255))
    kind           = 1
    label          = ''
    values         = []
    access_id      = Column("access_key", Integer)

    def __init__(self, object_id, name, value=None, access_id=None):
        # TODO: parse name into namespace & name
        self.parent_id = object_id
        (self.namespace, self.name) = ObjectProperty.Parse_Property_Name(name)
        self.set_value(value)
        self.access_id = access_id

    def __repr__(self):
        return '<ObjectProperty parentId={0} namespace="{1}" name="{2}">'.\
                format(self.parent_id, self.namespace, self.name)

    @staticmethod
    def get_preferred_kinds():
        return ['valueString', 'valueInt', 'valueFloat',
                 'valueDate', 'valueOID', 'valueBlob' ]

    @staticmethod
    def Parse_Property_Name(name):
        """ Takes a full formally formed property name and splits it into
            namespace and attribute.
            For example:
                {http://www.example.com/properties/ext-attr}skyColor
                - returns -
               ('http://www.example.com/properties/ext-attr', 'skyColor')
            DO NOT PARSE PROPERTY NAMES YOURSELF, USE THIS METHOD! """
        x = name.split('}')
        return (x[0][1:], x[1])

    def get_value(self):
        hint = self.get_hint()
        # Default to using the string value
        if (hint is None):
            hint = 'string'
        elif (self._data_hint not in ObjectProperty.get_preferred_kinds()):
            hint = 'string'
        # Return
        if (hint == 'string'):
            if self._blob_value:
                return self._blob_value
            return self._string_value
        elif (hint in ('timestamp')):
            return self._date_value
        elif (hint == 'int'):
            return self._integer_value
        elif (hint == 'float'):
            return self._float_value
        elif (hint == 'oid'):
            return self._oid_value
        elif (hint == 'data'):
            # TODO: Support OID properties
            # Should we UUDECODE here or let the client do it?
            raise 'Unsupported property type encountered, patches welcome.'
        else:
            return self._string_value

    def set_value(self, x):
        """ Store the value in the appropriate field(s) and hint for next time
            the value is retrieved: we get back the type we stored."""
         # TODO: What to do with OID value?
        if (x is None):
            # NOTE: We do not change the data type hint when null-ing.
            self._string_value = None
            self._integer_value = None
            self._date_value = None
            self._float_value = None
            # TODO: What to do with OID value?
            self._oid_value = None
            self._blob_value = None
        elif (isinstance(x, basestring)):
            try:
                self._integer_value = int(x)
            except:
                self._integer_value = None
            #TODO: Can this string be converted to a data?
            self._date_value = None
            try:
                self._float_value = int(x)
            except:
                self._float_value = None
            # TODO: What to do with OID value?
            self._oid_value = None
            if len(x) > 254:
                # Long strings get stashed in the BLOB field and the string
                # value is truncated;  when the value is read and the hint is
                # string the BLOB value will be returned instead of the string
                # value - so all this should be automatic.
                self._blob_value = x
                self._blob_size = len(x)
                self._string_value = x[:255] # Truncate to 255 characters
            else:
                # Make sure we NULL the BLOB value for short strings
                self._string_value = x
                self._blob_value = None
            # TODO: A set_hint method would be better than this
            self._data_hint = 'valueString'
        elif (isinstance(x, int) or isinstance(x, long)):
            self._string_value = str(x)
            self._integer_value = x
            #TODO: Can this integer be converted to a data?
            #      Make a u time value
            self._date_value = None
            self._float_value = x
            self._oid_value = None
            self._blob_value = None
            # TODO: A set_hint method would be better than this
            self._data_hint = 'valueInt'
        elif (isinstance(x, float)):
            self._string_value = str(x)
            self._integer_value = int(x)
            self._date_value = None
            self._float_value = x
            self._oid_value = None
            self._blob_value = None
            # TODO: A set_hint method would be better than this
            self._data_hint = 'valueFloat'
        elif (isinstance(x, datetime)):
            if not x.tzinfo:
                x = x.replace(tzinfo=UniversalTimeZone())
            x = x.astimezone(UniversalTimeZone())
            self._string_value = x.strftime('%Y-%m-%d %H:%M:%S')
            self._integer_value = x.toordinal()
            self._date_value = x
            self._float_value = float(self._integer_value)
            self._oid_value = None
            self._blob_value = None
            # TODO: A set_hint method would be better than this
            self._data_hint = 'valueDate'
        elif (isinstance(x, date)):
            x = datetime(x.year, x.month, x.day, tzinfo=UniversalTimeZone())
            self._string_value = x.strftime('%Y-%m-%d')
            self._integer_value = x.toordinal()
            self._date_value = x
            self._float_value = float(self._integer_value)
            self._oid_value = None
            self._blob_value = None
            # TODO: A set_hint method would be better than this
            self._data_hint = 'valueDate'
        else:
            #TODO: Store OID valudes ????
            #TODO: Store BLOB values.  What is the Python type for raw data?
            #      BLOB values should be stored Base64 encoded
            #TODO: Detect a "byte" type for storing BLOBs
            raise Exception('Property value of type {0} cannot be preserved for property {1}/{2}'.format(type(x).__name__, self.namespace, self.name))

    def get_hint(self):
        if (self._data_hint is None):
            return 'unknown'
        elif (self._data_hint == 'valueString'):
            return 'string'
        elif (self._data_hint == 'valueDate'):
            return 'timestamp'
        elif (self._data_hint == 'valueInt'):
            return 'int'
        elif (self._data_hint == 'valueFloat'):
            return 'float'
        elif (self._data_hint == 'valueOID'):
            return 'oid'
        elif (self._data_hint == 'valueBlob'):
            return 'data'
        else:
            return 'unknown'
