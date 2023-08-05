#
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
#
import os, pickle
import api.core as twython
from coils.foundation import ServerDefaultsManager, Backend
from coils.core  import Command, CoilsException
from exception   import TwitterAPIException

class TwitterCommand(Command):

    def __init__(self):
        Command.__init__(self)
        self._sd = ServerDefaultsManager()
        self._twitter = None
        self._cache_dir = '{0}/cache/plugin.twitter'.format(Backend.store_root())
        try:
            if (not os.path.exists(self._cache_dir)):
                self.log.info('Creating cache directory for Twitter bundle')
                os.mkdir(self._cache_dir)
        except Exception, e:
            self.log.exception(e)
            raise CoilsException('Unable to unitialize cache for Twitter bundle')

    def get_twitter_connection(self):
        # Get proxy configuration from server defaults
        try:
            # ServerDefaultsManager throws an exception if the requested
            # default does not exist, so we take exception to mean that.
            proxy_config = self._sd.default_as_dict('LSHTTPProxy')
        except Exception, e:
            self._proxy  = None
        else:
            # Format LSHTTPProxy to the proxyobj struct expected by Twython
            self._proxy = { 'host': proxy_config.get('host'),
                            'port': int(proxy_config.get('port')) }
            if ('username' in proxy_config):
                self._proxy['username'] = proxy_config.get('username')
                self._proxy['password'] = proxy_config.get('password')
            self.log.debug('Twitter API using proxy http://{0}:{1}'.format(self._proxy['host'],
                                                                           self._proxy['port']))
        # Create twitter config
        if (self._proxy is None):
            twitter = twython.setup(username = self._username,
                                    password = self._password)
        else:
            twitter = twython.setup(username = self._username,
                                    password = self._password,
                                    proxy    = self._proxy)
        if (twitter is not None):
            self._twitter = twitter
        else:
            raise CoilsException('Unable to create Twitter API object')

    def is_connected(self):
        if (self._twitter is not None):
            if (self._twitter.authenticated):
                return True
        return False

    def get_tweeter(self, tweeter_id):
        filename = '{0}/{1}.cpd'.format(self._cache_dir, str(tweeter_id))
        if (os.path.exists(filename)):
            handle = open(filename, 'rb')
            tweeter = pickle.load(handle)
            handle.close()
        else:
            tweeter = {'Oops': 'Not cached' }
        return tweeter

    def get_public_timeline(self):
        if (self.is_connected()):
            try:
                self.log.debug('Requesting Twitter public timeline.')
                _result = self._twitter.getPublicTimeline()
            except twython.TwythonError, e:
                self.log.exception(e)
                raise TwitterAPIException('Twitter API operation get-public-timeline failed.')
            else:
                return self.format_timeline(_result)
        else:
            raise TwitterAPIException('Not authenticated to the Twitter service.')

    def get_user_timeline(self, screenname):
        if (self.is_connected()):
            try:
                self.log.debug('Requesting Twitter timeline for user {0}'.format(screenname))
                _result = self._twitter.getUserTimeline(screen_name=screenname,count=50)
            except twython.TwythonError, e:
                self.log.exception(e)
                raise TwitterAPIException('Twitter API operation get-user-timeline failed.')
            else:
                return self.format_timeline(_result)
        else:
            raise TwitterAPIException('Not authenticated to the Twitter service.')
        return result

    def format_tweet(self, tweet):
        ''' Turn a tweet from the underlying API provider into something resembling
            an Omphalos entity representation.  This also strips out a bunch of
            redundant gunk. '''
        def squash_none(value, default):
            if (value is None):
                return default
            return value

        self.cache_tweeter(tweet.get('user'))
        # TODO: Include geo info, if available, in some sensible fashion.
        return { 'dataType':   'Tweet',
                  'id':         str(tweet.get('id')),
                  'created':    tweet.get('created_at', ''),
                  'inReplyTo': { 'screenName': squash_none(tweet.get('in_reply_to_screen_name'), ''),
                                 'id':         str(squash_none(tweet.get('in_reply_to_status_id'), '')),
                                 'userId':     squash_none(tweet.get('in_reply_to_user_id'), '') },
                  'text':       tweet.get('text', ''),
                  'userId':     str(tweet.get('user').get('id')),
                  'screenName': squash_none(tweet.get('user').get('screen_name', ''), '') }

    def format_tweeter(self, user):
        # TODO: Grab the image at the profile_image_url URL and b64 it,
        #       and put the image in the cache.  These should be small.
        def squash_none(value, default):
            if (value is None):
                return default
            return value

        return { 'dataType':   'Tweeter',
                  'id':          str(user.get('id')),
                  'description': squash_none(user.get('description'), ''),
                  'location':    squash_none(user.get('location'), ''),
                  'screenName':  squash_none(user.get('screen_name'), ''),
                  'timeZone':    squash_none(user.get('time_zone'), ''),
                  'url':         squash_none(user.get('url'), '') }

    def format_timeline(self, tweets):
        result   = []
        tweeters = []
        for _tweet in tweets:
            tweet = self.format_tweet(_tweet)
            result.append(tweet)
            if (tweet.get('userId') not in tweeters):
                tweeters.append(tweet.get('userId'))
        for tweeter_id in tweeters:
            tweeter = self.get_tweeter(tweeter_id)
            result.append(tweeter)
        return result

    def tweeter_cached(self, tweeter_id):
        filename = '{0}/{1}.cpd'.format(self._cache_dir, str(tweeter_id))
        return os.path.exists(filename)

    def cache_tweeter(self, user_data):
        # TODO: Should cache be per username/profile?
        if (self.tweeter_cached(user_data.get('id'))):
            return
        # TODO: Catch I/O exceptions
        filename = '{0}/{1}.cpd'.format(self._cache_dir, str(user_data.get('id')))
        handle = open(filename, 'wb')
        pickle.dump(self.format_tweeter(user_data), handle)
        handle.close()
        return True

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        if ('username' in params):
            # Username and password provided in parameters
            self._username = params.get('username')
            self._password = params.get('password')
        elif ('profile' in params):
            # Twitter account profile requested
            profile_obj = self._sd.default_as_dict('PYTwitterProfiles').get(params['profile'], None)
            if (profile_obj is not None):
                self._username = profile_obj.get('username')
                self._password = profile_obj.get('password')
        else:
            try:
                profiles = self._sd.default_as_dict('PYTwitterProfiles')
                default_name = profiles.get('default')
                profile_obj = profiles.get(default_name)
                self._username = profile_obj.get('username')
                self._password = profile_obj.get('password')
            except Exception, e:
                self.log.exception(e)
                raise CoilsException('Unable to configure TwitterCommand.')
