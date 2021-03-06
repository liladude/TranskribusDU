# -*- coding: utf-8 -*-
"""


    typoGenerator.py

    create (generate) textual annotated data 
     H. Déjean
    

    copyright Xerox 2017
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
"""
from __future__ import absolute_import
from __future__ import  print_function
from __future__ import unicode_literals

from dataGenerator.generator import Generator 

class typoGenerator(Generator):
    """
        generator for typographical position: 
    """
    lnames=[]
    
    def __init__(self, lw=[1,0,0]):
        """
            config: provides a weight for each typo positions
        """
        assert len(lw) == 3
        Generator.__init__(self,{})
        mylist=[]
        for i,w in enumerate(lw):
            mylist.append((self.lnames[i],w))
        self.loadResourcesFromList([mylist])
    
    def generate(self):
        """
            need to take into account element frequency! done in getRandomElt
            this generate is for terminal elements (otherwise use Generator.generate() )
        """
        # 11/14/2017: 
        
        self._generation = self.getRandomElt(self._value)
        while len(self._generation.strip()) == 0:
            self._generation = self.getRandomElt(self._value)
        
        return self    
    
class horizontalTypoGenerator(typoGenerator):
    TYPO_LEFT       = 0
    TYPO_RIGHT      = 1
    TYPO_HCENTER    = 2
    lnames = ['TYPO_LEFT','TYPO_RIGHT','TYPO_HCENTER']
  
class verticalTypoGenerator(typoGenerator):
    TYPO_TOP       = 0
    TYPO_BOTTOM      = 1
    TYPO_VCENTER    = 2
    lnames = ['TYPO_TOP','TYPO_BOTTOM','TYPO_VCENTER']
        
if __name__ == '__main__':
    typo=horizontalTypoGenerator([0.5,0.25,0.25])
    typo.instantiate()
    typo.generate()
    print (typo._generation)
    typo=verticalTypoGenerator([0.5,0.25,0.25])
    typo.instantiate()
    typo.generate()
    print (typo._generation)    