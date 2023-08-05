# -*- coding: utf-8 -*-
"""
 pyText2Pdf - Python script to convert plain text files into Adobe
 Acrobat PDF files.

 Version 1.2.2

 Source URL: <http://djangosnippets.org/snippets/1778/>

 Author: Anand B Pillai <abpillai at lycos dot com>
 With modifications from V. Sergeyev http://pythondevside.com/
 
 Keywords: python, django, tools, converter, pdf, text2pdf, adobe, acrobat,
           processing.

 Copyright (C) 2003-2004 Free Software Foundation, Inc.

 This file is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2, or (at your option)
 any later version.

 This file is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
    
 You should have received a copy of the GNU General Public License
 along with GNU Emacs; see the file COPYING.  If not, write to
 the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
 Boston, MA 02111-1307, USA.
    
 Commentary:

 Modification History:

 Mon Feb 17 12:20:13 2003 Changed option parsing algorithm to use
                          getopt. Use __main__ calling convention.
                          Bug in FF character fixed.
 Thu Apr 10 11:26:58 2003 Modified to use python style strings
                          and function objects.
 July 1 2003              Fixed help string errors. Added the
                          Creator property.
 Feb 25 2004              Rewrote argument parser to remove
                          duplicate code.Use string.join() instead
                          of concatenation. Modified sys.exit()
                          calls to print messages.
 Nov 04 2009              V.Sergeyev: Modified to act with stream objects (not files). 
                          Usefull for producing PDF on web-sites. 
 Example: produce PDF document from text and output it as HTTPResponse object (Django)
    import StringIO
    input_stream = StringIO.StringIO(text)
    result = StringIO.StringIO()
    
    pdfclass = pyText2Pdf(input_stream, result)
    pdfclass.Convert()
    
    response = HttpResponse(result.getvalue(), mimetype="application/pdf")
    response['Content-Disposition'] = 'attachment; filename=pdf_report.pdf'
    
    return response
 
    Code:
"""

# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/189858
# http://code.activestate.com/recipes/189858/

import sys, os
import string
import time
import getopt

LF_EXTRA=0
LINE_END='\015'
# form feed character (^L)
FF=chr(12)

ENCODING_STR = """\
/Encoding <<
/Differences [ 0 /.notdef /.notdef /.notdef /.notdef
/.notdef /.notdef /.notdef /.notdef /.notdef /.notdef
/.notdef /.notdef /.notdef /.notdef /.notdef /.notdef
/.notdef /.notdef /.notdef /.notdef /.notdef /.notdef
/.notdef /.notdef /.notdef /.notdef /.notdef /.notdef
/.notdef /.notdef /.notdef /.notdef /space /exclam
/quotedbl /numbersign /dollar /percent /ampersand
/quoteright /parenleft /parenright /asterisk /plus /comma
/hyphen /period /slash /zero /one /two /three /four /five
/six /seven /eight /nine /colon /semicolon /less /equal
/greater /question /at /A /B /C /D /E /F /G /H /I /J /K /L
/M /N /O /P /Q /R /S /T /U /V /W /X /Y /Z /bracketleft
/backslash /bracketright /asciicircum /underscore
/quoteleft /a /b /c /d /e /f /g /h /i /j /k /l /m /n /o /p
/q /r /s /t /u /v /w /x /y /z /braceleft /bar /braceright
/asciitilde /.notdef /.notdef /.notdef /.notdef /.notdef
/.notdef /.notdef /.notdef /.notdef /.notdef /.notdef
/.notdef /.notdef /.notdef /.notdef /.notdef /.notdef
/dotlessi /grave /acute /circumflex /tilde /macron /breve
/dotaccent /dieresis /.notdef /ring /cedilla /.notdef
/hungarumlaut /ogonek /caron /space /exclamdown /cent
/sterling /currency /yen /brokenbar /section /dieresis
/copyright /ordfeminine /guillemotleft /logicalnot /hyphen
/registered /macron /degree /plusminus /twosuperior
/threesuperior /acute /mu /paragraph /periodcentered
/cedilla /onesuperior /ordmasculine /guillemotright
/onequarter /onehalf /threequarters /questiondown /Agrave
/Aacute /Acircumflex /Atilde /Adieresis /Aring /AE
/Ccedilla /Egrave /Eacute /Ecircumflex /Edieresis /Igrave
/Iacute /Icircumflex /Idieresis /Eth /Ntilde /Ograve
/Oacute /Ocircumflex /Otilde /Odieresis /multiply /Oslash
/Ugrave /Uacute /Ucircumflex /Udieresis /Yacute /Thorn
/germandbls /agrave /aacute /acircumflex /atilde /adieresis
/aring /ae /ccedilla /egrave /eacute /ecircumflex
/edieresis /igrave /iacute /icircumflex /idieresis /eth
/ntilde /ograve /oacute /ocircumflex /otilde /odieresis
/divide /oslash /ugrave /uacute /ucircumflex /udieresis
/yacute /thorn /ydieresis ]
>>
"""


PROG_HELP = ""


class pyText2Pdf:

    def __init__(self, input_stream=None,
                       output_stream=None,
                       title="",
                       font="/Courier",
                       ptSize=10,
                       tab=4,
                       cols=80,
                       do_ffs=0):
        # version number
        self._version="1.2.2"
        # iso encoding flag
        self._IsoEnc=0
        # formfeeds flag
        self._doFFs=do_ffs
        self._progname="PyText2Pdf"
        self._appname = "".join((self._progname, " Version ", str(self._version)))
        # default font
        self._font=font
        # default font size
        self._ptSize=ptSize
        # default vert space
        self._vertSpace=12
        self._lines=0
        # number of characters in a row
        self._cols=cols
        self._columns=1
        # page ht
        self._pageHt=792
        # page wd
        self._pageWd=612
        
        # title 
        self._ititle = title
        # input file descriptor
        self._ifs = input_stream
        # output file descriptor
        self._ofs = output_stream
        # default tab width
        self._tab = tab
        
        # landscape flag
        self._landscape=0

        # marker objects
        self._curobj = 5
        self._pageObs = [0]
        self._locations = [0,0,0,0,0,0]
        self._pageNo=0

        # file position marker
        self._fpos=0

    def writestr(self, str):
        """ Write string to output file descriptor.
        All output operations go through this function.
        We keep the current file position also here"""

        # update current file position
        self._fpos += len(str)
        for x in range(0, len(str)):
            if str[x] == '\n':
                self._fpos += LF_EXTRA
        try:
            self._ofs.write(str)
        except IOError, e:
            print e
            return -1

        return 0
            
    def Convert(self):
        """ Perform the actual conversion """
    
        if self._landscape:
            # swap page width & height
            tmp = self._pageHt
            self._pageHt = self._pageWd
            self._pageWd = tmp

        if self._lines==0:
            self._lines = (self._pageHt - 72)/self._vertSpace
        if self._lines < 1:
            self._lines=1
        
        self.WriteHeader(self._ititle)
        self.WritePages()
        self.WriteRest()

        return 0

    def WriteHeader(self, title):
        """Write the PDF header"""

        ws = self.writestr

        t=time.localtime()
        timestr=str(time.strftime("D:%Y%m%d%H%M%S", t))
        ws("%PDF-1.4\n")
        self._locations[1] = self._fpos
        ws("1 0 obj\n")
        ws("<<\n")

        buf = "".join(("/Creator (", self._appname, " By Anand B Pillai )\n"))
        ws(buf)
        buf = "".join(("/CreationDate (", timestr, ")\n"))
        ws(buf)
        buf = "".join(("/Producer (", self._appname, "(\\251 Free Software Foundation, 2004))\n"))
        ws(buf)
        
        if title:
            buf = "".join(("/Title (", title, ")\n"))
            ws(buf)

        ws(">>\n")
        ws("endobj\n")
    
        self._locations[2] = self._fpos

        ws("2 0 obj\n")
        ws("<<\n")
        ws("/Type /Catalog\n")
        ws("/Pages 3 0 R\n")
        ws(">>\n")
        ws("endobj\n")
        
        self._locations[4] = self._fpos
        ws("4 0 obj\n")
        ws("<<\n")
        #buf = "".join(("/BaseFont ", str(self._font), " /Encoding /WinAnsiEncoding /Name /F1 /Subtype /Type1 /Type /Font >>\n"))
        buf = "".join(("/BaseFont ", str(self._font), " /Encoding /Identity-H /Name /F1 /Subtype /Type1 /Type /Font >>\n"))
        ws(buf)
    
        if self._IsoEnc:
            ws(ENCODING_STR)
            
        ws(">>\n")
        ws("endobj\n")
        
        self._locations[5] = self._fpos
        
        ws("5 0 obj\n")
        ws("<<\n")
        ws("  /Font << /F1 4 0 R >>\n")
        ws("  /ProcSet [ /PDF /Text ]\n")
        ws(">>\n")
        ws("endobj\n")
    
    def StartPage(self):
        """ Start a page of data """

        ws = self.writestr
        
        self._pageNo += 1
        self._curobj += 1

        self._locations.append(self._fpos)
        self._locations[self._curobj]=self._fpos
    
        self._pageObs.append(self._curobj)
        self._pageObs[self._pageNo] = self._curobj
        
        buf = "".join((str(self._curobj), " 0 obj\n"))

        ws(buf)
        ws("<<\n")
        ws("/Type /Page\n")
        ws("/Parent 3 0 R\n")
        ws("/Resources 5 0 R\n")

        self._curobj += 1
        buf = "".join(("/Contents ", str(self._curobj), " 0 R\n"))
        ws(buf)
        ws(">>\n")
        ws("endobj\n")
        
        self._locations.append(self._fpos)
        self._locations[self._curobj] = self._fpos

        buf = "".join((str(self._curobj), " 0 obj\n"))
        ws(buf)
        ws("<<\n")
        
        buf = "".join(("/Length ", str(self._curobj + 1), " 0 R\n"))
        ws(buf)
        ws(">>\n")
        ws("stream\n")
        strmPos = self._fpos
    
        ws("BT\n");
        buf = "".join(("/F1 ", str(self._ptSize), " Tf\n"))
        ws(buf)
        buf = "".join(("1 0 0 1 50 ", str(self._pageHt - 40), " Tm\n"))
        ws(buf)
        buf = "".join((str(self._vertSpace), " TL\n"))
        ws(buf)
    
        return strmPos

    def EndPage(self, streamStart):
        """End a page of data """
        
        ws = self.writestr

        ws("ET\n")
        streamEnd = self._fpos
        ws("endstream\n")
        ws("endobj\n")
    
        self._curobj += 1
        self._locations.append(self._fpos)
        self._locations[self._curobj] = self._fpos
    
        buf = "".join((str(self._curobj), " 0 obj\n"))
        ws(buf)
        buf = "".join((str(streamEnd - streamStart), '\n'))
        ws(buf)
        ws('endobj\n')
    
    def WritePages(self):
        """Write pages as PDF"""
        
        ws = self.writestr

        beginstream=0
        lineNo, charNo=0,0
        ch, column=0,0
        padding,i=0,0
        atEOF=0
        
        while not atEOF:
            beginstream = self.StartPage()
            column=1
            
            while column <= self._columns:
                column += 1
                atFF=0
                atBOP=0
                lineNo=0
            
                while lineNo < self._lines and not atFF and not atEOF:
                    
                    lineNo += 1
                    ws("(")
                    charNo=0
                    
                    while charNo < self._cols:
                        charNo += 1
                        ch = self._ifs.read(1)
                        cond = ((ch != '\n') and not(ch==FF and self._doFFs) and (ch != ''))
                        if not cond:
                            break

                        if ord(ch) >= 32 and ord(ch) <= 127:
                            if ch == '(' or ch == ')' or ch == '\\':
                                ws("\\")
                            ws(ch)
                        else:
                            if ord(ch) == 9:
                                padding =self._tab - ((charNo - 1) % self._tab)
                                for i in range(padding):
                                    ws(" ")
                                charNo += (padding -1)
                            else:
                                if ch != FF:
                                    # write \xxx form for dodgy character
                                    buf = "".join(('\\', ch))
                                    ws(buf)
                                else:
                                    # dont print anything for a FF
                                    charNo -= 1

                    ws(")'\n")
                    if ch == FF:
                        atFF=1
                    if lineNo == self._lines:
                        atBOP=1
                        
                    if atBOP:
                        pos=0
                        ch = self._ifs.read(1)
                        pos= self._ifs.tell()
                        if ch == FF:
                            ch = self._ifs.read(1)
                            pos=self._ifs.tell()
                        # python's EOF signature
                        if ch == '':
                            atEOF=1
                        else:
                            # push position back by one char
                            self._ifs.seek(pos-1)

                    elif atFF:
                        ch = self._ifs.read(1)
                        pos=self._ifs.tell()
                        if ch == '':
                            atEOF=1
                        else:
                            self._ifs.seek(pos-1)

                if column < self._columns:
                    buf = "".join(("1 0 0 1 ",
                                   str((self._pageWd/2 + 25)),
                                   " ",
                                   str(self._pageHt - 40),
                                   " Tm\n"))
                    ws(buf)

            self.EndPage(beginstream)

    def WriteRest(self):
        """Finish the file"""

        ws = self.writestr
        self._locations[3] = self._fpos
    
        ws("3 0 obj\n")
        ws("<<\n")
        ws("/Type /Pages\n")
        buf = "".join(("/Count ", str(self._pageNo), "\n"))
        ws(buf)
        buf = "".join(("/MediaBox [ 0 0 ", str(self._pageWd), " ", str(self._pageHt), " ]\n"))
        ws(buf)
        ws("/Kids [ ")
    
        for i in range(1, self._pageNo+1):
            buf = "".join((str(self._pageObs[i]), " 0 R "))
            ws(buf)

        ws("]\n")
        ws(">>\n")
        ws("endobj\n")
        
        xref = self._fpos
        ws("xref\n")
        buf = "".join(("0 ", str((self._curobj) + 1), "\n"))
        ws(buf)
        buf = "".join(("0000000000 65535 f ", str(LINE_END)))
        ws(buf)

        for i in range(1, self._curobj + 1):
            val = self._locations[i]
            buf = "".join((string.zfill(str(val), 10), " 00000 n ", str(LINE_END)))
            ws(buf)

        ws("trailer\n")
        ws("<<\n")
        buf = "".join(("/Size ", str(self._curobj + 1), "\n"))
        ws(buf)
        ws("/Root 2 0 R\n")
        ws("/Info 1 0 R\n")
        ws(">>\n")
        
        ws("startxref\n")
        buf = "".join((str(xref), "\n"))
        ws(buf)
        ws("%%EOF\n")
