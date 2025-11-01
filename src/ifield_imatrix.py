#==============================================================================
# Siqo class InfoFieldMatrix
#------------------------------------------------------------------------------
import functools
import math
import cmath
import numpy                  as np
import random                 as rnd

from   siqolib.logger         import SiqoLogger
from   siqo_imatrix           import InfoMatrix

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_VER    = '1.0'

#==============================================================================
# package's variables
#------------------------------------------------------------------------------

#==============================================================================
# InfoFieldMatrix
#------------------------------------------------------------------------------
class InfoFieldMatrix(InfoMatrix):

    #==========================================================================
    # Static variables & methods
    #--------------------------------------------------------------------------

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, name):
        "Calls constructor of InfoFieldMatrix"

        self.logger = SiqoLogger(name, level='DEBUG')
        self.logger.info(f"InfoFieldMatrix.constructor: {name}")

        #----------------------------------------------------------------------
        # Super constructor
        #----------------------------------------------------------------------
        super().__init__(name)

        #----------------------------------------------------------------------
        # Private datove polozky triedy
        #----------------------------------------------------------------------

        #----------------------------------------------------------------------
        # Inicializacia
        #----------------------------------------------------------------------

        #----------------------------------------------------------------------
        self.logger.info(f"{self.name}.constructor: done")

    #--------------------------------------------------------------------------
    # Method's methods
    #--------------------------------------------------------------------------
    def mapMethods(self) -> dict:
        "Returns map of methods setting keyed value to function value for respective parameters"

        methods = super().mapMethods()

        methods['IField epoch step'] = {'matrixMethod': self.epochStep, 'pointMethod':None,  'params':{}}

        return methods

    #==========================================================================
    # Matrix methods to apply in Dynamics methods
    #--------------------------------------------------------------------------
    def epochStep(self, valueKey:str, params:dict):
        """Compute next epoch state.
        """

        self.logger.debug(f"{self.name}.epochStep: for key '{valueKey}' with params {params}")

    #--------------------------------------------------------------------------

    #==========================================================================
    # Persistency methods
    #--------------------------------------------------------------------------

#------------------------------------------------------------------------------
print(f"InfoFieldMatrix ver {_VER}")

#==============================================================================
# Unit testy
#------------------------------------------------------------------------------
if __name__ == '__main__':

    #--------------------------------------------------------------------------
    # Test of the InfoFieldMatrix class
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Vytvorenie, generovanie osi
    #--------------------------------------------------------------------------
    im = InfoFieldMatrix('Test matrix')
    print(im)
    input('Press Enter to continue...')

    im.init()
    input('Press Enter to continue...')

    im.setIpType('ipTest')
    im.init()
    input('Press Enter to continue...')


    im.setSchemaAxe('a', 'Os A')
    im.setSchemaAxe('a', 'Os A')
    print(im.info(full=True)['msg'])
    input('Press Enter to continue...')

    im.init()
    print(im.info(full=True)['msg'])
    input('Press Enter to continue...')

    im.setSchemaVal('m', 'Hodnota M')
    print(im.info(full=True)['msg'])


    #--------------------------------------------------------------------------
    # generovanie hodnot
    #--------------------------------------------------------------------------
    im.applyPointMethod('BRandom fuuniform', 'm', params={'all':True, 'min':0, 'max':5})
    im.applyPointMethod('Random uniform', 'm', params={'all':True, 'min':0, 'max':5})
    print(im.info(full=True)['msg'])
    input('Press Enter to continue...')

    #--------------------------------------------------------------------------
    # Submatrix
    #--------------------------------------------------------------------------



#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------