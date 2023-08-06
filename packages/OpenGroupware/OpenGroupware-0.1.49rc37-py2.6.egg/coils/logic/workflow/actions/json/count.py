#
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
#
try:
    import ijson
except:
    class CountJSONPathAction(object):
        pass
else:
    from coils.core.logic    import ActionCommand
    
    class CountJSONPathAction(ActionCommand):
        __domain__    = "action"
        __operation__ = "count-json-path"
        __aliases__   = [ 'countJSONPathAction' ]
    
        def __init__(self):
            ActionCommand.__init__(self)
    
        def do_action(self):
            counter = 0
            for item in ijson.items(self.rfile, self._path):
                counter += 1
            self.wfile.write(str(counter))
    
        def parse_action_parameters(self):
            self._path = self.action_parameters.get('path')
            self._path = self.process_label_substitutions(self._path)
    
        def do_epilogue(self):
            pass