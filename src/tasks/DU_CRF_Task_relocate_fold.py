# -*- coding: utf-8 -*-

"""
    Utility to update the fold data, when the data files have moved
    
    Copyright Naver(C) 2017 JL. Meunier

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

import crf.Model

class DU_CRF_Task_RelocateFold:
    """

    """
    
    def __init__(self, sModelName, sModelDir):
        """
        we will do a string.replace on all path of all fold definition files
        """
        self.sModelName     = sModelName
        self.sModelDir      = sModelDir

    def replace(self, sOld, sNew):        
        """
        when the data files have been moved, we need to update the fold definitions...
        """
        traceln("-"*50)
        traceln("---------- RELOCATING CROSS-VALIDATION DEFINITION----------")
        traceln("Model files '%s' in folder '%s'"%(self.sModelName, self.sModelDir))
        traceln("-"*50)

        fnCrossValidDetails = os.path.join(self.sModelDir, self.sModelName+"_fold_def.pkl")
        if not os.path.exists(fnCrossValidDetails):
            traceln("ERROR: no CV data! (files %s%s%s_fold* )"%(self.sModelDir, os.sep, self.sModelName))
            exit(1)
        (lsTrnColDir, n_splits, test_size, random_state) = crf.Model.Model.gzip_cPickle_load(fnCrossValidDetails)
        
        for i in range(n_splits):
            iFold = i + 1
            traceln("---------- FOLD %d ----------"%iFold)
            fnFoldDetails = os.path.join(self.sModelDir, self.sModelName+"_fold_%d_def.pkl"%iFold)
            
            iFold, ts_trn, lFilename_trn, train_index, test_index = crf.Model.Model.gzip_cPickle_load(fnFoldDetails)
            
            lFilename_trn = [s.replace(sOld, sNew) for s in lFilename_trn]
            
            crf.Model.Model.gzip_cPickle_dump(fnFoldDetails, (iFold, ts_trn, lFilename_trn, train_index, test_index))
            
            #store the list for TRN and TST in a human readable form
            lFoldFilename_trn = [lFilename_trn[i] for i in train_index]
            lFoldFilename_tst = [lFilename_trn[i] for i in test_index]            
            for name, lFN in [('trn', lFoldFilename_trn), ('tst', lFoldFilename_tst)]:
                with open(os.path.join(self.sModelDir, self.sModelName+"_fold_%d_def_%s.txt"%(iFold, name)), "w") as fd:
                    fd.write("\n".join(lFN))
                    fd.write("\n")
            traceln("--- Fold info stored in : %s"%fnFoldDetails)
        
        
        
# ------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":

    try:
        modeldir, model, sOld, sNew  = sys.argv[1:5]
    except:
        traceln("Usage: %s  <modeldir> <model>  <old-string> <new-string>"%sys.argv[0])
        raise Exception()
        
    doer = DU_CRF_Task_RelocateFold(model, modeldir)
    doer.replace(sOld, sNew)
    
    traceln("DONE")
    