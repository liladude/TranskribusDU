# -*- coding: utf-8 -*-

"""
    Node and edge feature transformers to extract features for PageXml based on Logit classifiers
    
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
from __future__ import absolute_import
from __future__ import  print_function
from __future__ import unicode_literals

import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier  #for multilabel classif
from sklearn.model_selection import GridSearchCV  #0.18.1 REQUIRES NUMPY 1.12.1 or more recent
    
from common.trace import traceln
    
from .Transformer import Transformer
from .Transformer_PageXml import  NodeTransformerTextEnclosed

dGridSearch_CONF = {'C':[0.1, 0.5, 1.0, 2.0] }  #Grid search parameters for Logit training
dGridSearch_CONF = {'C':[0.01, 0.1, 1.0, 2.0] }  #Grid search parameters for Logit training

DEBUG=0

#------------------------------------------------------------------------------------------------------
class NodeTransformerLogit(Transformer):
    """
    we will get a list of blocks belonging to N classes.
    we train a logit classifier for those classes, as well as a multilabel classifier for the neighor of those classes

    the built feature vector is 2*N long
    """
    dGridSearch_LR_conf = dGridSearch_CONF
    
    def __init__(self, nbClass=None, n_feat_node=1000, t_ngrams_node=(2,4), b_node_lc=False, n_jobs=1):
        """
        input: 
        - number of classes
        - number of ngram
        - ngram min/max size
        - lowercase or not
        - njobs when fitting the logit using grid search
        if n_feat_node is negative, or 0, or None, we use all possible ngrams
        """
        Transformer.__init__(self)
        
        self.nbClass = nbClass
        self.n_feat_node, self.t_ngrams_node, self.b_node_lc = n_feat_node, t_ngrams_node, b_node_lc
        self.n_jobs = n_jobs
        
        self.text_pipeline = None    # feature extractor
        self.mdl_main      = None    # the main model predicting among the nbClass classes
        self.mdl_neighbor  = None    # the neighborhood model predicting zero to many of the classes
        
    
    def fit(self, X, y=None):
        """
        This tranformer needs the graphs to be fitted properly - see fitByGraph
        """
        return self
    
    def fitByGraph(self, lGraph, lAllNode=None):
        """
        we need to train 2 Logit: one to predict the node class, another to predict the class of the neighborhhod
        """
        self.text_pipeline = Pipeline([  ('selector'       , NodeTransformerTextEnclosed())
                                       , ('tf'             , TfidfVectorizer(lowercase=self.b_node_lc
                                                                        #, max_features=10000
                                                                        , analyzer = 'char'
                                                                        , ngram_range=self.t_ngrams_node)) #(2,6)), #we can use it separately from the pipleline once fitted
#                                        , ('word_selector'  , SelectKBest(chi2, k=self.n_feat_node))
                                       ])
        # the y
        if lAllNode==None: lAllNode = [nd for g in lGraph for nd in g.lNode]
        y = np.array([nd.cls for nd in lAllNode], dtype=np.int)
        if self.nbClass != len(np.unique(y)):
            traceln("Classes seen are: %s"%np.unique(y).tolist())
            traceln(self.nbClass)
            raise ValueError("ERROR: some class is not represented in the training set")
        
        #fitting the textual feature extractor
        self.text_pipeline.fit(lAllNode, y)
        
        #extracting textual features
        x = self.text_pipeline.transform(lAllNode)
        
        #creating and training the main logit model
        lr = LogisticRegression(class_weight='balanced')
        self.mdl_main = GridSearchCV(lr , self.dGridSearch_LR_conf, refit=True, n_jobs=self.n_jobs)        
        self.mdl_main.fit(x, y)
        del y
        if DEBUG: print(self.mdl_main)
        
        #now fit a multiclass multilabel logit to predict if a node is neighbor with at least one node of a certain class, for each class
        #Shape = (nb_tot_nodes x nb_tot_labels)
        y = np.vstack([g.getNeighborClassMask() for g in lGraph])  #we get this from the graph object. 
        assert y.shape[0] == len(lAllNode)
        
        lr = LogisticRegression(class_weight='balanced')
        gslr = GridSearchCV(lr , self.dGridSearch_LR_conf, refit=True, n_jobs=self.n_jobs)        
        self.mdl_neighbor = OneVsRestClassifier(gslr, n_jobs=self.n_jobs)
        self.mdl_neighbor.fit(x, y)

        del x, y
        if DEBUG: print(self.mdl_neighbor)

        return self
        
    def transform(self, lNode):
        """
        return the 2 logit scores
        """
        a = np.zeros( ( len(lNode), 3*self.nbClass ), dtype=np.float64)     #for each class: is_of_class? is_neighbor_of_class on same page or accross page?
        
        x = self.text_pipeline.transform(lNode)

        a[...,0:self.nbClass]                   = self.mdl_main     .predict_proba(x)
        a[...,  self.nbClass:3*self.nbClass]    = self.mdl_neighbor .predict_proba(x)
#         for i, nd in enumerate(lNode):
#             print i, nd, a[i]
        if DEBUG: print(a)
        return a

#     def testEco(self,lX, lY):
#         """
#         we test 2 Logit: one to predict the node class, another to predict the class of the neighborhood
#         and return a list of TestReport objects
#             [ ClassPredictor_Test_Report
#             , SamePageNeighborClassPredictor_Test_Report for each class
#             , CrossPageNeighborClassPredictor_Test_Report for each class
#             ]
#         """
#         loTstRpt = []
# ZZZZZ        
#         #extracting textual features
#         X = self.text_pipeline.transform(lAllNode)
# 
#         # the Y
#         Y = np.array([nd.cls for nd in lAllNode], dtype=np.int)
#         Y_pred = self.mdl_main.predict(X)
#         oTstRptMain = TestReportConfusion.newFromYYpred("TransformerLogit_main", Y_pred, Y, map(str, range(self.nbClass)))
#         loTstRpt.append(oTstRptMain)
#         
#         #the Y for neighboring
#         Y = np.vstack([g.getNeighborClassMask() for g in lGraph])  #we get this from the graph object. 
#         Y_pred = self.mdl_neighbor.predict(X)
#         nbCol = Y_pred.shape[1]
#         lsClassName = lGraph[0].getNeighborClassNameList()
#         assert nbCol == len(lsClassName)
#         for i, sClassName in enumerate(lsClassName):
#             oTstRpt = TestReportConfusion.newFromYYpred(sClassName, Y_pred[:,i], Y[:,i], ["no", "yes"])
#             loTstRpt.append(oTstRpt)
#         
#         return loTstRpt

#------------------------------------------------------------------------------------------------------
class EdgeTransformerLogit(Transformer):
    """
    we will get a list of edges belonging to N classes.
    we train a logit classifier for those classes, as well as a multilabel classifier for the neighor of those classes

    the built feature vector is 2*N long
    """
    dGridSearch_LR_conf = dGridSearch_CONF
    
    def __init__(self, nbClass, ndTrnsfLogit):
        """
        input: 
        - number of classes
        - number of ngram
        - ngram min/max size
        - lowercase or not
        - njobs when fitting the logit using grid search
        if n_feat_edge is negative, or 0, or None, we use all possible ngrams
        """
        Transformer.__init__(self)
        
        self.nbClass = nbClass
        self.transfNodeLogit = ndTrnsfLogit #fitted node transformer
        
    def transform(self, lEdge, bMirrorPage=True):
        """
        return the 2 logit scores
        """
        aA = self.transfNodeLogit.transform( [edge.A for edge in lEdge] )
        aB = self.transfNodeLogit.transform( [edge.B for edge in lEdge] )
        a = np.hstack([aA, aB])
        del aA, aB
        assert a.shape == (len(lEdge), 2 * 3 * self.nbClass) #src / target nodes, same_page/cross_page_neighbors/class
        
        return a


