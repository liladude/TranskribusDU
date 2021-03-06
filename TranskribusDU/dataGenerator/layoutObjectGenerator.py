# -*- coding: utf-8 -*-
"""


    Samples of layout generators
    
    generate Layout annotated data 
    
    copyright Naver Labs 2017
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
    
    @author: H. Déjean
"""
from __future__ import absolute_import
from __future__ import  print_function
from __future__ import unicode_literals


try:basestring
except NameError:basestring = str

from lxml import etree
import sys, os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))

from dataGenerator.numericalGenerator import numericalGenerator
from dataGenerator.numericalGenerator import  integerGenerator
from dataGenerator.numericalGenerator import positiveIntegerGenerator
from dataGenerator.generator import Generator
from dataGenerator.layoutGenerator import layoutZoneGenerator
from dataGenerator.listGenerator import listGenerator
from dataGenerator.typoGenerator import horizontalTypoGenerator,verticalTypoGenerator

class doublePageGenerator(layoutZoneGenerator):
    """
        a double page generator
        allows for layout on two pages (table)!
        
        useless??? could be useless for many stuff. so identify when it is useful! 
            pros: better for simulating breakpages (white pages for chapter?)
                  see which constraints when in alistGenerator: need 2pages generated. the very first :white. when chapter break 
                  structure=[left, right]
                  
                  a way to handle mirrored structure !  (at layout or content: see bar for marginalia)
                  
            cons: simply useless!
            
        for page break: need to work with content generator?
    """
    def __init__(self,config):
        """
          "page":{
            "scanning": None,
            "pageH":    (780, 50),
            "pageW":    (1000, 50),
            "nbPages":  (nbpages,0),
            "lmargin":  tlMarginGen,
            "rmargin":  trMarginGen,
            'pnum'  :True,
            "pnumZone": 0,
            "grid"  :   tGrid
        """
        layoutZoneGenerator.__init__(self,config)
        self.leftPage  = pageGenerator(config)
        self.leftPage.setLeftOrRight(1)
        self.leftPage.setParent(self)
        self.rightPage = pageGenerator(config)
        self.rightPage.setLeftOrRight(2)
        self.rightPage.setParent(self)
        
        self._structure = [
                            ((self.leftPage,1,100),(self.rightPage,1,100),100)
                            ]
    
    
class pageGenerator(layoutZoneGenerator):
    """
     need to add background zone 
    """
    ID=1
    def __init__(self,config):
        layoutZoneGenerator.__init__(self,config)
        self._label='PAGE'
        h=config['page']['pageH']
        w=config['page']['pageW']
        r= config['page']["grid"]
        
        hm,hsd=  h
        self.pageHeight = integerGenerator(hm,hsd)
        self.pageHeight.setLabel('height')
        wm,wsd=  w
        self.pageWidth = integerGenerator(wm,wsd)
        self.pageWidth.setLabel('width')

        ##background 

        ##also need X0 and y0 
        self._x0 = 0
        self._y0 = 0
        
        (gridType,(cm,cs),(gm,gs)) = r
        assert gridType == 'regular'
        
        self.nbcolumns = integerGenerator(cm, cs)
        self.nbcolumns.setLabel('nbCol')
        self.gutter = integerGenerator(gm,gs)
        self.ColumnsListGen  = listGenerator(config,columnGenerator, self.nbcolumns)
        self.ColumnsListGen.setLabel("GRIDCOL")
        
        # required at line level!
        self.leading=None        
        
        
        self.leftOrRight = None
        # WHITE SPACES
        self.pageNumber = None  # should come from documentGen.listGen(page)?
        if self.getConfig()['page']['pnum']:
            self.pageNumber = pageNumberGenerator(config)
        
        self._margin = marginGenerator(config)
        
        
        # need to build margin zones! (for text in margin)
        # should be replaced by a layoutZoneGenerator
        self._typeArea_x1 = None
        self._typeArea_y1 = None
        self._typeArea_x2 = None
        self._typeArea_y2 = None
        self._typeArea_h = None
        self._typeArea_w = None        

        #once generation is done
        self._lColumns = []

        # define 
        self._marginRegions = []
        self._typeArea  = [ self._typeArea_x1 , self._typeArea_y1 , self._typeArea_x2 , self._typeArea_x2 , self._typeArea_h , self._typeArea_w ]
        

        mystruct =  [ (self.pageHeight,1,100),(self.pageWidth,1,100)]

        if self.pageNumber is not None:
            mystruct.append((self.pageNumber,1,100))
            
        mystruct.append((self._margin,1,100))
        mystruct.append((self.ColumnsListGen,1,100))
                             
        mystruct.append(100)
        self._structure = [
                        mystruct
                          ]


    def setLeftOrRight(self,n): self.leftOrRight = n
    def getLeftMargin(self): return self._marginRegions[2]
    
    def getRightMargin(self):return self._marginRegions[3]
        
    def getColumns(self):
        """
            assume generation done
        """
        self._lColumns= self._ruling._generation[1:]
        return self._lColumns
    
    def computeAllValues(self,H,W,t,b,l,r):
        """
            from page dim and margins: compute typearea
        """
        self._typeArea_x1 = l
        self._typeArea_y1 = t
        self._typeArea_x2 = W - r
        self._typeArea_y2 = H - b
        self._typeArea_h  = H - t - b
        self._typeArea_w  = W - l - r
        
        self._marginRegions = [(self._x0,self._y0,self._typeArea_y1,self.pageWidth._generation), #top
                               (self._x0,H - b,b,self.pageWidth._generation), #bottom
                               (self._x0,self._y0,self.pageHeight._generation,l), #left 
                               (W - r,self._y0,self.pageHeight._generation,r)  #right
                               
                               ]
        self._typeArea = [ self._typeArea_x1 , self._typeArea_y1 , self._typeArea_x2 , self._typeArea_x2 , self._typeArea_h , self._typeArea_w]

        #define the 4 margins as layoutZone

    def addPageNumber(self,p):
        """
        """
        zoneIndx = self.getConfig()["page"]['pnumZone']
        region = self._marginRegions[zoneIndx]
        
        # in the middle of the zone
        p.setPositionalGenerators((region[0]+region[3]*0.5,5),(region[1]+region[2]*0,5),(10,0),(10,1))
        
    def generate(self):
        """
            bypass layoutZoneGen: specific to page
        """
        self.setConfig(self.getParent().getConfig())

        self.setNumber(1)
        self._generation = []
        for obj in self._instance[:2]:
            obj.generate()
            self._generation.append(obj)        
        
            
        if self._margin:
            self._margin.setPage(self)
            self._margin.generate()
            self._generation.append(self._margin)
        t,b,l,r = map(lambda x:x._generation,self._margin._generation)
#         
#         self.pageHeight.generate()
        pH = self.pageHeight._generation
#         self.pageWidth.generate()
        pW = self.pageWidth._generation
#         
        self.computeAllValues(pH,pW,t, b, l, r)

        ## margin elements: page numbers
        if self.pageNumber is  not None:
            self.addPageNumber(self.pageNumber)
            self.pageNumber.generate()                
            self._generation.append(self.pageNumber)
            
            
        obj = self._instance[-1]    
        nbCols =  self.ColumnsListGen.getValuedNb()
        self._columnWidth  = self._typeArea[5] / nbCols   #replace by a generator integerGenerator(self.TAW / nbCol,sd)??
        self._columnHeight = self._typeArea[4]
        
        x1,y1,x2,y2,h,w = self._typeArea

        self._generation.append(self.nbcolumns)
        for i,colGen in enumerate(self.ColumnsListGen._instance):
#             print i, colGen
            colx = x1 + ( ( i * self._columnWidth) + 0)
            coly = y1
            colH = h
            colW = self._columnWidth
            colGen.setPositionalGenerators((colx,5),(coly,5),(colH,5),(colW,5))
            colGen.setGrid(self)       
            colGen.setPage(self)
            if self.getConfig()['colStruct'][0] == listGenerator:
                content=listGenerator(self.getConfig(), self.getConfig()['colStruct'][1],integerGenerator(*self.getConfig()['colStruct'][2]))
            else:    
                content=self.getConfig()['colStruct'][0](self.getConfig())
#             try:content=self.getConfig()['colStruct'][0](self.getConfig())
#             except KeyError as e: content=None
            if content is not None:
                colGen.updateStructure((content,1,100))
                colGen.instantiate()
                colGen.generate()
                self._generation.append(colGen)            
            
            
        #how generate page content
    

    def PageXmlFormatAnnotatedData(self, linfo, obj):
        """
            PageXml format 
        """
        self.domNode = etree.Element(obj.getLabel())
        if obj.getNumber() is not None:
            self.domNode.set('number',str(obj.getNumber()))   
        for info,tag in linfo:
            if isinstance(tag,Generator):
                node=tag.PageXmlFormatAnnotatedData(info,tag)
                self.domNode.append(node)
            else:
                self.domNode.set(tag,str(info))
        
        return self.domNode
        
    def XMLDSFormatAnnotatedData(self, linfo, obj):
        """
            how to store GT info: need to respect DS format!
            PAGE + margin info
        """
        self.domNode = etree.Element(obj.getLabel())
        if obj.getNumber() is not None:
            self.domNode.set('number',str(obj.getNumber()))    
        for info,tag in linfo:
            if isinstance(tag,Generator):
                node=tag.XMLDSFormatAnnotatedData(info,tag)
                self.domNode.append(node)
            else:
                self.domNode.set(tag,str(info))
        
        return self.domNode


class columnGenerator(layoutZoneGenerator):
    """
        a column generator
        requires a parent : x,y,h,w computed in the parent:
        
        see  CSS Box Model: margin,border, padding
        
    """
    def __init__(self,config,x=None,y=None,h=None,w=None):
        layoutZoneGenerator.__init__(self,config,x=x,y=y,h=h,w=w)
        self.setLabel("COLUMN")
        # other elements? image+ caption
        self._structure = [
#                             [(self.getX(),1,100),(self.getY(),1,100),(self.getHeight(),1,100),(self.getWidth(),1,100),(self.LineListGen,1,100),100]
                            [(self.getX(),1,100),(self.getY(),1,100),(self.getHeight(),1,100),(self.getWidth(),1,100),100]

                          ]
    
    def setGrid(self,g):self._mygrid = g
    def getGrid(self): return self._mygrid
#     def setPage(self,p):self._page = p
#     def getPage(self): return self._page    
    
    def generate(self):
        """
            prepare data for line
            nbLines: at instanciate() level?
            
        """
        # x,h, w,h
        self._generation = []
        for obj in self._instance[:-1]:
            obj.generate()
            self._generation.append(obj)
        
        colContent =  self._instance[-1]
        if isinstance(colContent,tableGenerator):
            x1,y1,h,w = self.getX()._generation,self.getY()._generation,self.getHeight()._generation,self.getWidth()._generation
            colContent.setPositionalGenerators((x1,0),(y1,0),(h,0),(w,0))
            colContent.setPage(self.getPage())
            colContent.generate()
            self._generation.append(colContent)            
            
        elif isinstance(colContent,listGenerator):
            self.leading = integerGenerator(*self.getConfig()['line']['leading'])
            self.leading.generate()
            self.leading.setLabel('leading')
            for i,lineGen in enumerate(colContent._instance):
                # too many lines
                if (i * self.leading._generation) + self.getY()._generation > (self.getY()._generation + self.getHeight()._generation):
                    continue
                linex =self.getX()._generation
                liney = (i * self.leading._generation) + self.getY()._generation
                lineH = 10
                lineW = self.getWidth()._generation   
                lineGen.setParent(self)
                lineGen.setPage(self.getPage()) 
                lineGen.setPositionalGenerators((linex,2),(liney,2),(lineH,2),(lineW,2))
    #             lineGen.setParent(self)        
                lineGen.generate()
                self._generation.append(lineGen)
    
        
    
class pageNumberGenerator(layoutZoneGenerator):
    """
        a pagenumgen
    """
    def __init__(self,config,x=None,y=None,h=None,w=None):
        layoutZoneGenerator.__init__(self,config,x=x,y=y,h=h,w=w)
        self._label='LINE'
        
    
    def XMLDSFormatAnnotatedData(self, linfo, obj):
        self.domNode = etree.Element(obj.getLabel())
        self.domNode.set('pagenumber','yes')
        self.domNode.set('DU_row','O')       
        for info,tag in linfo:
            if isinstance(tag,Generator):
                node=tag.XMLDSFormatAnnotatedData(info,tag)
                self.domNode.append(node)
            else:
                self.domNode.set(tag,str(info))
        
        return self.domNode        
        
class marginGenerator(Generator):
    """
        define margins:  top, bottom, left, right
            and also the print space coordinates
            
        restricted to 1?2-column grid max for the moment? 
    """
    def __init__(self,config):
        Generator.__init__(self,config)
        
        top = config['page']["margin"][0][0]
        bottom =  config['page']["margin"][0][1]
        left =  config['page']["margin"][0][2]
        right =  config['page']["margin"][0][3]        
        m,sd = top
        self._top= integerGenerator(m,sd)
        self._top.setLabel('top')
        m,sd = bottom
        self._bottom = integerGenerator(m,sd)
        self._bottom.setLabel('bottom')
        m,sd = left
        self._left = integerGenerator(m,sd)
        self._left.setLabel('left')
        m,sd = right
        self._right= integerGenerator(m,sd)
        self._right .setLabel('right')
        
        self._label='margin'
        
        
        self.leftMarginGen=layoutZoneGenerator(config)
        self.leftMarginGen.setLabel('leftMargin')
        self.rightMarginGen=layoutZoneGenerator(config)
        self.rightMarginGen.setLabel('rightMargin')
        self.topMarginGen=layoutZoneGenerator(config)
        self.topMarginGen.setLabel('topMargin')
        self.bottomMarginGen=layoutZoneGenerator(config)
        self.bottomMarginGen.setLabel('bottomMargin')
        
        
        self._structure = [ ((self._top,1,100),(self._bottom,1,100),(self._left,1,100),(self._right,1,100),100) ]
    
    def setPage(self,p):self._page=p 
    def getPage(self):return self._page
    
    def getDimensions(self): return self._top,self._bottom,self._left, self._right
        
    def getMarginZones(self):
        """
            return the 4 margins as layoutZone
        """
        
        
    def exportAnnotatedData(self,foo=None):
         
        self._GT=[]
        for obj in self._generation:
            if isinstance(obj._generation,basestring):
                self._GT.append((obj._generation,obj.getLabel()))
            elif type(obj._generation) == int:
                self._GT.append((obj._generation,obj.getLabel()))
            else:        
                if obj is not None:
#                     print obj,obj.exportAnnotatedData([])
                    self._GT.append( (obj.exportAnnotatedData([]),obj.getLabel()))
        
        return self._GT  

    def PageXmlFormatAnnotatedData(self,linfo,obj):
        
        self.domNode = etree.Element(obj.getLabel())
         
        for info,tag in linfo:
            self.domNode.set(tag,str(info))
         
        return self.domNode
        
    def XMLDSFormatAnnotatedData(self,linfo,obj):
        
        self.domNode = etree.Element(obj.getLabel())
         
        for info,tag in linfo:
            self.domNode.set(tag,str(info))
         
        return self.domNode



class catchword(layoutZoneGenerator):
    """
        catchword: always bottom right?
    """
    def __init__(self,config,x=None,y=None,h=None,w=None):
        layoutZoneGenerator.__init__(self,config,x=x,y=y,h=h,w=w)
        self.setLabel("CATCHWORD")
        
        self._structure = [
                            ((self.getX(),1,100),(self.getY(),1,100),(self.getHeight(),1,100),(self.getWidth(),1,100),100)
                            ]        
                

class marginaliaGenerator(layoutZoneGenerator):
    """
        marginalia Gen: assume relation with 'body' part
    """
    def __init__(self,config,x=None,y=None,h=None,w=None):
        layoutZoneGenerator.__init__(self,config,x=x,y=y,h=h,w=w)
        self.setLabel("MARGINALIA")
        
        #pointer to the parent structures!! line? page,?
        #lineGen!!
        
        self._structure = [
                            ((self.getX(),1,100),(self.getY(),1,100),(self.getHeight(),1,100),(self.getWidth(),1,100),100)
                            ]        
            
class LineGenerator(layoutZoneGenerator):
    """
        what is specific to a line? : content
            content points to a textGenerator
            
        
        for table noteGen must be positioned better!
            if parent= column
            if parent= cell
            if parent =...
            
    """ 
    def __init__(self,config,x=None,y=None,h=None,w=None):
        layoutZoneGenerator.__init__(self,config,x=x,y=y,h=h,w=w)
        self.setLabel("LINE")
        
        self._noteGen = None
        self._noteGenProb = None
        
        self.BIES = 'O'
        if "marginalia" in self.getConfig()["line"]:
            self._noteGen = self.getConfig()["line"]["marginalia"][0](self.getConfig())
            self._noteGenProba= self.getConfig()["line"]["marginalia"][1]
            
        self._justifixationGen = None #justificationGenerator() # center, left, right, just, random
        
        self.bSkew = None  # (angle,std)
        
        self._structure = [
                            ((self.getX(),1,100),(self.getY(),1,100),(self.getHeight(),1,100),(self.getWidth(),1,100),100)
                            ]
        if self._noteGen is not None:
            self._structure = [
                           ((self.getX(),1,100),(self.getY(),1,100),(self.getHeight(),1,100),(self.getWidth(),1,100),(self._noteGen,1,self._noteGenProba),100)
                            ]
        
    def setPage(self,p):self._page=p
    def getPage(self): return self._page
    
    def computeBIES(self,pos,nbLines):
        """
            new annotation DU_row
        """
        
        
        if   nbLines == 1        : self.BIES='S'
        elif pos     == 0        : self.BIES='B'
        elif pos     == nbLines-1: self.BIES='E'
        else                     : self.BIES='I'
        
    def generate(self):
        """
        need a pointer to the column to select the possible margins
        need a pointer to the margin to add the element  if any
        
        need to be able to position vertically and horizontally
        
        """
        self._generation = []
        for obj in self._instance[:4]:
            obj.generate()
            self._generation.append(obj)

        #if marginalia
        if len(self._instance) == 5:
            # left or right margin
            # need to go up to the grid to know where the column is
            if self.getPage().leftOrRight == 1: 
                # get left margin
                myregion= self.getPage().getLeftMargin()
#                 print myregion
                #left page: put on the left margin, right otherwise? 
                marginaliax = myregion[0]+10
            else:
                #marginaliax = 600 
                myregion= self.getPage().getRightMargin()
                marginaliax = myregion[0]+10
                
            marginaliay = self.getY()._generation
            marginaliaH = 50
            marginaliaW = 50   
            # compute position according to the justifiaction : need parent, 
            self._noteGen.setPositionalGenerators((marginaliax,5),(marginaliay,5),(marginaliaH,5),(marginaliaW,5))
            self._noteGen.generate()
            self._generation.append(self._noteGen)
                    
        return self
    
    def XMLDSFormatAnnotatedData(self,linfo,obj):
        self.domNode = etree.Element(obj.getLabel())
        # for listed elements
#         self.domNode.set('type',str(self.BIES))        
        self.domNode.set('DU_row',str(self.BIES))        
        # need DU_col, DU_header 

        for info,tag in linfo:
            if isinstance(tag,Generator):
                self.domNode.append(tag.XMLDSFormatAnnotatedData(info,tag))
            else:
                self.domNode.set(tag,str(info))
        
        return self.domNode
    
class cellGenerator(layoutZoneGenerator):
    """
        cellGen
        
        for the set of lines: define at this level the horizontal and vertical justification
        
        
        similar to column? a cell containts a grid???
            for instance: padding as well
        
        
    """ 
    def __init__(self,config,x=None,y=None,h=None,w=None):
        layoutZoneGenerator.__init__(self,config,x=x,y=y,h=h,w=w)
        self.setLabel("CELL")
        
        self._index = None
#         self.VJustification = booleanGenerator(0.1)
#         self.VJustification.setLabel('VJustification')
#         self.HJustification = integerGenerator(3, 1)
        self.leading = integerGenerator(*self.getConfig()['line']['leading'])
        self.leading.setLabel('leading')
        self.nbLinesG = integerGenerator(5, 3)
        self._LineListGen = listGenerator(config,LineGenerator, self.nbLinesG)
        self._LineListGen.setLabel("cellline")
        self._structure =[((self.getX(),1,100),(self.getY(),1,100),(self.getHeight(),1,100),(self.getWidth(),1,100),
                           (self.leading,1,100),
#                            (self.VJustification,1,100),
                           (self._LineListGen,1,100),100)]
    
    
    def getIndex(self): return self._index
    def setIndex(self,i,j): self._index=(i,j)
    def setNbLinesGenerator(self,g):
        self.nbLinesG = g
        self._LineListGen = listGenerator(self.getConfig(),LineGenerator, self.nbLinesG)
    def getNbLinesGenerator(self): return self.nbLinesG
    
    def computeYStart(self,HJustification,blockH):
        """
            compute where to start 'writing' according to justification and number of lines (height of the block)
        """
        if HJustification == horizontalTypoGenerator.TYPO_TOP:
            return 0
        if HJustification == horizontalTypoGenerator.TYPO_HCENTER: 
            return  (0.5 * self.getHeight()._generation)  -  (0.5 * blockH)
        if HJustification == horizontalTypoGenerator.TYPO_BOTTOM:
            # not implemented: need the number of lines for this!
            return 0
        
    def generate(self):
        self._generation=[]
        for obj in self._instance[:-1]:
            obj.generate()
            self._generation.append(obj)
#         print self.getLabel(),self._generation
        self._LineListGen.instantiate()

        self.vjustification = self.getConfig()['vjustification'].generate()._generation
        self.hjustification = self.getConfig()['hjustification'].generate()._generation
        # vertical justification : find the y start
#         ystart=self.computeYStart(self.VJustification._generation, self._LineListGen.getValuedNb()*self.leading._generation)
        ystart=self.computeYStart( self.hjustification, self._LineListGen.getValuedNb()*self.leading._generation)
        xstart = self.getWidth()._generation * 0.1
        rowPaddingGen = numericalGenerator(1,0)
        rowPaddingGen.generate()
        
        lineH=integerGenerator(*self.getConfig()['line']['lineHeight'])
        lineH.generate()
        nexty= ystart +  self.getY()._generation + rowPaddingGen._generation
        lLines=[]
        for i,lineGen in enumerate(self._LineListGen._instance):
            # too many lines
#             if (i * self.leading._generation) + (self.getY()._generation + lineH) > (self.getY()._generation + self.getHeight()._generation):
            if nexty +lineH._generation >  (self.getY()._generation + self.getHeight()._generation):
                continue

            liney = nexty
            lineW=integerGenerator(self.getWidth()._generation*0.75,self.getWidth()._generation*0.1)
            lineW.generate()
            
            if self.vjustification == verticalTypoGenerator.TYPO_LEFT:
                linex = self.getX()._generation + (xstart)        
            if self.vjustification == verticalTypoGenerator.TYPO_RIGHT:
                linex = self.getX()._generation + self.getWidth()._generation - lineW._generation     
            elif self.vjustification == verticalTypoGenerator.TYPO_VCENTER:
                linex =  self.getX()._generation + self.getWidth()._generation * 0.5 - lineW._generation *0.5  
            lineGen.setPositionalGenerators((linex,1),(liney,1),(lineH._generation,0.5),(lineW._generation,0))
#             lineGen.setPositionalGenerators((linex,0),(liney,0),(lineH,0),(lineW * 0.5,lineW * 0.1))
            lineGen.setPage(self.getPage())  
            lineGen.setParent(self)
            lLines.append(lineGen)
            lineGen.generate()
            rowPaddingGen.generate()
            nexty= lineGen.getY()._generation +self.leading._generation +  lineGen.getHeight()._generation+ rowPaddingGen._generation
            lineGen.setLabel('LINE')
            self._generation.append(lineGen)
        
        nbLines=len(lLines)
        for i,lineGen in enumerate(lLines):
            lineGen.computeBIES(i,nbLines)
        return self    

    def XMLDSFormatAnnotatedData(self,linfo,obj):
        self.domNode = etree.Element(obj.getLabel())
        # for listed elements
        self.domNode.set('row',str(self.getIndex()[0]))        
        self.domNode.set('col',str(self.getIndex()[1]))        

        for info,tag in linfo:
            if isinstance(tag,Generator):
                self.domNode.append(tag.XMLDSFormatAnnotatedData(info,tag))
            else:
                self.domNode.set(tag,str(info))
        
        return self.domNode


class tableGenerator(layoutZoneGenerator):
    """
        a table generator
        
        "padding" between two rows  (either a line and smal padding, or a larger space)
        idem for columns 
        
        
        either: use number of  rows/columns
                or rows/column height/width  (or constraint = allthesamevalue)
        
    """   
    def __init__(self,config):
        layoutZoneGenerator.__init__(self,config)

        self.setLabel('TABLE')
                 
        nbRows=config['table']['nbRows']
        self.rowHeightVariation = config['table']['rowHeightVariation']
        self.rowHStd=self.rowHeightVariation[1]
        self.columnWidthVariation = config['table']['columnWidthVariation']
        
        if 'widths' in self.getConfig()['table']['column']:
            self.nbCols = integerGenerator(len(self.getConfig()['table']['column']['widths']),0)
        else:
            nbCols=config['table']['nbCols']
            self.nbCols = integerGenerator(nbCols[0],nbCols[1])
        self.nbCols.setLabel('nbCols')
        self.nbRows = integerGenerator(nbRows[0],nbRows[1])
        self.nbRows.setLabel('nbRows')
        
        self._bSameRowHeight=config['table']['row']['sameRowHeight']
        self._lRowsGen = listGenerator(config,layoutZoneGenerator, self.nbRows)
        self._lRowsGen.setLabel("row")
        self._lColumnsGen = listGenerator(config['table']['column'],layoutZoneGenerator, self.nbCols )
        self._lColumnsGen.setLabel("col")
        
        self._structure = [
            ((self.getX(),1,100),(self.getY(),1,100),(self.getHeight(),1,100),(self.getWidth(),1,100),
             (self.nbCols,1,100),(self.nbRows,1,100),
             (self._lColumnsGen,1,100),(self._lRowsGen,1,100),100)
            ]
        
    def generate(self):
        """
            generate the rows, the columns, and then the cells
        """
        self._generation = []
        for obj in self._instance[:-2]:
            obj.generate()
            self._generation.append(obj)
                    
        nbCols =  len(self._lColumnsGen._instance)
        nbRows= len(self._lRowsGen._instance)
        if nbRows == 0: 
            return 
        if nbCols == 0:
            return 
        self._columnWidthM  = int(round(self.getWidth()._generation / nbCols))
        self._columnWidthG = numericalGenerator(self._columnWidthM, self._columnWidthM*0.2)

        self._rowHeightM = int(round(self.getHeight()._generation / nbRows))
        self._rowHeightG = positiveIntegerGenerator(self._rowHeightM,self.rowHStd)
        
#         self._rowHeightM = int(round(self.getHeight()._generation / nbRows))
#         self._rowHeightG = numericalGenerator(self._rowHeightM,self._rowHeightM*0.5)
        self.lCols=[]
        self.lRows=[]
        nextx= self.getX()._generation
        
        
        for i,colGen in enumerate(self._lColumnsGen._instance):
            if nextx > self.getX()._generation + self.getWidth()._generation:
                continue
            colx = nextx #self.getX()._generation + ( i * self._columnWidth)
            coly = self.getY()._generation
            colH = self.getHeight()._generation
            if 'widths' in self.getConfig()['table']['column']:
                colW = self.getConfig()['table']['column']['widths'][i] * self.getWidth()._generation
            else:
                self._columnWidthG.generate()
                colW = self._columnWidthG._generation
            colGen.setNumber(i)
            colGen.setPositionalGenerators((colx,0),(coly,0),(colH,0),(colW,0))
#             colGen.setGrid(self)       
            colGen.setLabel("COL")
            colGen.setPage(self.getPage())
            colGen.generate()
            nextx= colGen.getX()._generation + colGen.getWidth()._generation
            self._generation.append(colGen)
            self.lCols.append(colGen)
            
        ## ROW
        # max nblines 
        if 'nbLines' in self.getConfig()['table']['column']:
                nbMaxLines = max(x[0] for x in self.getConfig()['table']['column']['nbLines'])
                lineH=self.getConfig()['line']['lineHeight']
                lineHG=positiveIntegerGenerator(*lineH)
                lineHG.generate()
                nblineG=positiveIntegerGenerator(nbMaxLines,0)
                nblineG.generate()
                self._rowHeightG = positiveIntegerGenerator(nblineG._generation*lineHG._generation,self.rowHStd)
        else: nbMaxLines=None
        rowH = None
        nexty = self.getY()._generation
        for i,rowGen in enumerate(self._lRowsGen._instance):
            if nexty > self.getHeight()._generation + self.getY()._generation:
                continue
            rowx = self.getX()._generation 
            # here   generator for height variation!
            if self._bSameRowHeight:
                if rowH is None:
                    self._rowHeightG.generate() 
                    rowH = self._rowHeightG._generation
            else:
                self._rowHeightG.generate() 
                rowH = self._rowHeightG._generation
#                 print (rowH)
            rowy = nexty 
            # here test that that there is enough space for the row!!
#             print self._rowHeightM, self._rowHeightG._generation
            rowW = self.getWidth()._generation
            rowGen.setLabel("ROW")
            rowGen.setNumber(i)
            rowGen.setPage(self.getPage())
            rowGen.setPositionalGenerators((rowx,0),(rowy,0),(rowH,0),(rowW,0))
            rowGen.generate()
            nexty = rowGen.getY()._generation + rowGen.getHeight()._generation 
#             print i, rowy, self.getHeight()._generation
            self.lRows.append(rowGen)
            self._generation.append(rowGen)       
#             print("%d %s %f"%(i,self._bSameRowHeight,rowGen.getHeight()._generation))     
            
        ## table specific stuff
        ## table headers, stub,....


        #### assume the grid col generated?
        ### introduce a hierarchical column
        #### split the col into N subcols  :: what is tricky: headers  split the first         
        ### hierarchical row: for this needs big rows and split
        
        ## creation of the cells; then content in the cells
        self.lCellGen=[]
        for icol,col in enumerate(self.lCols):
            if 'nbLines' in self.getConfig()['table']['column']:
                nblines=self.getConfig()['table']['column']['nbLines'][icol]
                nbLineG = positiveIntegerGenerator(*nblines)
            else: nbLineG=None
            for irow, row in enumerate(self.lRows):
                cell=cellGenerator(self.getConfig())
                cell.setLabel("CELL")
                cell.setPositionalGenerators((col.getX()._generation,0),(row.getY()._generation,0),(row.getHeight()._generation,0),(col.getWidth()._generation,0))
                # colunm header? {'column':{'header':{'colnumber':1,'justification':'centered'}}
                
                if irow < self.getConfig()['table']['column']['header']['colnumber'] :
                    cell.getConfig()['vjustification']= self.getConfig()['table']['column']['header']['vjustification']
#                     print(icol,cell.getConfig()['justification'])
                else:cell.getConfig()['vjustification'] = self.getConfig()['line']['vjustification']
                cell.getConfig()['hjustification'] = self.getConfig()['line']['hjustification']
                # row header?
                self.lCellGen.append(cell)
                cell.setNbLinesGenerator(nbLineG)
                cell.setIndex(irow,icol)
                cell.instantiate()
                cell.setPage(self.getPage())
                cell.generate()
                self._generation.append(cell)
        


    
        
class documentGenerator(Generator):
    """
        a document generator

        need to store the full list of parameters for sub elements
        
        in json!!
        
        pageNumber
        pageHeight
        pageWidth
        marginTop
        marginBottom
        marginLeft
        marginRight
        
        gridnbCol
            
            listObjects (structure!): weight for the potential objects
            colnbLines    ## replaced by a structure corresponding to a content stream (header/paragraph. table;...)
                lineleading 
                lineskew
                lineUnderline
                lineHjustification
                lineVjustification
                ...
            tableWidth
            tableHeight
            tablenbCol
            tablenbRow
            tableCellNbLines (similar to columnlines) 
                celllineleading  ...
                lineHjustification
                lineVjustification



        levels between document and page/double-page: usefull?
    """
    def __init__(self,dConfig):
        
#         tpageH = dConfig["page"]['pageH']
#         tpageW = dConfig["page"]['pageW']
        tnbpages = dConfig["page"]['nbPages']
#         tMargin = (dConfig["page"]['lmargin'],dConfig["page"]['rmargin'])
#         tRuling = dConfig["page"]['grid']
        
        Generator.__init__(self)
        self._name = 'DOC'

        # missing elements:
        self._isCropped = False  # cropped pages
        self._hasBackground = False # background is visible
        
        #how to serialize the four cover pages?
        #in instantiate (or generation?): put the 3-4cover at the end?
        self.lCoverPages = None
        self._hasBinding = False  # binding image
        
        self.scanner = None ## the way the pages are "scanned"
        # 1: single page ; 2 double page 3 cropped 4 _twoPageImage  # background
        
        # portion of the other page visible
        self._twoPageImage= False # two pages in one image 
        
        self._nbpages = integerGenerator(tnbpages[0],tnbpages[1])
        self._nbpages.setLabel('nbpages')

#         self._margin = tMargin
#         self._ruling = tRuling      
        
        
        self.pageListGen = listGenerator(dConfig,pageGenerator,self._nbpages)
        self.pageListGen.setLabel('pages')
        self._structure = [
                            #firstSofcover (first and second)
                            ((self.pageListGen,1,100),100) 
                            #lastofcover (if fistofcover??)
                            ]
    
    
    def PageXmlFormatAnnotatedData(self,gtdata):
        """
            convert into PageXMl
        """
        root  = etree.Element("PcGts")
        self.docDom = etree.ElementTree(root)
#         self.docDom.setRootElement(root)
        for info,page in gtdata:
            pageNode = page.XMLDSFormatAnnotatedData(info,page)
            root.append(pageNode)
        return self.docDom
        
        
        
    def XMLDSFormatAnnotatedData(self,gtdata):
        """
            convert into XMLDSDformat
            (write also PageXMLFormatAnnotatedData! )
        """
        root  = etree.Element("DOCUMENT")
        self.docDom = etree.ElementTree(root)
#         self.docDom.setRootElement(root)
        metadata= etree.Element("METADATA")
        root.append(metadata)
        metadata.text = str(self.getConfig())
        for info,page in gtdata:
            pageNode = page.XMLDSFormatAnnotatedData(info,page)
            root.append(pageNode)
        return self.docDom
        
        
    def generate(self):
        self._generation = []
        
        ## 1-2 cover pages
        
        for i,pageGen in enumerate(self.pageListGen._instance):
            #if double page: start with 1 = right?
            pageGen.setConfig(self.getConfig())
            pageGen.generate()
            self._generation.append(pageGen)
    
        ## 3-4 covcer pages
        return self
    
    def exportAnnotatedData(self,foo):
        """
            build a full version of generation: integration of the subparts (subtree)
            
            what are the GT annotation for document?  
             
        """
        ## export (generated value, label) for terminal 

        self._GT=[]
        for obj in self._generation:
            self._GT.append((obj.exportAnnotatedData([]),obj))
        
        return self._GT
    
class DocMirroredPages(documentGenerator):
#     def __init__(self,tpageH,tpageW,tnbpages,tMargin=None,tRuling=None):
    def __init__(self,dConfig):

#         scanning = dConfig['scanning']
#         tpageH = dConfig["page"]['pageH']
#         tpageW = dConfig["page"]['pageW']
        tnbpages = dConfig["page"]['nbPages']
        self._nbpages = integerGenerator(tnbpages[0],tnbpages[1])
        self._nbpages.setLabel('nbpages')        
#         tMargin = (dConfig["page"]['margin'],dConf)
#         tRuling = dConfig["page"]['grid']
        
#         documentGenerator.__init__(self,tpageH,tpageW,tnbpages,tMargin,tRuling)
        documentGenerator.__init__(self,dConfig)
        
        self.setConfig(dConfig)

#         self._lmargin, self._rmargin = tMargin
#         self._ruling= tRuling
        self.pageListGen = listGenerator(dConfig,doublePageGenerator,self._nbpages)
        self.pageListGen.setLabel('pages')
        self._structure = [
                            #firstSofcover (first and second)
                            ((self.pageListGen,1,100),100) 
                            #lastofcover (if fistofcover??)
                            ]
        
    def generate(self):
        self._generation = []
        
        for pageGen in self.pageListGen._instance:
            pageGen.generate()
            self._generation.append(pageGen)
        return self  
    
class paragraphGenerator(Generator):
    """
        needed: number of lines: no not at this level: simply 'length' and typographical specification
        no 'positional' info at this level: one stream_wise objects
        
        need to be recursive ==> treeGenerator (ala listGenerator!=
    """
    LEFT      = 1
    RIGHT     = 2
    CENTER    = 3
    JUSTIFIED = 4
    
    def __init__(self,nblinesGen, length):
        Generator.__init__(self)
        
        self.alignment = None
        self.firstLineIndent = None
        self.spaceBefore = None
        self.spaceAfter = None
        
        self.nblines = nblinesGen
        self.firstLine = LineGenerator()
        self.lines = LineGenerator()
        self._structure = [
                (  (self.firstLine,1,100),(self.lines,self.nblines,100),100) 
                    ]

class content(Generator):
    """
        stream_wise content : sequence of par/heders, , tables,...
        
        json profile: kind of css : css for headers, content, listitems,...
    """
    def __init__(self,nbElt,lenElt):
        Generator.__init__(self)
        
        mElt,sElt = nbElt
        self._nbElts = integerGenerator(mElt, sElt)
        mlenElt,slenElt = lenElt
        self._lenElt = integerGenerator(mlenElt, slenElt)        
        self.contentObjectListGen = listGenerator(paragraphGenerator,self._nbElts,self._lenElt)

def docm():
    
    # scanningZone: relative to the page 
    # % of zoom in 
    pageScanning = ((5, 2),(10, 2),(5, 3),(5, 2))
    
    tlMarginGen = ((100, 10),(100, 10),(150, 10),(50, 10))
    trMarginGen = ((100, 10),(100, 10),(50, 10),(150, 10))

    tGrid = ( 'regular',(2,0),(0,0) )
    
    Config = {
        "scanning": pageScanning,
        "pageH":    (700, 10),
        "pageW":    (500, 10),
        "nbPages":  (2,0),
        "lmargin":  tlMarginGen,
        "rmargin":  trMarginGen,
        "grid"  :   tGrid,
        "leading":  (12,1), 
        "lineHeight":(10,1)
        }
#     mydoc = DocMirroredPages((1200, 10),(700, 10),(1, 0),tMargin=(tlMarginGen,trMarginGen),tRuling=tGrid)
    mydoc = DocMirroredPages(Config)

    mydoc.instantiate()
    mydoc.generate()
    gt =  mydoc.exportAnnotatedData(())
#     print gt
    docDom = mydoc.XMLDSFormatAnnotatedData(gt)
#     print etree.tostring(docDom,encoding="utf-8", pretty_print=True)
    docDom.write("tmp.ds_xml",encoding='utf-8',pretty_print=True)    

def StAZHDataset(nbpages):
    """
        page header (centered)
        page number (mirrored: yes and no)
        catch word (bottom right)
        marginalia (left margin; mirrored also?)
         
    """
    tlMarginGen = ((50, 5),(50, 5),(50, 5),(50, 5))
    trMarginGen = ((50, 5),(50, 5),(50, 5),(50, 5))

    tGrid = ( 'regular',(1,0),(0,0) )
        
    Config = {
        "page":{
            "scanning": None
            ,"pageH":    (780, 50)
            ,"pageW":    (500, 50)
            ,"nbPages":  (nbpages,0)
            ,"margin": [tlMarginGen, trMarginGen]
            ,'pnum'  :{'position':"left"}
            ,"pnumZone": 0
            ,"grid"  :   tGrid
        }
        #column?
        ,"line":{
             "leading":     (15+5,1) 
            ,"lineHeight":  (15,1)
            ,"justification":'left'
            ,'marginalia':[marginaliaGenerator,10]
            ,'marginalialineHeight':10
            }
        
        ,"colStruct": (listGenerator,LineGenerator,(20,0))
#         ,'table':{
#             "nbRows":  (40,0)
#             ,"nbCols":  (5,0)
#             ,"rowHeightVariation":(0,0)
#             ,"columnWidthVariation":(0,0)
#             ,'column':{'header':{'colnumber':1,'justification':'centered'}}
#             ,'row':{"sameRowHeight": True }
#             ,'cell':{'justification':'right','line':{"leading":(14,0)}}
#             }
        }    
    mydoc = DocMirroredPages(Config)
    mydoc.instantiate()
    mydoc.generate()
    gt =  mydoc.exportAnnotatedData(())
#     print gt
    docDom = mydoc.XMLDSFormatAnnotatedData(gt)
    return docDom 
        
        
def ABPRegisterDataset(nbpages):
    """
        ABP register
        
    """
    tlMarginGen = ((50, 5),(50, 5),(50, 5),(50, 5))
    trMarginGen = ((50, 5),(50, 5),(50, 5),(50, 5))

    tGrid = ( 'regular',(1,0),(0,0) )
    
    # should be replaced by an object?
    ABPREGConfig = {
        "page":{
            "scanning": None
            ,"pageH":    (780, 50)
            ,"pageW":    (500, 50)
            ,"nbPages":  (nbpages,0)
            ,"margin": [tlMarginGen, trMarginGen]
            ,'pnum'  :{'position':"left"}  # also ramdom?
            ,"pnumZone": 0
            ,"grid"  :   tGrid
        }
        #column?
        ,"line":{
             "leading":     (5,4) 
            ,"lineHeight":  (18,2)
            ,"justification":'left'
            }
        
        ,"colStruct": (tableGenerator,1,nbpages)
        ,'table':{
            "nbRows":  (30,2)
            ,"nbCols":  (5,1)
            ,"rowHeightVariation":(0,0)
            ,"columnWidthVariation":(0,0)
            ,'column':{'header':{'colnumber':1,'justification':'centered'}}
            ,'row':{"sameRowHeight": True }
            ,'cell':{'justification':'right','line':{"leading":(14,0)}}
            }
        }    
    
    Config=ABPREGConfig
    mydoc = DocMirroredPages(Config)
    mydoc.instantiate()
    mydoc.generate()
    gt =  mydoc.exportAnnotatedData(())
#     print gt
    docDom = mydoc.XMLDSFormatAnnotatedData(gt)
    return docDom    

def NAFDataset(nbpages):
    tlMarginGen = ((50, 5),(50, 5),(50, 5),(50, 5))
    trMarginGen = ((50, 5),(50, 5),(50, 5),(50, 5))

    tGrid = ( 'regular',(1,0),(0,0) )
    #for NAF!: how to get the column width??? 
    NAFConfig = {
        "page":{
            "scanning": None,
            "pageH":    (780, 50),
            "pageW":    (500, 50),
            "nbPages":  (nbpages,0),
            "margin": [tlMarginGen, trMarginGen],
            'pnum'  :True,
            "pnumZone": 0,
            "grid"  :   tGrid
        }
        #column?
        ,"line":{
             "leading":     (5,4) 
            ,"lineHeight":  (10,1)
            ,"justification":'left'
            }
        
        ,"colStruct": (tableGenerator,1,nbpages)
        ,'table':{
             "nbRows":  (35,10)
            ,"nbCols":  (5,0)
            ,"rowHeightVariation":(20,5)
            ,"columnWidthVariation":(0,0)
            #                                                                      proportion of col width known          
            ,'column':{'header':{'colnumber':1,'justification':'centered'}
                       ,'widths':(0.01,0.05,0.05,0.5,0.2,0.05,0.05,0.05,0.05,0.05,0.05)
                       #nb textlines 
                        ,'nbLines':((1,0.1),(1,0.1),(1,0.1),(4,1),(3,1),(1,1),(1,0.5),(1,1),(1,0.5),(1,0.5),(1,0.5))

                       }
            ,'row':{"sameRowHeight": False }
            ,'cell':{'justification':'right','line':{"leading":(14,0)}}
            }
        }  
    Config=NAFConfig
    mydoc = DocMirroredPages(Config)
    mydoc.instantiate()
    mydoc.generate()
    gt =  mydoc.exportAnnotatedData(())
#     print gt
    docDom = mydoc.XMLDSFormatAnnotatedData(gt)
    return docDom    


def NAHDataset(nbpages):
    """
    @todo: need to put H centered lines
    """
    
    tlMarginGen = ((50, 5),(50, 5),(50, 5),(50, 5))
    trMarginGen = ((50, 5),(50, 5),(50, 5),(50, 5))

    tGrid = ( 'regular',(1,0),(0,0) )
    #for NAF!: how to get the column width??? 
    NAFConfig = {
        "page":{
            "scanning": None,
            "pageH":    (780, 50),
            "pageW":    (500, 50),
            "nbPages":  (nbpages,0),
            "margin": [tlMarginGen, trMarginGen],
            'pnum'  :True,
            "pnumZone": 0,
            "grid"  :   tGrid
        }
        #column?
        ,"line":{
             "leading":     (5,4) 
            ,"lineHeight":  (10,1)
            ,"vjustification":verticalTypoGenerator([0.5,0.25,0.25])
            #                  0: top
            ,'hjustification':horizontalTypoGenerator([0.33,0.33,0.33])
            }
        
        ,"colStruct": (tableGenerator,1,nbpages)
        ,'table':{
             "nbRows":  (35,10)
            ,"nbCols":  (5,0)
            ,"rowHeightVariation":(20,5)
            ,"columnWidthVariation":(0,0)
            #                                                                      proportion of col width known          
            ,'column':{'header':{'colnumber':1,'vjustification':verticalTypoGenerator([0,1,0])}
                       ,'widths':(0.01,0.05,0.05,0.5,0.2,0.05,0.05,0.05,0.05,0.05,0.05)
                       #nb textlines 
                        ,'nbLines':((1,0.1),(1,0.1),(1,0.1),(4,1),(3,1),(1,1),(1,0.5),(1,1),(1,0.5),(1,0.5),(1,0.5))

                       }
            ,'row':{"sameRowHeight": False }
            ,'cell':{'hjustification':horizontalTypoGenerator([0.75,0.25,0.0]),'vjustification':verticalTypoGenerator([0,0,1]),'line':{"leading":(14,0)}}
            }
        }  
    Config=NAFConfig
    mydoc = DocMirroredPages(Config)
    mydoc.instantiate()
    mydoc.generate()
    gt =  mydoc.exportAnnotatedData(())
#     print gt
    docDom = mydoc.XMLDSFormatAnnotatedData(gt)
    return docDom    

def BARDataset(nbpages):
    """
        ABP register
        
    """
    tlMarginGen = ((50, 5),(50, 5),(50, 5),(50, 5))
    trMarginGen = ((50, 5),(50, 5),(50, 5),(50, 5))

    tGrid = ( 'regular',(1,0),(0,0) )
    
    # should be replaced by an object?
    BARConfig = {
        "page":{
            "scanning": None,
            "pageH":    (780, 50),
            "pageW":    (500, 50),
            "nbPages":  (nbpages,0),
            "margin": [tlMarginGen, trMarginGen],
            'pnum'  :True,
            "pnumZone": 0,
            "grid"  :   tGrid
        }
        #column?
        ,"line":{
             "leading":     (15,1) 
            ,"lineHeight":  (15,1)
            ,"justification":'left'
            }
        
        ,"colStruct": (listGenerator,LineGenerator,(2,0))
        }    
    
    Config=BARConfig
    mydoc = DocMirroredPages(Config)
    mydoc.instantiate()
    mydoc.generate()
    gt =  mydoc.exportAnnotatedData(())
#     print gt
    docDom = mydoc.XMLDSFormatAnnotatedData(gt)
    return docDom  

if __name__ == "__main__":

    try: outfile =sys.argv[2]
    except IndexError as e:
        print("usage: layoutObjectGenerator.py #sample <FILENAME>")
        sys.exit() 
    
    try: nbpages = int(sys.argv[1])
    except IndexError as e: nbpages = 1
    
#     dom1 = ABPRegisterDataset(nbpages)
#     dom1 = NAFDataset(nbpages)
    dom1 = NAHDataset(nbpages)

#     dom1 = StAZHDataset(nbpages)
#     dom1 = BARDataset(nbpages)

    dom1.write(outfile,xml_declaration=True,encoding='utf-8',pretty_print=True)

    print("saved in %s"%outfile)    


    
    
