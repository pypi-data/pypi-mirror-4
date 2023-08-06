#
# Copyright (c) 2009, 2012
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
#
from sqlalchemy         import *
from coils.core         import *
from coils.core.logic   import GetCommand
from coils.foundation   import Appointment, Contact
from command            import AppointmentCommand

class GetAppointment(GetCommand, AppointmentCommand):
    __domain__ = "appointment"
    __operation__ = "get"

    def parse_parameters(self, **params):
        GetCommand.parse_parameters( self, **params )
        self._uid = None
        self._ref = None
        if bool( params.get( 'visible_only', False ) ):
            self._required_right = 'v'
        else:
            self._required_right = 'l'
        if len( self.object_ids ) == 0:
            self.set_single_result_mode( )
            self._ref = params.get( 'href', None )
            self._uid = params.get( 'uid', None )
            if not self._uid: self._uid = self._ref
            if not self._ref: self._ref = self._uid

    def run(self, **params):
        db = self._ctx.db_session( )
        query = db.query( Appointment ).with_labels(  )
        if self._uid:
            query = query.filter( and_( Appointment.status != 'archived',
                                        or_( Appointment.uid  == self._uid,
                                             Appointment.href == self._ref ) ) )                                                            
        else:
            query = query.filter( and_( Appointment.object_id.in_( self.object_ids ),
                                        Appointment.status != 'archived' ) )
        result = query.all()
        self.set_return_value(self.load_special_values(result), right=self._required_right)
