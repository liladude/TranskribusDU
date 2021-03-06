# -*- coding: utf-8 -*-

import os, glob
from optparse import OptionParser

from sklearn.linear_model import LogisticRegression
from sklearn.grid_search import GridSearchCV

import sys, os
import numpy as np

try: #to ease the use without proper Python installation
    import TranskribusDU_version
except ImportError:
    sys.path.append( os.path.dirname(os.path.dirname( os.path.abspath(sys.argv[0]) )) )
    import TranskribusDU_version

from common.trace import traceln
from tasks import _checkFindColDir, _exit

from crf.Graph_MultiPageXml import Graph_MultiPageXml
from crf.NodeType_PageXml   import NodeType_PageXml
from tasks.DU_CRF_Task import DU_CRF_Task



from common.trace import traceln

import crf.Model
from crf.BaselineModel import BaselineModel
from xml_formats.PageXml import MultiPageXml
import crf.FeatureDefinition
#from crf.FeatureDefinition_PageXml_std import FeatureDefinition_PageXml_StandardOnes
from crf.FeatureDefinition_PageXml_FeatSelect import FeatureDefinition_PageXml_FeatSelect

import pdb

class DU_BL_Task(DU_CRF_Task):
    cModelClass          = BaselineModel
    cFeatureDefinition   = FeatureDefinition_PageXml_FeatSelect

    sMetadata_Creator = "XRCE RXCE- v-0.000001"
    sMetadata_Comments = ""

    dGridSearch_LR_conf = {'C':[0.0001,0.001,0.1, 0.5, 1.0,10,100] }  #Grid search parameters for LR baseline method training

    def __init__(self, sModelName, sModelDir, cGraphClass, dFeatureConfig={}, dLearnerConfig={}, sComment=None, cFeatureDefinition=None):
        """
        """
        self.sModelName     = sModelName
        self.sModelDir      = sModelDir
        self.cGraphClass    = cGraphClass
        self.config_extractor_kwargs    = dFeatureConfig
        self.config_learner_kwargs      = dLearnerConfig
        if sComment: self.sMetadata_Comments    = sComment

        self._mdl = None
        self._lBaselineModel = []
        self.bVerbose = True

        if cFeatureDefinition: self.cFeatureDefinition = cFeatureDefinition
        assert issubclass(self.cModelClass, crf.Model.Model), "Your model class must inherit from crf.Model.Model"
        assert issubclass(self.cFeatureDefinition, crf.FeatureDefinition.FeatureDefinition), "Your feature definition class must inherit from crf.FeatureDefinition.FeatureDefinition"


    def train_save_test(self, lsTrnColDir, lsTstColDir, bWarm=False,filterFilesRegexp=True):
        """
        - Train a model on the tTRN collections, if not empty.
        - Test the trained model using the lTST collections, if not empty.
        - Also train/test any baseline model associated to the main model.
        - Trained models are saved on disk, for testing, redicting or further training (by warm-start)
        - if bWarm==True: warm-start the training from any data stored on disk. Otherwise, a non-empty model folder raises a ModelException
        return a test report object
        """
        self.traceln("-"*50)
        self.traceln("Model file '%s' in folder '%s'"%(self.sModelName, self.sModelDir))
        sConfigFile = os.path.join(self.sModelDir, self.sModelName+".py")
        self.traceln("  Configuration file: %s"%sConfigFile)
        self.traceln("Training with collection(s):", lsTrnColDir)
        self.traceln("Testing with  collection(s):", lsTstColDir)
        self.traceln("-"*50)

        #list the train and test files
        #NOTE: we check the presence of a digit before the '.' to eclude the *_du.xml files
        if filterFilesRegexp:
            ts_trn, lFilename_trn = self.listMaxTimestampFile(lsTrnColDir, "*[0-9]"+MultiPageXml.sEXT)
            _     , lFilename_tst = self.listMaxTimestampFile(lsTstColDir, "*[0-9]"+MultiPageXml.sEXT)
        else:
            #Assume the file list are correct
            lFilename_trn=lsTrnColDir
            lFilename_tst=lsTstColDir
            ts_trn = max([os.path.getmtime(sFilename) for sFilename in lFilename_trn])


        DU_GraphClass = self.cGraphClass

        self.traceln("- creating a %s model"%self.cModelClass)
        mdl = self.cModelClass(self.sModelName, self.sModelDir)

        if not bWarm:
            if os.path.exists(mdl.getModelFilename()): raise crf.Model.ModelException("Model exists on disk already, either remove it first or warm-start the training.")

        #mdl.configureLearner(**self.config_learner_kwargs)
        mdl.setBaselineModelList(self._lBaselineModel[0])
        mdl.saveConfiguration( (self.config_extractor_kwargs, self.config_learner_kwargs) )
        self.traceln("\t - configuration: ", self.config_learner_kwargs )

        self.traceln("- loading training graphs")
        lGraph_trn = DU_GraphClass.loadGraphs(lFilename_trn, bDetach=True, bLabelled=True, iVerbose=1,bNeighbourhood=True,attachEdge=True)
        self.traceln(" %d graphs loaded"%len(lGraph_trn))

        self.traceln("- retrieving or creating feature extractors...")
        try:
            mdl.loadTransformers(ts_trn)
        except crf.Model.ModelException:
            fe = self.cFeatureDefinition(**self.config_extractor_kwargs)
            #lY = [g.buildLabelMatrix() for g in lGraph_trn]
            #lY_flat = np.hstack(lY)
            #fe.fitTranformers(lGraph_trn,lY_flat)
            fe.fitTranformers(lGraph_trn)
            fe.cleanTransformers()
            mdl.setTranformers(fe.getTransformers())
            mdl.saveTransformers()
        self.traceln(" done")

        self.traceln("- training model...")

        #TODO Now do the connection in the BaselineModel with the Graph
        mdl.train(lGraph_trn, True, ts_trn)
        mdl.save()
        self.traceln("-training and save done ")


        self._mdl = mdl
        if lFilename_tst:
            self.traceln("- loading test graphs")
            lGraph_tst = DU_GraphClass.loadGraphs(lFilename_tst, bDetach=True, bLabelled=True, iVerbose=1,attachEdge=True)
            self.traceln(" %d graphs loaded"%len(lGraph_tst))

            oReport = mdl.test(lGraph_tst)
            print(oReport)
            for rep in oReport:
                print(rep)
        else:
            oReport = None, None

        self.traceln("-JOB-END-")
        return oReport

    def addFixedLR(self):
        lr = LogisticRegression(C=1.0,class_weight='balanced')
        self._lBaselineModel=[lr]

    def addBaseline_LogisticRegression(self):
        """
        add as Baseline a Logistic Regression model, trained via a grid search
        """
        lr = LogisticRegression(class_weight='balanced')
        glr = GridSearchCV(lr , self.dGridSearch_LR_conf)
        self._lBaselineModel=[glr]



    def test(self, lsTstColDir,test_sequential=True,filterFilesRegexp=True):
        """
        test the model
        return a TestReport object
        """
        self.traceln("-"*50)
        self.traceln("Trained model '%s' in folder '%s'"%(self.sModelName, self.sModelDir))
        self.traceln("Testing  collection(s):", lsTstColDir)
        self.traceln("-"*50)

        if not self._mdl: raise Exception("The model must be loaded beforehand!")

        if filterFilesRegexp:
            #list the train and test files
            _     , lFilename_tst = self.listMaxTimestampFile(lsTstColDir, self.sXmlFilenamePattern)
        else:
            #Assume the file list are correct
            lFilename_tst=lsTstColDir

        DU_GraphClass = self.cGraphClass

        lPageConstraint = DU_GraphClass.getPageConstraint()
        if lPageConstraint:
            for dat in lPageConstraint: self.traceln("\t\t%s"%str(dat))

        if test_sequential is False:
            #Load All
            self.traceln("- loading test graphs")
            lGraph_tst = DU_GraphClass.loadGraphs(lFilename_tst, bDetach=True, bLabelled=True, iVerbose=1,attachEdge=True)
            self.traceln(" %d graphs loaded"%len(lGraph_tst))
            oReport = self._mdl.test(lGraph_tst)

        else:
            #lower memory footprint
            self.traceln("- Testing...")
            self.traceln(" %d graphs to load, one by one"%len(lFilename_tst))
            oReport = self._mdl.testFiles(lFilename_tst, lambda s: DU_GraphClass.loadGraphs([s], bDetach=True, bLabelled=True, iVerbose=1,attachEdge=True))

        return oReport




    # === CONFIGURATION ====================================================================


 # === CONFIGURATION ====================================================================


class   DU_Baseline(DU_BL_Task):

    dFeatureConfig_Baseline = {'n_tfidf_node': 500
    , 't_ngrams_node': (2, 4)
    , 'b_tfidf_node_lc': False
    , 'n_tfidf_edge': 250
    , 't_ngrams_edge': (2, 4)
    , 'b_tfidf_edge_lc': False,
                           }

    dFeatureConfig_FeatSelect = {'n_tfidf_node': 500
    , 't_ngrams_node': (2, 4)
    , 'b_tfidf_node_lc': False
    , 'n_tfidf_edge': 250
    , 't_ngrams_edge': (2, 4)
    , 'b_tfidf_edge_lc': False
    , 'text_neighbors':False
    ,'n_tfidf_node_neighbors':500
    ,'XYWH_v2':False
    ,'edge_features':False
    }

    dLearnerConfig={  'C': .1
                            , 'njobs': 1
                            , 'inference_cache': 50
                            , 'tol': .1
                            , 'save_every': 50  # save every 50 iterations,for warm start
                            , 'max_iter': 250
                        }
     # === CONFIGURATION ====================================================================
    def __init__(self, sModelName, sModelDir,DU_GRAPH,logitID,sComment=None):

        if logitID=='logit_0':
            paramsBaseline=dict(self.dFeatureConfig_Baseline)
            DU_BL_Task.__init__(self, sModelName, sModelDir,DU_GRAPH,
                                dFeatureConfig=paramsBaseline,dLearnerConfig=self.dLearnerConfig,sComment=sComment)


        elif logitID=='logit_1':
            paramsFeatSelect=dict(self.dFeatureConfig_FeatSelect)
            paramsFeatSelect['feat_select']='chi2'
            paramsFeatSelect['n_tfidf_node']=500

            DU_BL_Task.__init__(self, sModelName, sModelDir,DU_GRAPH,
                                dFeatureConfig=paramsFeatSelect,dLearnerConfig=self.dLearnerConfig,sComment=sComment)
        elif logitID=='logit_2':
            paramsFeatSelect=dict(self.dFeatureConfig_FeatSelect)
            paramsFeatSelect['feat_select']='chi2'
            paramsFeatSelect['text_neighbors']=True

            DU_BL_Task.__init__(self, sModelName, sModelDir,DU_GRAPH,
                                dFeatureConfig=paramsFeatSelect,dLearnerConfig=self.dLearnerConfig,sComment=sComment)

        elif logitID=='logit_3':
            paramsFeatSelect=dict(self.dFeatureConfig_FeatSelect)
            #No feature selections for the node text feature
            paramsFeatSelect['n_tfidf_node']=100000
            #But Chi2 Feature selection of text feature
            paramsFeatSelect['text_neighbors']=True
            paramsFeatSelect['n_tfidf_node_neighbors']=500
            DU_BL_Task.__init__(self, sModelName, sModelDir,DU_GRAPH,
                                dFeatureConfig=paramsFeatSelect,dLearnerConfig=self.dLearnerConfig,sComment=sComment)

        elif logitID=='logit_4':
            paramsFeatSelect=dict(self.dFeatureConfig_FeatSelect)
            #No feature selections for the node text feature
            paramsFeatSelect['n_tfidf_node']=100000
            #But Chi2 Feature selection of text feature
            paramsFeatSelect['text_neighbors']=True
            paramsFeatSelect['n_tfidf_node_neighbors']=1000
            paramsFeatSelect['XYWH_v2']=True
            DU_BL_Task.__init__(self, sModelName, sModelDir,DU_GRAPH,
                                dFeatureConfig=paramsFeatSelect,dLearnerConfig=self.dLearnerConfig,sComment=sComment)

        elif logitID=='logit_5':
            paramsFeatSelect=dict(self.dFeatureConfig_FeatSelect)
            #No feature selections for the node text feature
            paramsFeatSelect['n_tfidf_node']=100000
            #But Chi2 Feature selection of text feature
            paramsFeatSelect['text_neighbors']=True
            paramsFeatSelect['n_tfidf_node_neighbors']=-1 #Means takes all
            paramsFeatSelect['XYWH_v2']=True
            DU_BL_Task.__init__(self, sModelName, sModelDir,DU_GRAPH,
                                dFeatureConfig=paramsFeatSelect,dLearnerConfig=self.dLearnerConfig,sComment=sComment)

        elif logitID=='logit_6':
            paramsFeatSelect=dict(self.dFeatureConfig_FeatSelect)
            #No feature selections for the node text feature
            paramsFeatSelect['n_tfidf_node']=100000
            #But Chi2 Feature selection of text feature
            paramsFeatSelect['text_neighbors']=True
            paramsFeatSelect['n_tfidf_node_neighbors']=1000 #Means takes all
            paramsFeatSelect['XYWH_v2']=True
            paramsFeatSelect['edge_features']=True
            DU_BL_Task.__init__(self, sModelName, sModelDir,DU_GRAPH,
                                dFeatureConfig=paramsFeatSelect,dLearnerConfig=self.dLearnerConfig,sComment=sComment)




        else:
            #TODO Takes all n_grams
            raise ValueError('Invalid modelID',logitID)


        self.addFixedLR()


