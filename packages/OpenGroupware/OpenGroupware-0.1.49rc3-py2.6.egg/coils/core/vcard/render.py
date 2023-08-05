#!/usr/bin/python
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
import logging
from coils.core import *
from render_contact import render_contact
from render_enterprise import render_enterprise
from render_team import render_team

class Render(object):

    @staticmethod
    def render(entity, ctx):
        Render.render(entity, ctx, {})

    @staticmethod
    def render(entity, ctx, **params):
        log = logging.getLogger('render')
        #TODO: log duration of render at debug level
        if (entity is None):
            raise CoilsException('Attempt to render a None')
        elif (isinstance(entity, Contact)):
            try:
                return render_contact(entity, ctx, **params)
            except Exception, e:
                log.error('exception rendering Contact objectId#%d' % entity.object_id, exc_info=1)
                raise e
        elif (isinstance(entity, Enterprise)):
            return render_enterprise(entity, ctx, **params)
        elif (isinstance(entity, Team)):
            return render_team(entity, ctx, **params)
        else:
            raise CoilsException('Entity %s cannot be rendered as a vCard' % entity.__entityName__)