#
# Copyright (c) 2010, 2012
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
# THE SOFTWARE.
#


from sqlalchemy                      import and_, or_
from sqlalchemy.orm                  import relation, relationship, backref
from sqlalchemy.orm.collections      import attribute_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy

from attachment     import Attachment
from internal       import ACL, AuditEntry, ObjectLink, ObjectInfo, Team
from task           import Task, TaskAction
from company        import Address, Telephone, CompanyValue, CompanyInfo
from contact        import Contact
from enterprise     import Enterprise
from appointment    import Appointment, Resource, DateInfo, Participant
from doc            import Note, Document, Folder
from project        import Project, ProjectInfo
from assignment     import ProjectAssignment, CompanyAssignment
from collection     import Collection, CollectionAssignment
from route          import Route
from process        import Process
from property      import ObjectProperty
from message        import Message

AuditEntry.actor                  = relation('Contact',
                                    uselist=False,
                                    primaryjoin='AuditEntry.actor_id==Contact.object_id')

Appointment.participants         = relation('Participant',
                                   lazy=True,
                                   uselist=True,
                                   cascade='delete',
                                   primaryjoin='Participant.appointment_id==Appointment.object_id')

Appointment.notes                    = relationship( 'Note',
                                                 primaryjoin = 'Note.appointment_id==Appointment.object_id',
                                                 collection_class=attribute_mapped_collection( 'object_id' ),
                                                 lazy = False,
                                                 cascade = 'all, delete-orphan' )                                        

Appointment.acls                 = relation('ACL',
                                   lazy=False,
                                   uselist=True,
                                   cascade='delete',
                                   order_by='ACL.context_id',
                                   primaryjoin='ACL.parent_id == Appointment.object_id')

Appointment.logs                 = relation('AuditEntry',
                                   lazy=True,
                                   uselist=True,
                                   order_by='AuditEntry.context_id',
                                   primaryjoin='Appointment.object_id==AuditEntry.context_id')

Appointment.properties           = relation('ObjectProperty',
                                   lazy=True,
                                   uselist=True,
                                   cascade='delete',
                                   order_by='ObjectProperty.parent_id',
                                   primaryjoin='Appointment.object_id==ObjectProperty.parent_id')

Appointment.info                = relation('ObjectInfo',
                                  lazy=True,
                                  uselist=False,
                                  order_by='ObjectInfo.object_id',
                                  primaryjoin='Appointment.object_id==ObjectInfo.object_id')

#CollectionAssignment.collection  = relation('Collection',
#                                   uselist=False,
#                                   primaryjoin='Collection.collection_id==CollectionAssignment.collection_id')

Collection.project                = relation('Project',
                                    uselist=False,
                                    primaryjoin='Collection.project_id==Project.object_id')

Collection.acls                   = relation('ACL',
                                    lazy=False,
                                    uselist=True,
                                    order_by='ACL.context_id',
                                    primaryjoin='ACL.parent_id == Collection.object_id')

Collection.assignments                = relation('CollectionAssignment',
                                    lazy=True,
                                    uselist=True,
                                    order_by='CollectionAssignment.object_id',
                                    primaryjoin='CollectionAssignment.collection_id == Collection.object_id')

Collection.info                = relation('ObjectInfo',
                                  lazy=True,
                                  uselist=False,
                                  order_by='ObjectInfo.object_id',
                                  primaryjoin='Collection.object_id==ObjectInfo.object_id')

#Collection.logs                   = relation('AuditEntry',
#                                    lazy=True,
#                                    uselist=True,
#                                    order_by='AuditEntry.context_id',
#                                    primaryjoin='Collection.object_id==AuditEntry.context_id')

#
# Contact
#
                                   
Contact.notes                    = relationship( 'Note',
                                                 primaryjoin = 'Note.company_id==Contact.object_id',
                                                 collection_class=attribute_mapped_collection( 'object_id' ),
                                                 lazy = False,
                                                 cascade = 'all, delete-orphan' )                                    

Contact.acls                      = relation('ACL',
                                    lazy=True,
                                    uselist=True,
                                    order_by='ACL.context_id',
                                    cascade='delete',
                                    primaryjoin='ACL.parent_id == Contact.object_id')

Contact.enterprises               = relation('CompanyAssignment',
                                    lazy=True,
                                    cascade='delete',
                                    uselist=True,
                                    order_by='CompanyAssignment.child_id',
                                    primaryjoin='CompanyAssignment.child_id == Contact.object_id')

Contact.teams                     = relation('CompanyAssignment',
                                    lazy=True,
#                                    cascade='delete',
                                    uselist=True,
                                    order_by='CompanyAssignment.child_id',
                                    primaryjoin='CompanyAssignment.child_id == Contact.object_id')

Contact.projects                  = relation('ProjectAssignment',
                                    lazy=True,
#                                    cascade='delete',
                                    uselist=True,
                                    order_by='ProjectAssignment.child_id',
                                    primaryjoin='Contact.object_id==ProjectAssignment.child_id')

Contact.logs                      = relation('AuditEntry',
                                    lazy=True,
#                                    cascade='delete',
                                    uselist=True,
                                    order_by='AuditEntry.context_id',
                                    primaryjoin='Contact.object_id==AuditEntry.context_id')

Contact.properties               = relation('ObjectProperty',
                                   lazy=True,
                                   uselist=True,
                                   order_by='ObjectProperty.parent_id',
                                   cascade='delete',
                                   primaryjoin='Contact.object_id==ObjectProperty.parent_id')

Contact.info                    = relation('ObjectInfo',
                                  lazy=True,
                                  uselist=False,
                                  order_by='ObjectInfo.object_id',
                                  primaryjoin='Contact.object_id==ObjectInfo.object_id')

Contact.telephones = relationship( 'Telephone',
                                   primaryjoin = 'Telephone.parent_id==Contact.object_id',
                                   collection_class=attribute_mapped_collection( 'kind' ),
                                   lazy = False,
                                   cascade = 'all, delete-orphan' )
                
Contact.addresses = relationship( 'Address',
                                  primaryjoin = 'Address.parent_id==Contact.object_id',
                                  collection_class = attribute_mapped_collection( 'kind' ),
                                  lazy = False,
                                  cascade = 'all, delete-orphan' )
                
Contact.company_values = relationship( 'CompanyValue',
                                       primaryjoin = 'CompanyValue.parent_id==Contact.object_id',
                                       collection_class = attribute_mapped_collection( 'name' ),
                                       lazy = False,
                                       cascade = 'all, delete-orphan')

#
# Company Value
#

CompanyValue.properties          = relation('ObjectProperty',
                                   lazy=True,
                                   uselist=True,
                                   order_by='ObjectProperty.parent_id',
                                   cascade='delete',
                                   primaryjoin='CompanyValue.object_id==ObjectProperty.parent_id')

#
# Note
#


Note.appointment                  = relation('Appointment',
                                    uselist=False,
                                    primaryjoin='Note.appointment_id==Appointment.object_id')

Note.project                      = relation('Project',
                                    uselist=False,
                                    primaryjoin='Note.project_id==Project.object_id')

Note.info                    = relation('ObjectInfo',
                                  lazy=True,
                                  uselist=False,
                                  order_by='ObjectInfo.object_id',
                                  primaryjoin='Note.object_id==ObjectInfo.object_id')

#
# Document
#

Document.project                  = relation('Project',
                                    uselist=False,
                                    primaryjoin='Document.project_id==Project.object_id')

Document.folder                     = relation('Folder', remote_side=Folder.object_id, uselist=False)                                    

Document.versions                 = relation('DocumentVersion',
                                             lazy=True,
                                             uselist=True,
                                             order_by='DocumentVersion.version',
                                             primaryjoin='Document.object_id==DocumentVersion.document_id')

Document.properties           = relation('ObjectProperty',
                                   lazy=True,
                                   uselist=True,
                                   cascade='delete',
                                   order_by='ObjectProperty.parent_id',
                                   primaryjoin='Document.object_id==ObjectProperty.parent_id')

Document.acls                  = relation('ACL',
                                    uselist=True,
                                    lazy=False,
                                    cascade='delete',
                                    order_by='ACL.context_id',
                                    primaryjoin='ACL.parent_id == Document.object_id')

Document.info                    = relation('ObjectInfo',
                                  lazy=True,
                                  uselist=False,
                                  order_by='ObjectInfo.object_id',
                                  primaryjoin='Document.object_id==ObjectInfo.object_id')

#
# Folder
#

Folder.project                    = relation('Project',
                                    uselist=False,
                                    primaryjoin='Document.project_id==Project.object_id')

# Return the Folder's parent folder, if any [if top-folder this will be None]
Folder.folder                     = relation('Folder', remote_side=Folder.object_id, uselist=False)

# Return the Folder's child folders, if any [if no child folders this will be an empty list]
Folder.folders                    = relation('Folder', remote_side=Folder.folder_id, uselist=True)

Folder.files                      = relation('Document',
                                    uselist=True,
                                    lazy=True,
                                    order_by='Document.object_id',
                                    primaryjoin='Document.folder_id == Folder.object_id')

# Return the ACLs applied to the folder
Folder.acls                       = relation('ACL',
                                    uselist=True,
                                    lazy=False,
                                    cascade='delete',
                                    order_by='ACL.context_id',
                                    primaryjoin='ACL.parent_id == Folder.object_id')

#
# Enterprise
#
                                    
Enterprise.notes                    = relationship( 'Note',
                                                 primaryjoin = 'Note.company_id==Enterprise.object_id',
                                                 collection_class=attribute_mapped_collection( 'object_id' ),
                                                 lazy = False,
                                                 cascade = 'all, delete-orphan' )                                         

Enterprise.company_values = relationship( 'CompanyValue',
                                          primaryjoin = 'CompanyValue.parent_id==Enterprise.object_id',
                                          collection_class = attribute_mapped_collection( 'name' ),
                                          lazy = False,
                                          cascade = 'all, delete-orphan')


Enterprise.contacts               = relation('CompanyAssignment',
                                    lazy=True,
                                    uselist=True,
                                    cascade='delete',
                                    order_by='CompanyAssignment.parent_id',
                                    primaryjoin='CompanyAssignment.parent_id == Enterprise.object_id')

Enterprise.projects               = relation('ProjectAssignment',
                                    uselist=True,
                                    lazy=True,
                                    order_by='ProjectAssignment.child_id',
                                    primaryjoin='ProjectAssignment.child_id == Enterprise.object_id')

Enterprise.logs                   = relation('AuditEntry',
                                    lazy=True,
                                    uselist=True,
                                    cascade='delete',
                                    order_by='AuditEntry.context_id',
                                    primaryjoin='Enterprise.object_id==AuditEntry.context_id')

Enterprise.acls                   = relation('ACL',
                                    uselist=True,
                                    lazy=False,
                                    cascade='delete',
                                    order_by='ACL.context_id',
                                    primaryjoin='ACL.parent_id == Enterprise.object_id')

Enterprise.properties            = relation('ObjectProperty',
                                   lazy=True,
                                   uselist=True,
                                   cascade='delete',
                                   order_by='ObjectProperty.parent_id',
                                   primaryjoin='Enterprise.object_id==ObjectProperty.parent_id')

Enterprise.info                    = relation('ObjectInfo',
                                     lazy=True,
                                     uselist=False,
                                     order_by='ObjectInfo.object_id',
                                     primaryjoin='Enterprise.object_id==ObjectInfo.object_id')
                                     
Enterprise.addresses = relationship( 'Address',
                                  primaryjoin = 'Address.parent_id==Enterprise.object_id',
                                  collection_class = attribute_mapped_collection( 'kind' ),
                                  lazy = False,
                                  cascade = 'all, delete-orphan' )                                     


Enterprise.telephones = relationship( 'Telephone',
                                   primaryjoin = 'Telephone.parent_id==Enterprise.object_id',
                                   collection_class=attribute_mapped_collection( 'kind' ),
                                   lazy = False,
                                   cascade = 'all, delete-orphan' )
                

#
# Team
#

Team.members                      = relation('CompanyAssignment',
                                    lazy=False,
                                    uselist=True,
                                    order_by='CompanyAssignment.child_id',
                                    primaryjoin=('CompanyAssignment.parent_id == Team.object_id'))

Team.info                          = relation('ObjectInfo',
                                     lazy=True,
                                     uselist=False,
                                     order_by='ObjectInfo.object_id',
                                     primaryjoin='Team.object_id==ObjectInfo.object_id')

#
# Process
#

Process.route                     = relation('Route',
                                    lazy=True,
                                    uselist=False,
                                    order_by='Route.object_id',
                                    primaryjoin='Process.route_id==Route.object_id')

Process.properties                = relation('ObjectProperty',
                                    lazy=True,
                                    uselist=True,
                                    order_by='ObjectProperty.parent_id',
                                    cascade='delete',
                                    primaryjoin='Process.object_id==ObjectProperty.parent_id')

Process.acls                        = relation('ACL',
                                    lazy=False,
                                    uselist=True,
                                    cascade='delete',
                                    order_by='ACL.context_id',
                                    primaryjoin='ACL.parent_id == Process.object_id')

Process.info                = relation('ObjectInfo',
                                  lazy=True,
                                  uselist=False,
                                  order_by='ObjectInfo.object_id',
                                  primaryjoin='Process.object_id==ObjectInfo.object_id')

#
# Project
#

Project.folder                    = relation('Folder',
                                    lazy=False,
                                    uselist=False,
                                    primaryjoin=and_(Project.object_id==Folder.project_id,
                                                     or_(Folder.folder_id == None,
                                                         Folder.folder_id == 0)))                                 
                                                                                                     


Project.tasks                     = relation('Task',
                                    uselist=True,
                                    primaryjoin=(Project.object_id==Task.project_id))

Project.assignments               = relation(ProjectAssignment,
                                    uselist=True,
                                    primaryjoin=(Project.object_id==ProjectAssignment.parent_id))

Project.acls                      = relation(ProjectAssignment,
                                    uselist=True,
                                    primaryjoin=and_(Project.object_id==ProjectAssignment.parent_id,
                                                     ProjectAssignment.rights != None))


Project.properties                = relation('ObjectProperty',
                                    lazy=True,
                                    uselist=True,
                                    order_by='ObjectProperty.parent_id',
                                    cascade='delete',
                                    primaryjoin='Project.object_id==ObjectProperty.parent_id')

#
# Route
#

Route.acls                        = relation('ACL',
                                    lazy=False,
                                    uselist=True,
                                    cascade='delete',
                                    order_by='ACL.context_id',
                                    primaryjoin='ACL.parent_id == Route.object_id')

Route.logs                        = relation('AuditEntry',
                                    lazy=True,
                                    uselist=True,
                                    cascade='delete',
                                    order_by='AuditEntry.context_id',
                                    primaryjoin='Route.object_id==AuditEntry.context_id')

Route.properties                  = relation('ObjectProperty',
                                    lazy=True,
                                    uselist=True,
                                    cascade='delete',
                                    order_by='ObjectProperty.parent_id',
                                    primaryjoin='Route.object_id==ObjectProperty.parent_id')

Route.processes                   = relation('Process',
                                    lazy=True,
                                    uselist=True,
                                    order_by='Process.object_id',
                                    primaryjoin='Route.object_id==Process.route_id')

#
# Task
# 

Task.notes                        = relation(TaskAction,
                                    lazy=False,
                                    uselist=True,
                                    cascade='delete',
                                    order_by=TaskAction.action_date,
                                    primaryjoin=Task.object_id==TaskAction.task_id)

Task.attachments                  = relation(Attachment,
                                    lazy=False,
                                    uselist=True,
                                    primaryjoin=Attachment.related_id==Task.object_id)

Task.parent                       = relation(Task,
                                    lazy=False,
                                    uselist=False,
                                    primaryjoin=Task.object_id==Task.parent_id)

Task.children                    = relation(Task,
                                    lazy=False,
                                    uselist=True,
                                    primaryjoin=Task.parent_id==Task.object_id)

Task.owner                        = relation('Contact',
                                    uselist=False,
                                    primaryjoin='Task.owner_id==Contact.object_id')

Task.project                      = relation('Project',
                                    uselist=False,
                                    primaryjoin='Task.project_id==Project.object_id')

Task.project_assignments          = relation('ProjectAssignment',
                                    uselist=True,
                                    primaryjoin='Task.project_id==ProjectAssignment.parent_id')


Task.creator                      = relation('Contact',
                                    uselist=False,
                                    primaryjoin='Task.creator_id==Contact.object_id')

Task.logs                         = relation('AuditEntry',
                                    lazy=True,
                                    uselist=True,
                                    cascade='delete',
                                    order_by='AuditEntry.context_id',
                                    primaryjoin='Task.object_id==AuditEntry.context_id')

Task.acls                         = relation(ACL,
                                    lazy=False,
                                    uselist=True,
                                    cascade='delete',
                                    order_by=ACL.context_id,
                                    primaryjoin=ACL.parent_id==Task.object_id)

Task.info                          = relation('ObjectInfo',
                                     lazy=True,
                                     uselist=False,
                                     order_by='ObjectInfo.object_id',
                                     primaryjoin='Task.object_id==ObjectInfo.object_id')

TaskAction.task                   = relation('Task',
                                    uselist=False,
                                    primaryjoin='TaskAction.task_id==Task.object_id')

TaskAction.actor                 = relation('Contact',
                                    uselist=False,
                                    primaryjoin='TaskAction.actor_id==Contact.object_id')

Task.properties                   = relation('ObjectProperty',
                                    lazy=True,
                                    uselist=True,
                                    order_by='ObjectProperty.parent_id',
                                    cascade='delete',
                                    primaryjoin='Task.object_id==ObjectProperty.parent_id')

ProjectAssignment.project         = relation(Project,
                                    uselist=False,
                                    primaryjoin=(ProjectAssignment.parent_id==Project.object_id))

