# -*- coding: utf-8 -*-

"""
    Utility to compute statistics regarding a PageXml collection.
    
    How many document? pages? objects? labels?
    
    The raw result is stored as a pikle file in a CSV file.  (in the future version!!!) 
    The statistics are reported on stdout.
    
    Copyright Xerox(C) 2017 JL. Meunier

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
from __future__ import absolute_import
from __future__ import  print_function
from __future__ import unicode_literals

import sys, os, collections, pickle, glob
from lxml import etree
import re
import gc
from optparse import OptionParser

try: #to ease the use without proper Python installation
    import TranskribusDU_version
except ImportError:
    sys.path.append( os.path.dirname(os.path.dirname( os.path.abspath(sys.argv[0]) )) )
    import TranskribusDU_version

from xml_formats.PageXml import PageXml

# ===============================================================================================================
#DEFINING THE CLASS OF GRAPH WE USE

# ===============================================================================================================

class DoubleHistogram:
    """
    Double keyed histogram
    """
    def __init__(self, name):
        self.name = name
        self.dCnt = collections.defaultdict(lambda : collections.defaultdict(int) )
        
    def seenK1K2(self, k1, k2):
        self.dCnt[k1][k2] += 1
    
    #--- First Key
    def addFirstKeys(self, lk1):
        """
        Make sure those key are present in the histogram, possibly with count of zero
        """
        for k1 in lk1: self.dCnt[k1]

    def getFirstKeyList(self): 
        """
        return the sorted list of first key
        """
        l = list(self.dCnt.keys()); l.sort()
        return l
    
    #--- Second Key
    def getAllSecondKeys(self):
        setK = set()
        for k in self.getFirstKeyList():
            setK = setK.union( self.getSecondKeyList(k) )
        return list(setK)
        
    def getSecondKeyList(self, k): 
        """
        return the sorted list of observed labels for this tag
        """
        l = list(self.dCnt[k].keys()); l.sort()
        return l
    
    def getSecondKeyCountList(self, k):
        """
        return the count of observed second keys, in same order as the second key list, for that first key
        """
        return [self.dCnt[k][v] for v in self.getSecondKeyList(k)]
    
    def getCount(self, k1, k2): return self.dCnt[k1][k2]

    #--- Sum
    def getSumByFirstKey(self, k1):
        """
        return the sum of counts of observed second keys, for that first key
        """
        return sum( self.dCnt[k1][v] for v in self.getSecondKeyList(k1) )
    
    def getSumBySecondKey(self, k2):
        """
        return the sum of counts of observed first keys, for that second key
        """
        cnt = 0
        for k1 in self.getFirstKeyList():
            if k2 in self.getSecondKeyList(k1): cnt += self.getCount(k1, k2)
        return cnt

class CollectionAnalyzer:
    def __init__(self, lTag):
        self.start()
        self.lTag = lTag    #all tag names
        
    def start(self):
        """
        reset any accumulated data
        """
        self.hPageCountPerDoc = DoubleHistogram("Page count stat")
        self.hTagCountPerDoc  = DoubleHistogram("Tag stat per document")
        self.hLblCountPerTag  = DoubleHistogram("Label stat per tag")
        
        self.lDoc           = None    #all doc names
        self.lNbPage        = None
        
    def runPageXml(self, sDir):
        """
        process one folder per document
        """
        assert False, "Method must be specialized"

    def runMultiPageXml(self, sDir):
        """
        process one PXML per document
        """
        assert False, "Method must be specialized"
    
    def end(self):
        """
        Consolidate the gathered data
        """
        self.lDoc = self.hPageCountPerDoc.getFirstKeyList()  #all doc are listed here
        self.hTagCountPerDoc.addFirstKeys(self.lDoc)         #to make sure we have all of them listed, even those without tags of interest
        self.lObservedTag = self.hTagCountPerDoc.getAllSecondKeys()  #all tag of interest observed in dataset
        
        self.lNbPage = list()
        for doc in self.lDoc:
            lNb = self.hPageCountPerDoc.getSecondKeyList(doc)
            assert len(lNb) == 1
            self.lNbPage.append(lNb[0])
        #label list per tag: self.hLblCountPerTag.getSecondKeyList(tag)
        
    def save(self, filename):
        t = (self.hPageCountPerDoc, self.hTagCountPerDoc, self.hLblCountPerTag)
        with open(filename, "wb") as fd: pickle.dump(t, fd)

    def load(self, filename):
        with open(filename, "rb")as fd: 
            self.hPageCountPerDoc, self.hTagCountPerDoc, self.hLblCountPerTag = pickle.load(fd)
    
    def prcnt(self, num, totnum):
        if totnum==0:
            return "n/a"
        else:
            f = num*100.0/totnum
            if 0.0 < f and f < 2.0:
                return "%.1f%%" % f
            else:
                return "%.0f%%" % f
            
    def report(self):
        """
        report on accumulated data so far
        """
        print( "-"*60)
        
        print( " ----- %d documents, %d pages" %(len(self.lDoc), sum(self.lNbPage)))
        for doc, nb in zip(self.lDoc, self.lNbPage): 
            print( "\t---- %40s  %6d pages"%(doc, nb))
        
        print()
        print( " ----- %d objects of interest (%d observed): %s"%(len(self.lTag), len(self.lObservedTag), self.lTag))
        for doc in self.lDoc:
            print( "\t---- %s  %6d occurences"%(doc, self.hTagCountPerDoc.getSumByFirstKey(doc)))
            for tag in self.lObservedTag: 
                print( "\t\t--%20s  %6d occurences" %(tag, self.hTagCountPerDoc.getCount(doc, tag)))
        print()
        for tag in self.lObservedTag: 
            print( "\t-- %s  %6d occurences" %(tag, self.hTagCountPerDoc.getSumBySecondKey(tag)))
            for doc in self.lDoc:
                print( "\t\t---- %40s  %6d occurences"%(doc, self.hTagCountPerDoc.getCount(doc, tag)))

        print()
        print( " ----- Label frequency for ALL %d objects of interest: %s"%(len(self.lTag), self.lTag))
        for tag in self.lTag: 
            totnb           = self.hTagCountPerDoc.getSumBySecondKey(tag)
            totnblabeled    = self.hLblCountPerTag.getSumByFirstKey(tag)
            print( "\t-- %s  %6d occurences  %d labelled" %(tag, totnb, totnblabeled))
            for lbl in self.hLblCountPerTag.getSecondKeyList(tag):
                nb = self.hLblCountPerTag.getCount(tag, lbl)
                print( "\t\t- %20s  %6d occurences\t(%5s)  (%5s)"%(lbl,
                                                                   nb,
                                                                   self.prcnt(nb, totnb),
                                                                   self.prcnt(nb, totnblabeled)))
            nb = totnb - totnblabeled
            lbl="<unlabeled>"
            print( "\t\t- %20s  %6d occurences\t(%5s)"%(lbl, nb, self.prcnt(nb, totnb)))
            
        print( "-"*60)
        return ""
    
    def seenDocPageCount(self, doc, pagecnt):
        self.hPageCountPerDoc.seenK1K2(doc, pagecnt)    #strange way to indicate the page count of a doc....
    def seenDocTag(self, doc, tag):
        self.hTagCountPerDoc.seenK1K2(doc, tag)
    def seenTagLabel(self, tag, lbl):
        self.hLblCountPerTag.seenK1K2(tag, lbl)

class PageXmlCollectionAnalyzer(CollectionAnalyzer):
    """
    Annalyse a collection of PageXmlDocuments
    """
    
    dNS = {"pg":"http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"}
    
    def __init__(self, sDocPattern, sPagePattern, lTag, sCustom=None):
        """
        sRootDir is the root directory of the collection
        sDocPattern is the pattern followed by folders, assuming one folder contains one document
        sPagePattern is the pattern followed by each PageXml file , assuming one file contains one PageXml XML
        ltTagAttr is the list of pair of tag of interest and label attribute
        """
        CollectionAnalyzer.__init__(self, lTag)
        self.sDocPattern    = sDocPattern
        self.sPagePattern   = sPagePattern
        self.lTag           = lTag
        self.sCustom        = sCustom
        self.ltCRES          = [] #list of tuple (cre, replacement-string)
        
    def setLabelPattern(self, sRE, sRepl):
        """
        replace any occurence of the pattern by the replacement string in a label
        """
        self.ltCRES.append( (re.compile(sRE), sRepl) )
        
    def runPageXml(self, sRootDir):
        lFolder = [os.path.basename(folder) for folder in glob.iglob(os.path.join(sRootDir, self.sDocPattern)) 
                                if os.path.isdir(folder)]
        lFolder.sort()
        print( "Documents: ", lFolder)
        
        for docdir in lFolder:
            print( "Document ", docdir)
            lPageFile = [os.path.basename(name) for name in glob.iglob(os.path.join(sRootDir, docdir, self.sPagePattern)) 
                                if os.path.isfile(os.path.join(sRootDir, docdir, name))]
            lPageFile.sort()
            self.seenDocPageCount(docdir, len(lPageFile))
            for sPageFile in lPageFile: 
                print( ".",)
                doc = etree.parse(os.path.join(sRootDir, docdir, sPageFile))
                self.parsePage(doc, doc.getroot(), docdir)
                doc = None
                gc.collect()
            print()
            sys.stdout.flush()
            
    def runMultiPageXml(self, sRootDir):
        print( os.path.join(sRootDir, self.sDocPattern))
        print( glob.glob(os.path.join(sRootDir, self.sDocPattern)))
        lDocFile = [os.path.basename(filename) for filename in glob.iglob(os.path.join(sRootDir, self.sDocPattern)) 
                                if os.path.isfile(filename)]
        lDocFile.sort()
        print( "Documents: ", lDocFile)
        
        for docFile in lDocFile:
            print( "Document ", docFile)
            doc = etree.parse(os.path.join(sRootDir, docFile))
            lNdPage = doc.getroot().xpath("//pg:Page",
                                          namespaces=self.dNS)
            self.seenDocPageCount(docFile, len(lNdPage))
            for ndPage in lNdPage:
                print( ".",)
                self.parsePage(doc, ndPage, docFile)
            print()
            sys.stdout.flush()

    def parsePage(self, doc, ctxtNd, name):
        for tag in self.lTag:
            lNdTag = ctxtNd.xpath(".//pg:%s"%tag, namespaces=self.dNS)
            for nd in lNdTag:
                self.seenDocTag(name, tag)
                if self.sCustom != None:
                    if self.sCustom == "":
                        try:
                            lbl = PageXml.getCustomAttr(nd, "structure", "type")
                        except:
                            lbl = ''
                    else:
                        lbl = nd.get(self.sCustom)
                else:
                    lbl = nd.get("type")
                    
                if lbl:
                    for cre, sRepl in self.ltCRES: lbl = cre.sub(sRepl, lbl)    #pattern processing 
                    self.seenTagLabel(tag, lbl)
        

def test_simple():
    sTESTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              "tests")
    
    sDATA_DIR = os.path.join(sTESTS_DIR, "data")
    
    doer = PageXmlCollectionAnalyzer("*.mpxml", 
                                     None,
                                     ["Page", "TextRegion", "TextLine"],
                                     #["type"],
                                      sCustom="")
    doer.start()
    doer.runMultiPageXml(os.path.join(sDATA_DIR, "abp_TABLE_9142_mpxml", "col"))
    doer.end()
    sReport = doer.report()
    print( sReport)
    
if __name__ == "__main__":

    if False:
        test_simple()

    sUsage="""Usage: %s <sRootDir> <sDocPattern> [sPagePattern])
For Multi-PageXml, only root directory and document pattern (2 arguments, e.g. 9142_GTRC/col '*.mpxml' )
For PageXml, give also the Xml page pattern (3 arguments, e.g. 9142_GTRC/col '[0-9]+' *.mpxml')
"""%sys.argv[0]

    #prepare for the parsing of the command line
    parser = OptionParser(usage=sUsage)
    
#     parser.add_option("--dir", dest='lTrn',  action="store", type="string"
#                       , help="Train or continue previous training session using the given annotated collection.")    
#     parser.add_option("--tst", dest='lTst',  action="store", type="string"
#                       , help="Test a model using the given annotated collection.")    
#     parser.add_option("--run", dest='lRun',  action="store", type="string"
#                       , help="Run a model on the given non-annotated collection.")    
#     parser.add_option("-w", "--warm", dest='warm',  action="store_true"
#                       , help="Attempt to warm-start the training")   
    parser.add_option("-c", "--custom", dest='custom',  action="store", type="string"
                      , help="With --custom= , it reads @custom Xml attribute instead of @type, or if you specify --custom=toto, it will read the @toto attribute.")   
    parser.add_option("--pattern", dest='pattern',  action="store"
                      , help="Replace the given pattern in the label by # (specific for BAR so far...)")  

    # --- 
#     bMODEUN = True
    
    #parse the command line
    (options, args) = parser.parse_args()
    # --- 
    try:
        try:
            sRootDir, sDocPattern, sPagePattern  = args[0:3]
            bMultiPageXml = False 
        except:
            sRootDir, sDocPattern  = args[0:2]
            bMultiPageXml = True 
            sPagePattern = None
    except:
        print(sUsage)
        exit(1)
        
    #all tag supporting the attribute type in PageXml 2003
    lTag = ["Page", "TextRegion", "GraphicRegion", "CharRegion", "RelationType"]
    #Pragmatism: don't think we will have annotatetd page
    lTag = ["TextRegion", "GraphicRegion", "CharRegion", "RelationType"]
    #Pragmatism: we may also have tagged TextLine ...
    lTag.append("TextLine")
    
    print( sRootDir, sDocPattern, sPagePattern, lTag)

#         if bMODEUN:
#             #all tag supporting the attribute type in PageXml 2003
#             ltTagAttr = [ (name, "type") for name in ["Page", "TextRegion", "GraphicRegion", "CharRegion", "RelationType"]]
#         else:
#             ls = args[3:]
#             ltTagAttr = zip(ls[slice(0, len(ls), 2)], ls[slice(1, len(ls), 2)])
#         print( sRootDir, sDocPattern, sPagePattern, ltTagAttr)
#     except:
# #         if bMODEUN:
# #             print( "Usage: %s sRootDir sDocPattern [sPagePattern]"%(sys.argv[0] ))
# #         else:
# #             print( "Usage: %s sRootDir sDocPattern [sPagePattern] [Tag Attr]+"%(sys.argv[0] ))
#         exit(1)

    doer = PageXmlCollectionAnalyzer(sDocPattern, sPagePattern, lTag, sCustom=options.custom)
    if options.pattern != None:
        doer.setLabelPattern(options.pattern, "#")
        
    doer.start()
    if bMultiPageXml:
        print( "--- MultiPageXml ---")
        doer.runMultiPageXml(sRootDir)
    else:
        print( "--- PageXml ---")
        doer.runPageXml(sRootDir)
        
    doer.end()
    sReport = doer.report()
    
    print( sReport)
    
