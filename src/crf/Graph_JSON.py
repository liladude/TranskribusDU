# -*- coding: utf-8 -*-

"""
    Computing the graph for a JSON document
    
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
import collections
import itertools
import json
import codecs

import numpy as np

from common.trace import traceln

from Graph import Graph

import Edge
from crf.Edge import SamePageEdge
from Page import Page
from IPython.core.page import page

class Graph_JSON(Graph):
    """
    A graph to be used as a CRF graph with pystruct
    """
    
    sXmlFilenamePattern = "*.json"    #how to find the DS XML files

    def __init__(self, lNode = [], lEdge = []):
        Graph.__init__(self, lNode, lEdge)       

    # --- Graph building --------------------------------------------------------
            
    def parseXmlFile(self, sFilename, iVerbose=0):
        """
        Load that JSON document as a CRF Graph.
        Also set the self.doc variable!
        
        The JSON data looks like below. A list of dictionary, 1 per word
        
        [
  {
    "pageNumber": 0,
    "top": 1070,
    "bottom": 1084,
    "left": 122,
    "right": 259,
    "text": "xxx:",
    "labels": [],
    "features": {
    ...
    
        Return a CRF Graph object
        """
    
        with codecs.open(sFilename, "rb",'utf-8') as fd: 
            self.doc = json.load(fd)
            
        self.lNode, self.lEdge = list(), list()

        #for pnum, page, domNdPage in self._iter_Page_DomNode(self.doc):
        #nor being sure of the ordering by page, we use a dictionary to group words per page
        dlWordPerPage = collections.defaultdict(list)
        
        #page level is not present in the json file
        dPagePerPage = dict()
        
        #set a fake nodeid in case it is required somewhere in the code (I think no)
        domid = 0
        for dicWord in self.doc:
            pnum = dicWord["pageNumber"]
            
            try:
                page = dPagePerPage[pnum]
            except KeyError:
                #ok, need to create the page object
                pagecnt = None #unknown for now
                iPageWidth  = int(dicWord["features"]["pageWidth"])  #seems to need int
                iPageHeight = int(dicWord["features"]["pageHeight"])
                page = Page(pnum, pagecnt, iPageWidth, iPageHeight)
                dPagePerPage[pnum] = page
                
            for nodeType in self.getNodeTypeList():
                try:
                    nd = nodeType.parse(page, dicWord, domid)
                    domid += 1
                    dlWordPerPage[pnum].append(nd)
                except ValueError:
                    pass #assume it does not match this node type
        
        #now group by page
        lpnum = dlWordPerPage.keys()
        lpnum.sort()
        
        #load the block of each page, keeping the list of blocks of previous page
        lPrevPageNode = None
        for pnum in lpnum:
            dPagePerPage[pnum].pagecnt = len(lpnum)
            
            lPageNode = dlWordPerPage[pnum]
            self.lNode.extend(lPageNode)

            lPageEdge = Edge.Edge.computeEdges(lPrevPageNode, lPageNode)
            
            self.lEdge.extend(lPageEdge)
            if iVerbose>=2: traceln("\tPage %5d    %6d nodes    %7d edges"%(pnum, len(lPageNode), len(lPageEdge)))
            
            lPrevPageNode = lPageNode
        if iVerbose: traceln("\t\t (%d nodes,  %d edges)"%(len(self.lNode), len(self.lEdge)) )
        
        return self

    def detachFromDOM(self):
        """
        Detach the graph from the DOM node, which can then be freed
        """
        if self.doc != None:
#             for nd in self.lNode: nd.detachFromDOM()
#             self.doc.freeDoc()
            self.doc = None

        

        
        
