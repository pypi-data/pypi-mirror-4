# Copyright (c) 2010, 2012 
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
#
from coils.foundation import KVC
from coils.core       import Command, CompanyValue, Address, Telephone
from keymap           import COILS_TELEPHONE_KEYMAP, COILS_ADDRESS_KEYMAP, COILS_COMPANYVALUE_KEYMAP

class CompanyCommand(Command):

    def _list_subtypes_types_for_entity(self, default_name):
        if default_name in ('LSAddressType', 'LSTeleType'):
            # Return address or telephone types
            subtypes = self.sd.default_as_dict(default_name)
            if (self.obj.__internalName__ in subtypes):
                if (isinstance(subtypes[self.obj.__internalName__], list)):
                    return subtypes[self.obj.__internalName__]
                else:
                    raise CoilsException(
                        'Sub-type list {0} in default {1} is improperly structured'.format(
                            self.obj.__internalName__,
                            default_name))
            raise CoilsException(
                'Not sub-type list defined in default {0} for entity type {1}'.format(
                    default_name,
                    str(self.obj)))
        else:
            return []


    #
    # Company Values
    #

    def _initialize_company_values(self):
        # TODO: We don't really support private CVs :(
        # TODO: This is kludy, de-kludgify
        subtypes = [ ]
        defaults = [ 'SkyPublicExtended{0}Attributes'.format(self.obj.__internalName__),
                     'SkyPrivateExtended{0}Attributes'.format(self.obj.__internalName__) ]
        for default in defaults:
            for attrdef in self.sd.default_as_list(default, fallback=[]):
                cv = CompanyValue( parent_id = self.obj.object_id, name = attrdef['key'] )
                self.obj.company_values[ cv.name ] = cv
                if 'type' in attrdef: cv.widget = attrdef['type']
                if 'label' in attrdef: cv.label = attrdef['label']

    def _update_company_values(self):
        
        if '_COMPANYVALUES' not in self.values:
            return

        tmp = KVC.subvalues_for_key(self.values, ['_COMPANYVALUES'])
        tmp = KVC.keyed_values(tmp, ['attribute'])
        for name, value in tmp.items():
            cv = self.obj.company_values.get( name, None )
            if not cv:
                cv = CompanyValue( parent_id = self.obj.object_id, attribute=name )
                self.obj.company_values[ cv.name ] = cv
            cv.take_values(value, COILS_COMPANYVALUE_KEYMAP)
            cv.set_value(value.get ( 'value', None ) )
            if name[0:5] == 'email':
                if 'xattr' in value:
                        self._ctx.property_manager.set_property( cv, 
                                                                 'http://coils.opengroupware.us/logic', 
                                                                 'xattr01', 
                                                                 value.get('xattr') )

    #
    # Telephones
    #

    def _initialize_telephones(self):
        for kind in self._list_subtypes_types_for_entity('LSTeleType'):
            tmp = Telephone( parent_id = self.obj.object_id, kind = kind )
            self.obj.telephones[kind] = tmp

    def _update_telephones(self):
        values = KVC.subvalues_for_key(self.values, ( '_PHONES', 'telephones', 'phones' ) )
        for kind, value in KVC.keyed_values(values, ['kind', 'type']).items():
            tmp = self.obj.telephones.get( kind, None )
            if not tmp:
                tmp = Telephone( parent_id = self.obj.object_id, kind = kind )
                self.obj.telephones[kind] = tmp
            tmp.take_values(value, COILS_TELEPHONE_KEYMAP)

    #
    # Addresses
    #

    def _initialize_addresses(self):
        for kind in self._list_subtypes_types_for_entity('LSAddressType'):
            tmp = Address( parent_id = self.obj.object_id, kind = kind )
            self.obj.addresses[kind] = tmp

    def _update_addresses(self):
        values = KVC.subvalues_for_key(self.values, ['_ADDRESSES', 'addresses'])
        for kind, value in  KVC.keyed_values(values, ['kind', 'type']).items():
            tmp = self.obj.addresses.get( kind, None )
            if not tmp:
                tmp = Address( parent_id=self.obj.object_id, kind=kind )
                self.obj.address[kind] = tmp
            tmp.take_values(value, COILS_ADDRESS_KEYMAP)                

    #
    # Projects
    #

    def _set_projects(self):
        assignments = KVC.subvalues_for_key(self.values,
                                         ['_PROJECTS', 'projects'],
                                         default=None)
        if (assignments is not None):
            _ids = []
            for a in assignments:
                _id = a.get('targetObjectId', a.get('child_id', None))
                if (_id is not None):
                    _ids.append(_id)
            self._ctx.run_command('company::set-projects', company=self.obj, project_ids=_ids)

    #
    # Access
    #

    def _set_access(self):
        acls = KVC.subvalues_for_key(self.values, ['_ACCESS', 'acls'], None)
        if (acls is not None):
            self._ctx.run_command('object::set-access', object=self.obj, acls=acls)
