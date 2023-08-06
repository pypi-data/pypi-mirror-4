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
import cgi, string
from datetime   import datetime
from StringIO   import StringIO
from coils.core import *
from pathobject  import PathObject
from bufferedwriter import BufferedWriter

TRANSCODE_TABLE = string.maketrans(#Input
                         chr(0x19) + chr(0x1c) + chr(0x1d) + chr(0x1e) +
                         chr(0x85) +
                         chr(0x91) + chr(0x92) + chr(0x93) + chr(0x94) +
                         chr(0x95) + chr(0x96) + chr(0x97) + chr(0x98) +
                         chr(0x99) +
                         # A - Graphics Characters
                         chr(0xa1) + chr(0xa2) + chr(0xa3) + chr(0xa4) +
                         chr(0xa5) + chr(0xa6) + chr(0xa7) + chr(0xa8) +
                         chr(0xa9) + chr(0xaa) + chr(0xab) + chr(0xac) +
                         chr(0xad) + chr(0xae) + chr(0xaf) +
                         # B - Block Characters
                         chr(0xb1) + chr(0xb2) + chr(0xb3) + chr(0xb4) +
                         chr(0xb5) + chr(0xb6) + chr(0xb7) + chr(0xb8) +
                         chr(0xb9) + chr(0xba) + chr(0xbb) + chr(0xbc) +
                         chr(0xbd) + chr(0xbe) + chr(0xbf) +
                         # C - Block Characters
                         chr(0xc1) + chr(0xc2) + chr(0xc3) + chr(0xc4) +
                         chr(0xc5) + chr(0xc6) + chr(0xc7) + chr(0xc8) +
                         chr(0xc9) + chr(0xca) + chr(0xcb) + chr(0xcc) +
                         chr(0xcd) + chr(0xce) + chr(0xcf) +
                         # D - Block Characters
                         chr(0xd1) + chr(0xd2) + chr(0xd3) + chr(0xd4) +
                         chr(0xd5) + chr(0xd6) + chr(0xd7) + chr(0xd8) +
                         chr(0xd9) + chr(0xda) + chr(0xdb) + chr(0xdc) +
                         chr(0xdd) + chr(0xde) + chr(0xdf) +
                         # E - Math Characters
                         chr(0xe1) + chr(0xe2) + chr(0xe3) + chr(0xe4) +
                         chr(0xe5) + chr(0xe6) + chr(0xe7) + chr(0xe8) +
                         chr(0xe9) + chr(0xea) + chr(0xeb) + chr(0xec) +
                         chr(0xed) + chr(0xee) + chr(0xef) +
                         # F - Math Characters
                         chr(0xf1) + chr(0xf2) + chr(0xf3) + chr(0xf4) +
                         chr(0xf5) + chr(0xf6) + chr(0xf7) + chr(0xf8) +
                         chr(0xf9) + chr(0xfa) + chr(0xfb) + chr(0xfc) +
                         chr(0xfd) + chr(0xfe) + chr(0xff),
                         #Output
                         chr(0x27) + chr(0x22) + chr(0x22) + chr(0x63) +
                         chr(0x63) +
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) + 
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) +
                         chr(0x2d) + 
                         # A - Graphics Characters
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) +
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) +
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) +
                         chr(0x63) + chr(0x63) + chr(0x63) +
                         # B - Block Characters
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) +
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) + 
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) + 
                         chr(0x63) + chr(0x63) + chr(0x63) +
                         # C - Block Characters
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) + 
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) +
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) + 
                         chr(0x63) + chr(0x63) + chr(0x63) + 
                         # D - Block Characters
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) + 
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) + 
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) +
                         chr(0x63) + chr(0x63) + chr(0x63) +
                         # E - Math Characters
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) +
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) + 
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) + 
                         chr(0x63) + chr(0x63) + chr(0x63) +
                         # F - Math Characters
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) + 
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) +
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) +
                         chr(0x63) + chr(0x63) + chr(0x63))

class RSSFeed(PathObject):

    def __init__(self, parent, name, **params):
        self.name = name
        PathObject.__init__(self, parent, **params)

    def get_items(self):
        ''' Override  me!

                return [ { 'description': 'Description\nfred fred <<<',
                   'title':       'Title',
                   'date':        datetime.now(),
                   'author':      'Me',
                   'link':        'http://www.lwn.net',
                   'guid':         'xyz',
                   'object_id':    5 } ]
        '''
        pass

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        self._metadata = value

    @property
    def feed_url(self):
        return self.metadata.get('feedUrl', 'http://{0}/{1}'.\
                    format(self.request.headers['Host'], self.request.path))

    @property
    def channel_url(self):
        return self.metadata.get('channelUrl', 'http://{0}/{1}'.\
                    format(self.request.headers['Host'], self.request.path))

    @property
    def channel_title(self):
        return self.metadata.get('channelTitle', None)

    @property
    def channel_description(self):
        return self.metadata.get('channelDescription', None)

    def _open_rss(self):
        self._stream.write(u'<rss version=\"2.0\" xmlns:atom=\"http://www.w3.org/2005/Atom\">\n')

    def _open_channel(self):
        ''' This method creates the header of the RSS feed which declares the channel,
            the title and description come from the rssChannelTitle and
            rssChannelDescription methods which should be overridden in subclasses that
            implement actual feeds.  The pubDate wil always be now. '''

        if (self.feed_url is None):
            self.log.warn('No feedURL provided for RSS feed, produced feed will not be valid')
        if (self.channel_url is None):
            self.log.warn('No channelURL provided for RSS feed, produced feed will not be valid!')

        self._stream.write(u'  <channel>\n')
        self._stream.write(u'    <title>{0}</title>\n'.format(cgi.escape(self.channel_title)))
        self._stream.write(u'    <description>{0}</description>\n'.format(cgi.escape(self.channel_description)))
        self._stream.write(u'    <generator>OpenGroupware Coils</generator>\n')
        if (self.feed_url is not None):
            self._stream.write(u'    <atom:link href=\"{0}\" rel=\"self\" type=\"application/rss+xml\"/>\n'.\
                format(self.feed_url))
        if (self.channel_url is not None):
            self._stream.write(u'    <link>{0}</link>\n'.format(self.channel_url))
        self._stream.write(u'    <pubDate>{0}</pubDate>\n'.format(datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')))

    def _append_rss_item(self, description = None, title = None, date = None, author = None,
                               link = None, guid = None, object_id = None):


        if (description is not None):
            from xml.sax.saxutils    import escape, unescape
            comment = escape(self._transcode_text(description).replace('\n', '<BR/>').replace('\r', ''))
        else:
            comment = u''

        timestamp = date.strftime('%a, %d %b %Y %H:%M:%S GMT')

        self._stream.write(u'    <item>\n'
                           u'      <title>{0}</title>\n'
                           u'      <description>{1}</description>\n'
                           u'      <pubDate>{2}</pubDate>\n'
                           u'      <guid isPermaLink=\"false\">{3}</guid>\n'.format(cgi.escape(title),
                                                                                  comment,
                                                                                  timestamp,
                                                                                  guid))

        if (author is not None):
            self._stream.write(u'      <author>{0}</author>\n'.format(author))

        if (link is not None):
            self._stream.write(u'      <link>{0}</link>\n'.format(link))
        else:
            sd = ServerDefaultsManager()
            pattern = sd.string_for_default('RSSDefaultItemLinkURL')
            if (pattern is not None):
                link = pattern.replace('$objectId', unicode(object_id))
                link = link.replace('$GUID', unicode(guid))
                self._stream.write(u'      <link>{0}</link>\n'.format(link))
        self._stream.write(u'    </item>\n')

    def _close_channel(self):
        self._stream.write(u'  </channel>\n')

    def _close_rss(self):
        self._stream.write(u'</rss>')

    def _render(self):
        self._stream = StringIO(u'')
        self._stream.write(u'<?xml version=\"1.0\" encoding=\"utf-8\"?>\n')
        self._open_rss()
        self._open_channel()
        for item in self.get_items():
            self._append_rss_item(**item)
        self._close_channel()
        self._close_rss()

    def __unicode__(self):
        self._render()
        return self._stream.getvalue()

    def do_GET(self):
        self.request.simple_response(200,
                                     mimetype='application/rss+xml; disposition-type=text; charset=utf-8',
                                     data=unicode(self))

    def _transcode_text(self, text):
        if (text is None):
            return u''
        try:
          text = text.encode('ascii', 'ignore')
        except Exception, e:
          print e
          text = text.translate(TRANSCODE_TABLE)
        return text


