# -*- coding: utf-8 -*-

"""
    Example DU task for ABP Table: separator categorization
        NOTE: graph construction is certainly with flaws : lines can intersect and then no relation between them.
    
    
    Copyright Naver Labs Europe (C) 2018 H. Déjean

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
from __future__ import absolute_import
from __future__ import  print_function
from __future__ import unicode_literals

import sys, os

try: #to ease the use without proper Python installation
    import TranskribusDU_version
except ImportError:
    sys.path.append( os.path.dirname(os.path.dirname( os.path.abspath(sys.argv[0]) )) )
    import TranskribusDU_version

from common.trace import traceln
from tasks import _checkFindColDir, _exit

from crf.Graph_Multi_SinglePageXml import Graph_MultiSinglePageXml
from crf.NodeType_PageXml   import NodeType_PageXml_type_woText
from tasks.DU_CRF_Task import DU_CRF_Task

#from crf.FeatureDefinition_PageXml_std_noText import FeatureDefinition_PageXml_StandardOnes_noText
from crf.FeatureDefinition_PageXml_std_noText_v3 import FeatureDefinition_PageXml_StandardOnes_noText_v3

import json

 
class DU_ABPTable(DU_CRF_Task):
    """
    We will do a CRF model for a DU task
    , with the below labels 
    """
    sXmlFilenamePattern = "*.mpxml"
    
    #sLabeledXmlFilenamePattern = "*.a_mpxml"
    sLabeledXmlFilenamePattern = "*.mpxml"

    sLabeledXmlFilenameEXT = ".mpxml"


    #=== CONFIGURATION ====================================================================
    @classmethod
    def getConfiguredGraphClass(cls):
        """
        In this class method, we must return a configured graph class
        """
        lLabels = ['O','I']
        
        lIgnoredLabels = None
        
        """
        if you play with a toy collection, which does not have all expected classes, you can reduce those.
        """
        
        lActuallySeen = None
        if lActuallySeen:
            print( "REDUCING THE CLASSES TO THOSE SEEN IN TRAINING")
            lIgnoredLabels  = [lLabels[i] for i in range(len(lLabels)) if i not in lActuallySeen]
            lLabels         = [lLabels[i] for i in lActuallySeen ]
            print( len(lLabels)          , lLabels)
            print( len(lIgnoredLabels)   , lIgnoredLabels)
        
        #DEFINING THE CLASS OF GRAPH WE USE
        DU_GRAPH = Graph_MultiSinglePageXml
        nt = NodeType_PageXml_type_woText("abp"                   #some short prefix because labels below are prefixed with it
                              , lLabels
                              , lIgnoredLabels
                              , False    #no label means OTHER
                              , BBoxDeltaFun=lambda v: max(v * 0.066, min(5, v/3))  #we reduce overlap in this way
                              )
        nt.setLabelAttribute("DU_sep")
        
        # ntA = NodeType_PageXml_type_woText("abp"                   #some short prefix because labels below are prefixed with it
        #                       , lLabels
        #                       , lIgnoredLabels
        #                       , False    #no label means OTHER
        #                       )
        
        nt.setXpathExpr( (".//pc:SeparatorRegion"        #how to find the nodes
                          , "./pc:TextEquiv")       #how to get their text
                       )
        
        # ntA.setXpathExpr( (".//pc:TextLine | .//pc:TextRegion"        #how to find the nodes
        #                   , "./pc:TextEquiv")       #how to get their text
        #                 )
        DU_GRAPH.addNodeType(nt)
        
        return DU_GRAPH
        
    def __init__(self, sModelName, sModelDir, sComment=None, C=None, tol=None, njobs=None, max_iter=None, inference_cache=None): 

        if sComment is None: sComment = sModelName
        DU_CRF_Task.__init__(self
                     , sModelName, sModelDir
                     , dFeatureConfig = {  }
                     , dLearnerConfig = {
                                   'C'                : .1   if C               is None else C
                                 , 'njobs'            : 2    if njobs           is None else njobs
                                 , 'inference_cache'  : 50   if inference_cache is None else inference_cache
                                 #, 'tol'              : .1
                                 , 'tol'              : .05  if tol             is None else tol
                                 , 'save_every'       : 50     #save every 50 iterations,for warm start
                                 , 'max_iter'         : 200 if max_iter        is None else max_iter
                         }
                     , sComment= sComment
                     #,cFeatureDefinition=FeatureDefinition_PageXml_StandardOnes_noText
                     ,cFeatureDefinition=FeatureDefinition_PageXml_StandardOnes_noText_v3
                     )
        
        #self.setNbClass(3)     #so that we check if all classes are represented in the training set
        
        if options.bBaseline:
            self.bsln_mdl = self.addBaseline_LogisticRegression()    #use a LR model trained by GridSearch as baseline
    #=== END OF CONFIGURATION =============================================================

  
    def predict(self, lsColDir):
        """
        Return the list of produced files
        """
        self.sXmlFilenamePattern = "*.mpxml"
        return DU_CRF_Task.predict(self, lsColDir)
        
    def runForExternalMLMethod(self, lsColDir, storeX, applyY, bRevertEdges=False):
        """
        Return the list of produced files
        """
        self.sXmlFilenamePattern = "*.mpxml"
        return DU_CRF_Task.runForExternalMLMethod(self, lsColDir, storeX, applyY, bRevertEdges)



try:
    from tasks.DU_ECN_Task import DU_ECN_Task
    import gcn.DU_Model_ECN
    class DU_ABPTable_ECN(DU_ECN_Task):
            """
            ECN Models
            """
            
            sMetadata_Creator = "NLE Document Understanding ECN"
            sXmlFilenamePattern = "*.mpxml"

            # sLabeledXmlFilenamePattern = "*.a_mpxml"
            sLabeledXmlFilenamePattern = "*.mpxml"

            sLabeledXmlFilenameEXT = ".mpxml"

            dLearnerConfig = {'nb_iter': 50,
                              'lr': 0.001,
                              'num_layers': 3,
                              'nconv_edge': 10,
                              'stack_convolutions': True,
                              'node_indim': -1,
                              'mu': 0.0,
                              'dropout_rate_edge': 0.0,
                              'dropout_rate_edge_feat': 0.0,
                              'dropout_rate_node': 0.0,
                              'ratio_train_val': 0.15,
                              #'activation': tf.nn.tanh, Problem I can not serialize function HERE
               }
            # === CONFIGURATION ====================================================================
            @classmethod
            def getConfiguredGraphClass(cls):
                """
                In this class method, we must return a configured graph class
                """
                lLabels = ['B', 'I', 'O']

                lIgnoredLabels = None

                """
                if you play with a toy collection, which does not have all expected classes, you can reduce those.
                """

                lActuallySeen = None
                if lActuallySeen:
                    print("REDUCING THE CLASSES TO THOSE SEEN IN TRAINING")
                    lIgnoredLabels = [lLabels[i] for i in range(len(lLabels)) if i not in lActuallySeen]
                    lLabels = [lLabels[i] for i in lActuallySeen]
                    print(len(lLabels), lLabels)
                    print(len(lIgnoredLabels), lIgnoredLabels)

                # DEFINING THE CLASS OF GRAPH WE USE
                DU_GRAPH = Graph_MultiSinglePageXml
                nt = NodeType_PageXml_type_woText("abp"  # some short prefix because labels below are prefixed with it
                                                  , lLabels
                                                  , lIgnoredLabels
                                                  , False  # no label means OTHER
                                                  , BBoxDeltaFun=lambda v: max(v * 0.066, min(5, v / 3))
                                                  # we reduce overlap in this way
                                                  )
                nt.setLabelAttribute("DU_row")
                nt.setXpathExpr((".//pc:TextLine"  # how to find the nodes
                                 , "./pc:TextEquiv")  # how to get their text
                                )
                DU_GRAPH.addNodeType(nt)

                return DU_GRAPH

            def __init__(self, sModelName, sModelDir, sComment=None,dLearnerConfigArg=None):
                if sComment is None: sComment  = sModelName

                if  dLearnerConfigArg is not None and "ecn_ensemble" in dLearnerConfigArg:
                    print('ECN_ENSEMBLE')
                    DU_ECN_Task.__init__(self
                                         , sModelName, sModelDir
                                         , dFeatureConfig={}
                                         ,
                                         dLearnerConfig=dLearnerConfigArg if dLearnerConfigArg is not None else self.dLearnerConfig
                                         , sComment=sComment
                                         , cFeatureDefinition=FeatureDefinition_PageXml_StandardOnes_noText_v3,
                                          cModelClass=gcn.DU_Model_ECN.DU_Ensemble_ECN
                                         )


                else:
                    #Default Case Single Model
                    DU_ECN_Task.__init__(self
                                         , sModelName, sModelDir
                                         , dFeatureConfig={}
                                         , dLearnerConfig= dLearnerConfigArg if dLearnerConfigArg is not None else self.dLearnerConfig
                                         , sComment= sComment
                                         , cFeatureDefinition=FeatureDefinition_PageXml_StandardOnes_noText_v3
                                         )

                #if options.bBaseline:
                #    self.bsln_mdl = self.addBaseline_LogisticRegression()  # use a LR model trained by GridSearch as baseline

            # === END OF CONFIGURATION =============================================================
            def predict(self, lsColDir):
                """
                Return the list of produced files
                """
                self.sXmlFilenamePattern = "*.mpxml"
                return DU_ECN_Task.predict(self, lsColDir)
except ImportError:
        print('Could not Load ECN Model, Is TensorFlow installed ?')


try:
    from tasks.DU_ECN_Task import DU_ECN_Task
    import gcn.DU_Model_ECN
    from gcn.DU_Model_ECN import DU_Model_GAT
    class DU_ABPTable_GAT(DU_ECN_Task):
            """
            ECN Models
            """
            
            sMetadata_Creator = "NLE Document Understanding GAT"


            sXmlFilenamePattern = "*.mpxml"

            # sLabeledXmlFilenamePattern = "*.a_mpxml"
            sLabeledXmlFilenamePattern = "*.mpxml"

            sLabeledXmlFilenameEXT = ".mpxml"


            dLearnerConfigOriginalGAT ={
                'nb_iter': 500,
                'lr': 0.001,
                'num_layers': 2,#2 Train Acc is lower 5 overfit both reach 81% accuracy on Fold-1
                'nb_attention': 5,
                'stack_convolutions': True,
                # 'node_indim': 50   , worked well 0.82
                'node_indim': -1,
                'dropout_rate_node': 0.0,
                'dropout_rate_attention': 0.0,
                'ratio_train_val': 0.15,
                "activation_name": 'tanh',
                "patience": 50,
                "mu": 0.00001,
                "original_model" : True

            }

            dLearnerConfigNewGAT = {'nb_iter': 500,
                              'lr': 0.001,
                              'num_layers': 5,
                              'nb_attention': 5,
                              'stack_convolutions': True,
                              'node_indim': -1,
                              'dropout_rate_node': 0.0,
                              'dropout_rate_attention'  : 0.0,
                              'ratio_train_val': 0.15,
                              "activation_name": 'tanh',
                              "patience":50,
                              "original_model": False,
                              "attn_type":0
               }
            dLearnerConfig = dLearnerConfigNewGAT
            #dLearnerConfig = dLearnerConfigOriginalGAT
            # === CONFIGURATION ====================================================================
            @classmethod
            def getConfiguredGraphClass(cls):
                """
                In this class method, we must return a configured graph class
                """
                lLabels = ['B', 'I', 'O']

                lIgnoredLabels = None

                """
                if you play with a toy collection, which does not have all expected classes, you can reduce those.
                """

                lActuallySeen = None
                if lActuallySeen:
                    print("REDUCING THE CLASSES TO THOSE SEEN IN TRAINING")
                    lIgnoredLabels = [lLabels[i] for i in range(len(lLabels)) if i not in lActuallySeen]
                    lLabels = [lLabels[i] for i in lActuallySeen]
                    print(len(lLabels), lLabels)
                    print(len(lIgnoredLabels), lIgnoredLabels)

                # DEFINING THE CLASS OF GRAPH WE USE
                DU_GRAPH = Graph_MultiSinglePageXml
                nt = NodeType_PageXml_type_woText("abp"  # some short prefix because labels below are prefixed with it
                                                  , lLabels
                                                  , lIgnoredLabels
                                                  , False  # no label means OTHER
                                                  , BBoxDeltaFun=lambda v: max(v * 0.066, min(5, v / 3))
                                                  # we reduce overlap in this way
                                                  )
                nt.setLabelAttribute("DU_row")
                nt.setXpathExpr((".//pc:TextLine"  # how to find the nodes
                                 , "./pc:TextEquiv")  # how to get their text
                                )
                DU_GRAPH.addNodeType(nt)

                return DU_GRAPH

            def __init__(self, sModelName, sModelDir, sComment=None,dLearnerConfigArg=None):
                if sComment is None : sComment= sModelName
                DU_ECN_Task.__init__(self
                                     , sModelName, sModelDir
                                     , dFeatureConfig={}
                                     , dLearnerConfig= dLearnerConfigArg if dLearnerConfigArg is not None else self.dLearnerConfig
                                     , sComment=sComment
                                     , cFeatureDefinition=FeatureDefinition_PageXml_StandardOnes_noText_v3
                                     , cModelClass=DU_Model_GAT
                                     )

                if options.bBaseline:
                    self.bsln_mdl = self.addBaseline_LogisticRegression()  # use a LR model trained by GridSearch as baseline

            # === END OF CONFIGURATION =============================================================
            def predict(self, lsColDir):
                """
                Return the list of produced files
                """
                self.sXmlFilenamePattern = "*.mpxml"
                return DU_ECN_Task.predict(self, lsColDir)
except ImportError:
        print('Could not Load GAT Model','Is tensorflow installed ?')



# ----------------------------------------------------------------------------

def main(sModelDir, sModelName, options):
    if options.use_ecn:
        if options.ecn_json_config is not None and options.ecn_json_config is not []:
            f = open(options.ecn_json_config[0])
            djson=json.loads(f.read())

            if "ecn_learner_config" in djson:
                dLearnerConfig=djson["ecn_learner_config"]
                f.close()
                doer = DU_ABPTable_ECN(sModelName, sModelDir,dLearnerConfigArg=dLearnerConfig)
            elif "ecn_ensemble" in djson:
                dLearnerConfig = djson
                f.close()
                doer = DU_ABPTable_ECN(sModelName, sModelDir, dLearnerConfigArg=dLearnerConfig)

        else:
            doer = DU_ABPTable_ECN(sModelName, sModelDir)
    elif options.use_gat:
        if options.gat_json_config is not None and options.gat_json_config is not []:

            f = open(options.gat_json_config[0])
            djson=json.loads(f.read())
            dLearnerConfig=djson["gat_learner_config"]
            f.close()
            doer = DU_ABPTable_GAT(sModelName, sModelDir,dLearnerConfigArg=dLearnerConfig)

        else:
            doer = DU_ABPTable_GAT(sModelName, sModelDir)

    else:
        doer = DU_ABPTable(sModelName, sModelDir,
                          C                 = options.crf_C,
                          tol               = options.crf_tol,
                          njobs             = options.crf_njobs,
                          max_iter          = options.crf_max_iter,
                          inference_cache   = options.crf_inference_cache)
    
    if options.rm:
        doer.rm()
        return

    lTrn, lTst, lRun, lFold = [_checkFindColDir(lsDir) for lsDir in [options.lTrn, options.lTst, options.lRun, options.lFold]] 
    
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
        if options.bDetailedReport:
            traceln(tstReport.getDetailledReport())
            import crf.Model
            for test in lTst:
                sReportPickleFilename = os.path.join('..',test, sModelName + "__report.pkl")
                traceln('Report dumped into %s'%sReportPickleFilename)
                crf.Model.Model.gzip_cPickle_dump(sReportPickleFilename, tstReport)
    
    if lRun:
        if options.storeX or options.applyY:
            try: doer.load() 
            except: pass    #we only need the transformer
            lsOutputFilename = doer.runForExternalMLMethod(lRun, options.storeX, options.applyY, options.bRevertEdges)
        else:
            doer.load()
            lsOutputFilename = doer.predict(lRun)
            
        traceln("Done, see in:\n  %s"%lsOutputFilename)
        
        
# ----------------------------------------------------------------------------
if __name__ == "__main__":

    version = "v.01"
    usage, description, parser = DU_CRF_Task.getBasicTrnTstRunOptionParser(sys.argv[0], version)
#     parser.add_option("--annotate", dest='bAnnotate',  action="store_true",default=False,  help="Annotate the textlines with BIES labels")    

    #FOR GCN
    parser.add_option("--revertEdges", dest='bRevertEdges',  action="store_true", help="Revert the direction of the edges") 
    parser.add_option("--detail", dest='bDetailedReport',  action="store_true", default=False,help="Display detailled reporting (score per document)") 
    parser.add_option("--baseline", dest='bBaseline',  action="store_true", default=False, help="report baseline method")
    parser.add_option("--ecn",dest='use_ecn',action="store_true", default=False, help="wether to use ECN Models")
    parser.add_option("--ecn_config", dest='ecn_json_config',action="append", type="string", help="The Config files for the ECN Model")
    parser.add_option("--gat", dest='use_gat', action="store_true", default=False, help="wether to use ECN Models")
    parser.add_option("--gat_config", dest='gat_json_config', action="append", type="string",
                      help="The Config files for the Gat Model")
    # --- 
    #parse the command line
    (options, args) = parser.parse_args()
    
    # --- 
    try:
        sModelDir, sModelName = args
    except Exception as e:
        traceln("Specify a model folder and a model name!")
        _exit(usage, 1, e)
        
    main(sModelDir, sModelName, options)
