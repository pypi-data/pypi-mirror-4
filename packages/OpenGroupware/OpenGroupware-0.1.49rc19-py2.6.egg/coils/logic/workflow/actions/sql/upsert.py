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
from StringIO            import StringIO
from time                import sleep
from lxml                import etree
from coils.core          import *
from coils.core.logic    import ActionCommand
from utility             import sql_connect
from command             import SQLCommand

class UpsertAction(ActionCommand, SQLCommand):
    __domain__    = "action"
    __operation__ = "sql-upsert"
    __aliases__   = [ 'sqlUpsert', 'sqlUpsertAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        db = sql_connect(self._source)
        cursor = db.cursor()
        summary = StringIO(u'')
        table_name, format_name, format_class = self._read_result_metadata(self.rfile)
        summary.write(u'Upsert target is table {0}\n'.format(table_name))
        counter = 0
        update_count = 0
        insert_count = 0
        try:
            for keys, fields in self._read_rows(self.rfile, []):
                # Parse row, building keys and fields
                if (len(keys) == 0):
                    raise CoilsException('No primary keys provided for update of SQL record.')
                # Perform SELECT based on values of keys
                sql, values = self._create_pk_select_from_keys(db, table_name, keys)
                cursor = db.cursor()
                try:
                    cursor.execute(sql, values)
                    count = len(cursor.fetchall())
                except Exception, e:
                    # TODO: Catch the more specific database exception
                    self.log_message('FAILED SQL: {0} VALUES: {1}'.format(unicode(sql), unicode(values)),
                                     category='error')
                    raise e
                finally:
                    cursor.close()
                # Perform Upsert
                if (count == 0):
                    # Insert
                    sql, values = self._create_insert_from_fields(db, table_name, keys, fields)
                    insert_count += 1
                elif (count == 1):
                    # Update
                    sql, values = self._create_update_from_fields(db, table_name, keys, fields)
                    update_count += 1
                else:
                    self.log_message('Primary key search returned more than one tuple.\n SQL: {0}\n VALUES: {1}'.\
                                        format(unicode(sql), unicode(values)),
                                     category='error')
                    raise CoilsException('Primary key search returned more than one record!')
                # TODO: Is it more efficient to re-use an existing cursor?
                cursor = db.cursor()
                try:
                    cursor.execute(sql, values)
                except Exception, e:
                    # TODO: Catch the more specific database exception
                    self.log_message('FAILED SQL: {0} VALUES: {1}'.format(unicode(sql), unicode(values)),
                                     category='error')
                    raise e
                finally:
                    cursor.close()
                # The pause
                counter += 1
                if ((counter % 1000) == 0):
                    sleep(0.5)
            if (self._commit == 'YES'):
                db.commit()
        finally:
            summary.write(u'{0} records processed.'.format(counter))
            self.log_message(summary.getvalue(), category='error')
            summary = None
            db.close()

    def parse_action_parameters(self):
        self._commit = self.action_parameters.get('commit', 'YES').upper()
        self._source = self.action_parameters.get('dataSource', None)
        self._keys   = self.action_parameters.get('primaryKeys', '').split(',')
        if (self._source is None):
            raise CoilsException('No source defined for selectAction')

    def do_epilogue(self):
        pass
        