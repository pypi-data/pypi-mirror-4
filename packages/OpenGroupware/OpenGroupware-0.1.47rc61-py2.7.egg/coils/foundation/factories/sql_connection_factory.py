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
import logging
from coils.foundation.defaultsmanager import ServerDefaultsManager

class SQLConnectionFactory(object):
    _classes = None

    @staticmethod
    def Init():
        log = logging.getLogger('OIE')
        SQLConnectionFactory._classes = {}
        # Informix
        try:
            import informixdb
        except:
            log.info('Unable to load Informix support')
        else:
            log.info('Informix support loaded')
            from informix_connection import InformixConnection
            SQLConnectionFactory._classes['informix'] = InformixConnection
        try:
            import psycopg2
        except:
            log.info('Unable to load PostgreSQL support')
        else:
            log.info('PostgreSQL support loaded')
            from postgres_connection import PostgresConnection
            SQLConnectionFactory._classes['postgres'] = PostgresConnection

    @staticmethod
    def Connect(source):
        if (SQLConnectionFactory._classes is None):
            SQLConnectionFactory.Init()
        log = logging.getLogger('OIE')
        sd = ServerDefaultsManager()
        config = sd.default_as_dict('OIESQLSources')
        if (source in config):
            config = config.get(source)
            try:
                driver = SQLConnectionFactory._classes.get(config.get('driver'))
                connection = driver(config)
            except Exception, e:
                log.exception(e)
                log.error('Unable to provide connection to source name {0}'.format(source))
                return None
            else:
                return connection
        else:
            log.error('No source defined with name {0}'.format(source))
            return None
