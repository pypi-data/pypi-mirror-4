# Copyright (c) 2009, 2012
#   Adam Tauno Williams <awilliam@whitemice.org>
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
import glob, inspect, logging
from coils.foundation      import Backend, ServerDefaultsManager
from coils.core            import ActionCommand, MacroCommand

class ActionMapper:

    @staticmethod
    def list_commands():
        if (not(hasattr(ActionMapper, '_action_dict'))):
            ActionMapper.log = logging.getLogger('actions')
            ActionMapper.load_actions()
        return ActionMapper._action_dict.keys()

    @staticmethod
    def list_macros():
        if (not(hasattr(ActionMapper, '_macro_dict'))):
            ActionMapper.log = logging.getLogger('actions')
            ActionMapper.load_actions()
        return ActionMapper._macro_dict.keys()

    @staticmethod
    def scan_bundle(bundle):
        sd = ServerDefaultsManager()
        for name, data in inspect.getmembers(bundle, inspect.isclass):
            # Only load classes specifically from this bundle
            if (data.__module__[:len(bundle.__name__)] == bundle.__name__):
                if(issubclass(data, ActionCommand)):
                    if (hasattr(data, '__aliases__')):
                        command = '%s::%s' % (data.__domain__, data.__operation__)
                        #ActionMapper.log.debug('Found aliased action {0}.'.format(data))
                        for alias in data.__aliases__:
                            #ActionMapper.log.debug('Action alias {0} for {1}.'.format(alias, command))
                            ActionMapper._action_dict[alias] = command
                    else:
                        ActionMapper.log.warn('Found ActionCommand {0} with no aliases.'.format(data))
                elif(issubclass(data, MacroCommand)):
                    if (hasattr(data, '__operation__')):
                        command = '%s::%s' % (data.__domain__, data.__operation__)
                        #ActionMapper.log.debug('Macro alias {0} for {1}.'.format(data.__operation__, command))
                        ActionMapper._macro_dict[data.__operation__] = command
        return

    @staticmethod
    def load_actions():
        ActionMapper._action_dict = { }
        ActionMapper._macro_dict = { }
        for bundle_name in Backend.get_logic_bundle_names():
            bundle = None
            try:
                bundle =  __import__(bundle_name, fromlist=['*'])
            except:
                ActionMapper.log.debug('Failed to import bundle {0}'.format(bundle_name))
            else:
                #ActionMapper.log.debug('scanning bundle: {0} list=* '.format(bundle_name))
                ActionMapper.scan_bundle(bundle)
        msg = 'Loaded actions:'
        for k in ActionMapper._action_dict.keys():
            msg = '%s [%s=%s]' % (msg, k, ActionMapper._action_dict[k])
        msg = 'Loaded macros:'
        for k in ActionMapper._macro_dict.keys():
            msg = '%s [%s=%s]' % (msg, k, ActionMapper._macro_dict[k])
        #ActionMapper.log.debug(msg)

    @staticmethod
    def get_action(name):
        if (not(hasattr(ActionMapper, '_action_dict'))):
            ActionMapper.log = logging.getLogger('actions')
            ActionMapper.load_actions()
        if (name in ActionMapper._action_dict):
            action = ActionMapper._action_dict.get(name, None)
            ActionMapper.log.debug('Returning action {0} for alias {1}'.format(action, name))
        else:
            action = None
            ActionMapper.log.warn('No command has an alias of {0}'.format(name))
        return action

    @staticmethod
    def get_macro(name):
        if (not(hasattr(ActionMapper, '_macro_dict'))):
            ActionMapper.log = logging.getLogger('actions')
            ActionMapper.load_actions()
        if (name in ActionMapper._macro_dict):
            action = ActionMapper._macro_dict.get(name, None)
            ActionMapper.log.debug('Returning macro {0} for alias {1}'.format(action, name))
        else:
            action = None
            ActionMapper.log.warn('No command has an alias of {0}'.format(name))
        return action
