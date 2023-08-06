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
import datetime, re, hashlib, base64, vobject
from dateutil.tz    import gettz
from coils.core     import CoilsException

def hash_for_data(value_):
        hash_ = hashlib.sha512()
        hash_.update(value_)
        return hash_.hexdigest()

def take_integer_value(values, key, name, vevent, default=None):
    key = key.replace('-', '_')
    if (hasattr(vevent.key)):
        try:
            values[name] = int(getattr(vevent, key).value)
        except:
            values[name] = default


def take_string_value(values, key, name, vevent, default=None):
    key = key.replace('-', '_')
    if (hasattr(vevent.key)):
        try:
            values[name] = str(getattr(vevent, key).value)
        except:
            values[name] = default


def find_attendee(ctx, email, log):
    if (len(email.strip()) < 6):
        #E-Mail address is impossibly short, don't even bother
        return None
    contacts = ctx.run_command('contact::get', email=email)
    if (len(contacts) == 1):
        contact_id = contacts[0].object_id
        log.debug('Found contact objectId#{0} for e-mail address {1}'.format(contact_id, email))
        return contact_id
    elif (len(contacts) > 1):
        log.warn('Multiple contacts found for e-mail address {0}'.format(email))
    else:
        log.warn('No contact found for e-mail address {0}'.format(email))
    teams = ctx.run_command('team::get', email=email)
    if (teams):
        if (len(teams) > 1):
            log.warn('Multiple teams found for e-mail address {0}'.format(email))
        return teams[0].object_id
    resources = ctx.run_command('resource::get', email=email)
    if (resources):
        if (len(resources) > 1):
            log.warn('Multiple resources found for e-mail address {0}'.format(email))
        return resources[0].object_id
    return None


def parse_attendee(line, ctx, log):
    # Attemdee
    pass

"""
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//PYVOBJECT//NONSGML Version 1//EN
BEGIN:VTODO
DESCRIPTION:*****************
DTSTART:20100716T094709Z
DUE:20100723T094709Z
ORGANIZER;CUTYPE=INDIVIDUAL;CN=Adam Tauno
  Williams:MAILTO:awilliam@whitemice.org
PERCENT-COMPLETE:0
PRIORITY:1
STATUS:NEEDS-ACTION
SUMMARY:*************************
UID:coils://Task/15349830
URL:http://**************/Tasks/view/15349830/History/
X-COILS-KIND:None
X-COILS-PROJECT;X-COILS-PROJECT-ID=1025770:************
END:VTODO
END:VCALENDAR
"""

def parse_vtodo(event, ctx, log, starts=[], duration=None, **params):
    # NOTE: vObject is kind enough to give us timezone aware datetimes from
    # start and end elements.  So this utz_tc value is used to convert those
    # TZ aware values to UTC for internal storage.
    utc_tz = gettz('UTC')
    values = {}
    for line in event.lines( ):
        
        if line.name == 'UID':
            values[ 'uid' ] = line.value
            
        elif line.name == 'STATUS':
            if line.value == 'NEEDS-ACTION':
                values[ 'status' ] = '00_created'
            elif line.value == 'IN-PROCESS':
                values[ 'status' ] = '20_processing'
            elif line.value == 'CANCELLED':
                values[ 'status' ] = '02_rejected'
            elif line.value == 'COMPLETED':
                values[ 'status' ] = '25_done'
                
        elif line.name == 'ATTENDEE':
            pass
            
        elif line.name == 'SUMMARY':
            values[ 'title' ] = line.value
            
        elif line.name == 'DESCRIPTION':
            values[ 'comment' ] = line.value
            
        elif line.name == 'PERCENT-COMPLETE':
            # HACK: Complete must be a multiple of 10; like 10, 20, 30, 40,...
            if line.value.isdigit():
                values[ 'complete' ] = int((int(line.value) / 10) * 10)
                
        elif line.name == 'PRIORITY':
            """ RFC2445 4.8.1.9 Priority
                Description: The priority is specified as an integer in the range
                zero to nine. A value of zero (US-ASCII decimal 48) specifies an
                undefined priority. A value of one (US-ASCII decimal 49) is the
                highest priority. A value of two (US-ASCII decimal 50) is the second
                highest priority. Subsequent numbers specify a decreasing ordinal
                priority. A value of nine (US-ASCII decimal 58) is the lowest
                priority.

                A CUA with a three-level priority scheme of "HIGH", "MEDIUM" and
                "LOW" is mapped into this property such that a property value in the
                range of one (US-ASCII decimal 49) to four (US-ASCII decimal 52)
                specifies "HIGH" priority. A value of five (US-ASCII decimal 53) is
                the normal or "MEDIUM" priority. A value in the range of six (US-
                ASCII decimal 54) to nine (US-ASCII decimal 58) is "LOW" priority. """
            if line.value == 'LOW':      values[ 'priority' ] = 5
            elif line.value == 'MEDIUM': values[ 'priority' ] = 3
            elif line.value == 'HIGH':   values[ 'priority' ] = 1
            elif line.value.isdigit( ):
                tmp = int( line.value )
                if tmp == 0 or tmp == 5: values[ 'priority' ] = 3
                elif tmp < 5: values[ 'priority' ] = 1
                elif tmp > 6: values[ 'priority' ] = 5
                else: raise CoilsException( 'Illegal numeric PRIORTY value "{0}" in VTODO'.format( line.value ) )
            else: raise CoilsException( 'Illegal PRIORTY value "{0}" in VTODO'.format( line.value ) )
            
        elif line.name == 'ATTACH':
            # TODO: Implement storing of attachments, of catching changes to attachments
            #       We probably need a SHA checksum for this too work
            ''' ATTACH;VALUE=BINARY;
                       ENCODING=BASE64;
                       X-EVOLUTION-CALDAV-ATTACHMENT-NAME=curl-json-rpc.php:
                         PD9QSFAKCmZ1bmN0aW9uIHpPR0lKU09OUlBDQ2FsbCgkdXNlcm5hbWUsICRwYXNzd29yZCwgJG
                         1ldGhvZCwgJHBhcmFtcywgCiAgICAgICAgICAgICAgICAgICAgICAgICAkaWQ9bnVsbCwgCiAg ... '''
            if ( ( line.params.get( 'VALUE', [ 'NOTBINARY' ] )[ 0 ] == 'BINARY' ) and
                 ( line.params.get( 'ENCODING', [ 'NOTBASE64' ] )[ 0 ] == 'BASE64' ) ):
                if '_ATTACHMENTS' not in values:
                    values[ '_ATTACHMENTS' ] = [ ]
                # Try to get at attachment name using one of the following attributes
                for attr in ( 'X-EVOLUTION-CALDAV-ATTACHMENT-NAME', 'X-ORACLE-FILENAME', 'X-COILS-FILENAME' ):
                    if attr in line.params:
                        name_ = line.params[ attr ][ 0 ]
                        break
                else:
                    name_ = None
                data_ = base64.decodestring( line.value )
                hash_ = hash_for_data( data_ )
                size_ = len( data_ )
                mime_ = line.params.get( 'FMTTYPE', [ 'application/octet-stream' ] )[ 0 ]
                values[ '_ATTACHMENTS' ].append( { 'entityName': 'Attachment',
                                                   'sha512checksum': hash_,
                                                   'data': data_,
                                                   'name': name_,
                                                   'mimetype': mime_,
                                                   'size': size_ } )
            else:
                # TODO: ticket#53 Support non-binary [aka "link"?] attachments 
                raise CoilsException( 'Unable to parse CalDAV ATTACH; not a binary attachment.' )
                
        elif line.name == 'CATEGORIES':
            value = None
            if isinstance( line.value, list ):
                if value:
                    value = line.value[ 0 ].strip( )
                else:
                    value = ''
            elif isinstance( line.value, basestring ):
                value = line.value.strip( )
            if value:
                value = value.replace( '\,', ',' )
                value = value.split( ',' )
                value = ','.join( [ x.strip( ) for x in value ] )
                values[ 'category' ] = value
                
        elif line.name == 'ORGANIZER':
            # TODO: This should only be available to someone with the HELPDESK role
            pass
            
        elif line.name == 'CLASS':
            """ RFC2445 4.8.1.3 Classification
                classvalue = "PUBLIC" / "PRIVATE" / "CONFIDENTIAL" """
            if line.value == 'PUBLIC': values[ 'sensitivity' ] = 0
            elif line.value == 'PRIVATE': values[ 'sensitivity' ] = 2
            elif line.value == 'CONFIDENTIAL': values[ 'sensitivity' ] = 3
            
        elif line.name == 'DUE':
            """ RFC2445 4.8.2.3 Date/Time Due
                Purpose: This property defines the date and time that a to-do is
                expected to be completed.
                Value Type: The default value type is DATE-TIME. The value type can
                be set to a DATE value type. """
            if isinstance( line.value, datetime.date ):
                values['end'] = line.value
            elif isinstance( line.value, datetime.datetime):
                values['end'] = line.value.locallize(utc_tz)
            else:
                raise CoilsException( 'Illegal data type "{0}" in VTODO DUE'.format( type( line.value ) ) )    
                
        elif line.name == 'DTSTART':
            """ RFC2445 4.8.2.4 Date/Time Start
                Purpose: This property specifies when the calendar component begins.
                Value Type: The default value type is DATE-TIME. The time value MUST
                be one of the forms defined for the DATE-TIME value type. The value
                type can be set to a DATE value type """
            if isinstance( line.value, datetime.date ):
                values[ 'start' ] = line.value
            elif isinstance( line.value, datetime.datetime ):
                values[ 'start' ] = line.value.locallize( utc_tz )
            else:
                raise CoilsException( 'Illegal data type "{0}" in VTODO DTSTART'.format( type( line.value ) ) )
                
        elif line.name == 'X-COILS-OBJECT-ID':
            values[ 'object_id' ] = int( line.value )
                
        elif line.name == 'X-COILS-PROJECT':
            # TODO: Check for project id parameter
            pass
            
        elif line.name =='X-COILS-KIND':
            values[ 'kind' ] = line.value
            
        else:
            # TODO: Save unknown properties as properties so we can put them back
            pass
            
    return [ values ]
