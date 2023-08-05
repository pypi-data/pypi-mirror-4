#!/usr/bin/env python
# Copyright (c) 2011, 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
import base64, logging
from time import time
from coils.core import CoilsException, Route, Process, Collection, Contact, Enterprise
from eofilter import process_eo_filter

def Caseless_Get(dict_, key_):
    if key_ in dict_:
        value= dict_[key_]
    else:
        for key, value in dict_.items():
            if key_.lower() == key.lower():
                value = dict_[key]
                break
        else:
            value = None
    return value


class ZOGIAPI(object):

    def __init__(self, context):
        self.context = context

    def process_eo_filter(self, results_in, filter_string):
        return process_eo_filter(results_in, filter_string)

    #
    # getObjectById methods
    #

    def get_accounts_by_ids(self, ids):
        # TODO: Implement
        return [ ]

    def get_appointments_by_ids(self, ids):
        x = self.context.run_command('appointment::get', ids=ids)
        return x

    def get_contacts_by_ids(self, ids):
        x = self.context.run_command('contact::get', ids=ids )
        return x

    def get_collections_by_ids(self, ids):
        x = self.context.run_command('collection::get', ids=ids )
        return x

    def get_documents_by_ids(self, ids):
        x = self.context.run_command('document::get', ids=ids )
        return x

    def get_enterprises_by_ids(self, ids):
        x = self.context.run_command('enterprise::get', ids=ids )
        return x
        
    def get_folders_by_ids(self, ids):
        x = self.context.run_command('folder::get', ids=ids )
        return x        

    def get_processs_by_ids(self, ids):
        # Yes, "processs" has an extra "s", that is not a typo
        x = self.context.run_command('process::get', ids=ids )
        return x

    def get_projects_by_ids(self, ids):
        x = self.context.run_command('project::get', ids=ids )
        return x

    def get_resources_by_ids(self, ids):
        x = self.context.run_command('resource::get', ids=ids )
        return x

    def get_routes_by_ids(self, ids):
        x = self.context.run_command('route::get', ids=ids )
        return x

    def get_tasks_by_ids(self, ids):
        x = self.context.run_command('task::get', ids=ids )
        return x

    def get_teams_by_ids(self, ids):
        x = self.context.run_command('team::get', ids=ids )
        return x

    def get_unknowns_by_ids(self, ids):
        # TODO: Implement
        return [ ]
        x = [ ]
        for object_id in ids:
            x.append({'entityName' : 'Unknown', 'objectId' : object_id})
        return x

    # searchForObjects methods

    def search_account(self, criteria, flags):
        #TODO: Implement
        raise 'Not Implemented'

    def search_appointment(self, criteria, flags):
        # TODO: extend the zOGI API to include support for startDate + timespan (in days?)
        result = [ ]
        params = {}
        # appointmentType (kinds of appointments)
        if (criteria.has_key('appointmentType')):
            params['kinds'] = criteria['appointmentType']
        # startDate
        if (criteria.has_key('startDate')):
            x = criteria['startDate']
            if (isinstance(x, basestring)):
                if (len(x) == 10):
                    x =  datetime.strptime(x, '%Y-%m-%d')
                    x.hour = 0
                    x.minute = 0
                elif (len(x) == 16):
                    x = datetime.strptime(x, '%Y-%m-%d %H:%M')
            params['start'] = x
        # endDate
        if (criteria.has_key('endDate')):
            x = criteria['endDate']
            if (isinstance(x, basestring)):
                if (len(x) == 10):
                    x =  datetime.strptime(x, '%Y-%m-%d')
                    x.hour = 23
                    x.minute = 59
                elif (len(x) == 16):
                    x = datetime.strptime(x, '%Y-%m-%d %H:%M')
            params['end'] = x
        # Clean up participants value if one provided
        # This is turned into a list of integers (presumed object-ids)
        # The appointment::get-range command will take care of the
        # internal ugliness of converting the object ids of resources
        # into resource names.
        if (criteria.has_key('participants')):
            parts = criteria['participants']
            if (isinstance(parts, int)):
                parts = [ parts ]
            elif (isinstance(parts, basestring)):
                r = [ ]
                for part in parts.split(','):
                    r.append(int(part.strip()))
                parts = r
            elif (isinstance(parts, list)):
                r = [ ]
                for part in parts:
                    r.append(int(part))
                parts = r
            else:
                raise CoilsException('Unable to parse participants value for search request.')
            params['participants'] = parts
        return self.context.run_command('appointment::get-range', **params)

    def polish_company_search_params(self, criteria, flags):
        # Used by _search_contact and _search_enterprise

        revolve = flags.get('revolve', False)
        if isinstance(revolve, basestring):
            revolve = revolve.upper()
            if revolve == 'YES':
                revolve = True
            else:
                revolve = False
        elif isinstance(revolve, bool):
            pass
        else:
            raise CoilsException('Revolve value of type {0} not understood'.format(type(revolve)))

        params = { 'limit':   int(flags.get('limit', 150)),
                   'revolve': revolve }

        if 'scope' in flags:
            params['contexts'] = [ int(flags['scope']) ]

        if (isinstance(criteria, list)):
            params['criteria'] = criteria
        elif (isinstance(criteria, dict)):
            params['criteria'] = [ criteria ]
        else:
            raise CoilsException('Unable to comprehend criteria')

        return params

    def search_collection(self, criteria, flags):
        if (isinstance(criteria, basestring)):
            if criteria.strip().lower() == 'list':
                return self.context.run_command('collection::list', properties=[Collection])
            else:
                raise CoilsException('Unknown string set-name in Collection Search')
        # Normal Search
        params = self.polish_company_search_params(criteria, flags)
        return self.context.run_command('collection::search', **params)

    def search_contact(self, criteria, flags):
        params = self.polish_company_search_params(criteria, flags)
        return self.context.run_command('contact::search', **params)

    def search_enterprise(self, criteria, flags):
        params = self.polish_company_search_params(criteria, flags)
        return self.context.run_command('enterprise::search', **params)

    def search_process(self, criteria, flags):
        # TODO: Implement!
        if (isinstance(criteria, basestring)):
            if criteria.strip().lower() == 'list':
                return self.context.run_command('process::list', properties=[Process])
            else:
                raise CoilsException('Unknown string set-name in Process Search')
        # Normal Search
        params = self.polish_company_search_params(criteria, flags)
        return self.context.run_command('process::search', **params)

    def search_project(self, criteria, flags):
        # TODO: Implement zOGI-ness
        # Supported keys: kind, name, number, objectId, ownerObjectId, and placeHolder
        # If a conjunction is specified (either "AND" or "OR") then the name and number
        # keys are compared fuzzy, otherwise all keys must match exactly [AND].
        if isinstance(criteria, basestring):
            if criteria == 'list':
                return self.context.run_command('account::get-projects')
            else:
                return [ ]
        query = [ ]
        if ('conjunction' in criteria):
            expression = 'ILIKE'
            conjunction = criteria['conjunction']
        else:
            expression = 'EQUALS'
            conjunction = 'AND'
        for key in ('kind','name', 'number', 'objectid', 'ownerobjectid', 'placeholder'):
            value = Caseless_Get(criteria, key)
            if value:
                if (expression == 'EQUALS') and isinstance(value, basestring):
                    value = value
                else:
                    value = '%{0}%'.format(value)
                query.append({ 'conjunction': conjunction,
                               'expression': expression,
                               'key': key,
                               'value': value } )
        return self.context.run_command('project::search', criteria=query, limit=flags.get('limit', None))

    def search_resource(self, criteria, flags):
        #Implemented: Implement "All Search", no criteria
        #Implemented: Implement "Exact Search", name or criteria
        #Implemented: "Fuzzy Search", indicated by any conjunction in criteria
        if (len(criteria) == 0):
            # All Search
            return self.context.run_command('resource::get')
        elif (isinstance(criteria, dict)):
            # Transform legacy zOGI search into a criteria search
            x = [ ]
            if ('conjunction' in criteria):
                conjunction = criteria['conjunction'].upper()
                expression = 'ILIKE'
                del criteria['conjunction']
            else:
                conjunction = 'AND'
                expression = 'EQUALS'
            for k in criteria:
                if (expression == 'ILIKE'):
                    value = '%{0}%'.format(criteria[k])
                else:
                    value = criteria[k]
                x.append({'key': k,
                          'value': value,
                          'expression': expression,
                          'conjunction': conjunction })
            return self.context.run_command('resource::search', criteria=x)
        elif (isinstance(criteria, list)):
            # Assume the search is a well-formed criteria server
            # WARN: This feature is not supported by legacy/Obj-C zOGI
            return self.context.run_command('resource::search', criteria=criteria)

    def search_route(self, criteria, flags):
        # TODO: Implement!
        if (isinstance(criteria, basestring)):
            if criteria.strip().lower() == 'list':
                tmp =  self.context.run_command('route::list', properties=[Route])
                return tmp
            else:
                raise CoilsException('Unknown string set-name in Route Search')
        # Normal Search
        params = self.polish_company_search_params(criteria, flags)
        return self.context.run_command('route::search', **params)

    def search_lock(self, criteria, flags):
        if isinstance( criteria, dict ):
            object_id = int( criteria.get( 'targetObjectId', 0 ) )
            if object_id:
                entity = self.context.type_manager.get_entity( object_id )
                if entity:
                    # TODO: allow operations and exclusivity to be specified in the search criteria
                    return self.context.lock_manager.locks_on( entity, all_locks=True )
            return [ ]
        else:
            raise CoilsException( 'Lock search criteria must be a dictionary' )

    def search_document(self, criteria, flags):
        # TODO: Are there any 'special' searches for documents?
        params = self.polish_company_search_params(criteria, flags)
        return self.context.run_command('document::search', **params)

    def search_task(self, criteria, flags):
        result = [ ]
        params = {}
        if (isinstance(criteria, basestring)):
            if (criteria == 'archived'):
                return self.context.run_command('task::get-archived')
            elif (criteria == 'delegated'):
                return self.context.run_command('task::get-delegated')
            elif (criteria == 'todo'):
                return self.context.run_command('task::get-todo')
            elif (criteria == 'assigned'):
                return self.context.run_command('task::get-assigned')
            elif (criteria == 'current'):
                return self.context.run_command('task::get-current')
        elif (isinstance(criteria, list)):
            #TODO: verify criteria is something like a valid search criteria
            limit = flags.get('limit', 150)
            result = self.context.run_command('task::search', criteria=criteria, limit=limit)
            return result
        raise CoilsException('Invalid search critieria')

    def search_time(self, criteria, flags):
       utctime = self.context.get_utctime()
       is_dst = 0
       if (self.context.get_timezone().dst(utctime).seconds > 0):
            is_dst = 1
       return [{ 'entityName': 'time',
                 'gmtTime': utctime,
                 'isDST': is_dst,
                 'offsetFromGMT': self.context.get_offset_from(utctime),
                 'offsetTimeZone': self.context.get_timezone().zone,
                 'userTime': self.context.as_localtime(utctime) }]

    def search_timezone(self, criteria, flags):
        result = [ ]
        utctime = self.context.get_utctime()
        for tz_def in COILS_TIMEZONES:
            #tz = pytz.timezone(tz_def['code'])
            #is_dst = 0
            #if (tz.dst(utctime).seconds > 0):
            #    is_dst = 1
            #result.append({ 'abbreviation': tz_def['abbreviation'],
            #                'description': tz_def['description'],
            #                'entityName': 'timeZone',
            #                'isCurrentlyDST': is_dst,
            #                'offsetFromGMT': as_integer((86400 - tz.utcoffset(utctime).seconds) * -1),
            #                'serverDateTime': utctime.astimezone(tz)})
            result.append(render_timezone(tz_def['code'], self.context))
        return result

    def search_team(self, criteria, flags):
        #TODO: Implement "All" query
        #TODO: Implement "Mine" query
        if (criteria == 'all'):
            return self.context.run_command('team::get')
        elif (criteria == 'mine'):
            return self.context.run_command('team::get', member_id=self.context.account_id)
        raise 'Not Implemented'

    # putObject methods

    def put_account(self, payload, flags):
        # TODO: Implement
        raise 'Not Implemented'

    def put_acl(self, payload, flags):
        object_id  = Caseless_Get(payload, 'parentObjectId')
        context_id = Caseless_Get(payload, 'targetObjectId')
        operations = Caseless_Get(payload, 'operations')
        direction  = Caseless_Get(payload, 'action')
        if not operations: optations = ''
        if not direction: direction = 'allowed'
        if direction not in ('allowed', 'denied'):
            raise CoilsException('ACL "action" must be either "allowed" or "denied".')
        target = self.context.type_manager.get_entity(object_id)
        if target:
            self.context.run_command('object::set-acl', object=target,
                                                        context_id=context_id,
                                                        permissions=operations,
                                                        action=direction)
            return target
        raise CoilsException('objectId#{0} not available for operation.'.format(object_id))

    def put_appointment(self, payload, flags):
        object_id = Caseless_Get(payload, 'objectId')
        if isinstance(object_id, basestring):
            object_id = int(object_id)
        if object_id:
            print 'update'
            appointment = self.context.run_command('appointment::set', values=payload, id=object_id)
        else:
            print 'new'
            appointment = self.context.run_command('appointment::new', values=payload)
        return appointment


    def put_collectionassignment(self, payload, flags):
        assigned_object_id = int(Caseless_Get(payload, 'assignedObjectId'))
        if assigned_object_id:
            entity = self.context.type_manager.get_entity(assigned_object_id)
            if entity:
                collection_id = int(Caseless_Get(payload, 'collectionObjectId'))
                collection = self.context.run_command('collection::get', id=collection_id)
                if collection and entity:
                    self.context.run_command('object::assign-to-collection', entity=entity, collection=collection)
                    return collection
                else:
                    raise CoilsException('putObject of a collectionAssignment must specify an existing collection')
        else:
            # TODO: raise exception
            return None


    def delete_collectionassignment(self, payload, flags):
        if isinstance(payload, int):
            object_id = payload
        elif isinstance(payload, basestring):
            object_id = int(payload)
        elif isinstance(payload, dict):
            object_id = Caseless_Get(payload, 'objectId')
            if not object_id:
                collection_id = Caseless_Get(payload, 'collectionObjectId')
                assigned_id = Caseless_Get(payload, 'assignedObjectId')
                if collection_id and assigned_id:
                    print 'CID, AID =', collection_id, assigned_id
                    collection = self.context.run_command('collection::get', id=collection_id)
                    if collection:
                        self.context.run_command('collection::delete-assignment', collection=collection,
                                                                                  assigned_id=assigned_id)
                        return True
                    else:
                        raise CoilsException('CollectionId#{0} not available'.format(collection_id))
                else:
                    raise CoilsException('Both collectionObjectId and assignedObjectId must be specified.')
        else:
            raise CoilsException('Unable to comprehend payload')
        result = self.context.run_command('collection::get-assignment', id=object_id)
        if (object_id in result):
            collection, entity = result[object_id]
            if (collection is not None) and (entity is not None):
                result = self.context.run_command('collection::delete-assignment', collection=collection,
                                                                                   entity=entity)
                return result
        return False

    def delete_contact(self, object_id, flags):
        contact = self.context.run_command('contact::get', id=object_id)
        if (contact is not None):
            return self.context.run_command('contact::delete', object=contact)
        return False

    def put_collection(self, payload, flags):
        object_id = Caseless_Get(payload, 'objectId')
        if (object_id == 0):
            collection = self.context.run_command('collection::new', values=payload)
        else:
            collection = self.context.run_command('collection::set', values=payload, id=object_id)
        return collection

    def put_contact(self, payload, flags):
        object_id = int(payload.get('objectId'))
        if (object_id == 0):
            contact = self.context.run_command('contact::new', values=payload)
        else:
            contact = self.context.run_command('contact::set', values=payload, id=object_id)
        return contact

    def delete_collection(self, object_id, flags):
        object_id = int(object_id)
        if (object_id):
            self.context.run_command('collection::delete', id=object_id)
            return True
        return False

    def put_defaults(self, payload, flags):
        # TODO: Implement
        raise 'Not Implemented'

    def put_file(self, payload, flags):
        return self.put_document(payload, flags)

    def put_document(self, payload, flags):
        object_id = int(payload.get('objectId'))
        if (object_id == 0):
            document = self.context.run_command('document::new', values=payload)
        else:
            document = self.context.run_command('document::get', id=object_id)
            if document:
                document = self.context.run_command('document::set', values=payload, object=document)
            else:
                raise CoilsException('Unable to marshall requested documentId#{0} for update'.format(object_id))
        return document        

    def delete_enterprise(self, object_id, flags):
        enterprise = self.context.run_command('enterprise::get', id=object_id)
        if (enterprise is not None):
            return self.context.run_command('enterprise::delete', object=enterprise)
        return False

    def put_enterprise(self, payload, flags):
        object_id = int(payload.get('objectId'))
        if (object_id == 0):
            enterprise = self.context.run_command('enterprise::new', values=payload)
        else:
            enterprise = self.context.run_command('enterprise::set', values=payload, id=object_id)
        return enterprise

    def put_lock(self, payload, flags):
        ''' { 'targetObjectId': opts.objectid, 
              'token': 'asdklfasdkjlfasdlkjfadsf',
              'entityName': 'lock',
              'targetObjectId': opts.contextid,
              'action': 'denied',
              'operations': 'wdlvx' } '''
        object_id = int( payload[ 'targetObjectId' ] )
        if object_id:
            entity = self.context.type_manager.get_entity( object_id )
            if entity:
                operations = payload.get( 'operations', 'w' ).lower( )
                duration   = int( payload.get( 'duration', 3600 ) )
                result, lock = self.context.lock_manager.lock( entity,
                                                               duration  = duration,
                                                               data      = None,
                                                               delete    = True if 'd' in operations else False,
                                                               write     = True if 'w' in operations else False,
                                                               run       = True if 'x' in operations else False,
                                                               exclusive = True if payload.get('exclusive', 'NO').upper() == 'YES' else False )
                if result:
                    return lock
        return None
        
    def delete_lock(self, payload, flags):
        object_id = int( payload.get( 'targetObjectId', 0 ) )
        if object_id:
            entity = self.context.type_manager.get_entity( object_id )
            if entity:
                if self.context.lock_manager.unlock( entity ):
                    return True
        return None

    def put_folder(self, payload, flags):
        object_id = int(payload.get('objectId'))
        # TODO: Implement
        if (object_id == 0):
            folder = self.context.run_command('folder::new', values=payload)
        else:
            folder = self.context.run_command('folder::set', values=payload, id=object_id)
        return folder

    def put_note(self, payload, flags):
        # TODO: Implement
        raise 'Not Implemented'

    def put_message(self, payload, flags):
        process_id = Caseless_Get(payload, 'processid')
        if not process_id:
            process_id = Caseless_Get(payload, 'processobjectid')
        if process_id:
            process = self.context.run_command('process::get', pid=process_id)
            if process:
                # Process exists, create message
                data = Caseless_Get(payload, 'data')
                if data:
                    data = base64.decodestring(payload['data'])
                else:
                    data = ''
                mimetype = Caseless_Get(payload, 'mimetype')
                if not mimetype:
                    mimetype = u'application/octet-stream'
                message = self.context.run_command('message::new', process=process,
                                                                   mimetype=mimetype,
                                                                   label=Caseless_Get(payload, None),
                                                                   data=data)
                self.context.commit()
                # Message commit'd to database - request process start
                # A process start signal is always implied by message creation - in this manner
                # the creation of a message may bring a process out of a parked state [if this is not
                # the message the process was waiting for it will return itself to a parked state]
                self.context.run_command('process::start', process=process)
                return message
            else:
                # TODO: Raise exception
                pass
        else:
            # TODO: Raise exception
            pass

    def put_note(self, payload, flags):
        # TODO: Implement
        raise 'Not Implemented'        

    def put_objectlink(self, payload, flags):
        # TODO: Implement
        raise 'Not Implemented'

    def put_objectproperty(self, payload, flags):
        object_id = Caseless_Get(payload, 'parentobjectid')
        if object_id:
            property_name = Caseless_Get(payload, 'propertyName')
            if property_name:
                namespace, attribute = PropertyManager.Parse_Property_Name(property_name)
            else:
                namespace = Caseless_Get(payload, 'namespace')
                attribute = Caseless_Get(payload, 'attribute')
            if namespace and attribute:
                entity = self.context.type_manager.get_entity(object_id)
                if entity:
                    self.context.property_manager.set_property(entity, namespace, attribute, Caseless_Get(payload, 'value'))
                    self.context.commit()
                    return entity
                else:
                    raise CoilsException('Entity objectId#{0} unavailable.'.format(object_id))
        raise CoilsException('ObjectProperty format invalid')

    def delete_objectproperty(self, payload, flags):
        object_id = Caseless_Get(payload, 'parentobjectid')
        entity = self.context.type_manager.get_entity(object_id)
        if entity:
            property_name = Caseless_Get(payload, 'propertyName')
            if property_name:
                namespace, attribute = PropertyManager.Parse_Property_Name(property_name)
            else:
                namespace = Caseless_Get(payload, 'namespace')
                attribute = Caseless_Get(payload, 'attribute')
            if namespace and attribute:
                self.context.property_manager.delete_property(entity, namespace, attribute)
                return True
            else:
                raise CoilsException('ObjectProperty format invalid')
        else:
            raise CoilsException('Entity objectId#{0} unavailable.'.format(object_id))

    def put_participantstatus(self, payload, flags):
        """ { 'comment': 'My very very very very long comment',
              'objectId': 10621,
              'rsvp': 1,
              'status': 'TENTATIVE',
              'entityName': 'ParticipantStatus' } """
        # The objectId is the objectId of THE APPOINTMENT, participantStatus is
        # unique in that it is a write-only entity.
        self.context.begin()
        object_id = int(payload['objectId'])
        self.context.run_command('participant::set', appointment_id=object_id,
                                                     participant_id=self.context.account_id,
                                                     status=payload.get('status', 'NEEDS-ACTION'),
                                                     comment=payload.get('comment', None),
                                                     rsvp=payload.get('rsvp',    None))
        self.context.commit()
        appointment = self.context.run_command('appointment::get', id=object_id)
        return appointment

    def delete_process(self, object_id, flags):
        process = self.context.run_command('process::get', id=object_id)
        if (process is not None):
            result = self.context.run_command('process::delete', object=process)
            return result
        return False

    def put_process(self, payload, flags):

        def get_priority(data, process):
            if 'priority' in data:
                priority = data['priority']
            elif process:
                priority = process.priority
            else:
                priority = 250
            if priority < 1:
                priority = 1
            elif priority > 250:
                priority = 250
            return priority

        object_id = int(payload.get('objectId', 0))
        # determine if a request to queue has been made
        if payload.get('state', 'I') == 'Q':
            queue = True
        else:
            queue = False

        # Create or update?
        if object_id:
            process = self.context('process:get', pid=object_id)
            if process:
                payload['priority'] = get_priority(payload, None)
            else:
                #TODO: Fail gracefully, somehow?
                pass
            process = self.context('process::set', object=process, values=payload)
        else:
            # alsy set state to I, don't let the client send us bogus states
            payload['state'] = 'I'
            payload['priority'] = get_priority(payload, None)
            # get mimetype of the input from the payload, then remove that attribute
            mimetype = payload.get('mimetype', 'application/octet-stream')
            if 'mimetype' in payload: del payload['mimetype']
            # get the data from the payload, base64 decode it
            if 'data' in payload:
                data = base64.decodestring(payload['data'])
                payload['data'] = data
            else:
                payload['data'] = ''
            process=self.context.run_command('process::new', values=payload, mimetype=mimetype )
            self.context.commit()
            if process and queue:
                self.context.run_command('process::start', process=process)
        return process

    def put_project(self, payload, flags):
        object_id = Caseless_Get(payload, 'objectid')
        if object_id:
            project = self.context.run_command('project::set', values=payload, id=object_id)
        else:
            project = self.context.run_command('project::new', values=payload)
        self.context.commit()
        return project

    def put_resource(self, payload, flags):
        # TODO: Implement
        raise 'Not Implemented'

    def put_task(self, payload, flags):
        object_id = int(payload.get('objectId', 0))
        if (object_id == 0):
            task = self.context.run_command('task::new', values=payload)
        else:
            task = self.context.run_command('task::set', values=payload, id=object_id)
        return task

    def put_tasknotation(self, payload, flags):
        object_id = int(payload.get('taskObjectId'))
        task = self.context.run_command('task::comment', values=payload, id=object_id)
        return task

    def delete_task(self, object_id, flags):
        return self.context.run_command('task::delete', id=object_id)

    def put_team(self, payload, flags):
        # TODO: Implement
        raise 'Not Implemented'

    def put_workflow(self, payload, flags):
        # TODO: Implement
        raise 'Not Implemented'

    def get_tombstone(self, object_id, flags):
        object_id = int(object_id)
        audit_entry = self.context.run_command('object::get-tombstone', id=object_id)
        if audit_entry:
            if audit_entry.actor is None:
                actor_text = None
            else:
                actor_text = audit_entry.actor.login
            return { 'entityName': 'Tombstone',
                     'actor': actor_text,
                     'eventTime': audit_entry.datetime,
                     'actorObjectId': audit_entry.actor_id,
                     'deletedObjectId': audit_entry.context_id,
                     'message': audit_entry.message }
        return { 'entityName': 'Unknown' }

    def list_tasks(self, list_set):
        if list_set == 'archived':
            tasks = self.context.run_command('task::get-archived')
        else:
            tasks = self.context.run_command('task::get-current')
        result = [ ]
        for task in tasks:
            result.append( { 'objectId':    task.object_id,
                             'entityName':  task.__entityName__,
                             'displayName': task.get_display_name(),
                             'version':     task.version } )
        return result

    def list_projects(self, list_set):
        projects = self.context.run_command('account::get-projects')
        result = [ ]
        for project in projects:
            result.append( { 'objectId':    project.object_id,
                             'entityName':  project.__entityName__,
                             'displayName': project.get_display_name(),
                             'version':     project.version } )
        return result

    def list_contacts(self, list_set):
        if list_set == 'users':
            contacts = self.context.run_command('account::get-all')
        else:
            contacts = [ ]
        result = [ ]
        for contact in contacts:
            result.append( { 'objectId':    contact.object_id,
                             'entityName':  'Contact',
                             'displayName': contact.get_display_name(),
                             'version':     contact.version } )
        return result

    def list_teams(self, list_set):
        result = [ ]
        for team in self.context.run_command('team::get'):
            result.append( { 'objectId':    team.object_id,
                             'entityName':  'Team',
                             'displayName': team.get_display_name(),
                             'version':     team.version } )
        return result

    def get_object_versions_by_id(self, ids):
        # TODO: Implement
        # Result: [{'entityName': 'Appointment', 'version': [''], 'objectId': 29420},
        #          {'entityName': 'Enterprise', 'version': [3], 'objectId': 21060},
        #          {'entityName': 'Contact', 'version': [7], 'objectId': 10120}]
        # http://code.google.com/p/zogi/wiki/getObjectVersionsById
        index = self.context.type_manager.group_ids_by_type(ids)
        result = [ ]
        for object_id in index.keys():
            if key == 'Unknown':
                for object_id in index[key]:
                    result.append( { 'entityName': 'Unknown',
                                     'version': [ '' ],
                                     'objectId': object_id  } )
            else:
                x = getattr(self, 'get_%ss_by_ids' % key.lower())(index[key])
                if (x is None):
                    self.context.log.debug('result of Logic was None')
                else:
                    for entity in x:
                        result.append( { 'entityName': x.__entityName__,
                                         'version': [ x.version ],
                                         'objectId':  x.object_id } )
        return result

    def list_objects_by_type(self, kind, list_name):
        entity_name = kind.lower()
        if hasattr(self, 'list_{0}s'.format(entity_name)):
            method = getattr(self, 'list_{0}s'.format(entity_name))
            return method(list_name)
        else:
            raise NotImplementedException('Cannot list objects of type {0}'.format(kind))
            
    def get_performance(self, category):
        if isinstance( category, basestring ):
            data = self.context.run_command('admin::get-performance-log', lname=category)
            result = [ ]
            # Results must be a list, outer dictionaries are too confusing, so we flatten
            # the performance results into a list moving the key into the value
            for key, value in data.items():
                value[ 'command' ] = key
                result.append ( value )
            return result
        return [ ]
        
    def ps(self):
        return self.context.run_command('workflow::get-process-list')
