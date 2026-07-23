#==============================================================================
# Siqo class IMarkov
#------------------------------------------------------------------------------
import cmath

from   .                      import logger
from   .idata                 import InfoData

#==============================================================================
# Module's constants
#------------------------------------------------------------------------------
_VER    = '1.1.0'

_AXES  = {'x'  : 'Value'}          # Axes for Markov process analysis
_VALS  = {'obs': 'Observations'    # Number of observations of the value X
         ,'mrk': 'Markov analyser' # Markov object for next dimension
         }

#==============================================================================
# Module's variables
#------------------------------------------------------------------------------

#==============================================================================
# IMarkov
#------------------------------------------------------------------------------
class IMarkov(InfoData):

    #==========================================================================
    # Static variables & methods
    #--------------------------------------------------------------------------

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, name, dim:int=1):
        "Calls constructor of IMarkov process analyser/generator"

        #----------------------------------------------------------------------
        # Super constructor
        #----------------------------------------------------------------------
        super().__init__(name)

        #----------------------------------------------------------------------
        # Private datove polozky triedy
        #----------------------------------------------------------------------
        self.totObs = 0     # Total number of observations in this Markov object
        self.actVal = None  # Actual value of the Markov process

        #----------------------------------------------------------------------
        # Inicializujem schemu a ipType podla dimenzie ftion
        #----------------------------------------------------------------------
        self.setIpType('ipMarkovGen')
        self.setSchema({'axes': _AXES, 'vals': _VALS})

        #----------------------------------------------------------------------
        # Inicializujem histogram, na zaciatku neobsahuje zidne body, preto cnts=(0,)
        #----------------------------------------------------------------------
        self.init( cnts=(0,) )

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.constructor: done")

    #==========================================================================
    # IMarkov methods
    #--------------------------------------------------------------------------
    def next(self, val:int|None=None):
        """Add new observation to the Markov analyser and/or generate next value.

        1. If val is provided, it is added as a new observation to the Markov analyser.

           - call _moveFwd() to update actVal of all Markov analysers with the new observation.
           - dive

        """

        logger.info(f"{self.name}.next: val={val}")

        #----------------------------------------------------------------------
        # If val is provided, add it as a new observation to the Markov analyser
        #----------------------------------------------------------------------
        if val is not None:

            #------------------------------------------------------------------
            # Move forward in the Markov process with the new observation
            #------------------------------------------------------------------
            self.actVal = self._moveFwd(val=val)
            self.totObs += 1


    #--------------------------------------------------------------------------
    # Internal methods for IMarkov
    #--------------------------------------------------------------------------
    def _idxByAxeVal(self, axeKey:str, axeVal:float) -> int|None:
        """Returns index in axe for respective coordinate.
           If axeKey is not in the schema, returns None.
           If coordinate is out of boundaries, return respective first or last axe value
           This is overloaded method from InfoData, because in Markov analyser uses
           non-equidistant axes, so the index can not be calculated by (axeVal-axeOrig)/diff
        """

        #----------------------------------------------------------------------
        # Kontrola existencie osi
        #----------------------------------------------------------------------
        if axeKey not in self._cnts.keys():
            logger.error(f"{self.name}._idxByAxeVal: Axe '{axeKey}' is not in InfoData axes {list(self._cnts.keys())}")
            return None

        #----------------------------------------------------------------------
        # Odstrihnem extremy pred a po min/max hodnatach
        #----------------------------------------------------------------------
        if   axeVal <= self._origs[axeKey]                      : toRet = 0
        elif axeVal >= self._origs[axeKey] + self._rects[axeKey]: toRet = self._cnts[axeKey]-1
        else:
            #------------------------------------------------------------------
            # Prechdzam vsetky InfoPoints az po _pos[axeKey] >= axeVal
            #------------------------------------------------------------------
            for idx, point in enumerate(self.points):
                if point._pos(axeKey) >= axeVal: break

            toRet = idx

        #----------------------------------------------------------------------
        logger.debug(f"{self.name}._idxByAxeVal: axeKey={axeKey}, axeVal={axeVal} -> idx={toRet}")
        return toRet

    #--------------------------------------------------------------------------
    def _getHistogramRecord(self, axeVal:int) -> dict:
        """Returns _VALS dict of InfoPoint in this Markov analyser with actVal = axeVal.
        If such axe value does not exist, it is created and added to the Markov analyser.
        """

        logger.info(f"{self.name}._getHistogramRecord: axeVal={axeVal}")

        #----------------------------------------------------------------------
        # If axeVal is provided, add it as a new observation to the Markov analyser
        #----------------------------------------------------------------------
        if axeVal is not None:
            self.next(val=axeVal)

        return self.actVal

    #--------------------------------------------------------------------------
    def _moveFwd(self, val:int) -> int|float:
        """Recursively dive into the Markov analysers till the last dimension and
        there update the actual value of the Markov process based on the new observation.
        Returns old value of the Markov process for updating actVal in parent dimension.
        """

        logger.info(f"{self.name}._moveFwd: val={val}")

        toRet = self.actVal  # Store old value to return to parent dimension

        #----------------------------------------------------------------------
        # Last dimension reached, update actVal based on the new observation
        #----------------------------------------------------------------------
        if self.dim == 1:

            self.actVal = val    # Update actVal with the new observation
            return toRet

        else:

            self.actVal = self._moveFwd(val=val)

        #----------------------------------------------------------------------
        # Not the last dimension, update actVal based on the new observation
        #----------------------------------------------------------------------
        self.actVal = val  # For simplicity, just set actVal to val; in a real implementation, this would involve more complex logic.

        return self.actVal

    #==========================================================================
    # Dynamics methods for IMarkov
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
    # IMarkov methods to apply in Dynamics methods
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
print(f"IMarkov ver {_VER}")

if __name__ == '__main__':

    logger.info("Testing IMarkov class")

    #--------------------------------------------------------------------------
    # Test of the IMarkov class
    #--------------------------------------------------------------------------
    imat = IMarkov(name='imatTest')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
