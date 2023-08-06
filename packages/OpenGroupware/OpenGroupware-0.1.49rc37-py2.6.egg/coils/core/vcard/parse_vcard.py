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
from coils.core import CoilsException
from utility import determine_ogo_address_type, determine_ogo_tel_type
from exception import UntypedTelephoneValueException, UntypedAddressValueException


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


def parse_vcard(card, ctx, log, **params):

    version21_hack_enabled = False
    if card.version.value == u'2.1':
        version21_hack_enabled = True

    entity_name = params.get('entity_name', 'Contact')
    if (entity_name not in ['Contact', 'Enterprise']):
        raise CoilsException('Parsing to this kind of entity not supported.')

    values = {}
    emails = []
    davuid = None
    for line in card.lines():
        if line.name == 'UID':
            # UID
            values[ 'carddav_uid' ] = line.value
            davuid = line.value
            log.debug( 'vCard UID: {0}'.format( line.value ) )
        elif line.name == 'ADR':
            # ADR (Postal Address)
            # TODO: It is always good to make this more intelligent
            kind = determine_ogo_address_type( line.params,
                                               line.singletonparams,
                                               version21_hack_enabled, **params)
            # WARN: If kind is None the address is discarded [on purpose, not a bug]
            if kind:
                log.debug( 'storing address of type "{0}"; street "{1}"'.format( kind, line.value.street ) )
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
            telephone = { 'type': determine_ogo_tel_type( line.params,
                                                          line.singletonparams,
                                                          version21_hack_enabled, **params ) }
            # preserve the actual telephone value
            telephone[ 'number' ] = line.value

            if not telephone[ 'type' ]:
                raise UntypedTelephoneValueException( line.value )
            else:
                log.debug( 'storing telephone of type "{0}"; number "{1}"'.format( telephone[ 'type' ], line.value ) )
                values[ '_PHONES' ].append( telephone )

        elif line.name == 'N':
            values[ 'lastName' ] = line.value.family
            values[ 'firstName' ] = line.value.given
            # Also contains: additional, prefix, suffix
        elif line.name == 'NICKNAME':
            values[ 'descripion' ] = line.value
        elif line.name == 'X-EVOLUTION-FILE-AS':
            values[ 'fileAs' ] = line.value
        elif line.name == 'X-EVOLUTION-MANAGER':
            # TODO: Implement, bossName
            values[ 'managersname' ] = line.value
        elif line.name == 'X-EVOLUTION-ASSISTANT':
            values[ 'assistantName' ] = line.value
        elif line.name == 'X-EVOLUTION-SPOUSE':
            # TODO: Implement, spouseName
            log.debug( 'TODO: support X-EVOLUTION-SPOUSE attribute' )
        elif line.name == 'X-EVOLUTION-ANNIVERSARY':
            # TODO: Implement, anniversary
            log.debug( 'TODO: support X-EVOLUTION-ANNIVERSARY attribute' )
        elif line.name == 'ROLE':
            values[ 'occupation' ] = line.value
            pass
        elif line.name == 'BDAY':
            # TODO: Implement
            log.debug( 'TODO: support BDAY attribute' )
        elif line.name == 'CALURL':
            # TODO: Implement
            log.debug( 'TODO: support CALURL attribute' )
        elif line.name == 'FBURL':
            log.debug( 'TODO: support FBURL attribute' )
        elif line.name == 'NOTE':
            # TODO: Implement, comment
            log.debug( 'TODO: support COMMENT attribute' )
        elif line.name == 'CATEGORIES':
            # TODO: Implement, keywords
            log.debug( 'TODO: support CATGORIES attribute' )
        elif line.name == 'CLASS':
            # TODO: Implement, sensistivity
            log.debug( 'TODO: support CLASS attribute' )
        elif line.name == 'ORG':
            values[ 'associatedcompany' ] = line.value[ 0 ]
            if len(line.value) > 1:
                values[ 'department' ] = line.value[ 1 ]
            if len(line.value) > 2:
                values[ 'office' ] = line.value[ 2 ]
            pass
        elif line.name == 'EMAIL':
            # NOTE: We construct a dict of the e-mail attributes we understand, we build them
            # all up in this array of dicts and then the e-mails are all syncronized to
            # company values after parsing is complete
            kind = line.params.get( 'TYPE', [ ] )
            slot = int( line.params.get( 'X-EVOLUTION-UI-SLOT', [ 0 ] )[ 0 ] )
            log.debug( 'storing e-mail type "{0}"; address "{1}" slot {2}'.format( kind, line.value, slot ) )
            emails.append( { 'value': line.value, 'slot':  slot, 'types': kind } )
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
    if 'objectId' not in values:
        # Attempt to lookup the objectId using the Omphalos values
        if entity_name == 'Contact':
            object_id = _lookup_object_id_of_contact( ctx, davuid, emails, log )
        elif entity_name == 'Enterprise':
            # TODO: Implement
            object_id = None
        elif entity_name == 'Team':
            # TODO: Implement
            object_id = None
        else:
            raise CoilsException( 'Unreachable code point' )

        if not object_id:
            log.debug('Identification of vCard via e-mail search failed.')
        else:
            log.debug('Identified vCard via e-mail search result; objectId = {0}'.format(object_id))
            values[ 'objectId' ] = object_id

    return values


def _lookup_object_id_of_contact(ctx, davuid, emails, log):
    if davuid:
        log.debug( 'Searching for contact by CARDAV/WebDAV UID "{0}"'.format( davuid ) )
        x = ctx.run_command( 'contact::get', uid=davuid )
        if x:
            return x.object_id
    log.debug( 'No WebDAV/CARDAV UID specified' )
    for email in emails:
        log.debug('Searching contacts for e-mail address "{0}"'.format( email['value'] ) )
        x = ctx.run_command('contact::search', criteria = [ { 'key':  'email1',
                                                              'value': email['value'] } ] )
        if (len(x) == 0):
            log.debug('Unable to identify contact via e-mail search: no candidates')
        elif len(x) == 1:
            return x[0].object_id
        else:
            log.debug('Unable to identify contact via e-mail search: too many candidates')
    return None
