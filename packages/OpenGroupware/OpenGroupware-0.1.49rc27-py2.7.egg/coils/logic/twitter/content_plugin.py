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
#
import os, pickle, time
from urllib2     import URLError
from coils.core  import *

class TwitterContentPlugin(ContentPlugin):
    __entity__     = [ 'Contact', 'Enterprise' ]
    __pluginName__ = 'org.opengroupware.coils.twitter'
    __cache_dir    = None

    def __repr__(cls):
        return u'TwitterContentPlugin'

    def __init__(self, ctx):
        ContentPlugin.__init__(self, ctx)
        if (TwitterContentPlugin.__cache_dir is None):
            TwitterContentPlugin.__cache_dir = 'cache/plugin.twitter'

    def get_extra_content(self, entity):
        prop = self._ctx.property_manager.get_property(entity,
                                                       'http://whitemice.consulting.com/coils.twitter',
                                                       'screenName')
        if (prop is None):
            return  { }
        screen_name = str(prop.get_value())
        timeline = self.get_cached_timeline(screen_name)
        if (timeline is None):
            self.log.debug('Retrieving timeline for Twitter user {0}.'.format(screen_name))
            try:
                timeline = self._ctx.run_command('twitter::get-user-timeline', screenname=screen_name)
            except URLError, e:
                self.log.error('Unable to communicate with Twitter.')
                self.log.exception(e)
                timeline = []
            else:
                self.cache_timeline(screen_name, timeline)
        else:
            self.log.debug('Using cached timeline for Twitter user {0}'.format(screen_name))
        self.log.debug('Twitter content plugin found {0} elements'.format(len(timeline)))
        return { 'screenName': screen_name,
                  'timeLine': timeline }

    def get_cached_timeline(self, screen_name):
        filename = '{0}/{1}.timeline.cpd'.format(TwitterContentPlugin.__cache_dir, screen_name)
        blob = BLOBManager.Open(filename, 'rb', encoding='binary')
        if (blob is not None):
            timeline = pickle.load(blob)
            BLOBManager.Close(blob)
            t = time.time()
            # TODO: Make lifespan of cached timelines configurable.
            if ((t - timeline.get('timestamp')) < 3600):
                return timeline.get('timeline')
            BLOBManager.Delete(filename)
        return None

    def cache_timeline(self, screen_name, timeline):
        filename = '{0}/{1}.timeline.cpd'.format(TwitterContentPlugin.__cache_dir,
                                                 screen_name)
        data = { 'timestamp': time.time(),
                 'timeline': timeline }
        blob = BLOBManager.Create(filename, encoding='binary')
        pickle.dump(data, blob)
        BLOBManager.Close(blob)
