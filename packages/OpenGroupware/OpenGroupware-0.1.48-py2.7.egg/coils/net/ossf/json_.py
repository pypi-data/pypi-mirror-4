#
# Copyright (c) 2010, 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
try:
    import ijson
except:
    HAS_IJSON = False
else:
    HAS_IJSON = True

import json
from coils.core    import NotImplementedException, \
                           BLOBManager
from filter       import OpenGroupwareServerSideFilter

# TODO: We need to implement a TEST-CASE for this class
#    Need to test - count mode
#                 - pagination mode with criteria
#                 - pagination mode with range
#                 - pagination mode with range & criteria
#                 - pagination mode without path

class JSONOSSFilter(OpenGroupwareServerSideFilter):

    @property
    def handle(self):
        if (self._mimetype != 'application/json'):
            raise Exception('Input type for JSONDecoder is not mimetype application/json')
        if (hasattr(self, '_mode')):
            if (self._mode == 'pagination'):
                return self.paginate()
            elif (self._mode == 'count'):
                return self.count()
            else:
                raise NotImplementedException('JSON OSSF mode {0} not implemented'.format(self._mode))
        else:
            # If no mode was specified then we don't do anything, just pass back our
            # input file handle.
            return self._rfile

    def paginate(self):

        if not HAS_IJSON:
            # TODO: Implement a non-ijson fallback (low-priority)
            raise NotImplementedException('JSON OSSF currently requires the ijson module.')

        # If a path isn't specified we don't do anything; what would we count? Data
        # just gets passed through without modification
        if hasattr(self, '_path'):
            if hasattr(self, '_range'):
                # If a range is specified scrape out a floor and cieling
                # Range specifications look like -#, #-#, #-
                # Range counts are inclusive
                value = self._range.split('-')
                if (len(value[0]) == 0): floor = 0
                else: floor = int(value[0])
                if (len(value[1]) == 0): cieling = None
                else: cieling = int(value[1])
            else:
                floor   = 0
                cieling = None

            if hasattr(self, '_criteria'):
                # User provided a criteria as a parameter
                # Parameter criteria is key,value
                # NOTE: THIS CREATES key, value, AND int_key VARIABLES
                key, value = self._criteria.split(',')
                # We try to make an integer version of they key for performing
                # list indexes, if this failes we won't inspect list items
                try:
                    int_key = int(key)
                except:
                    int_key = None
            else:
                # Set the criteria variables all to None, no criteria was specified
                key, value, int_key = None, None, None

            data = [ ]
            counter = 0

            # TODO: We can read JSON as a stream, but we cannot yet *write* JSON
            #       as a stream, so we have to stream-read our input, qualify it,
            #       and build up the result for the client which is then dumped to
            #       JSON.
            for item in ijson.items(self._rfile, self._path):
                if key is not None:
                    # There is a key for evaluating the JSON item, so do that
                    if isinstance(item, basestring) or isinstance(item, list):
                        # Lists and strings use the integer version of the key
                        if int_key is not None:
                            if item[int_key] != value:
                                item = None
                        else:
                            item = None
                    elif isinstance(item, dict):
                        # Evaluating a dictionary uses the literal value from the URL
                        if item[key] != value:
                            item = None

                if item:
                    # Increment counter, used for range
                    counter += 1
                    if counter >= floor:
                        # Put the item in the output list
                        data.append(item)
                    if cieling:
                        if counter >= cieling:
                            # We've hit the top of the range, we can stop
                            break

            tmp = BLOBManager.ScratchFile()
            json.dump(data, tmp)
            tmp.seek(0)
            return tmp
        else:
            # If no path for was specified then we don't paginate, just pass back our
            # input file handle.
            return self._rfile

    def count(self):
        counter = 0
        if (hasattr(self, '_path')):
            if (HAS_IJSON):
                for item in ijson.items(self._rfile, self._path):
                    counter += 1
            else:
                # TODO: Implement a non-ijson fallback
                raise NotImplementedException('JSON OSSF currently requires the ijson module.')
        tmp = BLOBManager.ScratchFile()
        tmp.write(unicode(counter))
        tmp.seek(0)
        return tmp

    @property
    def mimetype(self):
        if (self._mode == 'pagination'):
            return 'application/json'
        elif (self._mode == 'count'):
            return 'text/plain'
