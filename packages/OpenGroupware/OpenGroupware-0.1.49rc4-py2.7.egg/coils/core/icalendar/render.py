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
import logging, vobject
from dateutil.tz    import gettz
from coils.core         import *
from render_appointment import render_appointment
from render_process     import render_process
from render_task        import render_task
from render_note        import render_note


class Render(object):
# TODO: This is a mess of hacks, and needs to be refactored.  But it works.
    @staticmethod
    def render(entity, ctx):
        Render.render(entity, ctx, {})

    #TODO: Shouldn't this method be named Render, static method names are usually upper-cased
    @staticmethod
    def render(entities, ctx, **params):

        log = logging.getLogger('render')

        if (params is None): params = { }
        # Many rendering operations require information about server configuration,
        # so we make sure all those methods get a ServerDefaultsManager object.
        if ('sd' not in params): params['sd'] = ServerDefaultsManager()
        params['utc_tz'] = gettz('UTC')

        #TODO: log duration of render at debug level
        if (entities is None):
            raise CoilsException('Attempt to render a None')
        elif (isinstance(entities, list)):
            # OK
            pass
        else:
            entities = [ entities ]
        calendar = vobject.iCalendar()
        for entity in entities:
            if (isinstance(entity, Appointment)):
                event = calendar.add('vevent')
                render_appointment(entity, event, ctx, log, **params)
            elif (isinstance(entity, Process)):
                event = calendar.add('vevent')
                render_process(entity, event, ctx, **params)
            elif (isinstance(entity, Task)):
                task = calendar.add('vtodo')
                render_task(entity, task, ctx, **params)
            elif (isinstance(entity, Note)):
                journal = calendar.add('vjournal')
                render_note(entity, journal, ctx, **params)
            else:
                CoilsException('Entity {0} cannot be rendered as an iCalendar'.format(entity))
        return calendar.serialize()
