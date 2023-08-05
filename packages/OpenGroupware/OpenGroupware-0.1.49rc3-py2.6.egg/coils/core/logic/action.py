#
# Copyright (c) 2009, 2010, 2012
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
import os, re
from datetime            import datetime, timedelta, date
from xml.sax.saxutils    import escape, unescape
from tempfile            import mkstemp
from coils.core          import Command, CoilsException
from coils.foundation    import AuditEntry, BLOBManager

class ActionCommand(Command):

#
# ctor
#

    def __init__(self):
        Command.__init__(self)
        self._rfile    = None
        self._wfile    = None
        self._shelf    = None
        self._proceed  = True
        self._continue = True

#
# Implement your action here!
#

    def parse_action_parameters(self):
        pass

    def do_action(self):
        # Child MUST implement
        pass

    def do_epilogue(self):
        # Child MAY implement
        pass

    def audit_action(self):
        # Disable logging!
        pass

#
# Properties
#

    @property
    def rfile(self):
        return self._rfile

    @property
    def wfile(self):
        return self._wfile

    @property
    def input_message(self):
        return self._input

    @property
    def input_mimetype(self):
        return self._mime

    @property
    def action_parameters(self):
        return self._params

    @property
    def process(self):
        return self._process

    @property
    def pid(self):
        return self._process.object_id

    @property
    def state(self):
        return self._state

    @property
    def result_mimetype(self):
        # Actions that produce output other than XML MUST override this so that
        # their messages are approprately marked.
        return 'application/xml'

    @property
    def scope_stack(self):
        return self._scope

    @property
    def scope_tip(self):
        # Returns the outermost scope id; which is the UUID of the action which
        # created the scope.  Scopes are created by the Workflow Executor's
        # Process workers.  Honoring scope is implemented in the appropriate
        # Workflow bundle's Logic commands.
        if (len(self._scope) > 0):
            return self._scope[-1]
        return None

    @property
    def shelf(self):
        # CLUSTER-TODO
        # WARN: shelf transfer needs to be dealt with to add clustering
        if (self._shelf is None):
            self._shelf = BLOBManager.OpenShelf(uuid=self._process.uuid)
            self.log.debug('Shelf {0} open for {1}.'.format(self._shelf, self._process.uuid))
        return self._shelf

    @property
    def uuid(self):
        return self._uuid

#
# Utility
#

    def encode_text(self, text):
        ''' Wraps xml.sax.saxutils.escape so descendents don't have to do an import . '''
        return unicode(escape(text))

    def decode_text(self, text):
        ''' Wraps xml.sax.saxutils.unescape so descendents don't have to do an import . '''
        return unescape(text)

    def store_in_message(self, label, wfile, mimetype='application/octet-stream'):
        message = None
        if (label is not None):
            message = self._ctx.run_command('message::get', process=self._process,
                                                            scope=self._scope,
                                                            label=label)
        if (message is None):
            self._result = self._ctx.run_command('message::new', process=self._process,
                                                                 handle=wfile,
                                                                 scope=self.scope_tip,
                                                                 mimetype=mimetype,
                                                                 label=label)
        else:
            self._result = self._ctx.run_command('message::set', object=message,
                                                                 handle=wfile,
                                                                 mimetype=mimetype)

    def log_message(self, message, category=None):
        if category is None:
            category = 'info'
        if (self._ctx.amq_available):
            self._ctx.send(None,
                           'coils.workflow.logger/log',
                           { 'process_id': self._process.object_id,
                             'stanza': self.uuid,
                             'category': category,
                             'message': message } )
        else:
            self.log.debug('[{0}] {1}'.format(category, message))

#
# Internal - these methods should never be overridden
#

    def run(self):
        self.parse_action_parameters()
        if (self.verify_action()):
            self.do_prepare()
            self.do_action()
            # Must close _rfile before _wfile so messages can replace themselves!
            self._rfile.close()
            # Flush the output temp file
            self._wfile.flush()
            self.store_in_message(self._label, self._wfile, self.result_mimetype)
            BLOBManager.Delete(self._wfile)
            self.do_epilogue()
            if (self._shelf is not None):
                self._shelf.close()
        else:
            raise CoilsException('Action verification failed.')
        self._result = (self._continue, self._proceed)

    def set_proceed(self, value):
        self._proceed = bool(value)

    def set_continue(self, value):
        self._continue(self, bool(value))

    def parse_parameters(self, **params):
        self._input         = params.get('input', None)
        self._label         = params.get('label', None)
        self._params        = params.get('parameters', {})
        self._process       = params.get('process')
        self._uuid          = params.get('uuid')
        self._scope         = params.get('scope', [])
        self._state         = params.get('state', None)

    @staticmethod
    def get_builtin_value(ctx, process, label):
        """
        Return the value of the specified built-in label. This method is
        static as it is used both by this classes process_label_substitutions
        method and called possibly when creating XATTR values for processes
        created by the schedular component.
        
        :param ctx: The current operational context.
        :param process: The current process entity
        :param label: The full text of the label
        """
        
        # Tests for label values are in the CoilsCoreLogiActionLabelsTest test
        # tests/coils_cor_logic_action_labels
        
        if label == '$__DATE__;':
            return datetime.now( ).strftime( '%Y%m%d' )
        elif label == '$__TODAY__;':
            return date.today( ).strftime( '%Y-%m-%d' )
        elif label == '$__YESTERDAY__;':
            return ( date.today( ) - timedelta( days=1 ) ).strftime( '%Y-%m-%d' )
        elif label == '$__TOMORROW__;':
            return ( date.today( ) + timedelta( days=1 ) ).strftime( '%Y-%m-%d' )            
        elif label == '$__USCIVILIANDATE__;':
            return datetime.now( ).strftime( '%m/%d/%Y' )
        elif label == '$__OMPHALOSDATE__;':
            return datetime.now( ).strftime( '%Y-%m-%d' )
        elif label == '$__MONTHSTART__;':
            return datetime.now( ).strftime( '%Y-%m-01' )
        elif label == '$__DATETIME__;':
            return datetime.now( ).strftime( '%Y%m%dT%H:%M' )
        elif label == '$__OMPHALOSDATETIME__;':
            return datetime.now( ).strftime( '%Y-%m-%d %H:%M' )
        elif label == '$__NOW_Y2__;':
            return datetime.now( ).strftime( '%y' )
        elif label == '$__NOW_Y4__;':
            return datetime.now( ).strftime( '%Y' )
        elif label == '$__NOW_M2__;':
            return  datetime.now( ).strftime( '%m' )
        elif label == '$__PID__;':
            return str( process.object_id )
        elif label == '$__TASK__;':
            return str( process.task_id )
        elif label == '$__EMAIL__;':
            return ctx.email
        elif label == '$__ROUTE__;':
            if process.route:
                return process.route.name
            else:
                return u'UNKNOWN'
        else:
            # self.log.debug( 'Encountered unknown {0} content alias'.format( label ) )
            pass
        return None
        
    @staticmethod
    def scan_and_replace_labels( ctx, process, text, default=None, builtin_only=False, scope=None ):
        # Process special internal labels
        
        if not isinstance( text, basestring ):
            return text 
            
        labels = set( re.findall( '\$__[A-z0-9]*__;', text ) )
        for label in labels:
            if label[ 0:9 ] == '$__XATTR_' and not builtin_only:
                propname = label[ 9:-3 ].lower( )
                prop = ctx.property_manager.get_property( process,
                                                          'http://www.opengroupware.us/oie',
                                                          'xattr_{0}'.format( propname ) )
                if prop:
                    value = str( prop.get_value( ) )
                    text = text.replace( label, value )
                else:
                    if not default:
                        self.log.debug( 'Encountered unknown xattr reference "{0}"'.format( propname ) )
                        text = text.replace( label, '' )
                    else:
                        text = text.replace( label, default )
            else:
                value = ActionCommand.get_builtin_value( ctx, process, label )
                if value:
                    text = text.replace( label, value )

        # Do not scan for message labels in builtin-only mode
        if builtin_only:
            return text

        # Process message labels
        labels = set(re.findall('\$[A-z0-9]*;', text))
        if len( labels ) == 0:
            return text
        for label in labels:
            try:
                data = ctx.run_command( 'message::get-text', process=process,
                                                             scope=scope,
                                                             label=label[ :-1 ][ 1: ] )
            except Exception, e:
                # self.log.exception( e )
                # self.log.error( 'Exception retrieving text for label {0}'.format( label ) )
                raise e
            text = text.replace( label, data )
        return text
        
    def process_label_substitutions(self, text, default=None, builtin_only=False):
        """
        Process the provided text for any values that should be replaced.  
        This includes referrences to messages by label, references to 
        extended attributes [aka XATTRs], and usable of built-in labels.
        
        :param text: The text to be scanned for labels.
        :param default: A default value to be used as the value for any 
            message reference to which a corresponding XATTR reference 
            where the XATTR does not exist.
        :param builtin_only: Only process for built-in labels.
        """
        
        # guardian clauses
        if not text:
            return ''
        if isinstance( text, basestring ):
            if len( text ) < 3:
                return text
            else:
                pass
        else:
            return text
        
        return ActionCommand.scan_and_replace_labels( self._ctx, 
                                                      self._process, 
                                                      text, 
                                                      default=default, 
                                                      builtin_only=builtin_only, 
                                                      scope=self._scope )

    def verify_action(self):
        # Make sure an action has the three requisite components for execution
        # 1.) An Input
        # 2.) A process context
        # 3.) A copy of the current Process state
        #if (self._input is None):
        #    raise CoilsException('No input message specified for action.')
        if (self._process is None):
            raise CoilsException('No process associated with action.')
        if (self._state is None):
            raise CoilsException('No process state provided for action.')
        return True


    def do_prepare(self):
        if (self._input is None):
            self._rfile = BLOBManager.ScratchFile()
            self._mime  = 'application/octet-stream'
        else:
            self._rfile    = self._ctx.run_command('message::get-handle', object=self._input)
            self._mime     = self._input.mimetype
        self._wfile    = BLOBManager.ScratchFile()

