#
# Copyright (c) 2010, 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
import base64
from coils.core          import *
from coils.core.logic    import ActionCommand
from utility             import sql_connect

FIELD_OUT_FORMAT = u'<{0} dataType=\"{1}\" isPrimaryKey=\"{2}\" isBase64=\"{3}\" isNull=\"false\">{4}</{0}>'
NULL_FIELD_OUT_FORMAT = u'<{0} dataType=\"{1}\" isPrimaryKey=\"false\" isNull=\"true\"/>'

class SelectAction(ActionCommand):
    __domain__    = "action"
    __operation__ = "sql-select"
    __aliases__   = [ 'sqlSelectAction', 'sqlSelect' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        # TODO: Log the number of records selected to the logger service
        db = sql_connect(self._source)
        cursor = db.cursor()
        cursor.execute(self._query)
        self.wfile.write(u'<?xml version="1.0" encoding="UTF-8"?>')
        self.wfile.write(u'<ResultSet formatName=\"_sqlselect_\" className=\"\" tableName=\"{0}\">'.\
            format(self._table))
        record = cursor.fetchone()
        description = []
        #self.log.error(str(cursor.description))
        for x in cursor.description:
            description.append([x[0], x[1]])
        counter = 0
        while ((record is not None) and
               ((counter < self._limit) or (self._limit == -1))):
            self.wfile.write(u'<row>')
            for i in range(0, len(record)):
                is_base64 = False
                name = description[i][0].lower()
                kind = db.get_type_from_code(description[i][1])
                if (kind == 'binary'):
                    is_base64 = True
                    value = base64.encodestring(record[i])
                elif (isinstance(record[i], basestring)):
                    try:
                        value = record[i].decode(self._codepage).encode('utf-8', 'ignore')
                        value = self.encode_text(record[i])
                    except Exception, e:
                        # TODO: How should this be logged? To the log file or to the logger service?
                        self.log.error('Unable to convert value of field {0} to UTF-8 string, using base64 encoding'.format(name))
                        self.log.exception(e)
                        is_base64 = True
                        value = base64.encodestring(record[i])
                elif record[i] is not None:
                    value = record[i]
                else:
                    value = None
                is_key = (name in self._keys)
                if (value is None):
                    if (is_key):
                        raise CoilsException('NULL Primary Key value detected.')
                    self.wfile.write(NULL_FIELD_OUT_FORMAT.format(name.lower(),
                                                                   kind.lower()))
                else:
                    self.wfile.write(FIELD_OUT_FORMAT.format(name.lower(),
                                                              kind.lower(),
                                                              str(is_key).lower(),
                                                              str(is_base64).lower(),
                                                              value))

            self.wfile.write(u'</row>')
            record = cursor.fetchone()
            counter += 1
        self.wfile.write(u'</ResultSet>')
        description = None
        cursor.close()
        db.close()

    def parse_action_parameters(self):
        self._source   = self.action_parameters.get('dataSource', None)
        self._query    = self.action_parameters.get('queryText', None)
        self._limit    = int(self.action_parameters.get('limit', 150))
        self._table    = self.action_parameters.get('tableName', '_undefined_')
        self._keys     = self.action_parameters.get('primaryKeys', '').split(',')
        self._codepage = self.action_parameters.get('codepage', 'utf-8')
        if (self._source is None):
            raise CoilsException('No source defined for selectAction')
        if (self._query is None):
            raise CoilsException('No query defined for selectAction')
        else:
            self._query = self.decode_text(self._query)
            self._query = self.process_label_substitutions(self._query)

    def do_epilogue(self):
        pass
        
