# -*- coding: utf-8 -*-

"""
    Factorial CRF DU task core. Supports classical CRF and Typed CRF
    
    Copyright Xerox(C) 2016, 2017 JL. Meunier

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

import sys, os

import numpy as np

try: #to ease the use without proper Python installation
    import TranskribusDU_version
except ImportError:
    sys.path.append( os.path.dirname(os.path.dirname( os.path.abspath(sys.argv[0]) )) )
    import TranskribusDU_version

from common.trace import traceln

import crf.Model
from crf.Model_SSVM_AD3 import Model_SSVM_AD3
from crf.Model_SSVM_AD3_Multitype import Model_SSVM_AD3_Multitype

import crf.FeatureDefinition


from .DU_CRF_Task import DU_CRF_Task

class DU_FactorialCRF_Task(DU_CRF_Task):


    def __init__(self, sModelName, sModelDir,  dLearnerConfig={}, sComment=None
                 , cFeatureDefinition=None, dFeatureConfig={}
                 ): 
        """
        Same as DU_CRF_Task except for the cFeatureConfig
        """
        self.configureGraphClass()
        self.sModelName     = sModelName
        self.sModelDir      = sModelDir
#         self.cGraphClass    = cGraphClass
        #Because of the way of dealing with the command line, we may get singleton instead of scalar. We fix this here
        self.config_learner_kwargs      = {k:v[0] if type(v) is list and len(v)==1 else v for k,v in dLearnerConfig.items()}
        if sComment: self.sMetadata_Comments    = sComment
        
        self._mdl = None
        self._lBaselineModel = []
        self.bVerbose = True
        
        self.iNbCRFType = None #is set below
        
        #--- Number of class per type
        #We have either one number of class (single type) or a list of number of class per type
        #in single-type CRF, if we know the number of class, we check that the training set covers all
        self.nbClass  = None    #either the number or the sum of the numbers
        self.lNbClass = None    #a list of length #type of number of class

        #--- feature definition and configuration per type
        #Feature definition and their config
        if cFeatureDefinition: self.cFeatureDefinition  = cFeatureDefinition
        assert issubclass(self.cFeatureDefinition, crf.FeatureDefinition.FeatureDefinition), "Your feature definition class must inherit from crf.FeatureDefinition.FeatureDefinition"
        
        #for single- or multi-type CRF, the same applies!
        self.lNbClass = [len(nt.getLabelNameList()) for nt in self.cGraphClass.getNodeTypeList()]
        self.nbClass = sum(self.lNbClass)
        self.iNbCRFType = len(self.cGraphClass.getNodeTypeList())

        self.config_extractor_kwargs = dFeatureConfig

        self.cModelClass = Model_SSVM_AD3 if self.iNbCRFType == 1 else Model_SSVM_AD3_Multitype
        assert issubclass(self.cModelClass, crf.Model.Model), "Your model class must inherit from crf.Model.Model"
        
        
