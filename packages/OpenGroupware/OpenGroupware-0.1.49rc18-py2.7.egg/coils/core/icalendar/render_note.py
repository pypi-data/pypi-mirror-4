#
# Copyright (c) 2009, 2011, 2012
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
from dateutil.tz    import gettz

def render_note(note, journal, ctx, **params):
    # Core attributes

    # TODO: Include the server instance name in the UID
    journal.add('uid').value             = 'coils://Note/{0}'.format(note.object_id)
    journal.add('summary').value         = note.title
    journal.add('description').value     = note.content
    journal.add('dtstart').value         = note.created.astimezone(params['utc_tz'])
    if (note.modified is None):
        journal.add('last-modified').value = note.created.astimezone(params['utc_tz'])
    else:
        journal.add('last-modified').value   = note.modified.astimezone(params['utc_tz'])
    if (note.categories is not None): journal.add('categories').value = note.categories.split(',')
    # TODO: Include categories!
    # TODO: What about the URL attribute?
    # TODO: Include DTSTAMP, this is required by spec
    # TODO: Does "STATUS" mean anything to us?

    # X- Attribues

    # TODO: Is it usefule to represent these as RELATED-TO attribues?  Do any
    #        clients support the RELATED-TO attribues?
    if (note.appointment_id is not None):
        journal.add('x-coils-appointment-id').value = unicode(note.appointment_id)
    if (note.project_id is not None):
        journal.add('x-coils-project-id').value = unicode(note.project_id)
    if (note.company_id is not None):
        # TODO: Include the contact/enterprise type as a parameter
        journal.add('x-coils-company-id').value = unicode(note.company_id)
    if (note.version is None):
        journal.add('x-coils-object-version').value = u'0'
    else:
        journal.add('x-coils-object-version').value = unicode(note.version)
    if (note.abstract is not None):
        journal.add('x-coils-abstract').value = note.abstract
    #kind                = Column("file_type", String(255))
    # TODO: Is it useful to render create and owner as properties? Can these
    #        be rendered as attendees? Or the CONTACT properties?
    #creator_id          = Column("first_owner_id", Integer,
    #owner_id            = Column("current_owner_id", Integer,
    # TODO: Perhaps the owner should be represented in the ORGANIZER property?
