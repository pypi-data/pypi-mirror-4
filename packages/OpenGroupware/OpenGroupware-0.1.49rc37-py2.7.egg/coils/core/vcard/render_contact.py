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
import vobject
from render_company import *

def render_contact(contact, ctx, **params):

    # VCard *REQUIRES* a first and last name.  If we do not have a last name
    # we put in the object id, then we have at least something unique there.
    first_name = contact.first_name if contact.first_name else 'unknown'
    last_name = contact.last_name if contact.last_name else unicode( contact.object_id )

    card = vobject.vCard()

    if contact.uid:
        card.add( 'uid' ).value = contact.uid
    else:
        card.add( 'uid' ).value = '{0}@{1}'.format( contact.object_id, ctx.cluster_id )

    # RFC2426 3.1.2 "N" [REQUIRED]
    card.add('n').value = vobject.vcard.Name( family = last_name, given = first_name )

    # RFC2426 3.1.1 "FN" [REQUIRED]
    if contact.file_as:
        file_as = contact.file_as
    else:
        file_as = '{0}, {1}'.format( last_name, first_name )
    card.add( 'fn' ).value = file_as
    card.add( 'x-evolution-file-as' ).value = file_as

    # RFC2426 3.1.3 "NICKNAME"
    if contact.display_name:
        card.add('nickname').value = contact.display_name

    # X-JABBER (used by what clients?)
    if contact.im_address:
        card.add('x-jabber').value = contact.im_address

    # TODO: BDAY (Make birthday work)
    #if (contact.birth_date is not None):
    #    card.add('bday'). value = contact.birth_date

    # TODO: Construct a FB URL, short form
    # FBURL

    # RFC2426 2.1.4 "SOURCE"
    card.add('source').value = 'coils://{0}/{1}'.format( ctx.cluster_id[1:-1], contact.object_id )

    # TODO: NAME
    # NAME:vCard for contact with id 10100 (v1275)

    # RFC2426 3.6.2 "NOTE"
    if contact.comment:
        card.add("note").value = contact.comment

    # TODO: PHOTO

    # RFC2426 3.5.5 "ORG"
    if (((contact.associated_company is not None) and (len(contact.associated_company)> 0)) or
        ((contact.department is not None) and (len(contact.department)> 0))  or
        ((contact.office is not None) and (len(contact.office)> 0))):
        card.add('org').value = [ contact.associated_company if contact.associated_company is not None else '',
                                  contact.department if contact.department is not None else '',
                                  contact.office if contact.office is not None else '' ]

    # TODO: REV : "combination of the calendar date and time of day of the last
    #              update to the vCard object"
    #       This is the last modified datetime?

    # TODO: URL

    # TODO: KEY : "the public encryption key associated with the vCard object"

    # TODO: AGENT : "information about another person who will act on behalf of
    #                the vCard object. Typically this would be an area administrator,
    #                assistant, or secretary for the individual"

    # TODO: GEO : "The property specifies a latitude and longitude"

    # TODO: TZ : "information related to the standard time zone of the vCard object"
    #        Is this the contacts's time zone or the timezone of the server?

    # ROLE : "the role, occupation, or business category of the vCard
    #         object within an organization (eg. Executive)"
    if (contact.occupation is not None):
        if (len(contact.occupation) > 0):
            card.add('role').value = contact.occupation

    # TODO: LOGO

    # TODO: X-ANNIVERSARY : "arbitrary anniversary, in addition to BDAY = birthday"
    # Also: X-EVOLUTION-ANNIVERSARY

    # X-ASSISTANT : "assistant name (instead of Agent)"
    # Also: X-EVOLUTION-ASSISTANT
    if (contact.assistant_name is not None):
        if (len(contact.assistant_name) > 0):
            card.add('x-assistant').value = contact.assistant_name
            card.add('x-evolution-assistant').value = contact.assistant_name

    # X-MANAGER : "manager name"
    # Also: X-EVOLUTION-MANAGER
    if (contact.boss_name is not None):
        if (len(contact.boss_name) > 0):
            card.add('x-manager').value = contact.boss_name
            card.add('x-evolution-manager').value = contact.boss_name

    # X-SPOUSE : "spouse name"
    # Also: X-EVOLUTION-SPOUSE
    if (contact.partner_name is not None):
        if (len(contact.partner_name) > 0):
            card.add('x-spouse').value = contact.partner_name
            card.add('x-evolution-spouse').value = contact.partner_name

    # TODO: X-MS-IMADDRESS

    # TODO: X-MS-CARDPICTURE
    # Same as PHOTO or LOGO ?

    # TODO: X-EVOLUTION-BLOG-URL

    # TODO: X-EVOLUTION-TTYTDD

    # X-MOZILLA-HTML: We will never promote the evil of HTML e-mail
    card.add('x-mozilla-html').value = 'FALSE'

    # CATEGORIES
    if (contact.keywords is not None):
        if (len(contact.keywords) > 0):
            card.add('categories').value = contact.keywords

    # PRODID:-//OpenGroupware.org//LSAddress v5.5.111
    # TODO: Why?

    # PROFILE
    #card.add('profile').value = 'vCard'

    # CLASS
    # TODO: Use sensitivity value (?)
    card.add('class').value = 'PUBLIC'

    # X-COILS-*
    if ctx.user_agent_description[ 'vcard' ][ 'includeCoilsXAttributes' ]:
        # ObjectId
        x = card.add( 'x-coils-objectid' )
        x.value = str( contact.object_id )
        # Is account?
        x = card.add( 'x-coils-account' )
        if contact.is_account == 1:
            x.value = 'YES'
            x.x_coils_account_id_param = str( contact.object_id )
            x.x_coils_account_login_param = str( contact.login )
        else:
            x.value = 'NO'

    render_address(card, contact.addresses, ctx)
    render_telephones(card, contact.telephones, ctx)
    render_company_values(card, contact.company_values, ctx)

    if ctx.user_agent_description[ 'vcard' ][ 'includeObjectPropertes' ]:
        pm = ctx.property_manager
        render_properties(card,
                          pm.get_properties(contact),
                          exclude_namespace = ['http://coils.opengroupware.us/admin'])

    return (str(card.serialize(lineLength=5096)))
