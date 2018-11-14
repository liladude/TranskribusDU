# -*- coding: UTF-8 -*-
# generated by wxGlade 0.4 on Thu Jul 13 10:46:35 2006

import wx
from wx.lib.floatcanvas import NavCanvas, FloatCanvas

import os, types, sys, traceback
from lxml import etree

from document import Document
from config import Config

# begin wxGlade: dependencies
# end wxGlade

sEncoding = "utf-8"
sConfigFile = "wxvisu.ini"

sAbout = """MultiPageXML viewer- version 2.0
Copyright Xerox 2006-2008
J Fuselier, JL Meunier

In 2016 and 2017, further development by and for the EU project READ. The READ project has received funding from the European Union�s Horizon 2020 research and innovation programme under grant agreement No 674943.
JL Meunier, H Dejean

System info: 
   - python version %s
   - wx version %s
""" % (sys.version, wx.VERSION)

sHelp = """Have a look at http://dima.grenoble.xrce.xerox.com/wiki/WXVisu"""
sConfirmQuit = """Some unsaved actions occured - please confirm the quit _without_ saving!"""

#HACk to deal with the recent document by generating code
gdicRecentDoc = {}
gSELF = None

def setEncoding(s):
    global sEncoding
    sEncoding = s
    
def setConfigFile(s):
    global sConfigFile
    sConfigFile = s

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        
        # The NavCanvas
        self.wysi = NavCanvas.NavCanvas(self,
                                        1,
                                        Debug=0,
                                        BackgroundColor="WHITE")
        tb = self.wysi.ToolBar
        tsize=(20,20)
        bck_bmp =  wx.ArtProvider.GetBitmap(wx.ART_GO_BACK)
        for_bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD)
        jumpback_bmp = wx.ArtProvider.GetBitmap(wx.ART_UNDO)
        jumpback_bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_TO_PARENT)
        self.tc_pagesel = wx.TextCtrl(tb,
                                      style=wx.TE_PROCESS_ENTER)
#         self.tc_pagecur = wx.TextCtrl(tb,
#                                       style=wx.TE_READONLY)
# #                                     style=wx.TE_CENTRE|wx.TE_PROCESS_ENTER)
        self.tc_pagetot = wx.TextCtrl(tb, 
                                      style=wx.TE_READONLY)
        # Add some buttons to the canvas toolbar            
        tb.AddSeparator()
        ID_BACKWARD = wx.NewId()
        ID_FORWARD = wx.NewId()    
        tb.AddSimpleTool(ID_BACKWARD, bck_bmp, "Display the previous page")
#         tb.AddControl(self.tc_pagecur)
        tb.AddControl(self.tc_pagetot)
        tb.AddSimpleTool(ID_FORWARD, for_bmp, "Display the next page")
        tb.AddControl(self.tc_pagesel)
        ID_JUMPBACK = wx.NewId()
        tb.AddSeparator()
        tb.AddSimpleTool(ID_JUMPBACK, jumpback_bmp, "Back")
        tb.Realize()
        
        # Menu Bar
        self.frame_1_menubar = wx.MenuBar()
        self.SetMenuBar(self.frame_1_menubar)
        wxglade_tmp_menu = wx.Menu()
        id_load = wx.NewId()
        id_reload = wx.NewId()
        id_reloadini = wx.NewId()
        id_save = wx.NewId()
        id_saveas = wx.NewId()
        id_close = wx.NewId()
        id_quit = wx.NewId()
        wxglade_tmp_menu.Append(id_load, "&Load Xml File", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(id_reload, "&Re-load the Xml File", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(id_save, "&Save Xml File", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(id_saveas, "Save &As Xml File", "", wx.ITEM_NORMAL)
        
        #MARCHE PAS wxglade_tmp_menu.Append(id_reloadini, "&Reload INI File", "", wx.ITEM_NORMAL)
        #wxglade_tmp_menu.Append(id_close, "&Close", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(id_quit, "&Quit", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.AppendSeparator()
        self.frame_1_menubar.Append(wxglade_tmp_menu, "&File")
        self.wxglade_file_menu = wxglade_tmp_menu
        self.cntRecentDoc = 0
        
        wxglade_tmp_menu = wx.Menu()
        id_help = wx.NewId()
        id_about = wx.NewId()
        wxglade_tmp_menu.Append(id_help, "&Content", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(id_about, "&About", "", wx.ITEM_NORMAL)
        self.frame_1_menubar.Append(wxglade_tmp_menu, "&Help")
        # Menu Bar end

        # end wxGlade
        self.loadConfig(sConfigFile)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_MENU, self.OnMenu_LoadXML, id=id_load)
        self.Bind(wx.EVT_MENU, self.OnMenu_ReLoadXML, id=id_reload)
        self.Bind(wx.EVT_MENU, self.OnMenu_ReloadINI, id=id_reloadini)
        self.Bind(wx.EVT_MENU, self.OnMenu_SaveXML, id=id_save)
        self.Bind(wx.EVT_MENU, self.OnMenu_SaveAsXML, id=id_saveas)
        
        self.Bind(wx.EVT_MENU, self.OnMenu_Quit, id=id_quit)
        self.Bind(wx.EVT_MENU, self.OnMenu_Help, id=id_help)
        self.Bind(wx.EVT_MENU, self.OnMenu_About, id=id_about)
        
        self.Bind(wx.EVT_TEXT_ENTER, self.OnToolbar_ChangePage, self.tc_pagesel)
        self.Bind(wx.EVT_TOOL, self.OnToolbar_BackwardPage, id=ID_BACKWARD)
        self.Bind(wx.EVT_TOOL, self.OnToolbar_ForwardPage, id=ID_FORWARD)
        self.Bind(wx.EVT_TOOL, self.OnToolbar_JumpBack, id=ID_JUMPBACK)
        self.stackJump = []
        
        self.bindConfigWidget()
        
        self.current_page_node = None
        self.path = None
        self.doc = None
        self.current_fonts = None
        
        self.bModified = False

    def loadConfig(self, sConfigFile):
        self.sConfigFile = sConfigFile
        self.config = Config(sConfigFile)
        
        #now the checkboxes for the decoration types
        self.dChekBox2Deco = {} #checkbox -> deco
        self.dBut2Deco = {}     #button -> deco
        self.ltCheckboxObjects = []
        for deco in self.config.getDecoList():
            if deco.isSeparator():  #a separator in the toolbar
                chkbx, butPrev, butNext = None, None, None
            else:
                chkbx = wx.CheckBox(self, -1, deco.getSurname())
                chkbx.SetToolTipString(deco.getMainXPath())
                #chkbx.SetBackgroundColour("RED")
                if deco.isEnabled():
                    chkbx.SetValue(1)
                else:
                    chkbx.SetValue(0)
                self.dChekBox2Deco[chkbx] = deco
                
                #also include two buttons for each
                butPrev = wx.NewId()
                butPrev = wx.Button(self, butPrev, "<", size=(14,14), style=wx.BU_EXACTFIT)
                self.dBut2Deco[butPrev] = deco
                butNext = wx.NewId()
                butNext = wx.Button(self, butNext, ">", size=(14,14), style=wx.BU_EXACTFIT)
                self.dBut2Deco[butNext] = deco
            
            self.ltCheckboxObjects.append((chkbx, butPrev, butNext))
        
    def bindConfigWidget(self):
        for chkbx, butPrev, butNext in self.ltCheckboxObjects:
            if chkbx == None:
                assert butPrev == None and butNext == None, "SW INTERNAL ERROR: bindConfigWidget: %s"%( (butPrev, butNext))
            else:
                self.Bind(wx.EVT_CHECKBOX, self.cbkDecoCheckBox, chkbx)
                self.Bind(wx.EVT_BUTTON, self.cbkDecoPrev, butPrev)
                self.Bind(wx.EVT_BUTTON, self.cbkDecoNext, butNext)

        
    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        self.SetTitle("Xml Visualizer")
#        self.SetSize((1000, 800))
#        self.SetSize((1500, 1200))
#        self.SetSize((800, 900))
        self.SetSize((1100, 1200))
        self.SetBackgroundColour("light blue")
        #self.SetBackgroundColour(" jhfg ksd")  #default color.... :-)

        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
        
        self.sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.sizer_3, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        sizer_2.Add(self.wysi, 1, wx.EXPAND, 0)
        
        self.__do_layout_sizer3()
        
#        sizer_1.Add(self.wysi, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_1)
        self.Layout()
        # end wxGlade

    def __do_layout_sizer3(self):
        #self.lDecoSizer = []
#         self.sizer_3.AddSpacer( (20,20))
        self.sizer_3.AddSpacer( 20)

        for chkbx, butPrev, butNext in self.ltCheckboxObjects:
            sz = wx.BoxSizer(wx.HORIZONTAL)
            self.sizer_3.Add(sz, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
            if chkbx == None:
                #separator in the toolbar
                pass
                #okself.sizer_3.AddSpacer( (20,20))
                #self.sizer_3.Add( wx.StaticLine() )
                sz.Add( wx.StaticLine(self,size=(100, 2)), 0, wx.ALL|wx.CENTER|wx.EXPAND , 1 )
                #sz.Add( wx.StaticLine(self, size=(100, 3)), flag=wx.LI_HORIZONTAL|wx.SOLID )
            else:
#                sz = wx.BoxSizer(wx.HORIZONTAL)
#                self.sizer_3.Add(sz, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
                sz.Add(chkbx, 0, wx.ALL|wx.ADJUST_MINSIZE, 2)
                sz.Add(butPrev, 0, wx.ALL|wx.ADJUST_MINSIZE, 2)
                sz.Add(butNext, 0, wx.ALL|wx.ADJUST_MINSIZE, 2)
            #self.lDecoSizer.append(sz)
        
    #-------------------
    def OnMenu_LoadXML(self, event): # wxGlade: MyFrame.<event_handler>
        global gSELF, gdicRecentDoc
        try:
            curdir = os.path.dirname(self.path)
        except:
            curdir = self.config.working_dir
        #we also tolerate gzipped xml
        #wildcard = "Xml Document (*.xml; *.xml.gz)|*.xml;*.xml.gz"
        wildcard = "All files (*.*)|*.*|XML (*.xml; *.xml.gz)|*.xml;*.xml.gz|PageXml (*.pxml; *.mpxml)|*.pxml; *.mpxml"
        dlg = wx.FileDialog(self, message="Choose a model", 
                            wildcard=wildcard, defaultDir=curdir,
                            style=wx.FD_OPEN | wx.FD_CHANGE_DIR)
        dlg.CenterOnScreen()
        val = dlg.ShowModal()
        if val == wx.ID_OK:
            path = dlg.GetPath()
            if self.loadXML(path):
                #---deal with recent documents:
                if path not in gdicRecentDoc.values():
                    self.cntRecentDoc += 1
                    gdicRecentDoc[self.cntRecentDoc] = path
                    gSELF = self
                    id_doc = wx.NewId()
                    self.wxglade_file_menu.Append(id_doc, path, "", wx.ITEM_NORMAL)
                    #generate a callback function
                    sCode = """
def OnMenu_LoadRecent%d(event):
    global gSELF, gdicRecentDoc 
    try:
        gSELF.loadXML(gdicRecentDoc[%d])
    except KeyError: 
        pass
""" % (self.cntRecentDoc, self.cntRecentDoc) #we use a global dictionarry because of / and \ pbs...
                    #print sCode
                    exec sCode
                    fun = eval("OnMenu_LoadRecent%d"%self.cntRecentDoc)
                    #print fun
                    self.Bind(wx.EVT_MENU, fun, id=id_doc)
        dlg.Destroy()
        
    def OnMenu_ReLoadXML(self, event): # wxGlade: MyFrame.<event_handler>
        self.loadXML(self.path)

    def OnMenu_ReloadINI(self, event): # HACK!!!!
        #remove the widget of the decos
        for sz in self.lDecoSizer:
            self.sizer_3.Remove(sz)
        self.__do_layout()
        
        self.loadConfig(self.sConfigFile)
        self.config.setXPathContext( self.doc.getXPCtxt() )
        self.bindConfigWidget()
        self.__do_layout()
        self.Layout()
        self.display_page()

        
    def OnMenu_SaveXML(self, event):
        ret = self.doc.saveXML(self.doc.getFilename())
        if ret: self.bModified = False
        
    def OnMenu_SaveAsXML(self, event):
        curdir = os.path.dirname(self.doc.getFilename())
        if not curdir: curdir = os.getcwd()
        wildcard = "Xml Document (*.xml)|*.xml"
        dlg = wx.FileDialog(self, message="Choose a file", 
                            wildcard=wildcard, defaultDir=curdir,
                            style=wx.OPEN | wx.CHANGE_DIR)
        dlg.CenterOnScreen()
        val = dlg.ShowModal()
        if val == wx.ID_OK:
            ret = self.doc.saveXML(dlg.GetPath())
        dlg.Destroy()
        if ret: self.bModified = False
        
        
    def OnMenu_Quit(self, event):
        if self.bModified:
            dlg = wx.MessageDialog(self, message=sConfirmQuit, style = wx.OK | wx.CANCEL)
            val = dlg.ShowModal()
            if val != wx.ID_OK: return
        self.Destroy()
    
    #-------------------
    def OnMenu_Help(self, event):
        dlg = wx.MessageDialog(self, message=sHelp, 
                            caption="wxvisu help",
                            style=wx.ICON_INFORMATION)
        dlg.CenterOnScreen()
        val = dlg.ShowModal()
        dlg.Destroy()
        
    def OnMenu_About(self, event):
        dlg = wx.MessageDialog(self, message=sAbout, 
                            caption="About wxvisu",
                            style=wx.ICON_INFORMATION)
        dlg.CenterOnScreen()
        val = dlg.ShowModal()
        dlg.Destroy()

    #-------------------
        
    def OnCanvas_Enter(self, obj):
#        txt = self.doc.obj_n[obj].nsProp('segmantic_type', 'http://www.xrce.xerox.com/ML')
#        if not txt:
#            txt = self.doc.obj_n[obj].name
        txt = self.doc.obj_n[obj].serialize()
        txt = unicode(txt, sEncoding)
        tip = wx.TipWindow(self, txt)
        wx.FutureCall(3000, tip.Close)      
        
    def OnToolbar_BackwardPage(self, evt):
        """Click on the backward button of the toolbar of the canvas"""
        if self.doc:
            self.display_page( self.doc.getPrevPageIndex() )
    
    def OnToolbar_ForwardPage(self, evt):
        """Click on the forward button of the toolbar of the canvas"""
        if self.doc: 
            self.display_page( self.doc.getNextPageIndex() )
    
    
    def OnToolbar_Jump(self, evt, index, (x,y,w,h)):
        """Click on the jump back button of the toolbar of the canvas"""
        if self.doc: 
            #TODO!
            if index:
                self.stackJump.append( self.doc.getDisplayedIndex() )
                if x:
                    self.display_page( index, (x,y,w,h))
                else:
                    self.display_page( index )  #precise at the page level, not more.

    def OnToolbar_JumpBack(self, evt):
        """Click on the jump back button of the toolbar of the canvas"""
        if self.doc and self.stackJump: 
            self.display_page( self.stackJump.pop() )

    def OnToolbar_ChangePage(self, evt):
        """Modify the page number in the text control of the toolbar of the
        canvas"""
        if self.doc:
            new_page = evt.GetString()
            # to deal with "n (n/N)"  - hack for lazy people
            if ' ' in new_page:
                new_page = new_page.split()[0]
            if new_page:
                try:
                    if new_page[0] == "@":
                        #ok, we use the @number value
                        i = self.doc.getPageIndexByNumber(new_page[1:])
                    else:
                        i = (int(new_page)-1) % self.doc.getPageCount()
                    self.display_page(i)
                except KeyError:
                    print "Unknown page: %s"%new_page
                except ValueError:
                    print "Invalid page number: %s"%new_page
                
    def OnCanvas_RightMouse(self, obj):
        """Click on a widget in the canvas with the right mouse"""
        menu = wx.Menu() 
        # get the id of the corresponding node
        self.n = self.doc.obj_n[obj]
        tree_id = wx.NewId()     
        self.Bind(wx.EVT_MENU, self.OnPopup_RightCanvas, id=tree_id)
        menu.Append(tree_id, "XPath lab")
        c = self.wysi.Canvas
        pos = (c.PixelToWorld(obj.XY[0]),
               c.PixelToWorld(c.GetSize()[1]-obj.XY[1]))
        self.PopupMenu(menu, pos)
        menu.Destroy()
        
    def OnCanvas_LeftMouse(self, obj):
        txt = etree.tostring(self.doc.obj_n[obj])
        txt = unicode(txt, sEncoding)
        tip = wx.TipWindow(self, txt)
        wx.FutureCall(30000, tip.Close)      

    def OnCanvas_LeftMouseDecoAction(self, obj):
        """
        for decorations that support an action
        """
        nd = self.doc.obj_n[obj]
        deco = self.doc.obj_deco[obj]
        #now let the decoration perform its action
        ret = deco.act(obj, nd)
        if type(ret) == types.StringType:
            txt = ret 
            tip = wx.TipWindow(self, txt)
            wx.FutureCall(1000, tip.Close)
            self.display_page(self.doc.getDisplayedIndex())    
            self.bModified = True  
        elif type(ret) == types.TupleType:
            pagenum, x,y,w,h = ret
            self.OnToolbar_Jump(None, pagenum, (x,y,w,h))
            
            
    def OnPopup_RightCanvas(self, event):
        """Right click on a widget on the canvas"""
#        xpl.showXML()
        pn = max(1, self.doc.displayed + 1)
        xpl = xpathlab.MainFrame(None, -1, "")
        xpl.Show()
        xpl.setRootNode(self.current_page_node)
        sid = self.n.prop("id")
        if sid:
            #ok there is an id, let's use it
            sExpr = './/*[@id="%s"]'%sid
            xpl.showXPath(sExpr)
            xpl.doXPath(sExpr)
        else:
            xpl.showXML()
        xpl.setStatus("Page %d"% pn)
        #win = FrameTree(self, self.n)
        #win.Show()
            
    #-------------------
    def cbkDecoCheckBox(self, event): # wxGlade: MyFrame.<event_handler>
        """enable or disbale a decoration type"""
        deco = self.dChekBox2Deco[ event.GetEventObject() ]
        deco.setEnabled(event.IsChecked())
        if self.doc:
            d = self.doc.displayed
            self.display_page(d)
    
    def cbkDecoNext(self, event):
        """jump on the next page that has such a decoration"""
        deco = self.dBut2Deco[ event.GetEventObject() ]
        if self.doc:
            i = self.doc.getDisplayedIndex()
            xpDeco = deco.getMainXPath()
#            xpExpr = 'normalize-space(./following-sibling::%s[%s][1]/@number)' %(self.config.page_tag, xpDeco)
#            n = self.doc.getCurrentPageNode()
#            sNum = self.doc.xpathEval(xpExpr, n)
#            if sNum:
#                newI = int(self.doc.getPageIndexByNumber(sNum))
#                self.display_page(newI)
            xpExpr = 'count(./following::%s[%s][1]/preceding::%s)' %(self.config.page_tag, xpDeco, self.config.page_tag)
            n = self.doc.getCurrentPageNode()
            sNum = self.doc.xpathEval(xpExpr, n)
            if sNum:
                newI = int(sNum)
                self.display_page(newI)
    
    def cbkDecoPrev(self, event):
        deco = self.dBut2Deco[ event.GetEventObject() ]
        if self.doc:
            i = self.doc.getDisplayedIndex()
            xpDeco = deco.getMainXPath()
#            xpExpr = 'normalize-space(./preceding-sibling::%s[%s][1]/@number)' %(self.config.page_tag, xpDeco)
#            n = self.doc.getCurrentPageNode()
#            sNum = self.doc.xpathEval(xpExpr, n)
#            if sNum:
#                newI = int(self.doc.getPageIndexByNumber(sNum))
#                self.display_page(newI)
            xpExpr = 'count(./preceding::%s[%s][1]/preceding::%s)' %(self.config.page_tag, xpDeco, self.config.page_tag)
            n = self.doc.getCurrentPageNode()
            sNum = self.doc.xpathEval(xpExpr, n)
            if sNum != "":
                newI = int(sNum)
                self.display_page(newI)    
                
    #-------------------
    def loadXML(self, path):
        if self.doc: #release the memory!
            self.doc.free()
        try:
            self.path = path
            self.doc = Document(self.path, self.config)
            #now let's try to be clever if no page get loaded
            self.current_fonts = {}
            self.display_page()
            self.SetTitle('XML Visualizer - %s' % path)
        
        except Exception, e:
            self.path = self.doc = None
            print "ERROR opening %s; %s"%(path, e)
            traceback.print_exc(file=sys.stdout)
            dlg = wx.MessageDialog(self, message="ERROR opening %s: %s"%(path, e)
                                , caption="Error", style=wx.ICON_ERROR)
            dlg.CenterOnScreen()
            val = dlg.ShowModal()
            dlg.Destroy()
            return False
        return True    
    
    def display_page(self, i=0, (x,y,w,h)=(None, None, None, None)):
        """Display the page in the interface. If no argument then page=0, we 
        display the first page of the document.
        @param page: the page to display, the index does not correspond to the
        true number in the document but to the position in the list of all pages
        @type page: int.
        """        
        c = self.wysi.Canvas
        c.ClearAll()
        self.doc.new_page(i)
        
        try:
            self.current_page_node = self.doc.getPageByIndex(i)
        except IndexError:
            dlg = wx.MessageDialog(self, message="This XML file has no such page (%dth '%s' element) Try passing another .ini file as application parameter."%(i+1, self.config.page_tag), 
                            caption="Error",
                            style=wx.ICON_ERROR)
            dlg.CenterOnScreen()
            val = dlg.ShowModal()
            dlg.Destroy()
            return
#         s = "%s (%d/%d)" % (self.doc.getPageNumber(i), i+1, self.doc.getPageCount())
        #self.tc_pagesel.SetValue(self.doc.getPageNumber(i))
        self.tc_pagetot.SetValue("%d of %d" % (i+1, self.doc.getPageCount()))
        
        # The page
        s = self.doc.xpathEval(self.config.page_tag_attr_width, self.current_page_node )
        if type(s) == types.ListType: 
            try:
                s = s[0].text
            except AttributeError:
                s = s[0]
        w_page = int(float(s))
        s = self.doc.xpathEval(self.config.page_tag_attr_height, self.current_page_node )
        if type(s) == types.ListType: 
            try:
                s = s[0].text
            except AttributeError:
                s = s[0]            
        h_page = int(float(s))
#        w_page = int(float(self.current_page_node.prop(self.config.page_tag_attr_width)))

        
        page_rect = c.AddRectangle((0, -h_page), (w_page, h_page), 
                                 LineColor=self.config.page_border_color,
                                 FillColor=self.config.page_background_color,
                                 FillStyle="Solid") 
        self.doc.obj_n[page_rect] = self.current_page_node
        page_rect.Bind(FloatCanvas.EVT_FC_RIGHT_DOWN, self.OnCanvas_RightMouse)
        page_rect.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.OnCanvas_LeftMouse)
#        page_rect.Bind(FloatCanvas.EVT_FC_ENTER_OBJECT, self.OnCanvas_Enter) 
 
        #Now let's decorate the page according to the configuration
        for deco in self.config.getDecoList():
            if deco.isSeparator(): continue
            if deco.isEnabled():
                ln = self.doc.xpathEval( deco.getMainXPath(), self.current_page_node )
                deco.beginPage(self.current_page_node)
                
                for n in ln:
                    #TODO: deal with that!!!
                    inc = 1
                    lo = deco.draw(c, n)
                    
                    #let's bind on the first object of the list
                    if lo:
                        obj = lo[0]
                        self.doc.obj_n[obj] = n
                        obj.Bind(FloatCanvas.EVT_FC_RIGHT_DOWN, self.OnCanvas_RightMouse)
                        if deco.isActionable():
                            self.doc.obj_deco[obj] = deco
                            obj.Bind(FloatCanvas.EVT_FC_LEFT_DOWN,     self.OnCanvas_LeftMouseDecoAction)
                        else:
                            obj.Bind(FloatCanvas.EVT_FC_LEFT_DOWN,     self.OnCanvas_LeftMouse)
    #                    obj.Bind(FloatCanvas.EVT_FC_ENTER_OBJECT, self.OnCanvas_Enter) 
                deco.endPage(self.current_page_node)
                
        #eventually, highlight a bounding box
        if x != None:
            obj = c.AddRectangle((x, -y), (w, -h), LineWidth=4,
                                                     LineColor="GOLD",
                                                     FillColor="#FFFFFF",
                                                     FillStyle="Transparent")
            wx.FutureCall(1000, obj.Hide)
            #print dir(obj)
            #print (x,y,w,h)

        #self.tc_pagesel.Clear()

        c.ZoomToBB() 
        
