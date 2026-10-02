#==============================================================================
# Siqo class IMarkov
#------------------------------------------------------------------------------
import math

from   .                      import logger
from   .idata                 import InfoData

#==============================================================================
# Module's constants
#------------------------------------------------------------------------------
_VER    = '1.1.5'
_IND    = '|  '                        # Info indentation

_IPTYPE_MARKOV = 'ipMarkovGen'

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
    _INFO_STRUCT    = True
    _INFO_HISTOGRAM = True

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, name, dim:int=1):
        "Calls constructor of IMarkov process analyser/generator"

        logger.debug(f"{name}.constructor: Creating IMarkov object with dim={dim}")

        #----------------------------------------------------------------------
        # Super constructor
        #----------------------------------------------------------------------
        super().__init__(name)

        #----------------------------------------------------------------------
        # Private datove polozky triedy
        #----------------------------------------------------------------------
        self.dim      = dim   # Dimension, e.g. number of previous states to consider in the Markov process
        self.totObs   = 0     # Total number of observations in this Markov object
        self.mrkPro   = 1     # Probability associated with this Markov analyser, updated during computation
        self.eqProb   = 1     # Equal probability for all points, eqProb = 1 / len(self.points) if len(self.points) > 0 else 0

        #----------------------------------------------------------------------
        # Dynamic variables of the Markov process, used to store the last dim observed values
        #----------------------------------------------------------------------
        self.actVals     = []     # List of actual values for this Markov process, length = dim
        self.actPoint    = None   # Active InfoPoint in this Markov object
        self.needCompute = False  # Flag if probabilities and gains need to be recomputed

        #----------------------------------------------------------------------
        # Inicializujem schemu a ipType podla dimenzie ftion
        #----------------------------------------------------------------------
        self.setIpType(_IPTYPE_MARKOV)

        #----------------------------------------------------------------------
        # Inicializujem histogram, na zaciatku neobsahuje zidne body, preto cnts=(0,)
        #----------------------------------------------------------------------
        self.init( cnts=(0,) )

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.constructor: done")

    #--------------------------------------------------------------------------
    def setNamePro(self, mrkPro):
        """Name of Markov analyser has format 'Markov/(7)/(3){mrkPro}.
        This method sets the probability associated with this Markov analyser.
        """
        #----------------------------------------------------------------------
        # Odstranim z name {mrkPro} ak existuje
        #----------------------------------------------------------------------
        if '{' in self.name and '}' in self.name:
            self.name = self.name[:self.name.rfind('{')]

        #----------------------------------------------------------------------
        # Doplnim do name aktualnu hodnotu {mrkPro}
        #----------------------------------------------------------------------
        self.name += f"{{{mrkPro:6.4f}}}"

    #--------------------------------------------------------------------------
    def __str__(self):
        """Returns string representation of the IMarkov object.
        """
        toRet = ''

        for msg in self.info(struct=self._INFO_STRUCT, histogram=self._INFO_HISTOGRAM)['msg']:
            toRet += msg

        return toRet

    #--------------------------------------------------------------------------
    def info(self, indent=0, struct=_INFO_STRUCT, histogram=_INFO_HISTOGRAM) -> dict:
        """Returns information about the Markov analyser as a dictionary.
           If struct is True, returns structural information about the Markov analyser.
           If histogram is True, returns histogram information about the Markov analyser.
        """

        logger.debug(f"{self.name}.info: struct={struct}, histogram={histogram}")
        dat = {}
        msg = []
        if indent == 0: msg = [f"{indent*_IND}{60*'='}\n"]

        #----------------------------------------------------------------------
        # Recompute probabilities and gains if needed
        #----------------------------------------------------------------------
        if self.needCompute: self._compute()

        #----------------------------------------------------------------------
        # Info o strukture
        #----------------------------------------------------------------------
        if struct:
            dat['ver'           ] = _VER
            dat['axeName'       ] = self.axeNameByKey('x')
            dat['ipType'        ] = self.ipType
            dat['dim'           ] = self.dim
            dat['mrkPro'        ] = self.mrkPro
            dat['totObs'        ] = self.totObs
            dat['eqProb'        ] = self.eqProb
            dat['actVals'       ] = self.actVals

            #------------------------------------------------------------------
            # Konverzia do msg listu
            #------------------------------------------------------------------
            for key, val in dat.items():
                msg.append(f"{indent*_IND}{key:<15}: {val}\n")

            #------------------------------------------------------------------
            # Active Points
            #------------------------------------------------------------------
            msg.append(f"{indent*_IND}\n")
            msg.append(f"{indent*_IND}Active Points\n")

            for actPt in self.actPoints():

                posStr = actPt._posStr()
                valStr = actPt._valsStr()

                dat[f'actPoint[{posStr}]'] = valStr
                msg.append(f"{indent*_IND}actPoint {posStr}: {valStr}\n")

            msg.append(f"{indent*_IND}\n")

        #----------------------------------------------------------------------
        # Ak dat, pridam info o vsetkych InfoPoints a ich Markov objektoch
        #----------------------------------------------------------------------
        if histogram:

            msg.append(f"{indent*_IND}{60*'-'}\n")

            for point in self.points:

                #--------------------------------------------------------------
                # Prazdny riadok pred zmenou 1. urovne
                #--------------------------------------------------------------
                if indent == 0:
                    msg.append("|\n")

                #--------------------------------------------------------------
                # Riadok s informaciami o bode
                #--------------------------------------------------------------
                posStr = point._posStr()
                valStr = point._valsStr()

                dat[f'point[{posStr}]'] = valStr
                msg.append(f"{indent*_IND}point {posStr}: {valStr}\n")

                #--------------------------------------------------------------
                # Info o vnorenom Markov objekte, ak existuje
                #--------------------------------------------------------------
                mrk = point._vals['mrk']

                if mrk is not None and isinstance(mrk, IMarkov):

                    res = mrk.info(indent=indent+1, struct=False, histogram=True)

                    dat[f'point[{posStr}].mrk'] = res['dat']
                    msg.extend(res['msg'])

                #--------------------------------------------------------------

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.info: Created info")
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
        self.mrkPro      = 1
        self.totObs      = 0
        self.eqProb      = 1

        self.actVals     = []
        self.actPoint    = None
        self.needCompute = False

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.reset: Markov analyser reset complete")

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
        logger.info(f"{self.name}.setDim: Markov analyser dimension set to {self.dim}")

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
    def observe(self, val:int) -> bool:
        """Add new observation to the Markov analyser.

        1. Move the observation window forward one step.
        2. Activate the corresponding points and update their observation counts.
        3. Return True if the observation was successful, False otherwise.
        """

        logger.debug(f"{self.name}.observe: val={val}")
        self.needCompute = True

        #----------------------------------------------------------------------
        # Move one step forward and observe the new value
        #----------------------------------------------------------------------
        toRet = self.moveFwd(val=val, observe=True)

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.observe: '{val}' added")
        return toRet

    #--------------------------------------------------------------------------
    def amend(self, val:int)->int|None:
        """Advance the Markov analyser without recording a new observation.

        Probabilities are recomputed when necessary and the active Markov path
        is moved forward. The expected-value calculation is not implemented yet,
        so this method currently returns None.
        """

        logger.info(f"{self.name}.amend: val={val}")
        toRet = None

        #----------------------------------------------------------------------
        # Recompute probabilities and gains if needed
        #----------------------------------------------------------------------
        if self.needCompute: self._compute()

        #----------------------------------------------------------------------
        # Move the active Markov path one step forward
        #----------------------------------------------------------------------
        success = self.moveFwd(val=val)

        if not success: return None

        #----------------------------------------------------------------------
        return toRet

    #--------------------------------------------------------------------------
    def generate(self, observe=False)->int|None:
        """Generate value of the next observation from the Markov analyser.
        """

        logger.info(f"{self.name}.generate: observe={observe}")
        toRet = None

        #----------------------------------------------------------------------
        # Recompute probabilities and gains if needed
        #----------------------------------------------------------------------
        if self.needCompute: self._compute()

        #----------------------------------------------------------------------
        # Find InfoPoint with pos == val
        #----------------------------------------------------------------------

        #----------------------------------------------------------------------
        return toRet

    #--------------------------------------------------------------------------
    def maxForce(self, minForce=0.1, minObs=10, maxPatterns=0) -> dict:
        """Returns dict of patterns with maximum force in the Markov analyser.

        Crawls through all patterns in the Markov analyser and returns those with force >= minForce and observations >= minObs.
        Pattern is represented as a tuple of values in the Markov process, e.g. (val1, val2, ..., valN),
        it can be length 1 to dim

        Returns toRet[pattern] = {'frc': force, 'obs': obs, 'pro': pro}
        Returned dict is sorted by force in descending order.
        If maxPatterns > 0, returns only the first maxPatterns entries.
        """

        logger.info(f"{self.name}.maxForce: minForce={minForce}, minObs={minObs}, maxPatterns={maxPatterns}")

        #----------------------------------------------------------------------
        # Collect all patterns recursively
        #----------------------------------------------------------------------
        toRet = self._maxForceRecursive(minForce=minForce, minObs=minObs, pattern=())

        #----------------------------------------------------------------------
        # Sort by force in descending order
        #----------------------------------------------------------------------
        sorted_toRet = dict(sorted(toRet.items(), key=lambda x: x[1]['frc'], reverse=True))

        #----------------------------------------------------------------------
        # Limit to maxPatterns if specified
        #----------------------------------------------------------------------
        if maxPatterns > 0:
            sorted_toRet = dict(list(sorted_toRet.items())[:maxPatterns])

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.maxForce: Found {len(sorted_toRet)} patterns with force >= {minForce}")
        return sorted_toRet

    #--------------------------------------------------------------------------
    def moveFwd(self, val:int, *, observe:bool=False) -> bool:
        """Move values of the chain of Markov analysers forward with the new observation value.

        1. Move window of the Markov process forward one step
           M(dim).val <- M(dim-1).val <- M(dim-2).val <- ... <- M(1).val

        2. Activate the InfoPoints in each dimension > 1 according to the shifted values,
           activate the InfoPoint with pos == val in the last dimension of the Markov process.

        3. Return True if activation was successful, False otherwise.
        """

        logger.debug(f"{self.name}._moveFwd: val={val}")

        #----------------------------------------------------------------------
        # Move one step forward = last (dim-1) values from actVals plus new value val
        # Note: For dim=1, we keep only the current value (sliding window size = 1)
        # For dim=2, we keep the last 1 value plus new value (sliding window size = 2)
        # etc.
        #----------------------------------------------------------------------
        if self.dim > 1: self.actVals = self.actVals[-(self.dim-1):] + [val]
        else           : self.actVals = [val]

        #----------------------------------------------------------------------
        # Activate internal state of the Markov analyser according to the shifted values in actVals
        #----------------------------------------------------------------------
        return self._activate(actVals=self.actVals.copy(), observe=observe)

    #--------------------------------------------------------------------------
    # Internal methods for IMarkov
    #--------------------------------------------------------------------------
    def _activate(self, actVals:list, *, observe:bool=False) -> bool:
        """Activate the Markov analyser according to the list of values in actVals.

        1. For each dimension of the Markov process, find or create InfoPoint with val == actVals[dim].
        2. If values remain and this is not the last dimension, create the next
           Markov analyser and dive into it.
        3. If observe==True, update the observation count for the activated InfoPoint
           and total observation count for this dimension.
        4. Return True if activation was successful, False otherwise.
        """

        logger.debug(f"{self.name}._activate: actVals={actVals}")
        toRet = False

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
        logger.debug(f"{self.name}._activate: val={val}")

        #----------------------------------------------------------------------
        # Find/create InfoPoint with pos == val in this dimension of the Markov process
        #----------------------------------------------------------------------
        self.actPoint = self._getPoint(val=val, create=True)

        if self.actPoint is None:
            logger.error(f"{self.name}._activate: Failed to find or add InfoPoint with pos={val} to the Markov analyser")
            return toRet

        #----------------------------------------------------------------------
        # If observe is True, update the observation count for the activated InfoPoint and total observation count for this dimension
        #----------------------------------------------------------------------
        if observe:
            self.totObs                += 1
            self.actPoint._vals['obs'] += 1

        #----------------------------------------------------------------------
        # If this is not the last dimension (=1), dive into the next dimension
        #----------------------------------------------------------------------
        toRet = True

        if self.dim > 1:

            #------------------------------------------------------------------
            # Check if the sliding window has more values to activate
            # An incomplete initial window is a valid observation
            #------------------------------------------------------------------
            if len(actVals) > 0:

                #--------------------------------------------------------------
                # Get or create Markov analyser for the next dimension
                #--------------------------------------------------------------
                nextMark = self.actPoint._vals.get('mrk', None)

                if nextMark is None or not isinstance(nextMark, IMarkov):
                    nextMark = IMarkov(name=f"{self.name}/({val})", dim=self.dim-1)
                    self.actPoint.set(vals={'mrk': nextMark})

                #--------------------------------------------------------------
                # Activate the next dimension
                #--------------------------------------------------------------
                toRet = toRet and nextMark._activate(actVals=actVals, observe=observe)

        else:
            #------------------------------------------------------------------
            # Last dimension reached, check if there are still values in actPos, which should not happen
            #------------------------------------------------------------------
            if len(actVals) > 0:
                logger.error(f"{self.name}._activate: actVals list is not empty in the last dimension, remaining values: {actVals}")
                toRet = False

        #----------------------------------------------------------------------
        logger.debug(f"{self.name}._activate: Activation status: {toRet}")
        return toRet

    #--------------------------------------------------------------------------
    def _compute(self, mrkPro=1.0):
        """Recalculate all probabilities and forces for all points in this Markov layer.

        This method propagates probability (mrkPro) associated with this Markov analyser
        from parent dimension through all points and their nested Markov objects.

        Args:
            mrkPro   (float): Probability asociated with this Markov analyser (default: 1.0 at root level)
        """

        logger.debug(f"{self.name}._compute: mrkPro={mrkPro}")

        #----------------------------------------------------------------------
        # Set local probability (mrkPro) associated with this Markov analyser
        #----------------------------------------------------------------------
        self.mrkPro = mrkPro

        #----------------------------------------------------------------------
        # Recalculate probability for all points in this markov analyser
        #----------------------------------------------------------------------
        for point in self.points:

            # Local probability: P(X_i | ...) = obs / totObs
            point._vals['loc'] = point._vals['obs'] / self.totObs if self.totObs > 0 else 0.0

            # Joint probability: P(X_1, ..., X_i) = mrkPro * P(X_i | ...)
            point._vals['pro'] = mrkPro * point._vals['loc']

        #----------------------------------------------------------------------
        # Recalculate forces for all points in this markov analyser
        #----------------------------------------------------------------------
        for point in self.points:

            #------------------------------------------------------------------
            # Initialise force for this point
            #------------------------------------------------------------------
            force = 0

            #------------------------------------------------------------------
            # Sum all contributions to the force for this point
            #------------------------------------------------------------------
            for othPoint in self.points:

                if othPoint is not point:

                    dLoc = othPoint._vals['loc'] - point._vals['loc']  # Rozdiel lokálnych pravdepodobností
                    dVal = othPoint._pos ['x']   - point._pos['x']     # Rozdiel pozícií bodov v osi x

                    force += dLoc / dVal   # val pre rozne points v tom istom mrk nemozu byt rovnake

            #------------------------------------------------------------------
            # Set this point's force
            #------------------------------------------------------------------
            point._vals['for'] = force

        #----------------------------------------------------------------------
        # Recursively actualize nested Markov object for each point
        #----------------------------------------------------------------------
        for point in self.points:

            #------------------------------------------------------------------
            # Retrieve the nested Markov object for this point
            #------------------------------------------------------------------
            mrk = point._vals['mrk']

            if mrk is not None and isinstance(mrk, IMarkov):

                #--------------------------------------------------------------
                # Retrieve joint probability of this point as the probability for the nested Markov object
                #--------------------------------------------------------------
                newMrkPro = point._vals['pro']

                mrk.setNamePro(newMrkPro)
                mrk._compute(mrkPro=newMrkPro)

        #----------------------------------------------------------------------
        self.needCompute = False
        logger.info(f"{self.name}._compute: Probabilities and forces recalculated for {len(self.points)} points")

    #--------------------------------------------------------------------------
    def _maxForceRecursive(self, minForce=0.1, minObs=10, pattern=()):
        """Helper method to recursively crawl through all Markov patterns.

        Args:
            minForce (float): Minimum absolute value of the force threshold
            minObs     (int): Minimum observations threshold
            pattern  (tuple): Current pattern being built

        Returns:
            dict: Patterns found at this level and nested levels
        """

        logger.debug(f"{self.name}._maxForceRecursive: minForce={minForce}, minObs={minObs}, pattern={pattern}")
        toRet = {}

        #----------------------------------------------------------------------
        # Process all points in this level
        #----------------------------------------------------------------------
        for point in self.points:

            val = point.pos('x')
            new_pattern = pattern + (val,)

            frc = point._vals['for']
            obs = point._vals['obs']
            pro = point._vals['pro']

            #------------------------------------------------------------------
            # Add this pattern if it meets minForce threshold
            if abs(frc) >= minForce and obs >= minObs:
                toRet[new_pattern] = {'frc': frc, 'obs': obs, 'pro': pro}

            #------------------------------------------------------------------
            # Recursively process nested Markov if it exists
            #------------------------------------------------------------------
            mrk = point._vals['mrk']

            if mrk is not None and isinstance(mrk, IMarkov):
                nested = mrk._maxForceRecursive(minForce=minForce, minObs=minObs, pattern=new_pattern)
                toRet.update(nested)

        #----------------------------------------------------------------------
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

            if create:
                #--------------------------------------------------------------
                # Create new InfoPoint with pos == val
                #--------------------------------------------------------------
                point = self.initAdd(axeVal=val)

                #--------------------------------------------------------------
                # Compute equal probability for all points in this Markov analyser
                #--------------------------------------------------------------
                if point is not None:
                    self.eqProb = 1 / len(self.points) if len(self.points) > 0 else 1

                #--------------------------------------------------------------
                return point

            else:
                return None

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
           and must be found by iterating through the points.
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
