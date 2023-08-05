#
# Copyright (c) 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
import pprint
from coils.core          import *
from api                 import HordeAPI

def render_note(context, note):
    return { 'id': note.object_id,
             'uid': note.caldav_uid,
             'desc': note.title,
             'body': note.content,

             'category': note.categories }

class HordeMNemoAPI(HordeAPI):



    def api_mnemo_get_notpad(self, args):
        # notepad name
        project = self.context.run_command('project::get', name=args[0])
        if project:
            return True
        return False

    def api_mnemo_get(self, args):
        # id
        note = self.context.run_command('note::get', id=args[0])
        if note:
            return render_note(self.context, note)
        return False

    def api_mnemo_add(self, args):
        # notepad, desc, body, category, uid
        project = self.context.run_command('project::get', number=args[0])
        if project:
            note = self.context.run_command('note::new', values={ 'title': args[1],
                                                                  'categories': args[3] },
                                                         text=args[2],
                                                         context=project)
            self.context.commit()
            return render_note(self.context, note)
        return False


        pass

    def api_mnemo_modify(self, args):
        # noteid, desc, body, category
        note = self.context.run_command('note::get', id=args[0])
        if note:
            note = self.context.run_command('note::set', object=note,
                                                         values={ 'title': args[1],
                                                                  'categories': args[3] },
                                                         text=args[2])
            self.context.commit()
            return render_note(self.context, note)
        return False

    def api_mnemo_move(self, args):
        # noteid, notepad
        project = self.context.run_command('project::get', name=args[1])
        if project:
            note = self.context.run_command('note::get', id=args[0])
            if note:
                note.project_id = project.object_id
                self.context.commit()
                return True
        return False

    def api_mnemo_delete(self, args):
       # note id
       note = self.context.run_command('note::get', uid=args[1])
       if note:
            self.context.run_command('note::delete', object=note)
            return True
       return False

    def api_mnemo_retrieve(self, args):
        # notepad name
        project = self.context.run_command('project::get', number=args[0])
        if project:
            result = [ ]
            for note in self.context.run_command('project::get-notes', project=project):
                result.append(render_note(self.context, note))
            return result
        print 'no such project as {0}'.format(args[0])
        return [ ]


