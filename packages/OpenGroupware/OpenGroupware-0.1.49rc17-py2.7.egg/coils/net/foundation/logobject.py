from datetime import datetime
from StringIO import StringIO
from time import strftime
from davobject import DAVObject
from bufferedwriter import BufferedWriter

class LogObject(DAVObject):

    def __init__(self, parent, name, **params):
        DAVObject.__init__(self, parent, name, **params)

    def get_property_getetag(self):
        return unicode(self.entity.object_id)

    def get_property_webdav_displayname(self):
        return DAVObject.get_property_webdav_displayname(self)

    def get_property_webdav_getcontentlength(self):
        return unicode(len(self.get_representation()))

    def get_property_webdav_getcontenttype(self):
        return u'text/html'

    def get_property_webdav_getlastmodified(self):
        return self.most_recent_entry_datetime.strftime("%a, %d %b %Y %H:%M:%S GMT")

    def _load_contents(self):
        if (self._contents is None):
            if (self.entity is None):
                return False
            self.data = self.context.run_command('object::get-logs', object=self.entity)
        return True

    @property
    def most_recent_entry_datetime(self):
        if (self.load_contents()):
            self.log.debug(self.data)
            if (len(self.data) > 0):
                return self.data[-1].datetime
        return datetime(1969,12,31)

    def write_header(self, stream, refresh_interval=0):
        stream.write(u'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n')
        stream.write(u'<html xmlns="http://www.w3.org/1999/xhtml">\n')
        stream.write(u'<head">\n')
        if (refresh_interval > 0):
            stream.write(u'<meta http-equiv="refresh" content="{0}">\n'.format(refresh_interval))
        stream.write(u'<title>Audit entries for objectId#{0} [{1}]<title>\n'.format(self.entity.object_id, self.entity.__entityName__))
        stream.write(u'</head>\n')
        stream.write(u'<body>\n')

    def write_audit_table(self, stream):
        stream.write('<table width="100%" border="1">\n')
        if (self.load_contents()):
            if (len(self.data) == 0):
                stream.write('<tr><td colspan="4">No audit entries exist for objectId#{0} [{1}]</td></tr>\n'.\
                    format(self.entity.object_id, self.entity.__entityName__ ))
            else:
                stream.write('<tr><th colspan="2">Loaded @</th><th colspan="2">Most Recent Entry</th></td>\n')
                stream.write('<tr><td colspan="2" align="center">{0}</td><td colspan="2" align="center">{1}</td></tr>\n'.\
                    format(datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                           self.most_recent_entry_datetime.strftime("%Y-%m-%d %H:%M:%S UTC")))
                stream.write('<tr><th>AuditId#</th><th>Date/Time</th><th>Action</th><th>Actor</th></tr>\n')
                for entry in self.data:
                    stream.write('<tr><td align="center">{0}</td><td align="center">{1}</td><td align="center">{2}</td><td align="center">{3}</td></tr>\n'.\
                        format(entry.object_id,
                               entry.datetime.strftime("%Y-%m-%d %H:%M:%S UTC"),
                               entry.action,
                               entry.actor_id))
                    stream.write('<tr><td colspan="4"><pre>{0}</pre></td></tr>\n'.format(entry.message))
                stream.write('</table>\n')
        else:
            stream.write('<tr><td colspan="4">Unable to retrieve audit entries for objectId#{0} [{1}]</td></tr>\n'.\
                format(self.entity.object_id, self.entity.__entityName__ ))

    def write_footer(self, stream):
        stream.write(u'</body>\n')

    def get_representation(self):
        if (hasattr(self, 'representation')):
            return self.representation
        stream = StringIO(u'')
        self.write_header(stream, refresh_interval=15)
        self.write_audit_table(stream)
        self.write_footer(stream)
        self.representation = stream.getvalue()
        stream = None
        return self.representation

    def do_GET(self):
        payload = self.get_representation()
        if (payload is not None):
            self.request.simple_response(200,
                                         data=unicode(payload),
                                         mimetype=self.get_property_webdav_getcontenttype(),
                                         headers={ 'ETag': self.get_property_getetag() } )
            return
        else:
            raise NoSuchPathException('{0} not found'.format(self.name))
