#
# Copyright (c) 2009, 2012
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
import getopt, os
from coils.foundation import *
from context import Context
from broker import Broker
from bundlemanager import BundleManager
from accessmanager import AccessManager
from context       import AdministrativeContext

def initialize_COILS():
    initialize_COILS({})

def initialize_COILS( options = { } ):
    Backend.__alloc__(**options)
    if (Context._mapper == None ):
        Context._mapper = BundleManager( )
        Context._mapper.load_bundles( )
    #if (Context._accessManager == None):
    #    Context._accessManager = AccessManager(AdministrativeContext())

def initialize_tool(name, argv, arguments=['',[]]):

    def receive_message(message):
        return broker.packet_from_message(message)

    storeroot  = '/var/lib/opengroupware.org'
    add_modules = []
    ban_modules = []
    short_args = 's:i:x:{0}'.format(arguments[0])
    long_args = ["store=", "add-bundle=", "ban-bundle="]
    long_args.extend(arguments[1])
    parameters = { }
    try:
        opts, args = getopt.getopt(argv, short_args, long_args)
    except getopt.GetoptError, e:
        print e
        sys.exit(2)
    for opt, arg in opts:
            if opt in ("-s", "--store"):
                storeroot = arg
            elif opt in ("-i", "--add-bundle"):
                add_modules.append(arg)
            elif opt in ("-x", "--ban-bundle"):
                ban_modules.append(arg)
            else:
                parameters[opt] = arg

    initialize_COILS( { 'store_root':     storeroot,
                        'extra_modules':  add_modules,
                        'banned_modules': ban_modules } )

    broker = Broker()
    broker.subscribe('tool.{0}.{1}'.format(name, os.getpid()), receive_message)
    return AdministrativeContext(broker=broker), parameters
