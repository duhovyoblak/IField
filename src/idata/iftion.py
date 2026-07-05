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

_CNT   = (100,)                                            # Default number of points
_AX1D  = {'x': 'Os X'}                                     # Default axes for ftion of one variable
_AX2D  = {'x': 'Os X','y': 'Os Y'}                         # Default axes for ftion of two variables
_AX3D  = {'x': 'Os X','y': 'Os Y','z': 'Os Z'}             # Default axes for ftion of three variables
_AX4D  = {'x': 'Os X','y': 'Os Y','z': 'Os Z','w': 'Os W'} # Default axes for ftion of four variables
_VALS  = {'f': 'Ftion value'}                              # Default values

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
    def __init__(self, name, cnts:dict|tuple=_CNT, dim='1D'):
        "Calls constructor of ICurve"

        #----------------------------------------------------------------------
        # Super constructor
        #----------------------------------------------------------------------
        super().__init__(name)

        #----------------------------------------------------------------------
        # Private datove polozky triedy
        #----------------------------------------------------------------------


        #----------------------------------------------------------------------
        # Inicializujem schemu a ipType podla dimenzie ftion
        #----------------------------------------------------------------------
        if dim == '1D':
            self.setIpType('ipFtion1D')
            self.setSchema({'axes': _AX1D, 'vals': _VALS})

        elif dim == '2D':
            self.setIpType('ipFtion2D')
            self.setSchema({'axes': _AX2D, 'vals': _VALS})

        elif dim == '3D':
            self.setIpType('ipFtion3D')
            self.setSchema({'axes': _AX3D, 'vals': _VALS})

        elif dim == '4D':
            self.setIpType('ipFtion4D')
            self.setSchema({'axes': _AX4D, 'vals': _VALS})

        else:
            logger.error(f"{self.name}.constructor: Invalid dimension '{dim}' for IFtion")
            raise ValueError(f"Invalid dimension '{dim}' for IFtion")
        
        #----------------------------------------------------------------------
        # Ak tuple cnts neobsahuje dostatok prvkov, doplnim ho pridanim 1
        #----------------------------------------------------------------------
        if isinstance(cnts, tuple):
            while len(cnts) < len(self.getSchemaAxes()): cnts = cnts + (1,)

        #----------------------------------------------------------------------
        # Inicializujem InfoPoints s poctom bodov podla cnts
        #----------------------------------------------------------------------
        self.init( cnts=cnts )

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
