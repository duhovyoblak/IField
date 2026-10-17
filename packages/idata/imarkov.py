#==============================================================================
# Siqo class IMarkov
#------------------------------------------------------------------------------
import math

from   .                      import logger
from   .idata                 import InfoData

#==============================================================================
# Module's constants
#------------------------------------------------------------------------------
_VER    = '1.1.10'
_IND    = '|  '                        # Info indentation

_IPTYPE_MARKOV = 'ipMarkovGen'

_AXES = {"x"   : "Value"}

_VALS = {"obs" : "Observations"
        ,"loc" : "Local prob"
        ,"pro" : "Joint prob"
        ,"for" : "Force"
        ,"mrk" : "Markov analyser"
        }

#==============================================================================
# Module's variables
#------------------------------------------------------------------------------
InfoData.setSchema(_IPTYPE_MARKOV, {"axes": _AXES, "vals": _VALS})

#==============================================================================
# IMarkov
#------------------------------------------------------------------------------
class IMarkov(InfoData):

    #==========================================================================
    # Static variables & methods
    #--------------------------------------------------------------------------
    _INFO_STRUCT    = True
    _INFO_HISTOGRAM = False

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
        self.setIpType(_IPTYPE_MARKOV)

        #----------------------------------------------------------------------
        # IMarkov specific parameters
        #----------------------------------------------------------------------
        self.param['dim'] = {'label': 'Počet vnímaných stavov', 'value': dim, 'type': 'int'}  # Dimension, e.g. number of previous states to consider in the Markov process

        #----------------------------------------------------------------------
        # Private datove polozky triedy
        #----------------------------------------------------------------------
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
        # Inicializujem histogram, na zaciatku neobsahuje zidne body, preto cnts=(0,)
        #----------------------------------------------------------------------
        self.init( cnts=(0,) )

        #----------------------------------------------------------------------
        logger.info(f"{self.param['name']['value']}.constructor: done")

    #--------------------------------------------------------------------------
    def setNamePro(self, mrkPro):
        """Name of Markov analyser has format 'Markov/(7)/(3){mrkPro}.
        This method sets the probability associated with this Markov analyser.
        """
        #----------------------------------------------------------------------
        # Odstranim z name {mrkPro} ak existuje
        #----------------------------------------------------------------------
        if '{' in self.param['name']['value'] and '}' in self.param['name']['value']:
            self.param['name']['value'] = self.param['name']['value'][:self.param['name']['value'].rfind('{')]

        #----------------------------------------------------------------------
        # Doplnim do name aktualnu hodnotu {mrkPro}
        #----------------------------------------------------------------------
        self.param['name']['value'] += f"{{{mrkPro:6.4f}}}"

    #--------------------------------------------------------------------------
    def __str__(self):
        """Return all info message lines joined with a newline after each line.
        """
        return ''.join(f'{msg}\n' for msg in self.info()['msg'])

    #--------------------------------------------------------------------------
    def info(self, indent=0, full=False) -> dict:
        """Create information about this Markov analyser.

           If `full` is True, include information about all points and nested
           Markov analysers. Return a dictionary with 'res', 'dat', and 'msg'
           keys; 'msg' is a list of individual message lines without trailing
           newline characters.
        """

        logger.debug(f"{self.param['name']['value']}.info: full={full}")
        dat = {}
        msg = []
        if indent == 0: msg = [f"{indent*_IND}{60*'='}"]


        struct    = self._INFO_STRUCT
        histogram = True if full else False

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
            dat['idType'        ] = self.param['idType']['value']
            dat['ipType'        ] = self.param['ipType']['value']
            dat['dim'           ] = self.param['dim']['value']
            dat['mrkPro'        ] = self.mrkPro
            dat['totObs'        ] = self.totObs
            dat['eqProb'        ] = self.eqProb
            dat['actVals'       ] = self.actVals

            #------------------------------------------------------------------
            # Add each structural field as a separate message line.
            #------------------------------------------------------------------
            for key, val in dat.items():
                msg.append(f"{indent*_IND}{key:<15}: {val}")

            #------------------------------------------------------------------
            # Active Points
            #------------------------------------------------------------------
            msg.append(f"{indent*_IND}")
            msg.append(f"{indent*_IND}Active Points")

            for actPt in self.actPoints():

                posStr = actPt._posStr()
                valStr = actPt._valsStr()

                dat[f'actPoint[{posStr}]'] = valStr
                msg.append(f"{indent*_IND}actPoint {posStr}: {valStr}")

            msg.append(f"{indent*_IND}")

        #----------------------------------------------------------------------
        # Include point and nested Markov details in full reports.
        #----------------------------------------------------------------------
        if histogram:

            msg.append(f"{indent*_IND}{60*'-'}")

            for point in self.points:

                #--------------------------------------------------------------
                # Prazdny riadok pred zmenou 1. urovne
                #--------------------------------------------------------------
                if indent == 0:
                    msg.append("|")

                #--------------------------------------------------------------
                # Riadok s informaciami o bode
                #--------------------------------------------------------------
                posStr = point._posStr()
                valStr = point._valsStr()

                dat[f'point[{posStr}]'] = valStr
                msg.append(f"{indent*_IND}point {posStr}: {valStr}")

                #--------------------------------------------------------------
                # Info o vnorenom Markov objekte, ak existuje
                #--------------------------------------------------------------
                mrk = point._vals['mrk'] if 'mrk' in point._vals else None

                if mrk is not None and isinstance(mrk, IMarkov):

                    res = mrk.info(indent=indent+1, full=True)

                    dat[f'point[{posStr}].mrk'] = res['dat']
                    msg.extend(res['msg'])

                #--------------------------------------------------------------

        #----------------------------------------------------------------------
        logger.info(f"{self.param['name']['value']}.info: Created info")
        return {'res': 'OK', 'dat': dat, 'msg': msg}

    #--------------------------------------------------------------------------
    def getCreateParams(self)->list:
        """Returns list of params to be asked from the user during create dialogue.
        """

        return ['dim']

    #--------------------------------------------------------------------------
    def useCreateParams(self):
        """Use the class-specific parameters obtained during the creation of the InfoData.
        """

        self.setDim(self.param['dim']['value'])

    #--------------------------------------------------------------------------
    def reset(self):
        """Resets the Markov analyser to its initial state.
        """

        logger.debug(f"{self.param['name']['value']}.reset: Resetting Markov analyser")

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
        logger.info(f"{self.param['name']['value']}.reset: Markov analyser reset complete")

    #--------------------------------------------------------------------------
    def setDim(self, dim:int):
        """Sets the dimension of the Markov analyser.
        """

        logger.debug(f"{self.param['name']['value']}.setDim: dim={dim}")

        #----------------------------------------------------------------------
        # Check if the dimension is valid
        #----------------------------------------------------------------------
        if dim < 1:
            logger.error(f"{self.param['name']['value']}.setDim: Invalid dimension {dim}, must be >= 1")
            return

        #----------------------------------------------------------------------
        # Reset analyser and set the dimension
        #----------------------------------------------------------------------
        self.reset()
        self.param['dim']['value'] = dim

        #----------------------------------------------------------------------
        logger.info(f"{self.param['name']['value']}.setDim: Markov analyser dimension set to {self.param['dim']['value']}")

    #--------------------------------------------------------------------------
    def actPoints(self) -> list:
        """Returns list of the active Points in the Markov process.
        """

        logger.debug(f"{self.param['name']['value']}.actPoints:")
        toRet = []

        #---------------------------------------------------------------------
        # If there is no active point, return an empty list
        #---------------------------------------------------------------------
        if self.actPoint is None:
            logger.info(f"{self.param['name']['value']}.actPoints: [No active point]")
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
        logger.info(f"{self.param['name']['value']}.actPoints: Found {len(toRet)} active Points")
        return toRet

    #--------------------------------------------------------------------------
    def actAddress(self) -> str:
        """Returns string representation of the active Points in the Markov process.
        """

        logger.debug(f"{self.param['name']['value']}.actAddress:")
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
        logger.info(f"{self.param['name']['value']}.actAddress: '{toRet}'")
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

        logger.debug(f"{self.param['name']['value']}.observe: val={val}")
        self.needCompute = True

        #----------------------------------------------------------------------
        # Move one step forward and observe the new value
        #----------------------------------------------------------------------
        toRet = self.moveFwd(val=val, observe=True)

        #----------------------------------------------------------------------
        logger.info(f"{self.param['name']['value']}.observe: '{val}' added")
        return toRet

    #--------------------------------------------------------------------------
    def amend(self, val:int)->int|None:
        """Advance the Markov analyser without recording a new observation.

        Probabilities are recomputed when necessary and the active Markov path
        is moved forward. The expected-value calculation is not implemented yet,
        so this method currently returns None.
        """

        logger.info(f"{self.param['name']['value']}.amend: val={val}")
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

        logger.info(f"{self.param['name']['value']}.generate: observe={observe}")
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

        logger.info(f"{self.param['name']['value']}.maxForce: minForce={minForce}, minObs={minObs}, maxPatterns={maxPatterns}")

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
        logger.info(f"{self.param['name']['value']}.maxForce: Found {len(sorted_toRet)} patterns with force >= {minForce}")
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

        logger.debug(f"{self.param['name']['value']}._moveFwd: val={val}")

        #----------------------------------------------------------------------
        # Move one step forward = last (dim-1) values from actVals plus new value val
        # Note: For dim=1, we keep only the current value (sliding window size = 1)
        # For dim=2, we keep the last 1 value plus new value (sliding window size = 2)
        # etc.
        #----------------------------------------------------------------------
        dim = self.param['dim']['value']

        if dim > 1: self.actVals = self.actVals[-(dim-1):] + [val]
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

        logger.debug(f"{self.param['name']['value']}._activate: actVals={actVals}")
        toRet = False

        #----------------------------------------------------------------------
        # Check length of the actVals list
        #----------------------------------------------------------------------
        if len(actVals) == 0:
            logger.error(f"{self.param['name']['value']}._activate: actVals list is empty, cannot activate dim={self.param['dim']['value']}")
            return toRet

        #----------------------------------------------------------------------
        # Pop the leftmost value from actVals and use it as the new observation value for this dimension
        #----------------------------------------------------------------------
        val = actVals.pop(0)
        logger.debug(f"{self.param['name']['value']}._activate: val={val}")

        #----------------------------------------------------------------------
        # Find/create InfoPoint with pos == val in this dimension of the Markov process
        #----------------------------------------------------------------------
        self.actPoint = self._getPoint(val=val, create=True)

        if self.actPoint is None:
            logger.error(f"{self.param['name']['value']}._activate: Failed to find or add InfoPoint with pos={val} to the Markov analyser")
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

        if self.param['dim']['value'] > 1:

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
                    nextMark = IMarkov(name=f"{self.param['name']['value']}/({val})", dim=self.param['dim']['value']-1)
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
                logger.error(f"{self.param['name']['value']}._activate: actVals list is not empty in the last dimension, remaining values: {actVals}")
                toRet = False

        #----------------------------------------------------------------------
        logger.debug(f"{self.param['name']['value']}._activate: Activation status: {toRet}")
        return toRet

    #--------------------------------------------------------------------------
    def _compute(self, mrkPro=1.0):
        """Recalculate all probabilities and forces for all points in this Markov layer.

        This method propagates probability (mrkPro) associated with this Markov analyser
        from parent dimension through all points and their nested Markov objects.

        Args:
            mrkPro   (float): Probability asociated with this Markov analyser (default: 1.0 at root level)
        """

        logger.debug(f"{self.param['name']['value']}._compute: mrkPro={mrkPro}")

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
        logger.info(f"{self.param['name']['value']}._compute: Probabilities and forces recalculated for {len(self.points)} points")

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

        logger.debug(f"{self.param['name']['value']}._maxForceRecursive: minForce={minForce}, minObs={minObs}, pattern={pattern}")
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

        logger.debug(f"{self.param['name']['value']}._getPoint: val={val} with create={create}")

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

        logger.debug(f"{self.param['name']['value']}._idxByAxeVal: axeKey={axeKey}, axeVal={axeVal}")
        toRet = None

        #----------------------------------------------------------------------
        # Kontrola existencie osi
        #----------------------------------------------------------------------
        if axeKey not in self._cnts.keys():
            logger.error(f"{self.param['name']['value']}._idxByAxeVal: Axe '{axeKey}' is not in InfoData axes {list(self._cnts.keys())}")
            return toRet

        #----------------------------------------------------------------------
        # Prechadzam vsetky InfoPoints az po _pos[axeKey] == axeVal
        #----------------------------------------------------------------------
        for idx, point in enumerate(self.points):

            if point._pos[axeKey] == axeVal:
                toRet = idx
                break

        #----------------------------------------------------------------------
        logger.debug(f"{self.param['name']['value']}._idxByAxeVal: axeKey={axeKey}, axeVal={axeVal} -> idx={toRet}")
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

        logger.info(f"{self.param['name']['value']}.deltas: {outData.param['name']['value']}[{outKey}] = <Deltas>({inKey}) with params {params}")
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
        logger.info(f"{self.param['name']['value']}.deltas: {pts} InfoPoints was updated for key '{outKey}' in deltas")

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
