#
# Copyright (c) 2010, 2011, 2012
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
import datetime, re, vobject
from utility import determine_ogo_tel_type_from_caldav_type


def take_integer_value(values, key, name, vcard, default=None):
    key = key.replace('-', '_')
    if (hasattr(vcard.key)):
        try:
            values[name] = int(getattr(vcard, key).value)
        except:
            values[name] = default

def take_string_value(values, key, name, vcard, default=None):
    key = key.replace('-', '_')
    if (hasattr(vcard.key)):
        try:
            values[name] = str(getattr(vcard, key).value)
        except:
            values[name] = default


def determine_adr_type(attributes, **params):
    entity_name = params.get('entity_name', 'Contact')
    # TODO: Is the X-EVOLUTION-UI-SLOT=1 attribute usefule in any way? Can
    # we at least preserve that as an object property?  Yes [2010-07-23], we
    # can save it as an object property like we do with the type/kind
    # attributes from the EMAIL attribute when saving the email? CompanyValues.
    if ('X-COILS-ADDRESS-TYPE' in attributes):
       return attributes['X-COILS-ADDRESS-TYPE'][0]
    elif ('TYPE' in attributes):
        # ADR element does not contain a X-COILS-ADDRESS-TYPE property
        # so we need to generate an OGo address type from the vCard
        # TYPE params
        #
        if (entity_name == 'Contact'):
            if ('home' in attributes):
                return 'private'
            elif ('work' in attributes):
                return 'mailing'
            else:
                return 'location'
        elif (entity_name == 'Enterprise'):
            #TODO: Implement
            raise NotImplementedException()
        elif (entity_name == 'Team'):
            # Addresses in Team vCards are discarded
            return None
        else:
            # It isn't a Contact, Team, or Enterprise?
            raise CoilException('Unknown vCard to entity correspondence')
    else:
        raise CoilsException('Cannot parse vCard; address with no type')


def parse_vcard(card, ctx, log, **params):
    entity_name = params.get('entity_name', 'Contact')
    if (entity_name not in ['Contact', 'Enterprise']):
        raise CoilsException('Parsing to this kind of entity not supported.')
    values = {}
    emails = []
    for line in card.lines():
        if line.name == 'UID':
            # UID
            # Try to dig the objectId out of the UID
            if (line.value[:8] == 'coils://'):
                if ((entity_name == 'Contact') and
                    (line.value[:16] == 'coils://Contact/') and
                    line.value[16:].isdigit()):
                    values['objectId'] = int(line.value[16:])
                elif ((entity_name == 'Enterprise') and
                      (line.value[:19] == 'coils://Enterprise/') and
                      (line.value[19:].isdigit())):
                    values['objectId'] = int(line.value[19:])
                elif ((entity_name == 'Team') and
                      (line.value[:13] == 'coils://Team/') and
                      (line.value[13:].isdigit())):
                    values['objectId'] = int(line.value[13:])
                else:
                   log.warn('Corrupted COILS UID String: {0}'.format(line.value))
            else:
                log.debug('vCard UID not a COILS id: {0}'.format(line.value))
        elif line.name == 'ADR':
            # ADR (Postal Address)
            # TODO: It is always good to make this more intelligent
            kind = determine_adr_type(line.params, **params)
            # WARN: If kind is None the address is discarded [on purpose, not a bug]
            if (kind is not None):
                if ('_ADDRESSES' not in values):
                    values['_ADDRESSES'] = [ ]
                address = {'type': kind }
                address['name1']      = line.value.extended
                address['city']       = line.value.city
                address['postalCode'] = line.value.code
                address['country']    = line.value.country
                address['state']      = line.value.region
                address['street']     = line.value.street
                values['_ADDRESSES'].append(address)
        elif line.name == 'X-JABBER':
            values['imAddress'] = line.value
        elif line.name == 'TITLE':
            if '_COMPANYVALUES' not in values:
                values['_COMPANYVALUES'] = [ ]
            values['_COMPANYVALUES'].append({'attribute': 'job_title', 'value': line.value })
        elif line.name == 'TEL':
            # TELEPHONE ENTRY
            
            # initialize the _PHONES list in the values if this is the first telephone 
            if ('_PHONES' not in values):
                values['_PHONES'] = [ ]
            # initialize the telehone dictionary type to None
            telephone = { 'type': None }        
            
            # preseve the types sent to us my the client    
            if ('TYPE' in line.params):
                telephone['caldav_types'] = [ x.upper() for x in line.params[ 'TYPE' ] ]
                
            # determine the OGo / COILS telephone type
            if ('X-COILS-TEL-TYPE' in line.params):
                telephone['type'] = line.params['X-COILS-TEL-TYPE'][0]                
            elif 'caldav_types' in telephone:
                telephone[ 'type'] = determine_ogo_tel_type_from_caldav_type( telephone )
            if not telephone[ 'type' ]:
                raise CoilsException('Cannot parse vCard; telephone with no type')
                
            # preserve the actual telephone value
            telephone['number'] = line.value
            
            values['_PHONES'].append(telephone)
            
        elif line.name == 'N':
            values['lastName'] = line.value.family
            values['firstName'] = line.value.given
            # Also contains: additional, prefix, suffix
        elif line.name == 'NICKNAME':
            values['descripion'] = line.value
        elif line.name == 'X-EVOLUTION-FILE-AS':
            values['fileAs'] = line.value
        elif line.name == 'X-EVOLUTION-MANAGER':
            # TODO: Implement, bossName
            values['managersname'] = line.value
        elif line.name == 'X-EVOLUTION-ASSISTANT':
            values['assistantName'] = line.value
        elif line.name == 'X-EVOLUTION-SPOUSE':
            # TODO: Implement, spouseName
            pass
        elif line.name == 'X-EVOLUTION-ANNIVERSARY':
            # TODO: Implement, anniversary
            pass
        elif line.name == 'ROLE':
            values['occupation'] = line.value
            pass
        elif line.name == 'BDAY':
            # TODO: Implement
            pass
        elif line.name == 'CALURL':
            # TODO: Implement
            pass
        elif line.name == 'FBURL':
            values['comment'] = line.value
        elif line.name == 'NOTE':
            # TODO: Implement, comment
            pass
        elif line.name == 'CATEGORIES':
            # TODO: Implement, keywords
            pass
        elif line.name == 'CLASS':
            # TODO: Implement, sensistivity
            pass
        elif line.name == 'ORG':
            values['associatedcompany'] = line.value[0]
            if (len(line.value) > 1):
                values['department'] = line.value[1]
            if (len(line.value) > 2):
                values['office'] = line.value[2]
            pass
        elif line.name == 'EMAIL':
            # NOTE: We construct a dict of the e-mail attributes we understand, we build them
            # all up in this array of dicts and then the e-mails are all syncronized to
            # company values after parsing is complete
            emails.append({ 'value': line.value,
                            'slot':  int(line.params.get('X-EVOLUTION-UI-SLOT', [0])[0]),
                            'types': line.params.get('TYPE', []) })
        elif line.name == 'FN':
            pass
        elif line.name[:22] == 'X-COILS-COMPANY-VALUE-':
            attribute = line.name[22:].lower().replace('-', '_')
            if (len(attribute) > 0):
                if '_COMPANYVALUES' not in values:
                    values['_COMPANYVALUES'] = [ ]
                values['_COMPANYVALUES'].append({'attribute': attribute,
                                                 'value':     line.value})
            pass
        else:
            log.debug('unprocessed vcard attribute {0}'.format(line.name))

    #
    # Processing of vCard input complete, now to complete the Omphalos structure
    #

    # E-Mail Addresses
    if (len(emails) > 0):
        # NOTE: If e-mails were found we walk the list turning the dicts into
        # Omphalos CompanyValue entries.  The magick attribute "xattr" is included
        # in the CompanyValue - it encodes extra information about the e-mail
        # address found in the vCard's EMAIL element.  The company::set command
        # knows how to save xattr to the CompanyValues' object properties.  For
        # information on the xattr format see the render_company_values method
        # in the render_company file.
        #import pprint
        #pprint.pprint(emails)
        if '_COMPANYVALUES' not in values:
            values['_COMPANYVALUES'] = [ ]
        count = 1
        for email in emails:
           values['_COMPANYVALUES'].append({'attribute': 'email{0}'.format(count),
                                             'value':     email['value'],
                                             'xattr':     '1:{0}:{1}:'.\
                                                format(email['slot'],
                                                ','.join(email['types']))})
           count += 1
           if (count == 4):
               # WARN: We only save THREE e-mail addresses.  I suppose we could
               # save more, but we should probably check if an email4, email5, etc...
               # company value has been defined in the server's configuration
               # TODO: Check the above
               break

    # Object ID#
    if ('objectId' not in values):
        # TODO: Attempt to lookup the objectId using the Omphalos values
        if (len(emails) == 0):
            log.debug('No e-mail address provided in vCard, cannot attempt identification via e-mail search')
        else:
            for email in emails:
                x = ctx.run_command('contact::search', criteria = [ { 'key':  'email1',
                                                                      'value': email['value'] } ] )
                if (len(x) == 0):
                    log.debug('Unable to identify contact via e-mail search: no candidates')
                elif (len(x) == 1):
                    object_id = x[0].object_id
                    log.debug('Identified vCard via e-mail search result; objectId = {0}'.format(object_id))
                    values['objectId'] = object_id
                    break
                else:
                    log.debug('Unable to identify contact via e-mail search: too many candidates')
            else:
                log.debug('Identification of vCard via e-mail search failed.')
    return values

