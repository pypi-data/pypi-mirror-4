#
# Copyright (c) 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.foundation   import BLOBManager
from coils.core         import CoilsException
from lxml               import etree

class XMLDocument(object):
    __handle__ = None
    
    def __init__(self, name):
        self.name = name
    
    @property
    def filename(self):
        return 'wf/{0}/{1}'.format(self.__container__, self.name)
    
    @property
    def size(self):
        return BLOBManager.SizeOf(self.filename)
        
    @property
    def created(self):
        return BLOBManager.Created(self.filename)
        
    @property
    def modified(self):
        return BLOBManager.Modified(self.filename)            
    
    @property    
    def handle(self):
        # TODO: Should we lock this file?
        if not self.__handle__:
            self.__handle__ = BLOBManager.Open(self.filename, 'r+', encoding='binary', create=True)
        return self.__handle__
        
    @property
    def read_handle(self):
        return BLOBManager.Open(self.filename, 'r', encoding='binary')
        
    def close(self):
        if self.__handle__:
            BLOBManager.Close(self.__handle__)
        self.__handle__ = None
        
    def delete(self):
        self.close()
        BLOBManager.Delete(self.filename)
        
    def verify(self, rfile=None, data=None):
        pass
        
    def fill(self, rfile=None, data=None):
        self.verify(rfile=rfile, data=data)
        wfile = self.handle
        wfile.truncate( )
        if rfile:
            rfile.seek(0)
            shutil.copyfileobj(rfile, wfile)
        else:
            wfile.write(data)
        wfile.flush()
        
    def rewind(self):
        self.__handle__.seek(0)               
    
class XSDDocument(XMLDocument):
    __container__ = 'x'
    
    def verify(self, rfile=None, data=None):
        # TODO: Raise a better exception; indicating invalid content
        # TODO: Possibly generate an administrative notice        
        try:
            if rfile:
                xsd_doc = etree.parse(rfile)
            else:
                xsd_doc = etree.fromstring(data)
            etree.XMLSchema(xsd_doc)
        except Exception as e:
            raise e
    
    def __repr__( self ):
        return '<XSDDocument name="{0}" path="{1}"/>'.format( self.name, self.filename )
    
    @staticmethod
    def Marshall(name):
        return XSDDocument(name)
        
    @staticmethod
    def List():
        result = [ ]
        for name in BLOBManager.List('wf/{0}/'.format(XSDDocument.__container__)):
            result.append(name)
        return result        
            
class WSDLDocument(XMLDocument):
    #TODO: Implement verify(...)
    __container__ = 'w'
    
    @staticmethod
    def Marshall(name):
        return WSDLDocument(name)
        
        
    @staticmethod
    def List():
        result = [ ]
        for name in BLOBManager.List('wf/{0}/'.format(WSDLDocument.__container__)):
            result.append(name)
        return result             
 
class XSLTDocument(XMLDocument):
    __container__ = 'xslt'
    
    def verify(self, rfile=None, data=None):
        # TODO: Raise a better exception; indicating invalid content
        # TODO: Possibly generate an administrative notice
        try:
            if rfile:
                xsd_doc = etree.parse(rfile)
            else:
                xsd_doc = etree.fromstring(data)
            etree.XSLT(xsd_doc)
        except Exception as e:
            raise e
    
    @staticmethod
    def Marshall(name):
        return XSLTDocument(name)
        
    @staticmethod
    def List():
        result = [ ]
        for name in BLOBManager.List('wf/{0}/'.format(XSLTDocument.__container__)):
            result.append(name)
        return result             
 
