#==============================================================================
# Siqo class IFtion
#------------------------------------------------------------------------------
import cmath

from   .                      import logger
from   .idata                 import InfoData

#==============================================================================
# Module's constants
#------------------------------------------------------------------------------
_VER    = '1.1.0'

_CNT   = 1200                     # Default number of points
_AXES  = {'x': 'Os X'}            # Default axes
_VALS  = {'f': 'Ftion value'}     # Default values

#==============================================================================
# Module's variables
#------------------------------------------------------------------------------

#==============================================================================
# IFtion
#------------------------------------------------------------------------------
class IFtion(InfoData):

    #==========================================================================
    # Static variables & methods
    #--------------------------------------------------------------------------

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, name, cnt:dict|tuple=_CNT, axes:dict|tuple=_AXES, vals:dict|tuple=_VALS):
        "Calls constructor of ICurve"

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
        self.setIpType('ipFtion')
        self.setSchema({'axes': axes, 'vals': vals})
        self.init( cnts=(cnt,) )

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.constructor: done")

    #--------------------------------------------------------------------------
    # Dynamics methods for IFtion
    #--------------------------------------------------------------------------
    def mapSetMethods(self) -> dict:
        "Returns map of methods setting keyed value to function value for respective parameters"

        methods = super().mapSetMethods()

        methods['ISeries deltas'      ] = {'dataMethod' : self.deltas
                                          ,'pointMethod':None
                                          ,'params'     :{}
                                          ,'visible'    :True
                                          ,'paramAsk'   :True
                                          ,'outData'    :None
                                          ,'outKey'     :'d'
                                          }

        return methods

    #==========================================================================
    # Curve methods to apply in Dynamics methods
    #--------------------------------------------------------------------------
    def deltas(self, inKey:str, outKey:str, params:dict, outData:'InfoData'):
        """Compute auto-correlation of states for each phase.
        - inKey  : Key of the value to be read by the method
        - outKey : Key of the value to be set by the method
        - params : Parameters for the method as dict
        - outData: InfoData to store output data
        Returns count of updated InfoPoints or None if initialization failed due to incompatible parameters or undefined ipType.
        """

        logger.info(f"{self.name}.deltas: {outData.name}[{outKey}] = <Deltas>({inKey}) with params {params}")
        pts = 0

        #----------------------------------------------------------------------
        # Vsetky IPoints nastavim do subMatrix listu
        #----------------------------------------------------------------------
        points = self.actSubData()

        prevS = 0
        points[0].set( vals = {outKey: prevS} )

        #----------------------------------------------------------------------
        # Prejdem vsetky boby v subdata a pre kazdy bod nastavim hodnotu ako rozdiel medzi hodnotou bodu a predosleho bodu
        #----------------------------------------------------------------------
        for i in range(1, len(points)):

            point = points[i]
            currS = point.val(valKey='s')

            #------------------------------------------------------------------
            # Vypocet a nastavenie delty
            #------------------------------------------------------------------
            delta = currS - prevS
            point.set( vals = {outKey: delta})

            #------------------------------------------------------------------
            # Posun na nasledujuci bod
            #------------------------------------------------------------------
            prevS = currS
            pts += 1

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.deltas: {pts} InfoPoints was updated for key '{outKey}' in deltas")

    #==========================================================================
    # Internal tools
    #--------------------------------------------------------------------------

    #==========================================================================
    # Persistency methods
    #--------------------------------------------------------------------------

#==============================================================================
# Inicializacia modulu
#------------------------------------------------------------------------------
print(f"IFtion ver {_VER}")

if __name__ == '__main__':

    logger.info("Testing IFtion class")

    #--------------------------------------------------------------------------
    # Test of the IFtion class
    #--------------------------------------------------------------------------
    imat = IFtion(name='imatTest')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
