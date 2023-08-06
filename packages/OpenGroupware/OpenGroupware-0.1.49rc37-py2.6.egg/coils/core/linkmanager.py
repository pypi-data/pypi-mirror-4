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
from sqlalchemy import *
from coils.foundation import ObjectLink

class LinkManager(object):
    __slots__ = ('_ctx')

    def __init__(self, ctx):
        self._ctx = ctx

    def links_to(self, entity):
        db = self._ctx.db_session()
        query = db.query(ObjectLink).filter(ObjectLink.target_id == entity.object_id)
        data = query.all()
        query = None
        return data

    def links_from(self, entity):
        db = self._ctx.db_session()
        query = db.query(ObjectLink).filter(ObjectLink.source_id == entity.object_id)
        data = query.all()
        query = None
        return data

    def links_to_and_from(self, entity):
        db = self._ctx.db_session()
        query = db.query(ObjectLink).filter(or_(ObjectLink.source_id == entity.object_id,
                                                 ObjectLink.target_id == entity.object_id))
        query = query.order_by(ObjectLink.source_id, ObjectLink.target_id, ObjectLink.kind)
        data = query.all()
        query = None
        return data

    def links_between(self, entity1, entity2):
        db = self._ctx.db_session()
        query = db.query(ObjectLink).filter(and_(ObjectLink.source_id.in_((entity1.object_id, entity2.object_id)),
                                                 ObjectLink.target_id.in_((entity1.object_id, entity2.object_id))))
        query = query.order_by(ObjectLink.source_id, ObjectLink.target_id, ObjectLink.kind)
        data = query.all()
        query = None
        return data

    def link(self, source, target, kind='generic', label=None):
        #TODO: Give a new link a label if none was provided
        db = self._ctx.db_session()
        if (kind is None):
            query = db.query(ObjectLink).filter(and_(ObjectLink.source_id == source.object_id,
                                                      ObjectLink.target_id == target.object_id))
        else:
            query = db.query(ObjectLink).filter(and_(ObjectLink.source_id == source.object_id,
                                                      ObjectLink.target_id == target.object_id,
                                                      ObjectLink.kind == kind))
        links = query.all()
        # TODO: Tidy
        if links:
            link = links[0]
            link.label = label
        else:
            print source.object_id, target.object_id, kind, label
            link = ObjectLink(source, target, kind, label)
            self._ctx.db_session().add(link)

    def unlink(self, source, target, kind='generic'):
        #TODO: Give a new link a label if none was provided
        db = self._ctx.db_session()
        if (kind is None):
            query = db.query(ObjectLink).filter(and_(ObjectLink.source_id == source.object_id,
                                                      ObjectLink.target_id == target,object_id))
        else:
            query = db.query(ObjectLink).filter(and_(ObjectLink.source_id == source.object_id,
                                                      ObjectLink.target_id == target.object_id,
                                                      ObjectLink.kind == kind))
        link = query.one()
        if (link is not None):
            self._ctx.db_session().delete(link)

    # Private method, do not use externally
    def _is_linked(self, source_id, target_id, kind):
        db = self._ctx.db_session()
        if kind:
            query = db.query(ObjectLink).filter(and_(ObjectLink.source_id == source_id,
                                                     ObjectLink.target_id == target_id))
        else:
            query = db.query(ObjectLink).filter(and_(ObjectLink.source_id == source_id,
                                                     ObjectLink.target_id == target_id,
                                                     ObjectLink.kind == kind))
        result = query.all()
        if query.all():
            return result[0]
        else:
            return False

    # Private method, do not use externally
    def _get_entity(self, object_id):
        kind = self._ctx.type_manager.get_kind(object_id)
        # TODO: Catch the no-such-command exception and return None ???
        return self._ctx.run_command('{0}::get',format(kind.lower()), id=object_id)

    def sync_links(self, entity, links_b):
        db = self._ctx.db_session()
        # Assume we are going to delete all the existing links
        removes = [link.object_id for link in self.links_to_and_from(entity)]
        for link_b in links_b:
            if isinstance(link_b, dict):
                source_id = link_b.get('source_id')
                target_id = link_b.get('target_id')
                kind      = link_b.get('kind')
                label     = link_b.get('label')
            else:
                # assuming an ObjectLink entity
                source_id = link_b.source_id
                target_id = link_b.target_id
                kind      = link_b.kind
                label     = link_b.label
            # TODO: it would be better to load all these at once and check in memory (PERF)
            link = self._is_linked(source_id, target_id, kind)
            if link:
                # potentially update the link label
                link.label = label
                # client still wants this link, keep it
                removes.remove(link.object_id)
            else:
                if (entity.object_id == source_id):
                    # This link is from this entity to the target
                    source = entity
                    target = self._get_entity(target_id)
                else:
                    # This link is target to this entity from the souce
                    target = entity
                    source = self._get_entity(source_id)
                if target and source:
                    link = ObjectLink(source, target, kind, label)
                    db.add(link)
                else:
                    raise CoilsException('Unable to create new link from provided type.')
        # delete existing links that the client did not specify
        if removes:
            db.query(ObjectLink).filter(ObjectLink.object_id.in_(removes)).delete()
