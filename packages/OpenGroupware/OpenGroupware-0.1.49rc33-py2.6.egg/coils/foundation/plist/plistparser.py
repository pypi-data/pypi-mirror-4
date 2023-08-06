# License: public domain (none)
# Orignal Author: Marcus Muller <znek@mulle-kybernetik.com>
# Included in Coils 2009-10-15
from stringbuffer import StringBuffer

class PListParser:
    """
    A Parser capable of parsing Apple's oldschool property lists,
    aka OPENSTEP ones.
    """

    # iVars
    _lineNumber = 0
    _startOfLineCharIndex = 0
    _savedIndex = 0
    _savedLineNumber = 0
    _savedStartOfLineCharIndex = 0


    ##
    ## FACTORY
    ##


    def __init__(self):
        self._lineNumber = 0
        self._startOfLineCharIndex = 0


    ##
    ## PUBLIC ENTRY
    ##


    def propertyListFromString(self, s):
        if s == "":
            return None
        self._lineNumber = 1
        self._startOfLineCharIndex = 0
        i = 0
        ref = [None]
        i = self._readObjectIntoObjectReference(s, i, ref)
        i = self._skipWhitespaceAndComments(s, i)
        if i != -1:
            raise Exception("propertyListFromString parsed an object, but there's still more text in the string. A plist should contain only one top-level object. Line number: " + str(_lineNumber) + ", column: " + str(i - self._startOfLineCharIndex) + ".")
        return ref[0]


    ##
    ## PRIVATE API
    ##


    _hexdigits = "0123456789abcdefABCDEF"

    def _isHexDigit(self, c):
        return self._hexdigits.find(c) != -1

    _octaldigits = "01234567"

    def _isOctalDigit(self, c):
        return self._octaldigits.find(c) != -1

    def _saveIndexes(self, i, j, k):
        self._savedIndex = i
        self._savedLineNumber = j
        self._savedStartOfLineCharIndex = k;

    def _savedIndexesAsString(self):
        return "line number: " + str(self._savedLineNumber) + ", column: " + str(self._savedIndex - self._savedStartOfLineCharIndex)

    def _processWhitespace(self, s, i):
        while i < len(s) and s[i].isspace():
            if s[i] == '\n':
                self._lineNumber += 1
                self._startOfLineCharIndex = i + 1
            i += 1
        if i < len(s):
                return i
        return -1

    def _processSingleLineComment(self, s, i):
        i += 2
        while i < len(s) and s[i] != "\n":
            i += 1
        if i < len(s):
            return i
        return -1

    def _processMultiLineComment(self, s, i):
        self._saveIndexes(i, self._lineNumber, self._startOfLineCharIndex)
        i += 2
        while (i + 1) < len(s) and (s[i] != "*" or s[i + 1] != "/"):
            if s[i] == "/" and s[i + 1] == "*":
                raise Exception("Property list parsing does not support embedded multi line comments. The first /* was at " + self._savedIndexesAsString() + ". A second /* was found at line " + _lineNumber + ", column: " + (i - self._startOfLineCharIndex) + ".")
            if s[i] == "\n":
                self._lineNumber += 1
                self._startOfLineCharIndex = i + 1
            i += 1

    def _checkForWhitespaceOrComment(self, s, i):
        if (i == -1) or (i >= len(s)):
                return 1
        if s[i].isspace():
                return 2
        if (i + 1) < len(s):
            if s[i] == "/" and s[i + 1] == "/":
                    return 3
            if s[i] == "/" and s[i + 1] == "*":
                    return 4
        return 1

    def _skipWhitespaceAndComments(self, s, i):
        j = self._checkForWhitespaceOrComment(s, i)
        while j != 1:
            if j == 2:
                    i = self._processWhitespace(s, i)
                    break
            elif j == 3:
                    i = self._processSingleLineComment(s, i)
                    break
            elif j == 4:
                    i = self._processMultiLineComment(s, i)
                    break
            j = self._checkForWhitespaceOrComment(s, i)
        if i < len(s):
                return i
        return -1

    def _readUnquotedStringIntoStringBuffer(self, s, i, stringbuffer):
##              print "** s,i,sb:: " + str(s) + ", " + str(i) + ", " + str(stringbuffer)
        j = i
        stringbuffer.clear()
        # TODO: Should "-" be an allowed character?
        while i < len(s) and (s[i] >= "a" and s[i] <= "z" or s[i] >= "A" and s[i] <= "Z" or s[i] >= "0" and s[i] <= "9" or s[i] == "_" or s[i] == "$" or s[i] == ":" or s[i] == "." or s[i] == "/"):
            i += 1
        if j < i:
            stringbuffer.append(s[j:i])
        else:
            #print "** s:\n" + str(s[:i])
            raise Exception("Property list parsing failed while attempting to read unquoted string. No allowable characters were found. At line number: " + str(self._lineNumber) + ", column: " + str(i - self._startOfLineCharIndex) + ".")
        if i < len(s):
            return i
        return -1

    def _readQuotedStringIntoStringBuffer(self, s, i, stringbuffer):
        self._saveIndexes(i, self._lineNumber, self._startOfLineCharIndex)
        i += 1
        j = i

        while i < len(s) and s[i] != '"':
            if s[i] == '\\':
                if j < i:
                    stringbuffer.append(s[j:i])
                i += 1
                if i >= len(s):
                    raise Exception("Property list parsing failed while attempting to read quoted string. Input exhausted before closing quote was found. Opening quote was at " + self._savedIndexesAsString() + ".")
                if s[i] == 'n':
                    stringbuffer.append('\n')
                    i += 1
                elif s[i] == 'r':
                    stringbuffer.append('\r')
                    i += 1
                elif s[i] == 't':
                    stringbuffer.append('\t')
                    i += 1
                elif s[i] == 'f':
                    stringbuffer.append('\f')
                    i += 1
                elif s[i] == 'b':
                    stringbuffer.append('\b')
                    i += 1
                elif s[i] == 'a':
                    stringbuffer.append('\007')
                    i += 1
                elif s[i] == 'v':
                    stringbuffer.append('\013')
                    i += 1
                elif s[i] == 'u' or s[i] == 'U':
                    if i + 4 >= len(s):
                            raise Exception("Property list parsing failed while attempting to read quoted string. Input exhausted before escape sequence was completed. Opening quote was at " + self._savedIndexesAsString() + ".")
                    i += 1

                    if (not self._isHexDigit(s[i])) or (not self._isHexDigit(s[i + 1])) or (not self._isHexDigit(s[i + 2])) or (not self._isHexDigit(s[i + 3])):
                            raise Exception("Property list parsing failed while attempting to read quoted string. Improperly formed \\U type escape sequence. At line number: " + str(_lineNumber) + ", column: " + str(i - _startOfLineCharIndex) + ".")
                    stringbuffer.append(eval("\\u" + s[i:i + 4]))
                    i += 4
                elif s[i] >= '0' and s[i] <= '7':
                    if i + 3 >= len(s):
                            raise Exception("Property list parsing failed while attempting to read quoted string. Input exhausted before escape sequence was completed. Opening quote was at " + self._savedIndexesAsString() + ".")

                    if (not self._isOctalDigit(s[i])) or (not self._isOctalDigit(s[i + 1])) or (not self._isOctalDigit(s[i + 2])):
                            raise Exception("Property list parsing failed while attempting to read quoted string. Octal escape sequence too large (bigger than octal 377). At line number: " + str(_lineNumber) + ", column: " + str(i - _startOfLineCharIndex) + ".")
                    stringbuffer.append(eval("\\" + s[i:i + 3]))
                    i += 3
                else:
                    stringbuffer.append(s[i])
                    if s[i] == '\n':
                            self._lineNumber += 1
                            self._startOfLineCharIndex = i + 1
                    i += 1
                j = i
            else:
                if s[i] == '\n':
                    self._lineNumber += 1
                    self._startOfLineCharIndex = i + 1
                i += 1
        if j < i:
                stringbuffer.append(s[j:i])
        if i >= len(s):
                raise Exception("Property list parsing failed while attempting to read quoted string. Input exhausted before closing quote was found. Opening quote was at " + self._savedIndexesAsString() + ".")

        i += 1
        if i < len(s):
                return i
        return -1

    def _readArrayContentsIntoArray(self, s, i, array):
        aobj = [None]
        i += 1
        array[:-1] = [];
        i = self._skipWhitespaceAndComments(s, i)
        while i != -1 and s[i] != ")":
            if len(array) > 0:
                if s[i] != ",":
                    raise Exception("Property list parsing failed while attempting to read array. No comma found between array elements. At line number: " + str(_lineNumber) + ", column: " + str(i - _startOfLineCharIndex) + ".")
                i += 1
                i = self._skipWhitespaceAndComments(s, i)
                if i == -1:
                    raise Exception("Property list parsing failed while attempting to read array. Input exhausted before end of array was found. At line number: " + str(_lineNumber) + ", column: " + str(i - _startOfLineCharIndex) + ".")
            if s[i] != ')':
                aobj[0] = None;
                i = self._readObjectIntoObjectReference(s, i, aobj)
                if aobj[0] == None:
                    raise Exception("Property list parsing failed while attempting to read array. Failed to read content object. At line number: " + str(_lineNumber) + ", column: " + str(i - _startOfLineCharIndex) + ".")
                i = self._skipWhitespaceAndComments(s, i)
                array.append(aobj[0])

        if i == -1:
            raise Exception("Property list parsing failed while attempting to read array. Input exhausted before end of array was found. At line number: " + str(_lineNumber) + ", column: " + str(i - _startOfLineCharIndex) + ".")

        i += 1
        if i < len(s):
                return i
        return -1

    def _readDictionaryContentsIntoDictionary(self, s, i, dictionary):
        aobj = [None]
        aobj1 = [None]
        i += 1
        if len(dictionary) != 0:
                dictionary.clear()
        i = self._skipWhitespaceAndComments(s, i)
        while i != -1 and s[i] != u'}':
            i = self._readObjectIntoObjectReference(s, i, aobj)
            if aobj[0] == None: ## or !(aobj[0] instanceof String))
                    raise Exception("Property list parsing failed while attempting to read dictionary. Failed to read key or key is not a String. At line number: " + str(self._lineNumber) + ", column: " + str(i - self._startOfLineCharIndex) + ".")
            i = self._skipWhitespaceAndComments(s, i)
            if i == -1 or s[i] != u'=':
                    raise Exception("Property list parsing failed while attempting to read dictionary. Read key " + aobj[0] + " with no value. At line number: " + str(self._lineNumber) + ", column: " + str(i - self._startOfLineCharIndex) + ".")
            i += 1
            i = self._skipWhitespaceAndComments(s, i)
            if i == -1:
                    raise Exception("Property list parsing failed while attempting to read dictionary. Read key " + aobj[0] + " with no value. At line number: " + str(self._lineNumber) + ", column: " + str(i - self._startOfLineCharIndex) + ".")
            i = self._readObjectIntoObjectReference(s, i, aobj1)
            if aobj1[0] == None:
                    raise Exception("Property list parsing failed while attempting to read dictionary. Failed to read value. At line number: " + str(self._lineNumber) + ", column: " + str(i - self._startOfLineCharIndex) + ".")
            i = self._skipWhitespaceAndComments(s, i)
            if i == -1 or s[i] != u';':
##                              print "** aobj[] = " + str(aobj[0]) + "; aobj1[] = " + str(aobj1[0])
##                              print "** until i(" + str(i) + "): " + s[:i]
                    raise Exception("Property list parsing failed while attempting to read dictionary. Read key and value with no terminating semicolon. At line number: " + str(self._lineNumber) + ", column: " + str(i - self._startOfLineCharIndex) + ".")
            i += 1
            i = self._skipWhitespaceAndComments(s, i)
            dictionary[aobj[0]] = aobj1[0]

        if i >= len(s):
                raise Exception("Property list parsing failed while attempting to read dictionary. Exhausted input before end of dictionary was found. At line number: " + str(self._lineNumber) + ", column: " + str(i - self._startOfLineCharIndex) + ".")

        i += 1
        if i < len(s):
                return i
        return -1

    def _readObjectIntoObjectReference(self, s, i, ref):
        i = self._skipWhitespaceAndComments(s, i)
        if i == -1 or i >= len(s):
                ref[0] = None
        elif s[i] == '"':
                stringbuffer = StringBuffer()
                i = self._readQuotedStringIntoStringBuffer(s, i, stringbuffer)
                ref[0] = unicode(stringbuffer)
        elif s[i] == '<':
                raise Exception("Cannot read NSData, yet!")
##                NSMutableData nsmutabledata = new NSMutableData(_lengthOfData(ac, i));
##                i = _readDataContentsIntoData(ac, i, nsmutabledata);
##                ref[0] = nsmutabledata
        elif s[i] == '(':
                array = []
                i = self._readArrayContentsIntoArray(s, i, array)
                ref[0] = array
        elif s[i] == '{':
                dictionary = {}
                i = self._readDictionaryContentsIntoDictionary(s, i, dictionary)
                ref[0] = dictionary
        else:
                stringbuffer = StringBuffer()
                i = self._readUnquotedStringIntoStringBuffer(s, i, stringbuffer)
                ref[0] = unicode(stringbuffer)
        if i < len(s):
                return i
        return -1
