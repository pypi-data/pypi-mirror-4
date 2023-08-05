#
# Copyright (c) 2010, 2012
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

#
# Misc
#
from get_tombstone      import GetTombstone
from get_performance_log import GetPerformanceLog
from get_access import GetAccess # object::get-access
from set_access import SetAccess # object::set-access
from set_acl    import SetACL    # object::set-acl
from get_logs   import GetLogs   # object::get-logs
from set_alarm  import SetAlarm  # clock::set-alarm

#
# Access Managers
#
from accessmanager import CollectionAccessManager, \
                          AttachmentAccessManager, \
                          NoteAccessManager

#
# Services
#
from services   import AdministratorService, \
                         PublishSubscribeService, \
                         ClockService, \
                         Publish

#
# Notes
#                         
from get_note             import GetNote                  # note::get
from get_notes            import GetNotes                 # object::get-notes
from create_note          import CreateNote               # note::new
from update_note          import UpdateNote               # note::set
from delete_note          import DeleteNote               # note::delete
from get_handle           import GetNoteHandle            # note::get-handle

#
# Attachments
#
from create_attachment     import CreateAttachment       # attachment::new
from get_attachment        import GetAttachment          # attachment::get
from delete_attachment     import DeleteAttachment       # attachment::delete
from get_attachment_handle import GetAttachmentHandle    # attachment::get-handle
from update_attachment     import UpdateAttachment       # attachment::update
from get_attachments       import GetAttachments         # object::get-attachments

#
# Collections
#
from create_collection import CreateCollection
from get_collection    import GetCollection
from set_assignments   import SetAssignments
from update_collection import UpdateCollection
from delete_collection import DeleteCollection
from get_assignments   import GetAssignedEntities
from get_union         import GetUnionOfEntities
from get_intersection  import GetIntersectingEntities
from get_assignment    import GetAssignment            # collection::get-assignment
from search_collection import SearchCollections        # collection::search
from delete_assignment import DeleteCollectionAssignment
from assign_object     import AssignObject
from list_             import ListCollections #collection::list

#
# Representation
#
from get_as_ics         import GetObjectAsICalendar


