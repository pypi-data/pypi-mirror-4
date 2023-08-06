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
    
    @property
    def company_value_spec(self):
        """
        This property just provides a cache for the server's company value spec from
        the configuration; this is so we do not read and parse the configuration 
        multiple times in a run.  The company value spec becomes a Class attribute.
        """
        if not hasattr( CompanyCommand, '_company_value_spec_'):
             CompanyCommand._company_value_spec_ = self._read_company_value_spec( )
        return CompanyCommand._company_value_spec_
        
    def company_value_spec_for(self, name):
        """
        Return the spec for the named CompanyValue if such a spec is defined in the
        server's configuration; otherwise return None/NULL.
        """
        cvs = [ s for s in self.company_value_spec if s['name'] == name ]
        if cvs:
            return cvs[ 0 ]
        return None

    def _read_company_value_spec(self):
        """
        Retrieve a list of pre-defined company values from ther server's configuration.
        Result is a list of dicts with the keys type, label, and attribute. Type defaults
        to "1" if not specified in the configuration; only "attribute" (the 'name' of the
        CompanyValue) is required, and if "label" is not specified it defaults to be the
        same as the attribute/name.  User interfaces should localize off of the "label"
        value.
        """
        spec = [ ]
        defaults = [ 'SkyPublicExtended{0}Attributes'.format(self.obj.__internalName__),
                     'SkyPrivateExtended{0}Attributes'.format(self.obj.__internalName__) ]
        for default in defaults:
            for attrdef in self.sd.default_as_list( default, fallback=[ ] ):
                spec.append( { 'type':      attrdef.get( 'type', 1 ),
                               'label':     attrdef.get( 'label', attrdef[ 'key'] ),
                               'name':      attrdef[ 'key' ] } )
        return spec

    def _create_company_value(self, name ):
        """"
        Create and initialize a new CompanyValue obejct with the specified name.
        :param name: Attribute name of the new company value
        """
        object_id = self.generate_object_id( )
        cv = CompanyValue( object_id=self.generate_object_id( ) , parent_id=self.obj.object_id, name=name )
        cv.object_id = object_id
        spec = self.company_value_spec_for( name )
        if spec:
            if 'type'  in spec: cv.widget = spec['type']
            if 'label' in spec: cv.label = spec['label']
        self.obj.company_values[ cv.name ] = cv
        
        return cv

    def _initialize_company_values(self):
        """
        This should be called when a new Company object is create (either a Contact
        or an Enterprise).  This reads the server's configuration for defined 
        company values and creates the new, empty, CompanyValue objects on the new
        Company object.
        """
        # TODO: We don't really support private CVs :(
        for spec in self.company_value_spec:
            cv = self._create_company_value( name=spec[ 'name' ] )

    def _update_company_values(self):
        """
        Update the values of the CompanyValues related to this Company object.
        """
        # TODO: Write more docs!
        if '_COMPANYVALUES' in self.values:
            tmp = KVC.subvalues_for_key( self.values, [ '_COMPANYVALUES' ] )
            tmp = KVC.keyed_values(tmp, [ 'attribute' ] )
        else:
            # This is to support in-line usage of CompanyValue attributes
            tmp = { }
            for spec in self.company_value_spec:
                key = spec[ 'name' ]
                if  key in self.values:
                    tmp[ key ] = { 'value': self.values[ key ],
                                   'attribute': key,
                                   'label': spec[ 'label' ] }
            
        for name, value in tmp.items():
            cv = self.obj.company_values.get( name, None )
            if not cv:
                cv = self._create_company_value( name )
            cv.take_values(value, COILS_COMPANYVALUE_KEYMAP)
            cv.set_value(value.get ( 'value', None ) )
            if name.startswith( 'email' ):
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
                self.obj.addresses[kind] = tmp
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
