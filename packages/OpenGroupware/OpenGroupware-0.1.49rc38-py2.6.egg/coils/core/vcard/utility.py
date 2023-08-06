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
from coils.core import CoilsException


def determine_ogo_tel_type(parameters, singletons, version21_hack_enabled, **params):
    """
    Determine the OGo/Coils telephone entry type from the attribtues of a vCARD TEL element
    :param params:
    :param singletons:
    :param version21_hack_enabled:
    """

    if 'X-COILS-TEL-TYPE' in params:
        return parameters[ 'X-COILS-TEL-TYPE' ][ 0 ]

    # preseve the types sent to us my the client
    if 'TYPE' in parameters:
        caldav_types = [ x.upper( ) for x in parameters[ 'TYPE' ] ]
    elif version21_hack_enabled:
        caldav_types = [ x.upper( ) for x in singletons ]
    else:
        return None

    if 'FAX' in caldav_types:
        if 'HOME' in caldav_types: return "15_fax_private"
        else: return "10_fax"
    if 'PAGER' in caldav_types:
        if 'HOME' in caldav_types: return '20_pager_private'
        return '20_pager'
    if 'VOICE' in caldav_types and len( caldav_types ) == 1:
        # VOICE is the only type provided, we assume this is the primary phone#
        return '01_tel'
    if 'VOICE' in caldav_types and 'PREF' in caldav_types:
        return '01_tel'
    # Assuming VOICE type
    if 'CELL' in caldav_types: return '03_tel_funk'
    if 'WORK' in caldav_types: return '02_tel'
    if 'HOME' in caldav_types: return '05_tel_private'

    return None


def determine_ogo_address_type(parameters, singletons, version21_hack_enabled, **params):
    """
    Determine the OGo/Coils address entry from the attribtues of a vCARD ADR element
    :param params:
    :param singletons:
    :param version21_hack_enabled:
    """

    def translate_contact_type( values ):
        if 'HOME' in values: return 'private'
        elif 'WORK' in values: return 'mailing'
        else: return 'location'

    entity_name = params.get('entity_name', 'Contact')
    # TODO: Is the X-EVOLUTION-UI-SLOT=1 attribute usefule in any way? Can
    # we at least preserve that as an object property?  Yes [2010-07-23], we
    # can save it as an object property like we do with the type/kind
    # attributes from the EMAIL attribute when saving the email? CompanyValues.
    if ('X-COILS-ADDRESS-TYPE' in parameters):
       return parameters['X-COILS-ADDRESS-TYPE'][0]
    elif 'TYPE' in parameters:
        # ADR element does not contain a X-COILS-ADDRESS-TYPE property
        # so we need to generate an OGo address type from the vCard
        # TYPE params
        #
        attributes = [ x.upper() for x in parameters['TYPE'] ]
    elif version21_hack_enabled:
        attributes = [ x.upper() for x in singletons ]
    else:
        attribtues = None

    if attributes:
        if entity_name == 'Contact':
            return translate_contact_type( attributes )
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

