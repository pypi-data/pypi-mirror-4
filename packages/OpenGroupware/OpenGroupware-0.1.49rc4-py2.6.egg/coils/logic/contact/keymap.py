#
# Copyright (c) 2009 Adam Tauno Williams <awilliam@whitemice.org>
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
COILS_CONTACT_KEYMAP = {
    'objectid':             ['object_id', 'int', 0],
    'firstname':            ['first_name'],
    'givenname':            ['first_name'],
    'given_name':           ['first_name'],
    'lastname':             ['last_name'],
    'middle_name':          ['middle_name'],
    'middlename':           ['middle_name'],
    'url':                  ['URL'],
    'URL':                  ['URL'],
    'associatedcompany':    ['associated_company', 'csv', ','],
    'associated_company':   ['associated_company', 'csv', ','],
    'associatedcompanies':  ['associated_company', 'csv', ','],
    'associated_companies': ['associated_company', 'csv', ','],
    'associatedcontacts':   ['associated_contacts', 'csv', ','],
    'associatedcontact':    ['associated_contacts', 'csv', ','],
    'associated_contacts':  ['associated_contacts', 'csv', ','],
    'associated_contact':   ['associated_contacts', 'csv', ','],
    'associatedcategory':   ['associated_categories', 'csv', ','],
    'associatedcategories': ['associated_categories', 'csv', ','],
    'associated_category':  ['associated_categories', 'csv', ','],
    'associated_categories':['associated_categories', 'csv', ','],
    'category':             ['associated_categories', 'csv', ','],
    'categories':           ['associated_categories', 'csv', ','],
    'business_category':    ['associated_categories', 'csv', ','],
    'business_categories':  ['associated_categories', 'csv', ','],
    'businesscategories':   ['associated_categories', 'csv', ','],
    'businesscategory':     ['associated_categories', 'csv', ','],
    'birthdate':            ['birth_date', 'date'],
    'birth_date':           ['birth_date', 'date'],
    'birthday':             ['birth_date', 'date'],
    'birth_day':            ['birth_date', 'date'],
    'displayname':          ['display_name'],
    'fullname':             ['display_name'],
    'full_name':            ['display_name'],
    'description':          ['display_name'],
    'source_url':           ['source_url'],
    'sourceurl':            ['source_url'],
    'fileas':               ['file_as'],
    'imaddress':            ['im_address'],
    'is_account':           ['is_account', 'int'],
    'account':              ['is_account', 'int'],
    'isaccount':            ['is_account', 'int'],
    'is_private':           ['is_private', 'int', 0],
    'isprivate':            ['is_private', 'int', 0],
    'private':              ['is_private', 'int'],
    'bossname':             ['boss_name'],
    'managersname':         ['boss_name'],
    'manager':              ['boss_name'],
    'managers_name':        ['boss_name'],
    'department':           ['department'],
    'assistant':            ['assistant_name'],
    'office':               ['office'],
    'sex':                  ['gender'],
    'deathdate':            ['grave_date', 'date', None],
    'deathday':             ['grave_date', 'date', None],    
    'death_date':           ['grave_date', 'date', None],
    'gravedate':            ['grave_date', 'date', None],
    'grave_date':           ['grave_date', 'date', None],
    'birthname':            ['birth_name'],
    'birthplace':           ['birth_place'],
    'familystatus':         ['family_status'],
    'owner_id':             ['owner_id', 'int', 0],
    'ownerid':              ['owner_id', 'int', 0],
    'ownerobjectid':        ['owner_id', 'int', 0],
    'sensitivity':          ['sensitivity', 'int', 0],
    'keywords':             ['keywords', 'csv', ' '],
    'citizenship':          ['citizenship'],
    'carddav_uid':          ['carddav_uid'],
    'addresses':            None,
    '_addresses':           None,
    'telephones':           None,
    '_phones':              None,
    'logs':                 None,
    '_access':              None,
    'acls':                 None,
    'company_values':       None,
    'companyvalues':        None,
    '_companyvalues':       None,
    'enterprises':          None,
    '_enterprises':         None,
    'teams':                None,
    '_membership':          None,
    'projects':             None,
    '_projects':            None,
    'properties':           None,
    '_properties':          None,
    'notes':                None,
    '_notes':               None,
    'version':              ['version', 'int']
    }

COILS_ASSIGNMENT_KEYMAP = {
    'object_id':        [ 'object_id', 'int', 0],
    'objectid':         [ 'object_id', 'int', 0],
    'parent_id':        [ 'parent_id', 'int', 0],
    'parentid':         [ 'parent_id', 'int', 0],
    'sourceobjectid':   [ 'parent_id', 'int', 0],
    'companyid':        [ 'parent_id', 'int', 0],
    'company_id':       [ 'parent_id', 'int', 0],
    'targetobjectid':   [ 'child_id', 'int', 0],
    'child_id':         [ 'child_id', 'int', 0],
    'childid':          [ 'child_id', 'int', 0],
    'sub_company_id':   [ 'child_id', 'int', 0],
    'subcompanyid':     [ 'child_id', 'int', 0]
    }
    