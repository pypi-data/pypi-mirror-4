#
# Copyright (c) 2009, 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
from create_appointment         import CreateAppointment           # appointment::create
from get_appointment            import GetAppointment              # appointment::get
from get_resource               import GetResource                 #
from get_conflicts              import GetConflicts                #
from update_appointment         import UpdateAppointment           # appointment::set
from get_appointment_range      import GetAppointmentRange, \
                                        GetAppointmentOverviewRange # appointment::get-{overview-}range
from get_resource_names         import GetResourceNames            #
from set_participant            import SetParticipant              # participant::set
from delete_appointment         import DeleteAppointment           # appointment::delete
from delete_comment             import DeleteComment               # appointment::delete-comment
from delete_participant         import DeleteParticipant           # participant::delete
from delete_participants        import DeleteParticipants          # appointment::delete-participants
#from get_appointment_as_vevent  import GetAppointmentAsVEvent     # appointment::get-as-vevent
from set_participants           import SetParticipants             # appointment::set-participants
from accessmanager              import AppointmentAccessManager, \
                                        ResourceAccessManager
from notification               import NotificationService
from search                     import SearchResources
from get_free_busy              import GetFreeBusy                 # schedular::get-free-busy 
