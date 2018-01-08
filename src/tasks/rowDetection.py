# -*- coding: utf-8 -*-
"""


    IE module: for test

     H. Déjean
    

    copyright Xerox 2017
    READ project 

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
    from the European Union's Horizon 2020 research and innovation programme 
    under grant agreement No 674943.
"""

import libxml2

import sys, os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))


import common.Component as Component
from common.trace import traceln
import config.ds_xml_def as ds_xml
from ObjectModel.xmlDSDocumentClass import XMLDSDocument
from ObjectModel.XMLDSTEXTClass  import XMLDSTEXTClass
from ObjectModel.XMLDSTABLEClass import XMLDSTABLEClass
from ObjectModel.XMLDSCELLClass import XMLDSTABLECELLClass
from ObjectModel.XMLDSRowClass import XMLDSTABLEROWClass
from spm.spmTableRow import tableRowMiner
from xml_formats.Page2DS import primaAnalysis
from xml_formats.DS2PageXml import DS2PageXMLConvertor

class RowDetection(Component.Component):
    """
        
            row detection once
                column detection done
                BIES tagging done for text elements
                
    """
    usage = "" 
    version = "v.01"
    description = "description: test"

    #--- INIT -------------------------------------------------------------------------------------------------------------    
    def __init__(self):
        """
        Always call first the Component constructor.
        """
        Component.Component.__init__(self, "RowDetection", self.usage, self.version, self.description) 
        
        self.colname = None
        self.docid= None

        self.do2DS= False
        
        # for --test
        self.bCreateRef = False
        self.evalData = None
        
    def setParams(self, dParams):
        """
        Always call first the Component setParams
        Here, we set our internal attribute according to a possibly specified value (otherwise it stays at its default value)
        """
        Component.Component.setParams(self, dParams)
#         if dParams.has_key("coldir"): 
#             self.colname = dParams["coldir"]
        if dParams.has_key("docid"):         
            self.docid = dParams["docid"]
        if dParams.has_key("dsconv"):         
            self.do2DS = dParams["dsconv"]
                        
        if dParams.has_key("createref"):         
            self.bCreateRef = dParams["createref"]                        
    
    
    
    def tagCells(self, table):
        """
            cells are 'fake' cells from template tool:
            type RI  RB RI RE RO
            group text according
            
        """
        for col in table.getColumns():
            lNewCells=[]
            # keep original positions
            col.resizeMe(XMLDSTABLECELLClass)
            for cell in col.getCells():
#                 print cell
                curChunk=[]
                lChunks = []
#                 print map(lambda x:x.getAttribute('type'),cell.getObjects())
#                 print map(lambda x:x.getID(),cell.getObjects())
                cell.getObjects().sort(key=lambda x:x.getY())
                for txt in cell.getObjects():
#                     print txt.getAttribute("type")
                    if txt.getAttribute("type") == 'RS':
                        if curChunk != []:
                            lChunks.append(curChunk)
                            curChunk=[]
                        lChunks.append([txt])
                    elif txt.getAttribute("type") in ['RI', 'RE']:
                        curChunk.append(txt)
                    elif txt.getAttribute("type") == 'RB':
                        if curChunk != []:
                            lChunks.append(curChunk)
                        curChunk=[txt]
                    elif txt.getAttribute("type") == 'RO':
                        ## add Other as well???
                        curChunk.append(txt)
                        
                if curChunk != []:
                    lChunks.append(curChunk)
                    
                if lChunks != []:
                    # create new cells
                    table.delCell(cell)
                    irow= cell.getIndex()[0]
                    for i,c in enumerate(lChunks):
#                         print map(lambda x:x.getAttribute('type'),c)
                        #create a new cell per chunk and replace 'cell'
                        newCell = XMLDSTABLECELLClass()
                        newCell.setPage(cell.getPage())
                        newCell.setParent(table)
                        newCell.setName(ds_xml.sCELL)
                        newCell.setIndex(irow+i,cell.getIndex()[1])
                        newCell.setObjectsList(c)
                        newCell.resizeMe(XMLDSTEXTClass)
                        newCell.tagMe2()
                        for o in newCell.getObjects():
                            o.setParent(newCell)
                            o.tagMe()
#                         table.addCell(newCell)
                        lNewCells.append(newCell)
                    cell.getNode().unlinkNode()
                    del(cell)
            col.setObjectsList(lNewCells[:])
            [table.addCell(c) for c in lNewCells]        
        
#             print col.tagMe()
        

    def processRows(self,table,predefinedCuts=[]):
        """
        apply mining to get Y cuts for rows
        
        if everything is centered? not a realistic assumption 
        """
        rowMiner= tableRowMiner()
        lYcuts = rowMiner.columnMining(table,predefinedCuts)

        # shift up offset / find a better way to do this: integration skewing 
        [ x.setValue(x.getValue()-10) for x in lYcuts ]
        table.createRowsWithCuts(lYcuts)
        table.reintegrateCellsInColRow()

        table.buildNDARRAY()
        
    def findRowsInTable(self,table):
        """ 
            find row in this table
        """
        rowscuts = map(lambda r:r.getY(),table.getRows())
        self.tagCells(table)
        self.processRows(table,rowscuts)
        


    def findRowsInDoc(self,ODoc):
        """
        find rows
        """
        self.lPages = ODoc.getPages()   
        
        # not always?
#         self.mergeLineAndCells(self.lPages)
     
        for page in self.lPages:
            traceln("page: %d" %  page.getNumber())
            lTables = page.getAllNamedObjects(XMLDSTABLEClass)
            for table in lTables:
                rowscuts = map(lambda r:r.getY(),table.getRows())
                self.tagCells(table)
                self.processRows(table,rowscuts)        
    def run(self,doc):
        """
           load dom and find rows 
        """
        # conver to DS if needed
        if self.bCreateRef:
            if self.do2DS:
                dsconv = primaAnalysis()
                doc = dsconv.convert2DS(doc,self.docid)
            
            refdoc = self.createRef(doc)
            return refdoc
            # single ref per page
            refdoc= self.createRefPerPage(doc)
            return None
        
        if self.do2DS:
            dsconv = primaAnalysis()
            self.doc = dsconv.convert2DS(doc,self.docid)
        else:
            self.doc= doc
        self.ODoc = XMLDSDocument()
        self.ODoc.loadFromDom(self.doc,listPages = range(self.firstPage,self.lastPage+1))        
#         self.ODoc.loadFromDom(self.doc,listPages = range(30,31))        

        self.findRowsInDoc(self.ODoc)
        refdoc = self.createRef(self.doc)
#         print refdoc.serialize('utf-8', 1)

        if self.do2DS:
            # bakc to PageXml
            conv= DS2PageXMLConvertor()
            lPageXDoc = conv.run(self.doc)
            conv.storeMultiPageXml(lPageXDoc,self.getOutputFileName())
            print self.getOutputFileName()
            return None
        return self.doc
        
        

    ################ TEST ##################
    

    def testRun(self, filename, outFile=None):
        """
        evaluate using ABP new table dataset with tablecell
        """
        
        self.evalData=None
        doc = self.loadDom(filename)
        doc =self.run(doc)
        self.evalData = self.createRef(doc)
        if outFile: self.writeDom(doc)
        return self.evalData.serialize('utf-8',1)
    
    
    def overlapX(self,zone):
        
    
        [a1,a2] = self.getX(),self.getX()+ self.getWidth()
        [b1,b2] = zone.getX(),zone.getX()+ zone.getWidth()
        return min(a2, b2) >=   max(a1, b1) 
        
    def overlapY(self,zone):
        [a1,a2] = self.getY(),self.getY() + self.getHeight()
        [b1,b2] = zone.getY(),zone.getY() + zone.getHeight()
        return min(a2, b2) >=  max(a1, b1)      
    def signedRatioOverlap(self,z1,z2):
        """
         overlap self and zone
         return surface of self in zone 
        """
        [x1,y1,h1,w1] = z1.getX(),z1.getY(),z1.getHeight(),z1.getWidth()
        [x2,y2,h2,w2] = z2.getX(),z2.getY(),z2.getHeight(),z2.getWidth()
        
        fOverlap = 0.0
        
        if self.overlapX(z2) and self.overlapY(z2):
            [x11,y11,x12,y12] = [x1,y1,x1+w1,y1+h1]
            [x21,y21,x22,y22] = [x2,y2,x2+w2,y2+h2]
            
            s1 = w1 * h1
            
            # possible ?
            if s1 == 0: s1 = 1.0
            
            #intersection
            nx1 = max(x11,x21)
            nx2 = min(x12,x22)
            ny1 = max(y11,y21)
            ny2 = min(y12,y22)
            h = abs(nx2 - nx1)
            w = abs(ny2 - ny1)
            
            inter = h * w
            if inter > 0 :
                fOverlap = inter/s1
            else:
                # if overX and Y this is not possible !
                fOverlap = 0.0
            
        return  fOverlap     
    
    def findSignificantOverlap(self,TOverlap,ref,run):
        """
            return 
        """ 
        pref,rowref= ref
        prun, rowrun= run
        if pref != prun: return  False
        
        return rowref.ratioOverlap(rowrun) >=TOverlap 
        
        
    def testCPOUM(self, TOverlap, srefData, srunData, bVisual=False):
        """
            TOverlap: Threshols used for comparing two surfaces
            
            
            Correct Detections:
            under and over segmentation?
        """

        cntOk = cntErr = cntMissed = 0
        
        RefData = libxml2.parseMemory(srefData.strip("\n").encode('utf-8'), len(srefData.strip("\n").encode('utf-8')))
        RunData = libxml2.parseMemory(srunData.strip("\n").encode('utf-8'), len(srunData.strip("\n").encode('utf-8')))
#         try:
#             RunData = libxml2.parseMemory(srunData.strip("\n"), len(srunData.strip("\n")))
#         except:
#             RunData = None
#             return (cntOk, cntErr, cntMissed)        
        lRun = []
        if RunData:
            ctxt = RunData.xpathNewContext()
            lpages = ctxt.xpathEval('//%s' % ('PAGE'))
            for page in lpages:
                pnum=page.prop('number')
                #record level!
                xpath = ".//%s" % ("ROW")
                ctxt.setContextNode(page)
                lRows = ctxt.xpathEval(xpath)
                lORows = map(lambda x:XMLDSTABLEROWClass(0,x),lRows)
                for row in lORows:
                    row.fromDom(row._domNode)
                    row.setIndex(row.getAttribute('id'))
                    lRun.append((pnum,row))            
            ctxt.xpathFreeContext()

        lRef = []
        ctxt = RefData.xpathNewContext()
        lPages = ctxt.xpathEval('//%s' % ('PAGE'))
        for page in lPages:
            pnum=page.prop('number')
            xpath = ".//%s" % ("ROW")
            ctxt.setContextNode(page)
            lRows = ctxt.xpathEval(xpath)
            lORows = map(lambda x:XMLDSTABLEROWClass(0,x),lRows)
            for row in lORows:    
                row.fromDom(row._domNode)
                row.setIndex(row.getAttribute('id'))
                lRef.append((pnum,row))  
        ctxt.xpathFreeContext()          


#         print map(lambda x:(x.getY()),lRun)
#         print map(lambda (x,a):(x.getY()),lRef)
        refLen = len(lRef)
#         bVisual = True
        ltisRefsRunbErrbMiss= list()
        lRefCovered = []
        for i in range(0,len(lRun)):
            iRef =  0
            bFound = False
            bErr , bMiss= False, False
            runElt = lRun[i]
#             print '\t\t===',runElt
            while not bFound and iRef <= refLen - 1:  
                curRef = lRef[iRef]
                if runElt and curRef not in lRefCovered and self.findSignificantOverlap(TOverlap,runElt, curRef):
                    bFound = True
                    lRefCovered.append(curRef)
                iRef+=1
            if bFound:
                if bVisual:print "FOUND:", runElt, ' -- ', lRefCovered[-1]
                cntOk += 1
            else:
                curRef=''
                cntErr += 1
                bErr = True
                if bVisual:print "ERROR:", runElt
            if bFound or bErr:
                ltisRefsRunbErrbMiss.append( (int(runElt[0]), curRef, runElt,bErr, bMiss) )
             
        for i,curRef in enumerate(lRef):
            if curRef not in lRefCovered:
                if bVisual:print "MISSED:", curRef
                ltisRefsRunbErrbMiss.append( (int(curRef[0]), curRef, '',False, True) )
                cntMissed+=1
        ltisRefsRunbErrbMiss.sort(key=lambda (x,y,z,t,u):x)

#         print cntOk, cntErr, cntMissed,ltisRefsRunbErrbMiss
        return (cntOk, cntErr, cntMissed,ltisRefsRunbErrbMiss)              
                
        
    def testCompare(self, srefData, srunData, bVisual=False):
        """
        as in Shahad et al, DAS 2010

        Correct Detections 
        Partial Detections 
        Over-Segmented 
        Under-Segmented 
        Missed        
        False Positive
                
        """
        dicTestByTask = dict()
        dicTestByTask['T50']= self.testCPOUM(0.50,srefData,srunData,bVisual)
#         dicTestByTask['T75']= self.testCPOUM(0.750,srefData,srunData,bVisual)
#         dicTestByTask['T100']= self.testCPOUM(0.50,srefData,srunData,bVisual)

    #         dicTestByTask['FirstName']= self.testFirstNameRecord(srefData, srunData,bVisual)
#         dicTestByTask['Year']= self.testYear(srefData, srunData,bVisual)
    
        return dicTestByTask    
    
    def createRowsWithCuts(self,lYCuts,table,tableNode,bTagDoc=False):
        """
        REF XML
        """
        
        prevCut = None
#         prevCut = table.getY()
        
        lYCuts.sort()
        for index,cut in enumerate(lYCuts):
            # first correspond to the table: no rpw
            if prevCut is not None:
                rowNode= libxml2.newNode("ROW")
                if bTagDoc:
                    tableNode.addChild(rowNode)
                else:
                    tableNode.addChild(rowNode)
                rowNode.setProp('y',str(prevCut))
                rowNode.setProp('height',str(cut - prevCut))
                rowNode.setProp('x',str(table.getX()))
                rowNode.setProp('width',str(table.getWidth()))
                rowNode.setProp('id',str(index-1))

            prevCut= cut
        #last
        cut=table.getY2()
        rowNode= libxml2.newNode("ROW")
        tableNode.addChild(rowNode)
        rowNode.setProp('y',str(prevCut))
        rowNode.setProp('height',str(cut - prevCut))
        rowNode.setProp('x',str(table.getX()))
        rowNode.setProp('width',str(table.getWidth()))        
        rowNode.setProp('id',str(index))

            
    def createRef(self,doc):
        """
            create a ref file from the xml one
        """
        self.ODoc = XMLDSDocument()
        self.ODoc.loadFromDom(doc,listPages = range(self.firstPage,self.lastPage+1))        
  
  
        refdoc=libxml2.newDoc("1.0")
        root=libxml2.newNode("DOCUMENT")
        refdoc.setRootElement(root)
        

        for page in self.ODoc.getPages():
            #imageFilename="..\col\30275\S_Freyung_021_0001.jpg" width="977.52" height="780.0">
            pageNode = libxml2.newNode('PAGE')
            pageNode.setProp("number",page.getAttribute('number'))
            pageNode.setProp("imageFilename",page.getAttribute('imageFilename'))
            pageNode.setProp("width",page.getAttribute('width'))
            pageNode.setProp("height",page.getAttribute('height'))

            root.addChild(pageNode)   
            lTables = page.getAllNamedObjects(XMLDSTABLEClass)
            for table in lTables:
                dRows={}
                tableNode = libxml2.newNode('TABLE')
                tableNode.setProp("x",table.getAttribute('x'))
                tableNode.setProp("y",table.getAttribute('y'))
                tableNode.setProp("width",table.getAttribute('width'))
                tableNode.setProp("height",table.getAttribute('height'))
                pageNode.addChild(tableNode)
                for cell in table.getAllNamedObjects(XMLDSTABLECELLClass):
                    try:dRows[int(cell.getAttribute("row"))].append(cell)
                    except KeyError:dRows[int(cell.getAttribute("row"))] = [cell]
        
                lYcuts = []
                for rowid in sorted(dRows.keys()):
#                     print rowid, min(map(lambda x:x.getY(),dRows[rowid]))
                    lYcuts.append(min(map(lambda x:x.getY(),dRows[rowid])))
                self.createRowsWithCuts(lYcuts,table,tableNode)

        return refdoc
    
    def createRefPerPage(self,doc):
        """
            create a ref file from the xml one
            
            for DAS 2018
        """
        self.ODoc = XMLDSDocument()
        self.ODoc.loadFromDom(doc,listPages = range(self.firstPage,self.lastPage+1))        
  
  

        dRows={}
        for page in self.ODoc.getPages():
            #imageFilename="..\col\30275\S_Freyung_021_0001.jpg" width="977.52" height="780.0">
            pageNode = libxml2.newNode('PAGE')
#             pageNode.setProp("number",page.getAttribute('number'))
            #SINGLER PAGE pnum=1
            pageNode.setProp("number",'1')

            pageNode.setProp("imageFilename",page.getAttribute('imageFilename'))
            pageNode.setProp("width",page.getAttribute('width'))
            pageNode.setProp("height",page.getAttribute('height'))

            refdoc=libxml2.newDoc("1.0")
            root=libxml2.newNode("DOCUMENT")
            refdoc.setRootElement(root)
            root.addChild(pageNode)
               
            lTables = page.getAllNamedObjects(XMLDSTABLEClass)
            for table in lTables:
                tableNode = libxml2.newNode('TABLE')
                tableNode.setProp("x",table.getAttribute('x'))
                tableNode.setProp("y",table.getAttribute('y'))
                tableNode.setProp("width",table.getAttribute('width'))
                tableNode.setProp("height",table.getAttribute('height'))
                pageNode.addChild(tableNode)
                for cell in table.getAllNamedObjects(XMLDSTABLECELLClass):
                    try:dRows[int(cell.getAttribute("row"))].append(cell)
                    except KeyError:dRows[int(cell.getAttribute("row"))] = [cell]
        
                lYcuts = []
                for rowid in sorted(dRows.keys()):
#                     print rowid, min(map(lambda x:x.getY(),dRows[rowid]))
                    lYcuts.append(min(map(lambda x:x.getY(),dRows[rowid])))
                self.createRowsWithCuts(lYcuts,table,tableNode)

            
            self.outputFileName = os.path.basename(page.getAttribute('imageFilename')[:-3]+'ref')
            print self.outputFileName
            self.writeDom(refdoc, bIndent=True)

        return refdoc    
    
    #         print refdoc.serialize('utf-8', True)
#         self.testCPOUM(0.5,refdoc.serialize('utf-8', True),refdoc.serialize('utf-8', True))
            
if __name__ == "__main__":

    
    rdc = RowDetection()
    #prepare for the parsing of the command line
    rdc.createCommandLineParser()
#     rdc.add_option("--coldir", dest="coldir", action="store", type="string", help="collection folder")
    rdc.add_option("--docid", dest="docid", action="store", type="string", help="document id")
    rdc.add_option("--dsconv", dest="dsconv", action="store_true", default=False, help="convert page format to DS")
    rdc.add_option("--createref", dest="createref", action="store_true", default=False, help="create REF file for component")

    rdc.add_option('-f',"--first", dest="first", action="store", type="int", help="first page to be processed")
    rdc.add_option('-l',"--last", dest="last", action="store", type="int", help="last page to be processed")

    #parse the command line
    dParams, args = rdc.parseCommandLine()
    
    #Now we are back to the normal programmatic mode, we set the component parameters
    rdc.setParams(dParams)
    
    doc = rdc.loadDom()
    doc = rdc.run(doc)
    if doc is not None and rdc.getOutputFileName() != '-':
        rdc.writeDom(doc, bIndent=True) 
    
