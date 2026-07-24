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
        dat['address'       ] = self.actAddress()
        dat['totObs'        ] = self.totObs

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
    def actAddress(self) -> str:
        """Returns string representation of the actual address in the Markov process.
        """

        logger.info(f"{self.name}.actAddress: actPoint={self.actPoint}")

        #---------------------------------------------------------------------
        # If there is no active point, return a message indicating that
        #---------------------------------------------------------------------
        if self.actPoint is None:
            return f"{self.name}:[No active point]"

        #---------------------------------------------------------------------
        # If there is an active point, build its address
        #---------------------------------------------------------------------
        addr = f"{self.name}:[{self.actPoint._pos['x']}]"

        #---------------------------------------------------------------------
        # If there is a Markov analyser for the next dimension, dive into it
        #---------------------------------------------------------------------
        mrk = self.actPoint._vals['mrk']

        if mrk is not None and isinstance(mrk, IMarkov):  # Default hodnota po InitAdd je 0
            addr += f" <- {mrk.actAddress()}"

        #---------------------------------------------------------------------
        return addr

    #==========================================================================
    # IMarkov methods
    #--------------------------------------------------------------------------
    def observe(self, val:int):
        """Add new observation to the Markov analyser.
        """

        logger.info(f"{self.name}.observe: val={val}")

        res = self._moveFwd(val=val)


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
    # Internal methods for IMarkov
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

    #--------------------------------------------------------------------------
    def _getPoint(self, val:int, create=False):
        """Returns InfoPoint in this Markov analyser with pos = val.
        If create is True, creates new InfoPoint with pos = val if it does not exist.
        If create is False, returns None if InfoPoint with pos = val does not exist.
        """

        logger.info(f"{self.name}._getPoint: val={val} with create={create}")

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
    def _moveFwd(self, val:int) -> int|None:
        """Move values of the chain of Markov analysers forward with the new observation value.

        M(dim).val <- M(dim-1).val <- M(dim-2).val <- ... <- M(1).val
        Observe the value val in the last dimension of the Markov process and update the chain of Markov analysers accordingly.

        Returns last observed value of the Markov process for updating actPoint in parent dimension or None.
        """

        logger.info(f"{self.name}._moveFwd: val={val}")

        #----------------------------------------------------------------------
        # Save last value of the Markov process to return to parent dimension
        #----------------------------------------------------------------------
        if self.actPoint is not None: lastVal = self.actPoint._pos['x']
        else                        : lastVal = None

        #----------------------------------------------------------------------
        # Check if this is the last dimension of the Markov process
        #----------------------------------------------------------------------
        if self.dim == 1:

            #------------------------------------------------------------------
            # Last dimension reached. Find/create InfoPoint with pos == val
            #------------------------------------------------------------------
            self.actPoint = self._getPoint(val=val, create=True)

            if self.actPoint is None:
                logger.error(f"{self.name}._moveFwd: Failed to find or add InfoPoint with pos={val} to the Markov analyser")
                return None

            #------------------------------------------------------------------
            # Observe the value val in the Markov analyser
            #------------------------------------------------------------------
            self.actPoint._vals['obs'] += 1
            self.totObs += 1

        else:
            #------------------------------------------------------------------
            # Not last dimension, dive into next dimension or initialise it
            #------------------------------------------------------------------
            if self.actPoint is None:

                #--------------------------------------------------------------
                # Analyser is not initialised yet, create new InfoPoint with pos = val and initialise next dimension Markov analyser
                #--------------------------------------------------------------
                self.actPoint = self.initAdd(axeVal=val)

                if self.actPoint is None:
                    logger.error(f"{self.name}._moveFwd: Failed to add new InfoPoint with pos={val} to the Markov analyser")
                    return None

                #--------------------------------------------------------------
                # Create Markov analyser for the next dimension
                #--------------------------------------------------------------
                nextMark = IMarkov(name=f"{self.name}/({val})", dim=self.dim-1, axeName=self.axeNameByKey('x'))
                self.actPoint.set(vals={'mrk': nextMark})

                #--------------------------------------------------------------
                # Observe the value val in the Markov analyser
                #--------------------------------------------------------------
                self.actPoint._vals['obs'] += 1
                self.totObs += 1

            else:
                #--------------------------------------------------------------
                # Analyser is initialised, dive into the next dimension of the Markov process
                #--------------------------------------------------------------
                lastVal = self.actPoint._vals['mrk']._moveFwd(val=val)

                #--------------------------------------------------------------
                # If lastVal is not None, move self.actPoint to the InfoPoint with pos == lastVal in the current dimension
                #--------------------------------------------------------------
                if lastVal is not None:

                    #----------------------------------------------------------
                    # Find/create InfoPoint with pos == lastVal
                    #----------------------------------------------------------
                    self.actPoint = self._getPoint(val=lastVal, create=True)

                    if self.actPoint is None:
                        logger.error(f"{self.name}._moveFwd: Failed to add new InfoPoint with pos={lastVal} to the Markov analyser")
                        return None

                    #----------------------------------------------------------
                    # Create Markov analyser for the next dimension if it does not exist
                    #----------------------------------------------------------
                    if self.actPoint._vals['mrk'] is None:

                        nextMark = IMarkov(name=f"{self.name}/({val})", dim=self.dim-1, axeName=self.axeNameByKey('x'))
                        self.actPoint.set(vals={'mrk': nextMark})

                    #----------------------------------------------------------
                    # Observe the value val in the Markov analyser
                    #----------------------------------------------------------
                    self.actPoint._vals['obs'] += 1
                    self.totObs += 1

                else:
                    #----------------------------------------------------------
                    # lastVal is None, do not move forward in the Markov process
                    #----------------------------------------------------------
                    logger.debug(f"{self.name}._moveFwd: Cannot move forward in the Markov process, lastVal is None")
                    return None

        #----------------------------------------------------------------------
        return lastVal  # Return last value to parent dimension

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
