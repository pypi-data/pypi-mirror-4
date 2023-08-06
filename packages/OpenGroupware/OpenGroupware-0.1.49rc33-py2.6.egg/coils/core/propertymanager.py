#
# Copyright (c) 2009, 2010 Adam Tauno Williams <awilliam@whitemice.org>
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
from sqlalchemy       import *
from coils.foundation import *
from exception        import AccessForbiddenException, CoilsException

OGO_EXT_ATTR_SPACE ='http://www.opengroupware.org/properties/ext-attr'
OGO_APT_EXT_ATTR_DEFAULT = 'OGoExtendedAptAttributes'

# 2010-01-15 - Introduced the concept of server properties [which have a parent_id of 0]
#              These are used by the server to auotmatically preserve some specified values
#              such as a UUID;  PropertyManager now provides two methods get_server_property
#              and set_server_property for getting and setting these properties.  Only an
#              administrative context can set a server property (a property have a parent_id
#              of zero - anyone can read the server properties [by name].  

class PropertyManager(object):
    # TODO: Private Properties, issue#85
    __slots__ = ('_ctx')
    _apt_ext_attr_dict = None


    def __init__(self, ctx):
        self._ctx = ctx
        if (PropertyManager._apt_ext_attr_dict is None):
            PropertyManager.load_extended_attributes()

    @staticmethod
    def Get_Object_Id(value):
        object_id = None
        try:
            if (isinstance(value, ORMEntity)):
                object_id = value.object_id
            else:
                object_id = long(value)
        except Exception, e:
            print e
            raise CoilsException('Unable to understand {0} as an entity reference (objectId)'.format(value))
        return object_id
    
    @staticmethod
    def Parse_Property_Name(name):
        return ObjectProperty.Parse_Property_Name(name)

    @staticmethod
    def load_extended_attributes():
        """ Read the defined Appointment extended attributes from the server's
            global defaults.  Contacts and Enterprises use Company Values for
            extended (custom) attributes, where Appointments use the property
            system.
            Result:
              {'Billable': {'kind': '2', 'label': '', 'values': ['YES', 'NO']},
               'Color': {'kind': '1', 'label': '', 'values': []},
               'EMail': {'kind': '3', 'label': '', 'values': []}}
            Type: 1 = String, does not need to be specified, default
                  2 = Boolean (Check box) of YES / NO
                  3 = E-Mail Address (string)
                  9 = Multi-select, produces a CSV string """
        PropertyManager._apt_ext_attr_dict = { }
        sd = ServerDefaultsManager()
        if (sd.is_default_defined(OGO_APT_EXT_ATTR_DEFAULT)):
            for attr in sd.default_as_list(OGO_APT_EXT_ATTR_DEFAULT):
                spec = { }
                if (attr.has_key('type')):
                    spec['kind'] = attr['type']
                    if (spec['kind'] == '2'):
                        spec['values'] = [ 'YES', 'NO' ]
                    elif (attr.has_key('values')):
                        spec['values'] = attr['values'].keys()
                    else:
                        spec['values'] = []
                else:
                    spec['kind'] = '1'
                    spec['values'] = []
                if (attr.has_key('label')):
                    spec['label'] = attr['label']
                else:
                    spec['label'] = ''
                PropertyManager._apt_ext_attr_dict[attr['key']] = spec

    def get_defined_appointment_properties(self):
        return PropertyManager._apt_ext_attr_dict

    def get_preferred_kinds(self):
        return ['valueString', 'valueInt', 'valueFloat',
                 'valueDate', 'valueOID', 'valueBlob' ]

    def get_property(self, entity, namespace, name):
        db = self._ctx.db_session()
        object_id = PropertyManager.Get_Object_Id(entity)
        query = db.query(ObjectProperty).filter(and_(ObjectProperty.parent_id == object_id,
                                                     ObjectProperty.namespace == namespace,
                                                     ObjectProperty.name == name,
                                                     or_(ObjectProperty.access_id == self._ctx.account_id,
                                                         ObjectProperty.access_id == None)))
        result = query.first()
        return result

    def get_properties(self, entity):
        db = self._ctx.db_session()
        data = []
        object_id = PropertyManager.Get_Object_Id(entity)
        # TODO: Support private properties
        query = db.query(ObjectProperty).filter(and_(ObjectProperty.parent_id == object_id,
                                                      or_(ObjectProperty.access_id == self._ctx.account_id,
                                                          ObjectProperty.access_id == None)))
        for prop in query.all():
            if (prop.namespace == OGO_EXT_ATTR_SPACE):
                prop.kind = PropertyManager._apt_ext_attr_dict[prop.name]['kind']
                prop.label = PropertyManager._apt_ext_attr_dict[prop.name]['label']
                prop.values = PropertyManager._apt_ext_attr_dict[prop.name]['values']
            else:
                prop.kind = ''
                prop.label = ''
                prop.values = ''
            data.append(prop)
        query = None
        return data

    @staticmethod
    def Name_Of_Property(prop):
        if (isinstance(prop, dict)):
            # TODO: we shouldn't care about the case of the keys, this is a
            #       potential bug.  We really want a caseless dictionary.
            if ('propertyName' in prop):
                return PropertyManager.Parse_Property_Name(prop.get('propertyName'))
            if ('namespace' in prop):
                if ('name' in prop):
                    return (prop.get('namespace'), prop.get('name'))
                elif ('attribute' in prop):
                    return (prop.get('namespace'), prop.get('attribute'))
        elif (isinstance(prop, ObjectProperty)):
            return (prop.namespace, prop.name)
        return (None, None)

    def set_property(self, entity, namespace, attribute, value, private=False):
        object_id = PropertyManager.Get_Object_Id(entity)        
        # Security check for attempt to set a server property (2010-01-15)
        if object_id == 0:
            if not self._ctx.is_admin:
                raise AccessForbiddenException('Only administrative contexts can set server properties')
        # Get property
        prop = self.get_property(object_id, namespace, attribute)
        # Create or update the property
        if (prop is None):
            name = '{{{0}}}{1}'.format(namespace, attribute)
            if (private):
                self._ctx.db_session().add(ObjectProperty(object_id, name, value=value, access_id=self._ctx.account_id))
            else:
                self._ctx.db_session().add(ObjectProperty(object_id, name, value=value))
        else:
            prop.set_value(value)

    def set_properties(self, entity, props):
        object_id = PropertyManager.Get_Object_Id(entity)
        # Security check for attempt to set a server property (2010-01-15)
        if (entity.object_id == 0):
            if (self._ctx.is_admin):
                pass
            else:
                raise AccessForbiddenException('Only administrative contexts can set server properties')
        # TODO: ??? what if props is not a list (this silently fails, which is bad)
        if (isinstance(props, list)):
            db_props = self.get_properties(object_id)
            removes = [ ]
            for prop in db_props:
                removes.append(int(prop.object_id))
            for in_prop in props:
                in_namespace, in_name = PropertyManager.Name_Of_Property(in_prop)
                for ex_prop in db_props:
                    if ((in_namespace == ex_prop.namespace) and
                         (in_name == ex_prop.name)):
                        # Update existing property
                        ex_prop.set_value(in_prop.get('value'))
                        removes.remove(int(ex_prop.object_id))
                        break
                else:
                    # Did not find property in existing properties; Create
                    # TODO: Support sync of private properties
                    new_prop = ObjectProperty(object_id,
                                              '{{{0}}}{1}'.format(in_namespace, in_name),
                                              value=in_prop.get('value'))
                    self._ctx.db_session().add(new_prop)
                    new_prop = None
            db_props = None # Drop reference to existing properties                    
            db = self._ctx.db_session()
            if (len(removes) > 0):
                db.query(ObjectProperty).\
                   filter(ObjectProperty.object_id.in_(removes)).\
                   delete(synchronize_session='fetch')
        return

    def delete_property(self, entity, namespace, attribute,private=False):
        object_id = PropertyManager.Get_Object_Id(entity)
        # Security check for attempt to set a server property (2010-01-15)
        if object_id == 0:
            if not self._ctx.is_admin:
                raise AccessForbiddenException('Only administrative contexts can set server properties')
        # Get property
        prop = self.get_property(object_id, namespace, attribute)
        # TODO: CHECK PERMISSIONS ON ENTITY
        if prop:
            self._ctx.db_session().delete(prop)
            return True
        return False

    # Added 2010-01-15; just a utility wrapper to easily retrieve a named server property
    def get_server_property(self, namespace, name):
        return self.get_property(0, namespace, name)
        
    def get_server_properties(self):
        return self.get_properties(0)

    # Added 2010-01-15; just a utility wrapper to easily set a named server property
    def set_server_property(self, namespace, name, value):
        self.set_property(0, namespace, name, value)
