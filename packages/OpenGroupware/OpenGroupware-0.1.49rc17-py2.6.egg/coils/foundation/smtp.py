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
# THE SOFTWARE.
#
import smtplib
from email.mime.text import MIMEText
from defaultsmanager import ServerDefaultsManager

class SMTP(object):

    __slots__ = ()

    @staticmethod
    def send(from_address, to_addresses, message, mail_options=[], rcpt_options=[]):
        sd = ServerDefaultsManager()
        config = sd.default_as_dict('SMTPServer')
        hostname = config.get('hostname', 'localhost')
        username = config.get('username', None)
        password = config.get('password', None)
        starttls = config.get('starttls', 'YES').upper()

        server = smtplib.SMTP(hostname)
        if (starttls == 'YES'):
            server.starttls()
        if ((username is not None) and
            (password is not None)):
            server.login(username, password)
        if (not(isinstance(message, basestring))):
            message = message.as_string()
        server.sendmail(from_address,
                        to_addresses,
                        message,
                        mail_options,
                        rcpt_options)
        server.close()