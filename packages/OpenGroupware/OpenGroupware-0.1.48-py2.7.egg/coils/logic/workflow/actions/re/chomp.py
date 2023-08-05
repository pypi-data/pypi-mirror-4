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
#
from coils.core          import *
from coils.core.logic    import ActionCommand

class ChompTextAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "chomp-text"
    __aliases__   = [ 'chompText', 'chompTextAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        tof = False
        counter = 0

        def write_line(self, text):
            if self._right_chomp:
                self.wfile.write(text[self._left_chomp:(self._right_chomp * -1)])
            else:
                self.wfile.write(text[self._left_chomp:])
            #self.wfile.write(chr(10))

        for text in self.rfile.readlines():
            counter += 1
            if counter > self._skip_at_top:
                if len(text) > 2:
                    if chr(12) in text[-3:]:
                        self.log.debug('chomper detected form feed near end of line {0}'.format(counter))
                        text = text[self._left_chomp:text.find(chr(12))]
                        self.wfile.write(text)
                        self.wfile.write(chr(10))
                        while counter  < self._page_length + self._skip_at_top:
                            counter += 1
                            self.log.debug('chomper injecting blank padding line for line {0}'.format(counter))
                            #self.wfile.write(str(counter))
                            self.wfile.write(chr(10))
                        if self._do_form_feed:
                            self.log.debug('chomper injecting form feed at line {0}'.format(counter))
                            self.wfile.write(chr(12))
                        counter = 0
                    else:
                        #self.wfile.write(str(counter))
                        write_line(self, text)
                else:
                    #self.wfile.write(str(counter))
                    self.log.debug('chomper short line at line {0} - no chomping'.format(counter))
                    write_line(self, text)
            else:
                self.log.debug('chomper skipping line {0}'.format(counter))

    def parse_action_parameters(self):
        self._skip_at_top = self.process_label_substitutions(self.action_parameters.get('skipAtTop', '0'))
        self._left_chomp = self.process_label_substitutions(self.action_parameters.get('leftChomp', '0'))
        self._right_chomp = self.process_label_substitutions(self.action_parameters.get('rightChomp', '0'))
        self._page_length = self.process_label_substitutions(self.action_parameters.get('pageLength', '66'))
        self._do_form_feed = self.process_label_substitutions(self.action_parameters.get('doFormFeeds', 'NO'))
        self._skip_at_top = int(self._skip_at_top)
        self._left_chomp = int(self._left_chomp)
        self._right_chomp = int(self._right_chomp)
        self._page_length = int(self._page_length)
        if self._do_form_feed.upper() == 'YES':
            self._do_form_feed = True
        else:
            self._do_form_feed = False
