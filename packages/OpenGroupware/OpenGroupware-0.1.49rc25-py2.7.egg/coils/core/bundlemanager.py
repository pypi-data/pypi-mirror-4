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
import os, sys, glob, inspect, logging
from coils.foundation       import Backend, ServerDefaultsManager
from entityaccessmanager    import EntityAccessManager
from command                import Command
from service                import Service
from threadedservice        import ThreadedService
from content_plugin         import ContentPlugin

class BundleManager(object):
    __slots__ = ()
    _command_dict = None
    _service_dict = None
    _manager_dict = None
    _plugin_dict  = None

    @staticmethod
    def scan_bundle(bundle):
        sd = ServerDefaultsManager()
        for name, data in inspect.getmembers(bundle, inspect.isclass):
            # Only load classes specifically from this bundle
            if (data.__module__[:len(bundle.__name__)] == bundle.__name__):
                if(issubclass(data, Command)):
                    #
                    # Register command object
                    #
                    x = '%s::%s' % (data.__domain__, data.__operation__)
                    BundleManager._command_dict[x] = data
                elif(issubclass(data, Service) or issubclass(data, ThreadedService)):
                    #
                    # Register service objects
                    #
                    x = str(data.__service__)
                    BundleManager._service_dict[x] = data
                elif(issubclass(data, EntityAccessManager)):
                    #
                    # Register entity access manager
                    #
                    if (hasattr(data, '__entity__')):
                        if (hasattr(data.__entity__, '__iter__')):
                            for entity in data.__entity__:
                                BundleManager._manager_dict[entity.lower()] = data
                        else:
                            BundleManager._manager_dict[data.__entity__.lower()] = data
                elif(issubclass(data, ContentPlugin)):
                    #
                    # Register Content Plugin; possibly to multiple entity types
                    #
                    if (hasattr(data.__entity__, '__iter__')):
                        # Multiple relevent entities
                        for entity in data.__entity__:
                            if (entity.lower() in BundleManager._plugin_dict):
                                BundleManager._plugin_dict[entity.lower()].append(data)
                            else:
                                BundleManager._plugin_dict[entity.lower()] = [ data ]
                    else:
                        if (data.__entity__.lower() in BundleManager._plugin_dict):
                            BundleManager._plugin_dict[entity.lower()].append(data)
                        else:
                            BundleManager._plugin_dict[entity.lower()] = [ data ]
        # Load any defaults if present
        if (hasattr(bundle, 'COILS_DEFAULT_DEFAULTS')):
            x = getattr(bundle, 'COILS_DEFAULT_DEFAULTS')
            for key in x:
                sd.add_server_default(key, x[key])
        return

    @staticmethod
    def load_bundles():
        BundleManager.log = logging.getLogger('bundle')
        BundleManager._command_dict = { }
        BundleManager._service_dict = { }
        BundleManager._manager_dict = { }
        BundleManager._plugin_dict  = { }
        for bundle_name in Backend.get_logic_bundle_names():
            bundle = None
            try:
                bundle =  __import__(bundle_name, fromlist=['*'])
                BundleManager.log.info('Loaded bundle {0}'.format(bundle_name))
            except:
                BundleManager.log.error('Failed to load bundle {0}'.format(bundle_name))
            else:
                BundleManager.scan_bundle(bundle)
        msg = 'Loaded commands:'
        for k in BundleManager._command_dict.keys():
            msg = '%s [%s=%s]' % (msg, k, BundleManager._command_dict[k])
        BundleManager.log.debug(msg)
        msg = 'Loaded services:'
        for k in BundleManager._service_dict.keys():
            msg = '%s [%s=%s]' % (msg, k, BundleManager._service_dict[k])
        BundleManager.log.debug(msg)
        msg = 'Loaded plugins:'
        for k in BundleManager._plugin_dict.keys():
            msg = '%s [%s=%s]' % (msg, k, BundleManager._plugin_dict[k])
        BundleManager.log.debug(msg)
        msg = 'Loaded managers:'
        for k in BundleManager._manager_dict:
            msg = '%s [%s=%s]' % (msg, k, BundleManager._manager_dict[k])
        BundleManager.log.debug(msg)

    @staticmethod
    def list_commands():
        if (BundleManager._command_dict is None):
            BundleManager.load_bundles()
        return BundleManager._command_dict.keys()

    @staticmethod
    def get_command(name):
        if (BundleManager._command_dict is None):
            BundleManager.load_bundles()
        if (name in BundleManager._command_dict):
            return BundleManager._command_dict[name]()
        return None

    @staticmethod
    def has_command(name):
        if (name in BundleManager._command_dict):
            return True
        return False

    @staticmethod
    def list_services():
        if (BundleManager._service_dict is None):
            BundleManager.load_bundles()
        return BundleManager._service_dict.keys()

    @staticmethod
    def get_service(name):
        if (BundleManager._service_dict is None):
            BundleManager.load_bundles()
        if (name in BundleManager._service_dict):
            x = BundleManager._service_dict[name]()
            return x
        return None

    @staticmethod
    def has_service(name):
        if (name in BundleManager._service_dict):
            return True
        return False

    @staticmethod
    def list_access_managers():
        if (BundleManager._manager_dict is None):
            BundleManager.load_bundles()
        return BundleManager._manager_dict.keys()

    @staticmethod
    def get_access_manager(kind, ctx):
        kind = kind.lower()
        if (BundleManager._manager_dict is None):
            BundleManager.load_bundles()
        if (kind in BundleManager._manager_dict):
            return BundleManager._manager_dict[kind](ctx)
        return EntityAccessManager(ctx)

    @staticmethod
    def get_content_plugins(kind, ctx):
        kind = kind.lower()
        if (BundleManager._plugin_dict is None):
            BundleManager.load_bundles()
        if (kind in BundleManager._plugin_dict):
            result = []
            for plugin in BundleManager._plugin_dict[kind]:
                result.append(plugin(ctx))
            return result
        return []
