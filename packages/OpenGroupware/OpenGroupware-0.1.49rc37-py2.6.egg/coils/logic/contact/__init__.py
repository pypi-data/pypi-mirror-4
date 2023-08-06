#
# Copyright (c) 2009 Adam Tauno Williams <awilliam@whitemice.org>
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
from accessmanager        import ContactAccessManager
from get_contact          import GetContact           # contact::get
from update_contact       import UpdateContact        # contact::update
from create_contact       import CreateContact        # contact::create
from delete_contact       import DeleteContact        # contact::delete
from search_contact       import SearchContacts       # contact::search
from list                 import ListContacts         # contact::list
from get_birthdays        import GetUpcomingBirthdays # contact::get-upcoming-birthdays
from set_enterprises      import SetEnterprises       # contact::set-enterprises
from set_projects         import SetProjects          # contact::set-enterprises
from get_enterprises      import GetEnterprises       # contact::get-enterprises
from get_favorite         import GetFavorites         # contact::get-favorite
from add_favorite         import AddFavorite          # contact::add-favorite
from remove_favorite      import RemoveFavorite       # contact::remove-favorite
from set_favorite         import SetFavorite          # contact::set-favorite
from add_note             import AddContactNote       # contact::new-note
from get_companyvalue     import GetCompanyValue      # contact::get-companyvalue
from set_companyvalue     import SetCompanyValue      # contact::set-companyvalue
