#
# Copyright (c) 2009, 2010, 2011, 2012 
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# License: MIT/X11
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
from list_                  import ListProcesses, ListRoutes
from xmlobject              import XSDDocument, WSDLDocument, XSLTDocument
# Message
from create_message         import CreateMessage    # message::new
from get_message            import GetMessage       # message::get
from get_messages           import GetMessages      # process::get-messages
from get_input_message      import GetInputMessage  # process::get-input-message
from get_output_message     import GetOutputMessage # process::get-input-message
from get_message_text       import GetMessageText   # message::get-text
from get_message_handle     import GetMessageHandle # message::get-handle
from update_message         import UpdateMessage    # message::set
from delete_message         import DeleteMessage    # message:delete
# Routes
from create_route           import CreateRoute      # route::new
from get_route              import GetRoute         # route::get
from update_route           import UpdateRoute      # route::set
from delete_route           import DeleteRoute      # route::delete
from search_route           import SearchRoutes     # route::search
# Process
from create_process         import CreateProcess     # process:create
from get_process            import GetProcess        # process:get  (Retrieve by PID)
from get_processes          import GetProcesses      # route::get-processes
from start_process          import StartProcess      # process::start
from delete_process         import DeleteProcess     # process::delete
from schedule_process       import ScheduleProcess   # process:schedule
from unschedule_process     import UnscheduleProcess # process::unschedule
from get_schedule           import GetProcessSchdule # process::get-schedule
from kill_process           import KillProcess       # process::kill
from get_process_properties import GetProcessProperties
from get_process_log        import GetProcessLog
from get_process_range      import GetProcessRange    # prcoess::get-range
from archive_process        import ArchiveProcess     # process::archive
#from get_as_vevent          import GetProcessAsVEvent # process::get-as-vevent
# Format
from create_format          import CreateFormat     # format::new
from get_format             import GetFormat        # format::get
from delete_format          import DeleteFormat     # format::delete
from formats                import Format           # Format class
# Admin
from get_process_list       import GetProcessList   # workflow::get-process-list
# Actions
from actions                import ReadAction, WriteAction, StartAction, \
                                     SelectAction, TranslateAction, SendMailAction, \
                                     DelayAction, WaitAction, TransformAction, XPathAction, \
                                     SearchAction, ExecuteAction, AssignAction, \
                                     GetEntityAction, ReadJSONAction, FindAction, \
                                     InsertAction, UpdateAction, CountAction, \
                                     TrimAction, UpperCaseAction, LowerCaseAction, \
                                     StripAction, QueueProcessAction, CreateTaskAction, \
                                     AcceptTaskAction, TaskCommentAction, \
                                     CompleteTaskAction, RejectTaskAction, \
                                     ArchiveTaskAction, ContactList, EnterpriseList, \
                                     XPathMerge, NoActionAction, UpsertAction, \
                                     SetValueAction, AddColumnAction, RemoveAccountStatusAction, \
                                     ArchiveAccountTasksAction, GetUserAccountAction, \
                                     RemoveAccountMembershipAction, RowTemplateAction, \
                                     XPathTestAction, GetEntityLogAction, PrefixColumnAction, \
                                     MapAction, GetProcessLogAction, FixMicrosoftTextAction, \
                                     GrantAction, SetProcessPropertyAction, CountJSONPathAction, \
                                     SimpleFilter, TextToPDFAction, WatermarkPDFAction, \
                                     PrintToLPRAction, AbendAction, ExceptionAction, \
                                     MailBlastAction, UnsubscribeAction, CreateCollection, \
                                     ArchiveOldTasksAction, UpdateUsersFromLDAP, UpdateTeamsFromPOSIXGroups, \
                                     RevertArchivedLoginValues, ChompTextAction, FillLDAPMailRoutingAction, \
                                     TransactionLoggerAction, InjectMessageAction, SMBGetFileAction, \
                                     SMBPutFileAction, WhitespaceChunkAction, FTPPutFileAction, \
                                     GetSequenceValue, SSHExecAction, SSHGetFileAction, SSHPutFileAction, \
                                     RMLToPDFAction
from actions                import DSML1Writer
# Misc
from accessmanager          import MessageAccessManager, RouteAccessManager, ProcessAccessManager
from action_mapper          import ActionMapper
#from create_process import CreateProcess
# Services
from services               import ExecutorService, SchedulerService, ManagerService, ReaperService, \
                                    LoggerService, Raw9100Service
#from services               import ExecutorService, QueueManagerService, ArchiveService
from bpml_handler           import BPMLSAXHandler
# Macros
from macros                 import  EvaluateMapMacro, IfThenElseMapMacro, UnlessMapMacro, \
                                     AndMacro, NotMacro, OrMacro, XORMacro, \
                                     ConstantMacro, \
                                     DateMacro, IdGeneratorMacro, IncrementorMacro, \
                                     SimpleFilterMacro, VariableMacro, SQLLookupMacro, \
                                     SQLLookupMacro, ConcatenationMacro, ReplaceMacro, \
                                     SubstringMacro, TrimMacro, UnionMacro, \
                                     CentigradeToFarenheitMacro, CentimeterToInchMacro, FeetToInchMacro, \
                                     FarenheitToCentigrade, InchToCentimeterMacro, AbsoluteMacro, \
                                     AdditionMacro, DivisionMacro, MaximumMacro, \
                                     MinimumMacro, ModulusMacro, MultiplicationMacro, \
                                     RoundMacro, SquareRootMacro, SubtractionMacro, \
                                     SumOfMacro, \
                                     AbsoluteMacro, AdditionMacro, DivisionMacro, \
                                     MaximumMacro, MinimumMacro, ModulusMacro, \
                                     MultiplicationMacro, RoundMacro, SquareRootMacro, \
                                     SubtractionMacro, SumOfMacro
#
# Table operations
#                                     
from tables                 import Table, PresenceLookupTable, StaticLookupTable, SQLLookupTable, XPathLookupTable
from create_table           import CreateTable
from delete_table           import DeleteTable
