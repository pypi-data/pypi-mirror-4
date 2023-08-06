#
# Copyright (c) 2011, 2013
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
import smtpd, re, asyncore, threading, pprint, string, time
from email.generator import Generator
from email.Parser import Parser
from coils.core  import *

INTERESTING_HEADERS = ( 'subject', 'x-spam-level', 'from', 'to', 'date',
                        'x-spam-status', 'reply-to', 'x-virus-scanned',
                        'x-bugzilla-classification', 'x-bugzilla-product',
                        'x-bugzilla-component', 'x-bugzilla-severity',
                        'x-bugzilla-status', 'x-bugzilla-url', 'x-mailer',
                        'x-original-sender', 'mailing-list', 'list-id',
                        'x-opengroupware-regarding', 'x-opengroupware-objectid',
                        'x-original-to', 'in-reply-to', 'cc',
                        'x-gm-message-state',  )

TRANSCODE_MAP = string.maketrans(' <>%&/\\', '____---' )

def transcode_to_filename( filename ):
    return filename.translate( TRANSCODE_MAP )

def parse_message_from_string( data ):
    return Parser( ).parsestr( data )


def get_raw_message_stream( message ):
    s = BLOBManager.ScratchFile( encoding='binary' )
    g = Generator( s, mangle_from_=False, maxheaderlen=255 )
    g.flatten( message )
    return s

def get_streams_from_message( message, mimetype, logger ):
    message_id = message.get( 'message-id' )
    streams = { }
    if mimetype == 'message/rfc822':
        filename = transcode_to_filename( '{0}.{1}.mbox'.format( message_id, time.time( ) ) )
        streams[ filename ] = get_raw_message_stream( message )
        logger.debug( 'Saving full raw message' )
    elif message.is_multipart( ):
        counter = 0
        for section in message.get_payload():
            if section.get_content_type() == mimetype:
                counter += 1
                filename = transcode_to_filename( '{0}.{1}.{2}.part'.format( message_id, counter, time.time( ) ) )
                if not section.is_multipart( ):
                    s = BLOBManager.ScratchFile( encoding='binary' )
                    s.write( section.get_payload( decode=True ) )
                    streams[ filename ] = s
                else:
                    streams[ filename ] = get_raw_message_stream( section )
        logger.debug( 'Found {0} parts in message of type "{1}"'.format( counter, mimetype ) )
    elif mimetype == 'text/plain':
        s = BLOBManager.ScratchFile( encoding='binary' )
        s.write( message.get_payload() )
        streams[ transcode_to_filename( '{0}.{1}.txt'.format( message_id, time.time( ) ) ) ] = s
        logger.debug( 'Saving text of non-multipart message' )
    else:
        logger.debug( 'No candidate parts of message to save' )
    return message_id, streams


def get_properties_from_message( message, mimetype=None ):
    message_id = message.get( 'message-id' )
    props = [ ( 'us.opengroupware.mail.header', 'message-id', message_id, ), ]
    if mimetype:
        props.append( ( 'http://www.opengroupware.us/mswebdav', 'contentType', mimetype, ) )
    for header in INTERESTING_HEADERS:
        if message.has_key( header ):
            props.append( ( 'us.opengroupware.mail.header', header, message.get( header ), ) )
    return props


class SMTPServer(smtpd.SMTPServer):

    def __init__(self, manager):
        self.manager = manager
        sd = ServerDefaultsManager()
        SMTP_ADDR = sd.string_for_default('SMTPListenAddress', '127.0.0.1')
        SMTP_PORT = sd.integer_for_default('SMTPListenPort', 25252)
        smtpd.SMTPServer.__init__(self, (SMTP_ADDR, SMTP_PORT), None)

    def process_message(self, peer, from_, to_, data):
        # TODO: Verify one of the recipients is a candidate
        # TODO: discard messgaes over a given size?
        # TODO: discard messages with more tha n recipients?
        self.manager.enqueue_message((from_, to_, data))


class SMTPService(Service):
    __service__ = 'coils.smtpd'
    __auto_dispatch__ = True
    __is_worker__     = True

    @property
    def queue(self):
        return self._queue

    @property
    def queue_lock(self):
        return self._queue_lock

    @property
    def smtp_prefix(self):
        return self._prefix

    @property
    def ctx(self):
        return self._ctx

    def prepare(self):
        Service.prepare(self)
        try:
            sd = ServerDefaultsManager()
            self._prefix= sd.string_for_default('SMTPAddressPrefix', 'ogo').lower()
            self._queue = [ ]
            self._queue_lock = threading.Lock()
            self._smptd = SMTPServer(self)
            self._thread = threading.Thread(target=lambda:asyncore.loop())
            self._thread.start()
            self._ctx = NetworkContext(broker=self._broker)
        except Exception, e:
            self.log.warn('Exception in SMTP component prepare')
            self.log.exception(e)
            raise e

    def shutdown(self):
        self._smtpd.stop()
        Service.shutdown(self)

    def enqueue_message(self, message):
        with self.queue_lock:
            self.queue.append(message)

    def work(self):
        # TODO: Component check should be a time-based, not iteration based, component
        with self.queue_lock:
            self.log.debug( 'SMTP service checking message queue' )
            while self.queue:
                data = self.queue.pop( )
                self.log.info( 'SMTP server found message!' )
                try:
                    recipient = None
                    message = parse_message_from_string( data[ 2 ] )
                    if message.has_key( 'message-id' ):
                        for recipient in data[ 1 ]:
                            recipient = recipient.lower( ).strip( )
                            self.log.debug( 'checking recipient {0}'.format( recipient ) )
                            x = recipient.split( '@' )[ 0 ].split( '+', 1 )
                            if len( x ) == 2:
                                if x[0].lower() == self.smtp_prefix:
                                    recipient = x[ 1 ]
                                    break
                        else:
                            self.log.warn( 'Discarding message, no matching recipients' )
                    else:
                        self.log.warn( 'Invalid message, message received with no Message-ID' )
                except Exception, e:
                    self.log.info( 'SMTP failed to parse message' )
                    self.log.exception( e )
                else:
                    self.log.info('SMTP sending administrative message')
                    try:
                        # TODO: Allow capturing of received messages via a toggle default
                        '''self.send_administrative_notice(subject='Received messgae via SMTP',
                                                        message=pprint.pformat((recipient, data[0], data[1], data[2])),
                                                        urgency=4,
                                                        category='network',
                                                        attachments=[])'''
                        self.process_recipient(data[0], recipient, message)
                    except Exception, e:
                        self.log.exception(e)


    def process_recipient(self, from_, to_, message):
        targets = to_.split('+')
        if len( targets ) == 1:
            try:
                object_id = int(targets[0])
            except:
                self.log.warn('Unable to convert single recipient target "{0}" into an integer value'.format(target[0]))
            else:
                self.log.info('Processing SMTP recipient as an objectId')
                # TODO: Support e-mails to entities, like tasks
                kind = self._ctx.type_manager.get_type(object_id)
                self.log.info('objectId#{0} identitified as a "{1}"'.format(object_id, kind))
                if (kind == 'Task'):
                    self.annotate_task(object_id, message)
                elif (kind == 'Collection'):
                    self.send_to_collection(object_id, message)
                elif (kind == 'Folder'):
                    self.send_to_folder(object_id, message, from_, to_)
        elif (len(targets) == 2):
            if (targets[0] == 'wf'):
                self.create_process(from_, targets[1], message)
            else:
                self.log.warn('Nested outer target type of "{0}" not recognized'.format(targets[0]))
        else:
            self.log.warn('Target of message has too many components')

    def annotate_task(self, object_id, message):
        pass

    def send_to_folder(self, object_id, message, from_, to_):

        def save_streams( context, folder, props, streams, mimetype ):
            for filename, stream in streams.items( ):
                # Create the document
                stream.seek( 0 )
                document = context.run_command( 'document::new', name=filename,
                                                                 handle=stream,
                                                                 values = { },
                                                                 folder=folder,
                                                                 access_check=False )
            for prop in props:
                context.property_manager.set_property( document, prop[0], prop[1], prop[2] )

            return True

        folder = self._ctx.run_command( 'folder::get', id=object_id )
        if folder is None:
            self.log.warn( 'OGo#{0} [Folder] not available to the NetworkContext'.format( object_id ) )
            self.send_administrative_notice(
                subject='Insufficient permissions to deliver SMTP message to folder',
                message='Attempt to delivery message from {0} to folder OGo#{1}.\nCannot marshall folder.\n'.format( from_, object_id ),
                urgency=5,
                category='security',
                attachments=[ ] )
            return
             
        rights = self._ctx.access_manager.access_rights( folder )
        if 'w' not in rights:
            self.log.warn('OGo#{0} [Folder] not available to the NetworkContext'.format(object_id))
            self.send_administrative_notice(
                subject='Insufficient permissions to deliver SMTP message to folder',
                message='Attempt to delivery message from {0} to folder OGo#{1}.\nWrite access required.\n'.format( from_, object_id ),
                urgency=5,
                category='security',
                attachments=[])
            return

        prop = self._ctx.property_manager.get_property( folder, 'http://www.opengroupware.us/smtp', 'collectMIMEType' )
        if prop:
            mimetype = prop.get_value( )
        else:
            mimetype = 'message/rfc822'
            self.log.debug( 'No collectMIMEType specified for folder, default to raw message storage' )

        message_id, streams = get_streams_from_message( message=message, mimetype=mimetype, logger=self.log )

        if not streams:
            self.log.debug( 'No streams discovered from message' )
            return

        props = get_properties_from_message( message, mimetype=mimetype )
        save_streams( self._ctx, folder, props, streams, mimetype )
        self._ctx.commit( )

    def send_to_collection(self, object_id, message):
        collection = self._ctx.run_command('collection::get', id=object_id)

        def authenticate_collection(object_id, message):
            collection = self._ctx.run_command('collection::get', id=object_id)
            if (collection is None):
                self.log.warn('CollectionId#{0} not available to the NetworkContext'.format(object_id))
            elif (collection.owner_id == 10000):
                self.log.warn('CollectionId#{0} is owned by the administrator; forbidden.'.format(object_id))
            elif (collection.auth_token is None):
                self.log.warn('CollectionId#{0} has no authentication token'.format(object_id))
            elif (collection.auth_token == 'unpublished'):
                self.log.warn('CollectionId#{0} is specifically not published'.format(object_id))
            elif (collection.auth_token == 'published'):
                return collection
            elif (message.has_key('subject')):
                auth_tokens = re.findall('^\[[A-z0-9_]*\]', message.get('subject'))
                if (len(auth_tokens) == 1):
                    auth_token = auth_tokens[0]
                    if (len(auth_token) == 12):
                        if (auth_token == collection.auth_token):
                            self.log.warn('Message authenticated to CollectionId#{0}'.format(object_id))
                            return collection
                        else:
                            self.log.warn('Authentication token mismatch for CollectionId#{0}'.format(object_id))
                    else:
                        self.log.warn('Authentication token "{0} has inappropriate length.'.format(auth_token))
                else:
                    # No authentication token in subject
                    self.log.warn('No authentication token in message subject')
            return None

        def retrieve_route():
            route = self.ctx.run_command('route::get', name='CoilsSendToCollection')
            if (route is None):
                message = 'Built-In route "{0}" available.'.format('CoilsSendToCollection')
                self.log.warn(message)
                self.send_administrative_notice(subject='Unable to marshall route requested via SMTP',
                            message=message,
                            urgency=7,
                            category='workflow',
                            attachments=[])
                return None
            return route

        collection = authenticate_collection(object_id, message)
        if (collection is not None):
            # Authentication token is now removed from the message subject!
            message.replace_header('subject', message.get('subject')[12:])
            route = retrieve_route()
            if (route is not None):
                #
                # Serialize the message in a temporary file, this will be in the input of our OIE route
                #
                tmp = BLOBManager.ScratchFile()
                g = Generator(tmp, mangle_from_=False, maxheaderlen=60)
                g.flatten(message)
                tmp.seek(0)
                #
                # Create and start the process
                #
                process =  self._ctx.run_command('process::new', values={ 'route_id': route.object_id,
                                                                          'handle':   tmp,
                                                                          'priority': 210 } )
                process.owner_id = collection.owner_id
                self._ctx.property_manager.set_property(process,
                                                        'http://www.opengroupware.us/oie',
                                                        'xattr_collectionid',
                                                        str(object_id))
                self.ctx.commit()
                BLOBManager.Close(tmp)
                self.ctx.run_command('process::start', process=process, runas=10100)
                message = 'Requesting to start ProcessId#{0} / RouteId#{0}.'.format(process.object_id, route.object_id)
                self.log.info(message)
            else:
                self.log.error('OIE Route entity for message delivery to Collection entities not available')

    def create_process(self, from_, to_, message):
        # This is meant to trigger a workflow!
        route = self._ctx.run_command( 'route::get', name=to_ )
        if route:
            self.log.warn( 'Creating process from route routeId#{0}'.format( route.object_id ) )
            if message.is_multipart( ):
                message = 'A multipart message was submitted to routeId#{0}'.format(route.object_id)
                self.send_administrative_notice(subject='Multipart message submitted to workflow',
                            message=message,
                            urgency=8,
                            category='workflow',
                            attachments=[])
            else:
                # Single part message
                try:
                    #payload = message.get( 'Subject' )
                    # For a non-multipart message the get_payload returns the message body
                    payload = message.get_payload( decode=True )
                except Exception, e:
                    self.log.exception( e )
                else:
                    process =  self._ctx.run_command( 'process::new', values={ 'route_id': route.object_id,
                                                                               'data':     payload,
                                                                               'priority': 210 } )
                    self._ctx.property_manager.set_property( process,
                                                             'http://www.opengroupware.us/oie',
                                                             'xattr_from', from_ )
                    self._ctx.commit( )
                    self._ctx.run_command( 'process::start', process=process )
                    message = 'Requesting to start ProcessId#{0} / RouteId#{0}.'.format( process.object_id, route.object_id )
                    self.log.info( message )
        else:
            message = 'No such route as "{0}" available in the network context\nFrom: {1}\n'.format( to_, from_ )
            self.log.warn(message)
            self.send_administrative_notice( subject='Unable to marshall route requested via SMTP',
                                             message=message,
                                             urgency=7,
                                             category='workflow',
                                             attachments=[ ] )
