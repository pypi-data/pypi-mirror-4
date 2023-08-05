#
# Copyright (c) 2011, 2012
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
import pprint
from coils.core          import *
from api                 import HordeAPI

def render_contact(context, contact):
    #  comment, fileAs, imAddress,
    # occupation, office, birthname,
    # birth place, citizenship, family status,  sensitivity, salutation
    if (contact.file_as is None):
        display_name = contact.get_display_name()
    elif (len(contact.file_as.strip()) == 0):
        display_name = contact.get_display_name()
    else:
        display_name = contact.file_as
    if (contact.carddav_uid is None):
        key = 'LUID:{0}@{1}'.format(contact.object_id, context.cluster_id)
    else:
        key = 'GUID:{0}'.format(contact.carddav_uid)
    response = { 'key':         key,
                 'birthday':    contact.birth_date,
                 'department':  contact.department,
                 'url':         contact.URL,
                 'manager':     contact.boss_name,
                 'assistant':   contact.assistant_name,
                 'fileas':      display_name,
                 'lastname':    contact.last_name,
                 'gender':      contact.gender,
                 'guid':        contact.carddav_uid,
                 'keywords':    contact.keywords,
                 'firstname':   contact.first_name,
                 'jobtitle':    contact.get_company_value_text('job_title'),
                 'email':       contact.get_company_value_text('email1'),
                 'phone-work':  contact.telephones[ '01_tel' ],
                 'phone-fax':   contact.telephones[ '10_fax' ],
                 'phone-home':  contact.telephones[ '05_tel_private' ],
                 'phone-cell':  contact.telephones[ '03_tel_funk' ],
                 'deathday':    contact.grave_date,
                 'citizenship': contact.citizenship,
                 'birthplace':  contact.birth_place,
                 'birthname':   contact.birth_name,
                 'freebusyURL': '' }
    for address in contact.addresses.values( ):
        response['address-{0}-{1}'.format(address.kind, 'name1')] = address.name1
        response['address-{0}-{1}'.format(address.kind, 'name2')] = address.name2
        response['address-{0}-{1}'.format(address.kind, 'name3')] = address.name3
        response['address-{0}-{1}'.format(address.kind, 'street')] = address.street
        response['address-{0}-{1}'.format(address.kind, 'province')] = address.province
        response['address-{0}-{1}'.format(address.kind, 'district')] = address.district
        response['address-{0}-{1}'.format(address.kind, 'postalcode')] = address.postal_code
        response['address-{0}-{1}'.format(address.kind, 'city')] = address.city
        response['address-{0}-{1}'.format(address.kind, 'country')] = address.country
    return response

def translate_key(key):
    if (key == 'email'): return 'email1'
    elif (key == 'jobtitle'): return 'job_title'
    elif (key.startswith('phone-')): return 'phone.number'
    elif (key.startswith('address-')):
        return 'address.{0}'.format(key.split('-')[2])
    return key

def key_to_object_id(context, key):
    if (key.startswith('LUID:')):
        return int(key[5:].split('@')[0])
    else:
        db = context.db_session()
        record = db.query(Contact.object_id).filter(Contact.carddav_uid == key[5:]).first()
        #print record
        if (record is not None):
            return int(record[0])
        record = db.query(Enterprise.object_id).filter(Enterprise.carddav_uid == key[5:]).first()
        if (record is not None):
            return int(record[0])
    return None

def translate_contact(context, contact, key=None):
    ''' Converts the Turba representation to Omphalos so we can update and
        create via Logic. '''
    response = { '_COMPANYVALUES': [ ] }
    if (key is not None):
        response['carddav_uid'] = key
        #print 'Using UID: {0}'.format(response['carddav_uid'])
    addresses = None
    for key in contact:
        if (key in ('fullname',   'lastname',  'firstname',  'keywords',  'url',
                    'department', 'manager',   'gender',      'birthday', 'deathday',
                    'keywords',   'assistant', 'citizenship', 'birthplace',
                    'birthname')):
            response[key] = contact.get(key)
        elif (key in ('email', 'jobtitle')):
            if   key == 'email':    map_key = 'email1'
            elif key == 'jobtitle': map_key = 'job_title'
            else: map_key = key
            response['_COMPANYVALUES'].append( { 'attribute': map_key, 'value': contact.get(key) } )
        elif (key.startswith('phone-')):
            if ('_PHONES' not in response):
                response['_PHONES'] = [ ]
            if (key.endswith('-work')):
                response['_PHONES'].append( { 'kind': '01_tel', 'number': contact.get(key) } )
            elif (key.endswith('-fax')):
                response['_PHONES'].append( { 'kind': '10_fax', 'number': contact.get(key) } )
            elif (key.endswith('-home')):
                response['_PHONES'].append( { 'kind': '05_tel_private', 'number': contact.get(key) } )
            elif (key.endswith('-cell')):
                response['_PHONES'].append( { 'kind': '03_tel_funk', 'number': contact.get(key) } )
        elif (key.startswith('address-')):
            if addresses is None: addresses = { }
            kind = key.split('-')[1]
            attr = key.split('-')[2]
            if (kind not in addresses):
                addresses[kind] = { }
            addresses[kind][attr] = contact.get(key)
    if (addresses is not None):
        response['_ADDRESSES'] = [ ]
        for key in addresses:
            address = { 'kind':     key }
            if 'name1'      in addresses[key]: address['name1']      = addresses[key]['name1']
            if 'name2'      in addresses[key]: address['name2']      = addresses[key]['name2']
            if 'name2'      in addresses[key]: address['name3']      = addresses[key]['name3']
            if 'street'     in addresses[key]: address['street']     = addresses[key]['street']
            if 'city'       in addresses[key]: address['city']       = addresses[key]['city']
            if 'province'   in addresses[key]: address['province']   = addresses[key]['province']
            if 'postalcode' in addresses[key]: address['postalcode'] = addresses[key]['postalcode']
            if 'district'   in addresses[key]: address['district']   = addresses[key]['district']
            if 'country'    in addresses[key]: address['country']    = addresses[key]['country']
            response['_ADDRESSES'].append( address )
    return response

class HordeTurbaAPI(HordeAPI):

    def api_turba_search(self, args):
        #pprint.pprint(args)
        ''' "params": [ { "AND" :{ "AND": [ {"field":"__owner","op":"=","test":"awilliam"} ],
                                   "0": { "AND": [ { "field":"__type",
                                                     "op": "LIKE",
                                                     "test": "Group",
                                                     "begin": false,
                                                     "approximate": false } ]
                                        }
                                 }
                        },
                        ["name","__type","__owner","fullname"]
                      ] '''

        book_name       = args[0]
        search_criteria = args[1]
        criteria = [ ]
        if (isinstance(search_criteria, dict)):
            conjunction = None
            if ('AND' in search_criteria):
                conjunction = 'AND'
            elif ('OR' in search_criteria):
                conjunction = 'OR'
            if (conjunction is not None):
                for criterion in search_criteria[conjunction]:
                    key = translate_key(criterion['field'])
                    if criterion['op'] == 'LIKE':
                        expression = 'ILIKE'
                        value = '{0}'.format(criterion['test'])
                    else:
                        expression = criterion['op']
                        value = str(criterion['test'])
                    # TODO: What about the expression??? Comes from
                    criteria.append( { 'key': key,
                                       'expression': 'ILIKE',
                                       'conjunction': conjunction,
                                       'value': '%{0}%'.format(criterion['test']) } )
            else:
                raise CoilsException('No criteria specified for search')
            #print '----'
            #pprint.pprint(criteria)
            contacts = self.context.run_command('contact::search', criteria=criteria);
            #print '----'
        else:
            contacts = [ ]
            #print 'no criteria'
        result = [ render_contact(self.context, contact) for contact in contacts]
        # TODO: filter attributes
        return result


    def api_turba_read(self, args):
        '''[ 'objectId',  # key
             ['10100'],   # ids
             'awilliam',  # owner
             [ 'objectId', 'fullname', 'last_name',  'first_name', 'email', 'alias',
               'company',  'phone-work', 'fax', 'phone-home',  'cellphone', 'freebusyUrl' ] # fields
           ] '''
        book_name  = args[0]
        key_name   = args[1]
        key_values = args[2]
        owner_uid  = args[3]
        attributes = args[4]
        #pprint.pprint(args)
        if (key_name== 'key'):
            object_ids = [ ]
            for object_id in [ key_to_object_id(self.context, x) for x in key_values ]:
                if object_id is not None:
                    object_ids.append(object_id)
            contacts = self.context.run_command('contact::get', ids=object_ids)
        else:
            contacts = [ ]
        # TODO: filter attributes
        result = [ render_contact(self.context, contact) for contact in contacts]
        return result

    def api_turba_save(self, args):
        book_name  = args[0]
        key_name   = args[1]
        key_value  = args[2]
        attributes = args[3]
        attributes = translate_contact(self.context, attributes)
        if (key_name == 'key'):
            object_id = key_to_object_id(self.context, key_value)
            contact = self.context.run_command('contact::get', id=object_id)
            if (contact is not None):
                self.context.run_command('contact::set', object=contact, values=attributes)
                self.context.commit()
                return contact.object_id
            else:
                self.log.warn('No such contact as objectId#{0}'.format(object_id))
        # TODO: Fail

    def api_turba_add(self, args):
        if (len(args) == 3):
            book_name  = args[0]
            object_key = args[1]
            if (object_key is None):
                raise CoilsException('NULL object key specified for new object')
            elif (isinstance(object_key, basestring)):
                if (len(object_key) > 25):
                    object_key        = object_key[5:]
                else:
                    raise CoilsExcpetion('Insufficient entropy in new object key')
            else:
                raise CoilsExcpetion('Invalid data-type for object key')

            attributes = args[2]
            attributes = translate_contact(self.context, attributes, key=object_key)
            #pprint.pprint(attributes)
            contact = self.context.run_command('contact::new', values=attributes)
            self.context.commit()
            return 'GUID:{0}'.format(contact.carddav_uid)
        else:
            # TODO: Raise an exception
            pass

    def api_turba_delete(self, args):
        if (len(args) > 2):
            book_name  = args[0]
            key_name   = args[1]
            key_value  = args[2]

            if (key_value is None):
                raise CoilsException('NULL object key specified for delete')
            elif not isinstance(key_value, basestring):
                raise CoilsExcpetion('Invalid data-type for object key')
            self.log.debug('key_name is "{0}"'.format(key_name));
            if (key_name == 'key'):
                self.log.debug('Attempting to resolve object id from "{0}"'.format(key_value));
                object_id = key_to_object_id(self.context, key_value)
                self.log.debug('Resolved key to objectId "{0}"'.format(object_id))
                if (object_id is not None):
                    contact = self.context.run_command('contact::delete', id=object_id)
                    self.context.commit()
                    return True
                else:
                    raise CoilsException('Unable to resolve key {0} to objectId'.format(key_value))
            else:
                raise CoilsException('Delete requests by attribute {0} unsupported'.format(key_name))
        # TODO: Raise an exception
