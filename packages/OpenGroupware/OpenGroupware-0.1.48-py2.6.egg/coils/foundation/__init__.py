# Copyright (c) 2010 Adam Tauno Williams <awilliam@whitemice.org>
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
from sqlalchemy.orm import sessionmaker

# Import SQL-Alchemy Classes (Database Model)
from coils.foundation.alchemy  import ACL, \
                                       AuditEntry, \
                                       ObjectLink, \
                                       ObjectInfo, \
                                       Team, \
                                       Task, \
                                       Address, \
                                       Telephone, \
                                       CompanyValue, \
                                       Contact, \
                                       Enterprise, \
                                       Appointment, \
                                       Resource, \
                                       Note, \
                                       Document, \
                                       Folder, \
                                       Project, \
                                       ProjectAssignment, \
                                       Participant, \
                                       CompanyAssignment, \
                                       ObjectProperty, \
                                       Route, \
                                       Collection, \
                                       CollectionAssignment, \
                                       Process, \
                                       Message, \
                                       CompanyInfo, \
                                       KVC, \
                                       DateInfo, \
                                       TaskAction, \
                                       CTag, \
                                       DocumentVersion, \
                                       AuthenticationToken, \
                                       ProcessLogEntry, \
                                       Lock, \
                                       Attachment, \
                                       UniversalTimeZone, \
                                       UTCDateTime, \
                                       ORMEntity, \
                                       ProjectInfo
# Import core components
from log import *
from blobmanager import BLOBManager

from defaultsmanager              import UserDefaultsManager, \
                                          ServerDefaultsManager

from plist                        import PListParser, \
                                          PListWriter

from picklejar                    import PickleParser, \
                                          PickleWriter


#Session = sessionmaker()

from backend                      import Backend, Session
from coils.foundation.blobmanager import blob_manager_for_ds
from coils.foundation.dbfs1       import DBFS1Manager
from coils.foundation.skyfs       import SkyFSManager
from coils.foundation.imap        import IMAPManager

from smtp        import SMTP

from tzdata import COILS_TIMEZONES

from factories import LDAPConnectionFactory, \
                        SQLConnectionFactory

from utility import diff_id_lists, change_to_backend_usergroup, fix_microsoft_text,ldap_paged_search

from standard_xml import StandardXML

from constants import *
