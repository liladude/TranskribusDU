# -*- coding: utf-8 -*-

"""
    Example DU task for JSON Invoices
    
    Copyright Naver(C) 2017 H. Déjean, JL Meunier

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
import sys, os

try: #to ease the use without proper Python installation
    import TranskribusDU_version
except ImportError:
    sys.path.append( os.path.dirname(os.path.dirname( os.path.abspath(sys.argv[0]) )) )
    import TranskribusDU_version

import json, codecs
from common.chrono import chronoOn, chronoOff
from common.trace import traceln
from tasks import _checkFindColDir, _exit

from crf.Graph_JSON import Graph_JSON
from crf.NodeType_JSONInvoice   import NodeType_JSONInvoice
from DU_CRF_Task import DU_CRF_Task
#from crf.FeatureDefinition_PageXml_std_noText import FeatureDefinition_PageXml_StandardOnes_noText
from crf.FeatureDefinition_JSON_Invoice_v1 import FeatureDefinition_JSON_Invoice_v1

 
class DU_JSON_Invoice_v1(DU_CRF_Task):
    """
    We will do a CRF model for a DU task
    , with the below labels 
    """
    sXmlFilenamePattern = "*.json"
    
    #sLabeledXmlFilenamePattern = "*.a_mpxml"
    sLabeledXmlFilenamePattern = "*.json"

    sLabeledXmlFilenameEXT = ".json"


    #=== CONFIGURATION ====================================================================
    def __init__(self, sModelName, sModelDir, sComment=None, C=None, tol=None, njobs=None, max_iter=None, inference_cache=None): 

        # ===============================================================================================================
        classifications = ['NUMBER',
                   'DATE',
                   'ORDER_DATE',
                   'PAYMENT_DUE_DATE',
                   'COST_CENTER',
                   'CURRENCY_CODE',
                   'RECEIVER_CUSTOMER_ASSIGNED_ACCOUNT_ID',
                   'BUYERS_ORDER_ID',
                   'SBS_ORG_CODE',
                   'RECEIVER_CONTACT_ID',
                   'RECEIVER_PARTY_NAME',
                   'SENDER_PARTY_NAME',
                   'RECEIVER_CITY_NAME',
                   'SENDER_CITY_NAME',
                   'RECEIVER_STREET_NAME',
                   'SENDER_STREET_NAME',
                   'RECEIVER_POSTAL_ZONE',
                   'SENDER_POSTAL_ZONE',
                   'RECEIVER_LEGAL_COMPANY_ID',
                   'SENDER_LEGAL_COMPANY_ID',
                   'TOTAL',
                   'TOTAL_LINE_AMOUNT',
                   'TOTAL_TAX_AMOUNT',
                   'SUB_TOTAL_TAX_CATEGORY_PERCENT',
                   'LINE_EXTENSION_AMOUNT',
                   'LINE_UNIT_PRICE',
                   'LINE_QUANTITY',
                   'LINE_ITEM_DESCRIPTION',
                   'LINE_SELLERS_ITEM_ID',
                   'LINE_UNIT_CODE',
                   'LINE_ORDER_LINE_REFERENCE_ID',
                   'LINE_BUYERS_ORDER_ID']

        positions = ['BEGINNING', 'INSIDE']
        labels = ['OUTSIDE']
        
        for c in classifications:
            for p in positions:
                labels.append(p + ' ' + c)
        
        #labels_dict = {v: i for i, v in enumerate(labels)}

        #lLabels = ['RB', 'RI', 'RE', 'RS','RO']
        lLabels = labels
        
        lIgnoredLabels = None
        
        nbClass = len(lLabels)
        
        """
        if you play with a toy collection, which does not have all expected classes, you can reduce those.
        """
        #HACK
        if False:
            lActuallySeen = ['i_OUTSIDE', 'i_BEGINNING NUMBER',  'i_BEGINNING DATE']
            lActuallySeen_index = [lLabels.index(s[2:]) for s in lActuallySeen]
            if lActuallySeen:
                print "REDUCING THE CLASSES TO THOSE SEEN IN TRAINING"
                lIgnoredLabels  = [lLabels[i] for i in range(len(lLabels)) if i not in lActuallySeen_index]
                lLabels         = [lLabels[i] for i in lActuallySeen_index ]
                print len(lLabels)          , lLabels
                print len(lIgnoredLabels)   , lIgnoredLabels
                nbClass = len(lLabels) + 1  #because the ignored labels will become OTHER
        
        #DEFINING THE CLASS OF GRAPH WE USE
        DU_GRAPH = Graph_JSON
        nt = NodeType_JSONInvoice("i"                   #some short prefix because labels below are prefixed with it
                              , lLabels
                              , lIgnoredLabels
                              , False    #no label means OTHER
                              , BBoxDeltaFun=None   #lambda v: max(v * 0.066, min(5, v/3))  #we reduce overlap in this way
                              
                              )
        # ntA = NodeType_PageXml_type_woText("abp"                   #some short prefix because labels below are prefixed with it
        #                       , lLabels
        #                       , lIgnoredLabels
        #                       , False    #no label means OTHER
        #                       )
        
#         nt.setXpathExpr( (".//pc:TextLine"        #how to find the nodes
#                           , "./pc:TextEquiv")       #how to get their text
#                        )
        
        # ntA.setXpathExpr( (".//pc:TextLine | .//pc:TextRegion"        #how to find the nodes
        #                   , "./pc:TextEquiv")       #how to get their text
        #                 )
        
        DU_GRAPH.addNodeType(nt)
        
        # ===============================================================================================================

        
        DU_CRF_Task.__init__(self
                     , sModelName, sModelDir
                     , DU_GRAPH
                     , dFeatureConfig = {  
                              'n_tfidf_node':None
                            , 't_ngrams_node':(2,4)
                            , 'b_tfidf_node_lc':None
                            , 'n_tfidf_edge':None
                            , 't_ngrams_edge':(2,4)
                            , 'b_tfidf_edge_lc':None
                         }
                     , dLearnerConfig = {
                                   'C'                : .1   if C               is None else C
                                 , 'njobs'            : 8    if njobs           is None else njobs
                                 , 'inference_cache'  : 50   if inference_cache is None else inference_cache
                                 #, 'tol'              : .1
                                 , 'tol'              : .05  if tol             is None else tol
                                 , 'save_every'       : 50     #save every 50 iterations,for warm start
                                 , 'max_iter'         : 1000 if max_iter        is None else max_iter
                         }
                     , sComment=sComment
                     #,cFeatureDefinition=FeatureDefinition_PageXml_StandardOnes_noText
                     ,cFeatureDefinition=FeatureDefinition_JSON_Invoice_v1
                     )
        
        #self.setNbClass(3)     #so that we check if all classes are represented in the training set
        
        self.bsln_mdl = self.addBaseline_LogisticRegression()    #use a LR model trained by GridSearch as baseline
    #=== END OF CONFIGURATION =============================================================

  
    def predict(self, lsColDir, docid=None):
        """
        Return the list of produced files
        """
        self.traceln("-"*50)
        self.traceln("Predicting for collection(s):", lsColDir)
        self.traceln("-"*50)

        if not self._mdl: raise Exception("The model must be loaded beforehand!")
        
        #list files
        if docid is None:
            _     , lFilename = self.listMaxTimestampFile(lsColDir, self.sXmlFilenamePattern)
        # predict for this file only
        else:
            try: 
                lFilename = [os.path.abspath(os.path.join(lsColDir[0], 'col',docid+".json"  ))]
            except IndexError:raise Exception("a collection directory must be provided!")
            
        
        DU_GraphClass = self.getGraphClass()

        lPageConstraint = DU_GraphClass.getPageConstraint()
        if lPageConstraint: 
            for dat in lPageConstraint: self.traceln("\t\t%s"%str(dat))
        
        chronoOn("predict")
        self.traceln("- loading collection as graphs, and processing each in turn. (%d files)"%len(lFilename))
        du_postfix = "_du.json"
        lsOutputFilename = []
        for sFilename in lFilename:
            if sFilename.endswith(du_postfix): continue #:)
            chronoOn("predict_1")
            lg = DU_GraphClass.loadGraphs([sFilename], bDetach=False, bLabelled=False, iVerbose=1)
            #normally, we get one graph per file, but in case we load one graph per page, for instance, we have a list
            
            if lg:
                assert len(lg) == 1, "Careful this code becomes bad when multiple graphs per file"
                for g in lg:
                    doc = g.doc
                    if lPageConstraint:
                        self.traceln("\t- prediction with logical constraints: %s"%sFilename)
                    else:
                        self.traceln("\t- prediction : %s"%sFilename)
                    Y = self._mdl.predict(g)
                    
                    JsonResult = g.setDomLabels(Y)
                    del Y
                del lg
                
                sDUFilename = sFilename[:-len(".json")]+du_postfix
                
                with codecs.open(sDUFilename, "wb",'utf-8') as fd: 
                    self.doc = json.dump(JsonResult, fd, sort_keys=True, indent=2)
                lsOutputFilename.append(sDUFilename)
            else:
                self.traceln("\t- no prediction to do for: %s"%sFilename)
                
            self.traceln("\t done [%.2fs]"%chronoOff("predict_1"))
        self.traceln(" done [%.2fs]"%chronoOff("predict"))

        return lsOutputFilename
              
    
if __name__ == "__main__":

    version = "v.01"
    usage, description, parser = DU_CRF_Task.getBasicTrnTstRunOptionParser(sys.argv[0], version)
#     parser.add_option("--annotate", dest='bAnnotate',  action="store_true",default=False,  help="Annotate the textlines with BIES labels")    
    # --- 
    #parse the command line
    (options, args) = parser.parse_args()
    
    # --- 
    try:
        sModelDir, sModelName = args
    except Exception as e:
        traceln("Specify a model folder and a model name!")
        _exit(usage, 1, e)
        
    doer = DU_JSON_Invoice_v1(sModelName, sModelDir,
                      C                 = options.crf_C,
                      tol               = options.crf_tol,
                      njobs             = options.crf_njobs,
                      max_iter          = options.crf_max_iter,
                      inference_cache   = options.crf_inference_cache)
    
    
    
    if options.rm:
        doer.rm()
        sys.exit(0)

    lTrn, lTst, lRun, lFold = [_checkFindColDir(lsDir) for lsDir in [options.lTrn, options.lTst, options.lRun, options.lFold]] 
#     if options.bAnnotate:
#         doer.annotateDocument(lTrn)
#         traceln('annotation done')    
#         sys.exit(0)
    
    
    traceln("- classes: ", doer.getGraphClass().getLabelNameList())
    
    ## use. a_mpxml files
    doer.sXmlFilenamePattern = doer.sLabeledXmlFilenamePattern


    if options.iFoldInitNum or options.iFoldRunNum or options.bFoldFinish:
        if options.iFoldInitNum:
            """
            initialization of a cross-validation
            """
            splitter, ts_trn, lFilename_trn = doer._nfold_Init(lFold, options.iFoldInitNum, test_size=0.25, random_state=None, bStoreOnDisk=True)
        elif options.iFoldRunNum:
            """
            Run one fold
            """
            oReport = doer._nfold_RunFoldFromDisk(options.iFoldRunNum, options.warm, options.pkl)
            traceln(oReport)
        elif options.bFoldFinish:
            tstReport = doer._nfold_Finish()
            traceln(tstReport)
        else:
            assert False, "Internal error"    
        #no more processing!!
        exit(0)
        #-------------------
        
    if lFold:
        loTstRpt = doer.nfold_Eval(lFold, 3, .25, None, options.pkl)
        import crf.Model
        sReportPickleFilename = os.path.join(sModelDir, sModelName + "__report.txt")
        traceln("Results are in %s"%sReportPickleFilename)
        crf.Model.Model.gzip_cPickle_dump(sReportPickleFilename, loTstRpt)
    elif lTrn:
        doer.train_save_test(lTrn, lTst, options.warm, options.pkl)
        try:    traceln("Baseline best estimator: %s"%doer.bsln_mdl.best_params_)   #for GridSearch
        except: pass
        traceln(" --- CRF Model ---")
        traceln(doer.getModel().getModelInfo())
    elif lTst:
        doer.load()
        tstReport = doer.test(lTst)
        traceln(tstReport)
    
    if lRun:
        doer.load()
        lsOutputFilename = doer.predict(lRun)
        traceln("Done, see in:\n  %s"%lsOutputFilename)
    
