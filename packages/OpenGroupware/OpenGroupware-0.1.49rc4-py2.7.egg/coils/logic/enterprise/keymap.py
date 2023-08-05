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
COILS_ENTERPRISE_KEYMAP = {
    'objectid':             ['object_id', 'int', 0],
    'object_id':            ['object_id', 'int', 0],
    'bankcode':             ['bank_code'],
    'email1':               ['email'],
    'fileas':               ['file_as'],
    'imaddress':            ['im_address'],
    'ownerobjectid':        ['owner_id', 'int', 0],
    'ownerid':              ['owner_id', 'int', 0],
    'owner_id':             ['owner_id', 'int', 0],
    'description':          ['name'],
    'is_private':           ['is_private', 'int'],
    'isprivate':            ['is_private', 'int'],
    'private':              ['is_private', 'int'],
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
    'contacts':             None,
    '_contacts':            None,
    'projects':             None,
    '_projects':            None,
    'properties':           None,
    '_properties':          None,
    'notes':                None,
    '_notes':               None,
    'keywords':             ['keywords', 'csv', ' '],
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
    'businesscategory':     ['associated_categories', 'csv', ',']
    }