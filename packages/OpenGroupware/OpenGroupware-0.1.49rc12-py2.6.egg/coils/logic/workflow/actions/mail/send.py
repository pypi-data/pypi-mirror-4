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
import os
from email               import Encoders
from email.Utils         import COMMASPACE, formatdate
from email.MIMEBase      import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.mime.text     import MIMEText
from coils.core          import *
from coils.core.logic    import ActionCommand


class SendMailAction(ActionCommand):
    __domain__    = "action"
    __operation__ = "send-mail"
    __aliases__   = [ 'sendMail', 'sendMailAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        if (self._attach == 'YES'):
            # TODO: Implement
            message = MIMEMultipart()
            if (self._body is not None):
                message.attach(MIMEText(self._body))
            else:
                message.attach(MIMEText(''))
            part    = MIMEBase(self._mime.split('/')[0], self._mime.split('/')[1])
            part.set_payload(self.rfile.read())
            part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(self._partname))
            Encoders.encode_base64(part)
            message.attach(part)
        else:
            if (self._body is not None):
                message = MIMEText(self._body)
            else:
                message = MIMEText(self.rfile.read())
        message['Subject'] = self._subject
        message['From'] = self._from
        message['To'] = COMMASPACE.join(self._to)
        if (len(self._cc)):
            message['Cc'] = COMMASPACE.join(self._cc)
        message['Date'] = formatdate(localtime=True)
        
        # Set the X-OpenGroupware-Regarding header to the task related to the
        # process if such a relation exists, otherwise set it to the PID.
        if self.process.task_id:
            message['X-Opengroupware-Regarding'] = str(self.process.task_id)
        else:
            message['X-Opengroupware-Regarding'] = str(self.pid)
            
        message['X-Opengroupware-Process-Id'] = str(self.pid)
        message['X-Opengroupware-Context'] = '{0}[{1}]'.format(self._ctx.get_login(), self._ctx.account_id)
        addresses = []
        addresses.extend(self._to)
        addresses.extend(self._cc)
        addresses.extend(self._bcc)
        SMTP.send(self._from, addresses, message)

    def parse_action_parameters(self):
        self._from     = self.action_parameters.get('from', None)
        self._to       = self.action_parameters.get('to', self._ctx.email)
        self._body     = self.action_parameters.get('bodyText', None)
        self._cc       = self.action_parameters.get('CC', '')
        self._bcc      = self.action_parameters.get('BCC', '')
        self._attach   = self.action_parameters.get('asAttachment', 'YES').upper()
        self._partname = self.action_parameters.get('filename', 'message.data')
        self._subject  = self.action_parameters.get('subject', '')
        #
        if (self._to is None):
            raise CoilsException('Attempt to send e-mail with no destination!')
        #
        self._from     = self.process_label_substitutions(self._from)
        self._to       = self.process_label_substitutions(self._to)
        self._to       = self._to.split(',')
        self._cc       = self.process_label_substitutions(self._cc)
        self._cc       = self._cc.split(',')
        self._bcc      = self.process_label_substitutions(self._bcc)
        self._bcc       = self._bcc.split(',')
        if (self._body is not None):
            self._body     = self.process_label_substitutions(self._body)
        self._subject  = self.process_label_substitutions(self._subject)
        self._partname = self.process_label_substitutions(self._partname)

    def do_epilogue(self):
        pass
