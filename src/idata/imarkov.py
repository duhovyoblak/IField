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
_IND    = '|  '                    # Info indentation

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
    def __init__(self, name, dim:int=1, axeName:str='Value'):
        "Calls constructor of IMarkov process analyser/generator"

        logger.debug(f"{name}.constructor: Creating IMarkov object with dim={dim} and axeName='{axeName}'")

        #----------------------------------------------------------------------
        # Super constructor
        #----------------------------------------------------------------------
        super().__init__(name)

        #----------------------------------------------------------------------
        # Private datove polozky triedy
        #----------------------------------------------------------------------
        self.dim      = dim   # Dimension, e.g. number of previous states to consider in the Markov process
        self.totObs   = 0     # Total number of observations in this Markov object
        self.actPoint = None  # Actual InfoPoint in this Markov object
        self.actVals  = []    # List of actual values in the Markov process, length = dim

        #----------------------------------------------------------------------
        # Inicializujem schemu a ipType podla dimenzie ftion
        #----------------------------------------------------------------------
        self.setIpType('ipMarkovGen')
        self.setSchema({'axes': {'x':axeName}, 'vals': _VALS})

        #----------------------------------------------------------------------
        # Inicializujem histogram, na zaciatku neobsahuje zidne body, preto cnts=(0,)
        #----------------------------------------------------------------------
        self.init( cnts=(0,) )

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.constructor: done")

    #--------------------------------------------------------------------------
    def __str__(self):
        """Returns string representation of the IMarkov object.
        """

        return self.info(full=False)['msg']

    #--------------------------------------------------------------------------
    def info(self, indent=0, full=False) -> dict:
        """Returns information about the Markov analyser as a dictionary.
           If full is True, returns detailed information about the Markov analyser.
        """

        logger.debug(f"{self.name}.info: full={full}")
        dat = {}
        msg = ''

        #----------------------------------------------------------------------
        # Info o strukture
        #----------------------------------------------------------------------
        dat['name'          ] = self.name
        dat['ipType'        ] = self.ipType
        dat['dim'           ] = self.dim
        dat['schema_axes'   ] = self.getSchemaAxes()
        dat['schema_vals'   ] = self.getSchemaVals()
        dat['totObs'        ] = self.totObs
        dat['actPoint'      ] = self.actPoint.pos('x') if self.actPoint is not None else None
        dat['actVals'       ] = self.actVals

        #----------------------------------------------------------------------
        # Ak full, pridam info o vsetkych InfoPoints
        #----------------------------------------------------------------------
        if full:

            for idx, point in enumerate(self.points):
                dat[f'point[{idx}]'] = point.info(indent=indent+1, full=full)['dat']

        #----------------------------------------------------------------------
        # Konverzia do msg listu
        #----------------------------------------------------------------------
        if indent == 0: msg = f"{indent*_IND}{60*'='}\n"

        for key, val in dat.items():
            msg += f"{indent*_IND}{key:<15}: {val}\n"

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.info: Created info dictionary with {len(dat)} items, full={full}")
        return {'res': 'OK', 'dat': dat, 'msg': msg}

    #--------------------------------------------------------------------------
    def reset(self):
        """Resets the Markov analyser to its initial state.
        """

        logger.debug(f"{self.name}.reset: Resetting Markov analyser")

        #----------------------------------------------------------------------
        # Reset total observations and active point
        #----------------------------------------------------------------------
        self.init( cnts=(0,) )
        self.totObs   = 0
        self.actPoint = None
        self.actVals  = []

        #----------------------------------------------------------------------
        logger.audit(f"{self.name}.reset: Markov analyser reset complete")

    #--------------------------------------------------------------------------
    def setDim(self, dim:int):
        """Sets the dimension of the Markov analyser.
        """

        logger.debug(f"{self.name}.setDim: dim={dim}")

        #----------------------------------------------------------------------
        # Check if the dimension is valid
        #----------------------------------------------------------------------
        if dim < 1:
            logger.error(f"{self.name}.setDim: Invalid dimension {dim}, must be >= 1")
            return

        #----------------------------------------------------------------------
        # Reset analyser and set the dimension
        #----------------------------------------------------------------------
        self.reset()
        self.dim = dim

        #----------------------------------------------------------------------
        logger.audit(f"{self.name}.setDim: Markov analyser dimension set to {self.dim}")

    #--------------------------------------------------------------------------
    def actPoints(self) -> list:
        """Returns list of the active Points in the Markov process.
        """

        logger.debug(f"{self.name}.actPoints:")
        toRet = []

        #---------------------------------------------------------------------
        # If there is no active point, return an empty list
        #---------------------------------------------------------------------
        if self.actPoint is None:
            logger.info(f"{self.name}.actPoints: [No active point]")
            return toRet

        #---------------------------------------------------------------------
        # If there is an active point, initialise list
        #---------------------------------------------------------------------
        toRet = [self.actPoint]

        #---------------------------------------------------------------------
        # If there is a Markov analyser for the next dimension, dive into it
        #---------------------------------------------------------------------
        mrk = self.actPoint._vals['mrk']

        if mrk is not None and isinstance(mrk, IMarkov):  # Default hodnota po InitAdd je 0
            toRet.extend(mrk.actPoints())

        #---------------------------------------------------------------------
        logger.info(f"{self.name}.actPoints: Found {len(toRet)} active Points")
        return toRet

    #--------------------------------------------------------------------------
    def actAddress(self) -> str:
        """Returns string representation of the active Points in the Markov process.
        """

        logger.debug(f"{self.name}.actAddress:")
        toRet = ''

        #---------------------------------------------------------------------
        # Ziskam list of active Points in the Markov process
        #---------------------------------------------------------------------
        actPts = self.actPoints()

        #---------------------------------------------------------------------
        # Konvertujem list of active Points to string representation
        #---------------------------------------------------------------------
        for i, point in enumerate(actPts):

            if i == 0: toRet = f"{point.pos('x')}"
            else     : toRet += f" -> {point.pos('x')}"

        #---------------------------------------------------------------------
        logger.info(f"{self.name}.actAddress: '{toRet}'")
        return toRet

    #==========================================================================
    # IMarkov methods
    #--------------------------------------------------------------------------
    def observe(self, val:int):
        """Add new observation to the Markov analyser.

        1. Move window of the observed values forward one step and acquire list of active Points
        2. Increment the observation count for each active Point and increment the total observation count for each dimension.
    """

        logger.info(f"{self.name}.observe: val={val}")

        #----------------------------------------------------------------------
        # Move one step forward and acquire list of active Points
        #----------------------------------------------------------------------
        actPts = self.moveFwd(val=val)

        #----------------------------------------------------------------------
        # Increment the observation count of Point in all dimenesions
        #----------------------------------------------------------------------
        for actPt in actPts:
            actPt._vals['obs'] += 1

        #----------------------------------------------------------------------
        # Increment the total observation in this dimension
        #----------------------------------------------------------------------
        self.totObs += 1

        #----------------------------------------------------------------------
        # Increment the total observation count for each dimension > 1
        #----------------------------------------------------------------------
        for actPt in actPts[:-1]:  # Exclude the last dimension, there is no Markov analyser to dive in

            mrk = actPt._vals['mrk']

            if mrk is not None and isinstance(mrk, IMarkov):  # Default hodnota po InitAdd je 0
                mrk.totObs += 1

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.observe: Observation of value {val} added, total observations = {self.totObs}")

    #--------------------------------------------------------------------------
    def generate(self, observe=False)->int|None:
        """Generate new observation from the Markov analyser.
        """

        logger.info(f"{self.name}.generate: observe={observe}")
        toRet = None

        #----------------------------------------------------------------------
        # Find InfoPoint with pos == val
        #----------------------------------------------------------------------

        #----------------------------------------------------------------------
        return toRet

    #--------------------------------------------------------------------------
    def moveFwd(self, val:int) -> list:
        """Move values of the chain of Markov analysers forward with the new observation value.

        1. Move window of the Markov process forward one step
           M(dim).val <- M(dim-1).val <- M(dim-2).val <- ... <- M(1).val

        2. Activate the InfoPoints in each dimension > 1 according to the shifted values,
           activate the InfoPoint with pos == val in the last dimension of the Markov process.

        3. Return list of activated InfoPoints in the Markov process.
        """

        logger.debug(f"{self.name}._moveFwd: val={val}")

        #----------------------------------------------------------------------
        # Move one step forward = last (dim-1) values from actVals plus new value val
        #----------------------------------------------------------------------
        self.actVals = self.actVals[-(self.dim-1):] + [val]

        #----------------------------------------------------------------------
        # Activate internal state of the Markov analyser according to the shifted values in actVals
        #----------------------------------------------------------------------
        actPts = self._activate(actVals=self.actVals.copy())
        return actPts

    #--------------------------------------------------------------------------
    # Internal methods for IMarkov
    #--------------------------------------------------------------------------
    def _activate(self, actVals:list) -> list:
        """Activate the Markov analyser according to the list of values in actVals.

        1. For each dimension of the Markov process, find or create InfoPoint with val == actVals[dim].
        2. If this is not the last dimension, create Markov analyser for the next dimension and dive into it.
        3. Return list of activated InfoPoints in the Markov process.
        4. If actVals is empty, return empty list.
        """

        logger.info(f"{self.name}._activate: actVals={actVals}")
        toRet = []

        #----------------------------------------------------------------------
        # Check length of the actVals list
        #----------------------------------------------------------------------
        if len(actVals) == 0:
            logger.error(f"{self.name}._activate: actVals list is empty, cannot activate dim={self.dim}")
            return toRet

        #----------------------------------------------------------------------
        # Pop the leftmost value from actVals and use it as the new observation value for this dimension
        #----------------------------------------------------------------------
        val = actVals.pop(0)
        logger.info(f"{self.name}._activate: val={val}")

        #----------------------------------------------------------------------
        # Find/create InfoPoint with pos == val in this dimension of the Markov process
        #----------------------------------------------------------------------
        self.actPoint = self._getPoint(val=val, create=True)

        if self.actPoint is None:
            logger.error(f"{self.name}._activate: Failed to find or add InfoPoint with pos={val} to the Markov analyser")
            return toRet

        toRet.append(self.actPoint)

        #----------------------------------------------------------------------
        # If this is not the last dimension (=1), dive into the next dimension
        #----------------------------------------------------------------------
        if self.dim > 1:

            #------------------------------------------------------------------
            # Create Markov analyser for the next dimension
            #------------------------------------------------------------------
            nextMark = IMarkov(name=f"{self.name}/({val})", dim=self.dim-1, axeName=self.axeNameByKey('x'))
            self.actPoint.set(vals={'mrk': nextMark})

            #------------------------------------------------------------------
            # Dive into the next dimension
            #------------------------------------------------------------------
            toRet.extend(nextMark._activate(actVals=actVals))

        else:
            #------------------------------------------------------------------
            # Last dimension reached, check if there are still values in actPos, which should not happen
            #------------------------------------------------------------------
            if len(actVals) > 0:
                logger.error(f"{self.name}._activate: actVals list is not empty in the last dimension, remaining values: {actVals}")

        #----------------------------------------------------------------------
        logger.info(f"{self.name}._activate: Activated {len(toRet)} InfoPoints in the Markov process")
        return toRet

    #--------------------------------------------------------------------------
    def _getPoint(self, val:int, create=False):
        """Returns InfoPoint in this Markov analyser with pos = val.
        If create is True, creates new InfoPoint with pos = val if it does not exist.
        If create is False, returns None if InfoPoint with pos = val does not exist.
        """

        logger.debug(f"{self.name}._getPoint: val={val} with create={create}")

        #----------------------------------------------------------------------
        # Find InfoPoint with pos == val
        #----------------------------------------------------------------------
        pointIdx = self._idxByAxeVal(axeKey='x', axeVal=val)

        #----------------------------------------------------------------------
        # InfoPoint with pos == val does not exists
        #----------------------------------------------------------------------
        if pointIdx is None:

            if create: return self.initAdd(axeVal=val)
            else     : return None

        else:
            #------------------------------------------------------------------
            # InfoPoint with pos == val exists
            #------------------------------------------------------------------
            return self.points[pointIdx]

    #--------------------------------------------------------------------------
    def _idxByAxeVal(self, axeKey:str, axeVal:float) -> int|None:
        """Returns index in axe for respective coordinate.
           If axeKey is not in the schema, returns None.
           Return only exact match of pos == axeVal, otherwise returns None.
           This is overloaded method from InfoData, because in Markov analyser uses
           non-equidistant axes, so the index can not be calculated by (axeVal-axeOrig)/diff
        """

        logger.debug(f"{self.name}._idxByAxeVal: axeKey={axeKey}, axeVal={axeVal}")
        toRet = None

        #----------------------------------------------------------------------
        # Kontrola existencie osi
        #----------------------------------------------------------------------
        if axeKey not in self._cnts.keys():
            logger.error(f"{self.name}._idxByAxeVal: Axe '{axeKey}' is not in InfoData axes {list(self._cnts.keys())}")
            return toRet

        #----------------------------------------------------------------------
        # Prechadzam vsetky InfoPoints az po _pos[axeKey] == axeVal
        #----------------------------------------------------------------------
        for idx, point in enumerate(self.points):

            if point._pos[axeKey] == axeVal:
                toRet = idx
                break

        #----------------------------------------------------------------------
        logger.debug(f"{self.name}._idxByAxeVal: axeKey={axeKey}, axeVal={axeVal} -> idx={toRet}")
        return toRet


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
