# License: public domain (none)
# Orignal Author: Marcus Muller <znek@mulle-kybernetik.com>
# Included in Coils 2009-10-15
import StringIO
class StringBuffer:
    """
    A mutable string. This implementation is quite inefficient, but I doubt
    that implementing it with lists would be considerably faster.
    """

    def __init__(self):
            self._buffer = StringIO.StringIO(u'')

    def __str__(self):
            return self._buffer.getvalue()

    def __repr__(self):
            return repr(self.__str___())

    def __len__(self):
            return self._buffer.len

    def __hash__(self):
            return hash(self._buffer.getvalue())
    
    def clear(self):
            self._buffer = StringIO.StringIO(u'')

    def append(self, string):
        #TODO: Is this the right thing to do?
        # We may have incoming characters like \\xe0
        self._buffer.write(string)
        return
        self._buffer.write(repr(string).encode('utf-8'))
