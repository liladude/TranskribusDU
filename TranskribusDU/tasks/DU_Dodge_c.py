# -*- coding: utf-8 -*-

"""
    Example DU task for Dodge, using the logit textual feature extractor
    
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
import sys, os

try: #to ease the use without proper Python installation
    import TranskribusDU_version
except ImportError:
    sys.path.append( os.path.dirname(os.path.dirname( os.path.abspath(sys.argv[0]) )) )
    import TranskribusDU_version

from common.trace import traceln
from tasks import _checkFindColDir, _exit

from crf.Graph_DSXml import Graph_DSXml
from crf.NodeType_DSXml   import NodeType_DS
from DU_CRF_Task import DU_CRF_Task
from crf.FeatureDefinition_PageXml_logit import FeatureDefinition_PageXml_LogitExtractor

# ===============================================================================================================
#DEFINING THE CLASS OF GRAPH WE USE


import dodge_graph
 
class DU_Dodge_c(DU_CRF_Task):
    """
    We will do a CRF model for a DU task
    , working on a DS XML document at BLOCK level
    , with the below labels 
    """
    sXmlFilenamePattern = "*_ds.xml"
    
    #=== CONFIGURATION ====================================================================
    def __init__(self, sModelName, sModelDir, sComment=None): 
        
        DU_CRF_Task.__init__(self
                             , sModelName, sModelDir
                             , dodge_graph.DU_GRAPH
                             , dFeatureConfig = {
                                    'nbClass'    : 3
                                  , 'n_feat_node'    : 500
                                  , 't_ngrams_node'   : (2,4)
                                  , 'b_node_lc' : False    
                                  , 'n_feat_edge'    : 250
                                  , 't_ngrams_edge'   : (2,4)
                                  , 'b_edge_lc' : False    
                                  , 'n_jobs'      : 8         #n_jobs when fitting the internal Logit feat extractor model by grid search
                              }
                             , dLearnerConfig = {
                                   'C'                : .1 
                                 , 'njobs'            : 8
                                 , 'inference_cache'  : 50
                                 #, 'tol'              : .1
                                 , 'tol'              : .05
                                 , 'save_every'       : 50     #save every 50 iterations,for warm start
                                 , 'max_iter'         : 1000
                                 }
                             , sComment=sComment
                             , cFeatureDefinition=FeatureDefinition_PageXml_LogitExtractor
                             )
        
        self.addBaseline_LogisticRegression()    #use a LR model as baseline
    #=== END OF CONFIGURATION =============================================================

#Uniform Weight for the CRF
class DU_Dodge_c_UW(DU_CRF_Task):
    sXmlFilenamePattern = "*_ds.xml"

    #=== CONFIGURATION ====================================================================
    def __init__(self, sModelName, sModelDir, sComment=None):

        DU_CRF_Task.__init__(self
                             , sModelName, sModelDir
                             , dodge_graph.DU_GRAPH
                             , dFeatureConfig = {
                                    'nbClass'    : 3
                                  , 'n_feat_node'    : 500
                                  , 't_ngrams_node'   : (2,4)
                                  , 'b_node_lc' : False
                                  , 'n_feat_edge'    : 250
                                  , 't_ngrams_edge'   : (2,4)
                                  , 'b_edge_lc' : False
                                  , 'n_jobs'      : 8         #n_jobs when fitting the internal Logit feat extractor model by grid search
                              }
                             , dLearnerConfig = {
                                   'C'                : .1
                                 , 'njobs'            : 8
                                 , 'inference_cache'  : 50
                                 #, 'tol'              : .1
                                 , 'tol'              : .05
                                 , 'save_every'       : 50     #save every 50 iterations,for warm start
                                 , 'max_iter'         : 1000
                                 ,'uniform_classweight':True
                             }
                             , sComment=sComment
                             , cFeatureDefinition=FeatureDefinition_PageXml_LogitExtractor
                             )

        self.addBaseline_LogisticRegression()    #use a LR model as baseline





if __name__ == "__main__":

    version = "v.01"
    usage, description, parser = DU_CRF_Task.getBasicTrnTstRunOptionParser(sys.argv[0], version)

    # --- 
    #parse the command line
    (options, args) = parser.parse_args()
    # --- 
    try:
        sModelDir, sModelName = args
    except Exception as e:
        _exit(usage, 1, e)
        
    doer = DU_Dodge_c(sModelName, sModelDir)
    
    if options.rm:
        doer.rm()
        sys.exit(0)
    
    traceln("- classes: ", dodge_graph.DU_GRAPH.getLabelNameList())
    
    
    #Add the "out" subdir if needed
    lTrn, lTst, lRun = [_checkFindColDir(lsDir, "out") for lsDir in [options.lTrn, options.lTst, options.lRun]] 

    if lTrn:
        doer.train_save_test(lTrn, lTst, options.warm)
    elif lTst:
        doer.load()
        tstReport = doer.test(lTst)
        traceln(tstReport)
    
    if lRun:
        doer.load()
        lsOutputFilename = doer.predict(lRun)
        traceln("Done, see in:\n  %s"%lsOutputFilename)
