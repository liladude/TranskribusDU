# -*- coding: utf-8 -*-

"""
    a type of nodes 
    
    It defines:
    - the labels of this node type
    - how to read and write the JSON corresponding to this node type
    

    Copyright Naver(C) 2017 JL. Meunier

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    
    
    Developed  for the EU project READ. The READ project has received funding 
    from the European Union�s Horizon 2020 research and innovation programme 
    under grant agreement No 674943.
    
"""
import random
import types
from common.trace import traceln

from NodeType import NodeType
from xml_formats.PageXml import PageXml
from util.Polygon import Polygon
from Block import Block


class NodeType_JSONInvoice(NodeType):


    def __init__(self, sNodeTypeName, lsLabel, lsIgnoredLabel=None, bOther=True, BBoxDeltaFun=None):
        NodeType.__init__(self, sNodeTypeName, lsLabel, lsIgnoredLabel, bOther)
        
        self.BBoxDeltaFun = BBoxDeltaFun
        if BBoxDeltaFun:
            assert type(self.BBoxDeltaFun) == types.FunctionType, "Error: BBoxDeltaFun must be a function (or a lambda)"
                
#     def setXpathExpr(self, sxpNode): #, sxpTextual)):
#         pass
#         #self.sxpNode    = sxpNode
# 
#     def getXpathExpr(self):
#         """
#         get any Xpath related information to extract the nodes from an XML file
#         """
#         return None
#         #return self.sxpNode
    
    def parse(self, page, data, domid):
        
        x1 = float(data["left"])
        y1 = float(data["top"])
        x2 = float(data["right"])
        y2 = float(data["bottom"])
        
        #we reduce a bit this rectangle, to ovoid overlap (PROBABLY USELESS HERE)
        if self.BBoxDeltaFun:
            w,h = x2-x1, y2-y1
            dx = self.BBoxDeltaFun(w)
            dy = self.BBoxDeltaFun(h)
            x1,y1, x2,y2 = [ int(round(v)) for v in [x1+dx,y1+dy, x2-dx,y2-dy] ]
                    
        sText = data["text"]
        orientation = 0  #unless we have more info from pdf2xml²
        classIndex = 0   #is computed later on
        ndBlock = data   #equivalent to the xml structure
        
        blk = Block(page, (x1, y1, x2-x1, y2-y1), sText, orientation
                    , classIndex, self, ndBlock, domid=domid)

        
        return blk
    
    def _getLabelList(self, jsonDat):
        """
        Labels take this for in the json data
        "labels": [
  {
    "position": "BEGINNING",
    "classification": "LINE_EXTENSION_AMOUNT"
  },
  {
    "position": "BEGINNING",
    "classification": "LINE_UNIT_PRICE"
  }
],
        """
        labels = jsonDat["labels"]
        if labels:
            return [dic['position']+' '+dic['classification'] for dic in labels]
        else:
            return ['OUTSIDE']
        
    def parseDomNodeLabel(self, domnode, defaultCls=None):
        """
        Parse and set the graph node label and return its class index
        raise a ValueError if the label is missing while bOther was not True, or if the label is neither a valid one nor an ignored one
        """
        sLabel = self.sDefaultLabel
        try:
            #we may have several labels associted with one word
            #for now we choose one at random
            sXmlLabel = random.choice( self._getLabelList(domnode) )
            try:
                sLabel = self.dXmlLabel2Label[sXmlLabel]
            except KeyError:
                #not a label of interest
                try:
                    self.checkIsIgnored(sXmlLabel)
                    #if self.lsXmlIgnoredLabel and sXmlLabel not in self.lsXmlIgnoredLabel: 
                except:
                    raise ValueError("Invalid label '%s' in node %s"%(sXmlLabel, str(domnode)))
        except KeyError:
            #no label at all
            if not self.sDefaultLabel: raise ValueError("Missing label in node %s"%str(domnode))
        
        return sLabel


    def setDomNodeLabel(self, domnode, sLabel):
        """
        Set the DOM node label in the format-dependent way
        """
        raise Exception("NOT YET IMPLEMENTED")
        return sLabel
