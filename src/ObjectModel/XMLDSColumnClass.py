# -*- coding: utf-8 -*-
"""

    XMLDS CELL
    Hervé Déjean
    cpy Xerox 2017
    
    a class for table cell from a XMLDocument

"""

from XMLDSObjectClass import XMLDSObjectClass
from XMLDSTEXTClass import XMLDSTEXTClass
from config import ds_xml_def as ds_xml

class  XMLDSTABLECOLUMNClass(XMLDSObjectClass):
    """
        LINE class
    """
    name = ds_xml.sLINE_Elt
    def __init__(self,index=None,domNode = None):
        XMLDSObjectClass.__init__(self)
        XMLDSObjectClass.id += 1
        self._domNode = domNode
        self._index= index
        self._lcells=[]
        self.tagName= 'COL'
    
    def getIndex(self): return self._index
    def setIndex(self,i): self._index = i
    
    def getCells(self): return self._lcells
    def addCell(self,c): 
        if c not in self.getCells():
            self._lcells.append(c)
            self.addObject(c)                
#     
#     ## possible
#     def fromDom(self,domNode):
#         """
#             only contains TEXT?
#         """
#         self.setName(domNode.name)
#         self.setNode(domNode)
#         # get properties
#         prop = domNode.properties
#         while prop:
#             self.addAttribute(prop.name,prop.getContent())
#             # add attributes
#             prop = prop.next
#         self.setIndex(int(self.getAttribute('irow')),int(self.getAttribute('icol')))
#             
#         ctxt = domNode.doc.xpathNewContext()
#         ctxt.setContextNode(domNode)
#         ldomElts = ctxt.xpathEval('./%s'%(ds_xml.sCELL))
#         ctxt.xpathFreeContext()
#         for elt in ldomElts:
#             myObject= XMLDSTEXTClass(elt)
#             self.addObject(myObject)
#             myObject.setPage(self.getPage())
#             myObject.fromDom(elt)
        
         
        
