# -*- coding: utf-8 -*-
"""

    XMLDS COLUMN object class 
    
    Hervé Déjean
    cpy Naver labs Europe 2018
    
    a class for line from a XMLDocument

"""
from __future__ import absolute_import
from __future__ import  print_function
from __future__ import unicode_literals

from .XMLDSObjectClass import XMLDSObjectClass
from .XMLDSTEXTClass import XMLDSTEXTClass
from .XMLDSLINEClass import XMLDSLINEClass
from .XMLDSTABLEClass import XMLDSTABLEClass
from config import ds_xml_def as ds_xml

class  XMLDSCOLUMNClass(XMLDSObjectClass):
    """
        COLUMN class
    """
    name = ds_xml.sLINE_Elt
    def __init__(self,domNode = None):
        XMLDSObjectClass.__init__(self)
        XMLDSObjectClass.id += 1
        self._domNode = domNode
        self.name=ds_xml.sCOL_Elt
    
    def fromDom(self,domNode):
        """
            only contains TEXT?
        """
        self.setName(domNode.tag)
        self.setNode(domNode)
        # get properties
        for prop in domNode.keys():
            self.addAttribute(prop,domNode.get(prop))
            
            
#         ctxt = domNode.doc.xpathNewContext()
#         ctxt.setContextNode(domNode)
#         ldomElts = ctxt.xpathEval('./*')
#         ctxt.xpathFreeContext()
        
        ldomElts = domNode.findall('./*')
         
        for elt in ldomElts:
            if elt.tag  == XMLDSLINEClass.name:
                myObject= XMLDSLINEClass(elt)
                self.addObject(myObject)
                myObject.setPage(self)
                myObject.fromDom(elt)
            elif elt.tag == XMLDSTEXTClass.name:
                myObject= XMLDSTEXTClass(elt)
                self.addObject(myObject)
                myObject.setPage(self.getPage())
                myObject.fromDom(elt)        
            elif elt.tag == XMLDSTABLEClass.name:
                myObject= XMLDSTABLEClass(elt)
                self.addObject(myObject)
                myObject.setPage(self)
                myObject.fromDom(elt)    
#             else:
#                     myObject= XMLDSObjectClass()
#                     myObject.setNode(elt)
#                     # per type?
#                     self.addObject(myObject)
#                     myObject.setPage(self.getPage())
#                     myObject.fromDom(elt)   
                                
        
         
        
