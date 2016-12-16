# -*- coding: utf-8 -*-

"""
    Second DU task for StAZH, use of constraints
    
    Copyright Xerox(C) 2016 JL. Meunier

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
from optparse import OptionParser

try: #to ease the use without proper Python installation
    import TranskribusDU_version
except ImportError:
    sys.path.append( os.path.dirname(os.path.dirname( os.path.abspath(sys.argv[0]) )) )
    import TranskribusDU_version

from tasks import _checkFindColDir, _exit

from crf.Graph_MultiPageXml_TextRegion import Graph_MultiPageXml_TextRegion
from crf.Model import ModelException

from DU_CRF_Task import DU_CRF_Task

from common.trace import traceln
 
class DU_StAZH_b(DU_CRF_Task):
    """
    We will do a CRF model for a DU task
    , working on a MultiPageXMl document at TextRegion level
    , with the below labels 
    """
    
    #=== CONFIGURATION ====================================================================
    Metadata_Creator = "XRCE Document Understanding CRF-based + constraints - v0.1"
    Metadata_Comments = None

    #  0=OTHER        1            2            3        4                5
    TASK_LABELS = ['catch-word', 'header', 'heading', 'marginalia', 'page-number']

    """
    The constraints must be a list of tuples like ( <operator>, <unaries>, <states>, <negated> )
    where:
    - operator is one of 'XOR' 'XOROUT' 'ATMOSTONE' 'OR' 'OROUT' 'ANDOUT' 'IMPLY'
    - states is a list of unary state names, 1 per involved unary. If the states are all the same, you can pass it directly as a single string.
    - negated is a list of boolean indicated if the unary must be negated. Again, if all values are the same, pass a single boolean value instead of a list 
    """
    lCONSTRAINT_PER_PAGE = [
           ('ATMOSTONE', 'catch-word', False)   #0 or 1 catch_word per page
         , ('ATMOSTONE', 'heading', False)      #0 or 1 heading pare page
         , ('ATMOSTONE', 'page-number', False)  #0 or 1 page number per page
         ]
    
    featureExtractorConfig = { 
                        'n_tfidf_node'    : 500
                      , 't_ngrams_node'   : (2,4)
                      , 'b_tfidf_node_lc' : False    
                      , 'n_tfidf_edge'    : 250
                      , 't_ngrams_edge'   : (2,4)
                      , 'b_tfidf_edge_lc' : False    
                      }

    learnerConfig = { 'C'                 : .1 
                     , 'njobs'            : 4
                     , 'inference_cache'  : 50
                     , 'tol'              : .1
                     , 'save_every'       : 50     #save every 50 iterations,for warm start
                     , 'max_iter'         : 1000
                     }
    
    def getGraphClass(self):
        DU_StAZH_Graph = Graph_MultiPageXml_TextRegion
        DU_StAZH_Graph.setLabelList(self.TASK_LABELS, True)  #True means non-annotated node are of class 0 = OTHER
        traceln("- classes: ", DU_StAZH_Graph.getLabelList())
        
        DU_StAZH_Graph.setPageConstraint(self.lCONSTRAINT_PER_PAGE)
        return DU_StAZH_Graph

    #=== END OF CONFIGURATION =======================


if __name__ == "__main__":

    version = "v.01"
    usage, description, parser = DU_CRF_Task.getBasicTrnTstRunOptionParser(sys.argv[0], version)

    # --- 
    #parse the command line
    (options, args) = parser.parse_args()
    # --- 
    try:
        sModelName, sModelDir = args
    except Exception as e:
        _exit(usage, 1, e)
        
    doer = DU_StAZH_b(dFeatureConfig=DU_StAZH_b.featureExtractorConfig
                      , dLearnerConfig=DU_StAZH_b.learnerConfig)

    #Add the "col" subdir if needed
    lTrn, lTst, lRun = [_checkFindColDir(lsDir) for lsDir in [options.lTrn, options.lTst, options.lRun]]

    if lTrn:
        doer.train_test(sModelName, sModelDir, lTrn, lTst)
    elif lTst:
        doer.test(sModelName, sModelDir, lTst)
    
    if lRun:
        lsOutputFilename = doer.predict(sModelName, sModelDir, lRun)
        traceln("Done, see in:\n  %s"%lsOutputFilename)
    