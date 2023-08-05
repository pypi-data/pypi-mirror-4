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

def _is_none(v):
    if (v is None):
        return ''
    else:
        return str(v)

def render_address(card, addresses, ctx, **params):
    # ADR
    # OpenGroupware:  mailing : WORK
    #                 location : ?
    #                 private : HOME


    for address in addresses.values():
        if address.kind in ctx.user_agent_description['vcard']['adrTypeMap']:
            kind = ctx.user_agent_description['vcard']['adrTypeMap'][address.kind]['types']
            # TODO: Should we allow address types of "other"?  What happens when clients see those?
            adr = card.add('adr')
            adr.value = vobject.vcard.Address(street   = _is_none(address.street),
                                              city     = _is_none(address.city),
                                              region   = _is_none(address.province),
                                              code     = _is_none(address.postal_code),
                                              country  = _is_none(address.country),
                                              box      = '',
                                              extended = _is_none(address.name1))
            adr.type_paramlist = kind
            if ctx.user_agent_description['vcard']['setCoilsTypeInAdr']:
                adr.x_coils_address_type_param = address.kind

def render_telephones(card, phones, ctx, **params):
    # TEL
    # OpenGroupware: 10_fax           fax, work,
    #                15_fax_private
    #                03_tel_funk      cell
    #                01_tel           work, voice
    #                05_tel_private   home, voice
    #                30_pager         pager
    #                31_other1
    for phone in phones.values():
        if phone.kind in ctx.user_agent_description['vcard']['telTypeMap']:
            kind = ctx.user_agent_description['vcard']['telTypeMap'][phone.kind]['types']
            if (ctx.user_agent_description['vcard']['telTypeMap'][phone.kind]['voice'] and
                ctx.user_agent_description['vcard']['setVoiceAttrInTel']):
                kind.append('voice')
            tel = card.add('tel')
            tel.value = _is_none(phone.number)
            tel.type_paramlist = kind
            if ctx.user_agent_description['vcard']['setCoilsTypeInTel']:
                tel.x_coils_tel_type_param = phone.kind
        else:
            # TODO: Can we do something intelligent here, we have an unmapped phone type
            # WARN: Potential data-loss
            pass

def render_company_values(card, values, ctx, **params):
    for name, cv in values.items():
        if ((name in ['email1', 'email2', 'email3']) and
            (cv.string_value is not None) and
            (len(cv.string_value))):
            e = card.add('email')
            e.value = cv.string_value
            kind = []
            prop = ctx.property_manager.get_property(cv, 'http://coils.opengroupware.us/logic', 'xattr01')
            if (prop is None):
                e.x_evolution_ui_slot_param = '0'
            else:
                xattr = prop.get_value()
                # NOTE: xattr01 is a colon delimited list of values describing an e-mail address
                # * first value is version of the xattr01, currently we only parse version "1"
                # * second value is the GNOME Evolution Slot#, this will be zero if the slot# is
                #   undefined - which will be the case if the contact has not been modified using
                #   GNOME Evolution [client should upgrade their software!]
                # * third value is a CSV list of types.  This is the primary purpose of xattr01,
                #   as OpenGroupware Legacy cannot store the e-mail address type properties
                if (xattr is not None) and (len(xattr) > 2) and (xattr[0:2] == '1:'):
                    slot = xattr.split(':')[1]
                    if (slot != '0'):
                        e.x_evolution_ui_slot_param = slot
                    kinds = xattr.split(':')[2].split(',')
                    for _kind in kinds:
                        if (len(_kind) > 0):
                            kind.append(_kind)
            if (len(kind) > 0):
                e.type_param = kind
        elif ((name == 'job_title') and
               (cv.string_value is not None) and
               (len(cv.string_value))):
            card.add('title').value = cv.string_value
        elif ctx.user_agent_description['vcard']['includeCompanyValues']:
            value = None
            if (cv.string_value is not None):
                if (len(cv.string_value) > 0):
                    value = cv.string_value
            elif (cv.integer_value is not None):
                value = str(cv.integer_value)
            if (value is not None):
                x = card.add(('x-coils-company-value-%s' % cv.name))
                x.value = value
                x.x_coils_company_value_widget_param = str(cv.widget)
                if (cv.label is not None):
                    x.x_coils_company_value_label_param = cv.label

def render_properties(card, props, **params):
    # X: Render object properties as X-COILS-PROPERTY- attributes
    for prop in props:
        if (prop.namespace not in params['exclude_namespace']):
            value = None
            if (value is not None):
                x = card.add(('x-coils-property-%s' % prop.name))
                x.value = prop.get_value()
                x.x_coils_property_namespace_param = prop.namespace
