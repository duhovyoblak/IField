#==============================================================================
# Siqo class InfoFieldLine
#------------------------------------------------------------------------------
import cmath

from   .                      import logger
from   idata.imatrix          import InfoMatrix

#==============================================================================
# Module's constants
#------------------------------------------------------------------------------
_VER    = '1.1.0'

_LAMBDA = 1200       # Default points for Lambda axis
_AMP    =  200       # Default amplituda

#==============================================================================
# Module's variables
#------------------------------------------------------------------------------

#==============================================================================
# InfoFieldLine
#------------------------------------------------------------------------------
class InfoFieldLine(InfoMatrix):

    #==========================================================================
    # Static variables & methods
    #--------------------------------------------------------------------------

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, name):
        "Calls constructor of InfoFieldLine"

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
        self.setIpType('ipIntLine')
        self.setSchema({'axes': {'l': 'Lambda'}, 'vals': {'s': 'State'}})
        self.init(cnts={'l':_LAMBDA})

        self.applyMatrixMethod(methodKey='Integer random uniform', valueKey='s', params={'min':-_AMP, 'max':_AMP})

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.constructor: done")

    #--------------------------------------------------------------------------
    # Dynamics methods for InfoFieldLine
    #--------------------------------------------------------------------------
    def mapSetMethods(self) -> dict:
        "Returns map of methods setting keyed value to function value for respective parameters"

        methods = super().mapSetMethods()

        methods['ILine epoch step'  ] = {'matrixMethod': self.epochStep, 'pointMethod':None, 'params':{}                               , 'type':'ask'  }

        for methodKey in methods.keys():
            if not methodKey.startswith('ILine '): methods[methodKey]['visible'] = False

        return methods

    #==========================================================================
    # Line methods to apply in Dynamics methods
    #--------------------------------------------------------------------------
    def rndBool(self, valueKey:str, params:dict):
        """Clear all model and set state as random Boolean values."""
        logger.debug(f"{self.name}.rndBool: for key '{valueKey}' with params {params}")
        pts = 0

        self.clearPoints(defs={valueKey: False})
        self.actSubmatrix( {'e': 0} )
        pts = self.applyMatrixMethod(methodKey='Random bit', valueKey=valueKey, params=params)
        self.actSubmatrix()

        logger.info(f"{self.name}.rndBool: {pts} InfoPoints was set to random Boolean values for key '{valueKey}'")

    #==========================================================================
    # Internal tools
    #--------------------------------------------------------------------------

    #==========================================================================
    # Persistency methods
    #--------------------------------------------------------------------------

#==============================================================================
# Inicializacia modulu
#------------------------------------------------------------------------------
print(f"InfoFieldLine ver {_VER}")

if __name__ == '__main__':

    logger.info("Testing InfoFieldLine class")

    #--------------------------------------------------------------------------
    # Test of the InfoFieldLine class
    #--------------------------------------------------------------------------
    imat = InfoFieldLine(name='imatTest')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
