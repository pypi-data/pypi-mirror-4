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
# THE SOFTWARE.
#

COILS_DEFAULT_DEFAULTS = {
    'LSConnectionDictionary': { 'databaseName': 'OGo',
                                'hostName': '127.0.0.1',
                                'password': '',
                                'port': 5432,
                                'userName': 'OGo' },
    'LSDisableEnterpriseProjectCreate': 'YES',
    'AMQConfigDictionary': { 'hostname': '127.0.0.1',
                             'port': 5672,
                             'username': 'guest',
                             'password': 'guest' },
    'LSAttachmentPath': '/var/lib/opengroupware.org/documents',
    'SkyPublicExtendedPersonAttributes': [ { 'key': "email1", 'type': 3 },
                                           { 'key': "email2", 'type': 3 },
                                           { 'key': "email3", 'type': 3 },
                                           { 'key': "job_title" },
                                           { 'key': "other_title1" },
                                           { 'key': "other_title2" }
    ],
    'SkyPrivateExtendedPersonAttributes': [ ],
    'SkyPublicExtendedEnterpriseAttributes': [ { 'key': "email2", 'type': 3 },
                                               { 'key': "email3", 'type': 3 },
                                               { 'key': "job_title" },
                                               { 'key': "other_title1" },
                                               { 'key': "other_title2" }
    ],
    'SkyPrivateExtendedEnterpriseAttributes': [],
    'LSAutoCompanyLoginPrefix': 'OGo',
    'LSAutoCompanyNumberPrefix': 'OGo',
    'LSDisableSessionLog':  False,
    'OGoTeamCreatorRoleName': 'team creators',
    'PYTrustedHosts': [''],
    'LSCalendars': [ ],
    'zOGIExpandAllIntranet': False,
    'OIEProcessDebugEnabled': True,
    'CoilsExtensionMIMEMap': { 'pdf':  'application/pdf',
                               'txt':  'text/plain',
                               'text': 'text/plain',
                               'htm':  'text/html',
                               'html': 'text/html',
                               'tgz':  'application/x-compressed',
                               'gz':   'application/x-compressed',
                               'tar':  'application/x-tar',
                               'jpg':  'image/jpeg',
                               'jpeg': 'image/jpeg',
                               'sxw':  'application/vnd.sun.xml.writer',
                               'stw':  'application/vnd.sun.xml.writer.template',
                               'sxg':  'application/vnd.sun.xml.writer.global',
                               'sxc':  'application/vnd.sun.xml.calc',
                               'stc':  'aapplication/vnd.sun.xml.calc.template',
                               'sxi':  'application/vnd.sun.xml.impress',
                               'sti':  'application/vnd.sun.xml.impress.template',
                               'sxd':  'application/vnd.sun.xml.draw',
                               'std':  'application/vnd.sun.xml.draw.template',
                               'sxm':  'application/vnd.sun.xml.math',
                               'odb':  'application/vnd.oasis.opendocument.database',
                               'odc':  'application/vnd.oasis.opendocument.chart ',
                               'odf':  'application/vnd.oasis.opendocument.formula',
                               'odg':  'application/vnd.oasis.opendocument.graphics',
                               'odi':  'application/vnd.oasis.opendocument.image',
                               'odm':  'application/vnd.oasis.opendocument.text-master',
                               'odp':  'application/vnd.oasis.opendocument.presentation',
                               'ods':  'application/vnd.oasis.opendocument.spreadsheet',
                               'odt':  'application/vnd.oasis.opendocument.text',
                               'otg':  'application/vnd.oasis.opendocument.graphics-template',
                               'oth':  'application/vnd.oasis.opendocument.text-web',
                               'otp':  'application/vnd.oasis.opendocument.presentation-template',
                               'ots':  'application/vnd.oasis.opendocument.spreadsheet-template',
                               'ott':  'application/vnd.oasis.opendocument.text-template',
                               'doc':  'application/msword',
                               'dot':  'application/msword',
                               'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                               'dotx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.template',
                               'docm': 'application/vnd.ms-word.document.macroEnabled.12',
                               'dotm': 'application/vnd.ms-word.template.macroEnabled.12',
                               'xls':  'application/vnd.ms-excel',
                               'xlt':  'application/vnd.ms-excel',
                               'xla':  'application/vnd.ms-excel',
                               'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                               'xltx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.template',
                               'xlsm': 'application/vnd.ms-excel.sheet.macroEnabled.12',
                               'xltm': 'application/vnd.ms-excel.template.macroEnabled.12',
                               'xlam': 'application/vnd.ms-excel.addin.macroEnabled.12',
                               'xlsb': 'application/vnd.ms-excel.sheet.binary.macroEnabled.12',
                               'png':  'image/png',
                               'ppt':  'application/vnd.ms-powerpoint',
                               'pot':  'application/vnd.ms-powerpoint',
                               'pps':  'application/vnd.ms-powerpoint',
                               'ppa':  'application/vnd.ms-powerpoint',
                               'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                               'potx': 'application/vnd.openxmlformats-officedocument.presentationml.template',
                               'ppsx': 'application/vnd.openxmlformats-officedocument.presentationml.slideshow',
                               'ppam': 'application/vnd.ms-powerpoint.addin.macroEnabled.12',
                               'pptm': 'application/vnd.ms-powerpoint.presentation.macroEnabled.12',
                               'potm': 'application/vnd.ms-powerpoint.template.macroEnabled.12',
                               'ppsm': 'application/vnd.ms-powerpoint.slideshow.macroEnabled.12',
                               'cs':   'text/x-csharp',
                               'tif':  'image/tiff',
                               'tiff': 'image/tiff'
                              }
    }