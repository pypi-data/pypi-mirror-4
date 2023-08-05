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
from get                        import GetEntityAction
from task_create                import CreateTaskAction
from task_accept                import AcceptTaskAction
from task_comment               import TaskCommentAction
from task_done                  import CompleteTaskAction
from task_reject                import RejectTaskAction
from task_archive               import ArchiveTaskAction
from contact_list               import ContactList
from enterprise_list            import EnterpriseList
from account_remove_status      import RemoveAccountStatusAction
from account_archive_tasks      import ArchiveAccountTasksAction
from archive_old_tasks          import ArchiveOldTasksAction       # action::archive-old-tasks
from get_user_account           import GetUserAccountAction        # action::get-user-account
from account_remove_membership  import RemoveAccountMembershipAction
from get_log                    import GetEntityLogAction
from create_collection          import CreateCollection
from revert_login_values        import RevertArchivedLoginValues   # action::revert-archived-login-values
