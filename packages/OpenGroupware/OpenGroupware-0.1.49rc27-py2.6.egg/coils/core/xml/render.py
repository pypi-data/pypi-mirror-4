#
# Copyright (c) 2010, 2012, 2013
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
import logging, StringIO, traceback
from datetime                   import datetime, date
from coils.foundation.api       import elementflow
from coils.core                 import *
from coils.core.omphalos        import Render as Omphalos


class Render(object):

    @staticmethod
    def open_stream(wfile, indent=False ):
        namespaces = { '': 'http://www.opengroupware.us/model' }
        return elementflow.xml(wfile, u'ResultSet', namespaces=namespaces, indent=indent )

    @staticmethod
    def render_entity(entity, ctx, detail_level, container):
        if detail_level is None: detail_level = 65503
        try:
            with container.container( u'entity',
                                      attrs={ u'entityname': entity.__entityName__,
                                              u'objectid':   unicode( entity.object_id ) } ) as container:
                Render._render_entity( entity, ctx, xml=container, detail_level=detail_level )
        except UnicodeDecodeError, e:
            ctx.send_administrative_notice(
                subject='Unicode error serializing OGo#{0} [{1}]'.format( entity.object_id, entity.__entityName__ ),
                category='unicode',
                message='{0}\n{1}\n'.format( e, traceback.format_exc( ) ) )
            raise e

    @staticmethod
    def close_stream(stream):
        stream.close( )

    @staticmethod
    def render(entity, ctx, detail_level=None, stream=None):

        if detail_level is None: detail_level = 65503

        if stream:
            stringify_result = False
        else:
            stream = StringIO.StringIO()
            stringify_result = True

        namespaces = { '': 'http://www.opengroupware.us/model' }

        if isinstance(entity, list):

            with elementflow.xml(stream, u'ResultSet', namespaces=namespaces ) as xml:

                for x in entity:

                    with xml.container(u'entity', attrs={ u'entityname': x.__entityName__,
                                                          u'objectid':   unicode(x.object_id) } ):
                        Render._render_entity(x, ctx, xml=xml, detail_level=detail_level)

        else:

            with elementflow.xml(stream, u'entity', attrs={ u'entityname': entity.__entityName__,
                                                            u'objectid':   unicode(entity.object_id) },
                                                    namespaces=namespaces ) as xml:
                Render._render_entity(entity, ctx, xml=xml, detail_level=detail_level)

        if stringify_result:
            data = stream.getvalue()
            stream.close()
            return data
        else:
            return None

    @staticmethod
    def _render_entity(entity, ctx):
        Render.render(entity, ctx, {})

    @staticmethod
    def _render_entity(entity, ctx, detail_level=65503, xml=None):

        def render_value(xml, value):
            if isinstance(value, list):
                with xml.container('value', attrs={ u'datatype': u'list' } ):
                    for entry in value:
                        with xml.container('item'):
                            render_value(xml, entry)
            elif isinstance(value, dict):
                with xml.container('value', attrs={ u'datatype': u'dict' } ):
                    for k, v in value.items():
                        render_key_value(xml, k, v)
            elif (isinstance(value, datetime)):
                with xml.container('value', attrs={ u'datatype': u'datetime' } ):
                    xml.text(value.strftime(u'%Y-%m-%dT%H:%M:%s'))
            elif (isinstance(value, date)):
                with xml.container('value', attrs={ u'datatype': u'date' } ):
                    xml.text(value.strftime(u'%Y-%m-%d'))
            elif (isinstance(value, basestring)):
                if value:
                    with xml.container('value', attrs={ u'datatype': u'string' } ):
                        xml.text(unicode(value))
            elif (isinstance(value, int)):
                with xml.container('value', attrs={ u'datatype': u'integer' } ):
                    xml.text(unicode(value))
            elif isinstance( value, float ):
                with xml.container( 'value', attrs={ u'datatype': u'float' } ):
                    xml.text( unicode( value ) )
            elif not value:
                pass

        def render_key_value(xml, key, value):
            key = key.lower( )
            key = key if not key.isdigit() else 'id{0}'.format( key )
            if isinstance( value, list ):
                with xml.container( key, attrs={ u'datatype': u'list' } ):
                    for entry in value:
                        with xml.container( 'item' ):
                            render_value( xml, entry )
            elif isinstance( value, dict ):
                with xml.container( key ):
                    for k, v in value.items( ):
                        render_key_value( xml, k, v )
            elif isinstance( value, basestring ):
                xml.element( key, text=unicode( value ), attrs={ u'dataType': u'string' } )
            elif ( isinstance( value, int ) or isinstance( value, long ) ):
                xml.element( key, text=unicode( value ), attrs={ u'dataType': u'integer' } )
            elif isinstance( value, datetime ):
                xml.element( key, text=value.strftime( u'%Y-%m-%dT%H:%M:%s' ), attrs={ u'dataType': 'datetime' } )
            elif isinstance( value, date ):
                xml.element( key, text=value.strftime( u'%Y-%m-%d' ), attrs={ u'dataType': 'date' } )
            elif isinstance( value, float ):
                xml.element( key, text=unicode(value), attrs={ u'dataType': 'float' } )
            else:
                raise CoilsException( 'Data type "{0}" cannot be encoded for value of {1}'.format( type( value ), key ) )

        omphalos = Omphalos.Result(entity, detail_level, ctx)

        # TODO: FLAGS

        if '_PLUGINDATA' in omphalos:
            with xml.container( u'plugins' ):
                for plugin in omphalos[ '_PLUGINDATA' ]:
                    with xml.container( u'plugin', attrs={ 'pluginname': plugin[ 'pluginName' ] } ):
                       for k,v in plugin.items( ):
                           render_key_value(xml, k, v)

        if '_PROPERTIES' in omphalos:
            with xml.container(u'objectproperties'):
                for prop in omphalos['_PROPERTIES']:
                    # TODO: encode type
                    # TODO: encode values
                    label = prop['label'] if prop['label'] else prop['attribute']
                    with xml.container(u'objectproperty', attrs={ 'attribute': prop['attribute'],
                                                                  'namespace': prop['namespace'],
                                                                  'parentid':  unicode(prop['parentObjectId']) } ):
                        render_value(xml, prop['value'])


        if '_COMPANYVALUES' in omphalos:
            with xml.container(u'companyvalues'):
                for cv in omphalos['_COMPANYVALUES']:
                    label = cv['label'] if cv['label'] else cv['attribute']
                    if cv['type'] == 1: hint = 'string'
                    elif cv['type'] == 2: hint = 'checkbox'
                    elif cv['type'] == 3: hint = 'email'
                    elif cv['type'] == 9: hint = 'multiselect'
                    else: hint = 'string'
                    # TODO: Type
                    # TODO: Value
                    with xml.container(u'companyvalue', attrs={ 'attribute': cv['attribute'],
                                                               'label': label,
                                                               'uihint': hint,
                                                               'objectId': str(cv['objectId']),
                                                               'parentId': str(cv['companyObjectId']) } ):
                        render_value(xml, cv['value'])

        if '_PHONES' in omphalos:
            with xml.container(u'phones'):
                for phone in omphalos['_PHONES']:
                    info = phone['info'] if phone['info'] else ''
                    with xml.container(u'phone', attrs={ 'kind': phone['type'],
                                                         'info': info,
                                                         'objectid': str(phone['objectId']),
                                                         'parentid': str(phone['companyObjectId']) } ):
                        if phone['number']:
                            xml.text(phone['number'])

        if '_ADDRESSES' in omphalos:
            with xml.container(u'addresses'):
                for address in omphalos['_ADDRESSES']:
                    with xml.container(u'address', attrs={ 'kind': address['type'],
                                                           'objectId': str(address['objectId']),
                                                           'parentId': str(address['companyObjectId']) } ):
                        xml.element(u'city', text=address['city'])
                        xml.element(u'country', text=address['country'])
                        xml.element(u'name1', text=address['name1'])
                        xml.element(u'name2', text=address['name2'])
                        xml.element(u'name3', text=address['name3'])
                        xml.element(u'state', text=address['state'])
                        xml.element(u'street', text=address['street'])
                        xml.element(u'district', text=address['district'])
                        xml.element(u'zip', text=address['zip'])

        if '_CONTACTS' in omphalos:
            with xml.container(u'assignedcontacts'):
                for assignment in omphalos['_CONTACTS']:
                    xml.element(u'contactid', text=unicode(assignment['targetObjectId']),
                                              attrs = { 'objectid': unicode(assignment['objectId']) } )

        if '_ENTERPRISES' in omphalos:
            with xml.container(u'assignedenterprises'):
                for assignment in omphalos['_ENTERPRISES']:
                    xml.element(u'enterpriseid', text=unicode(assignment['targetObjectId']),
                                              attrs = { 'objectid': unicode(assignment['objectId']) } )


        for k, v in omphalos.items():
            # Skip keys that start with "_" and the FLAGS key
            if not k[0:1] == '_' and k != 'FLAGS':
                render_key_value(xml, k, v)

