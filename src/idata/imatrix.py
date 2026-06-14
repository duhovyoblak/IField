#==============================================================================
# Siqo class InfoMatrix
#------------------------------------------------------------------------------
import functools
import math
import cmath
import numpy                  as np
import random                 as rnd

from   .                      import logger
from   .ipoint                import InfoPoint

#==============================================================================
# Module's constants
#------------------------------------------------------------------------------
_VER    = '3.4'
_IND    = '|  '       # Info indentation
_UPP    = 10          # distance units per period

_F_POS  =  8          # Format for position

#==============================================================================
# Module's variables
#------------------------------------------------------------------------------

#==============================================================================
# Only when matrix is not empty
#------------------------------------------------------------------------------
def noEmptyMatrix(function):
    """This decorator assures that matrix is not empty before calling decorated function.
       If matrix is empty, decorated function is not called and warning is logged.
    """

    #--------------------------------------------------------------------------
    # Interna wrapper funkcia
    #--------------------------------------------------------------------------
    @functools.wraps(function)
    def wrapper(*args, **kwargs):

        #----------------------------------------------------------------------
        # Before decorated function
        #----------------------------------------------------------------------
        self = args[0]
        logger.debug(f"{self.name}.noEmptyMatrix: {function.__name__}")
        resp = None

        #----------------------------------------------------------------------
        # Kontrola existencie bodov v InfoMatrix
        #----------------------------------------------------------------------
        if self.count() > 0: resp = function(*args, **kwargs)
        else               : logger.warning(f"{self.name}.noEmptyMatrix: Matrix is empty, function {function.__name__} denied")

        #----------------------------------------------------------------------
        # After decorated function
        #----------------------------------------------------------------------
        return resp

    #--------------------------------------------------------------------------
    # Koniec internej wrapper fcie
    #--------------------------------------------------------------------------
    return wrapper

#==============================================================================
# InfoMatrix
#------------------------------------------------------------------------------
class InfoMatrix:
    """Define InfoMatrix as a dynamic data structure of InfoPoints in the space
       defined by schema of respective InfoPoint type <ipType>.
       InfoMatrix is defined by its name and ipType.
       InfoMatrix contains list of InfoPoints and internal structures for fast
       retrieval of points by coordinates and definition of active submatrix.
       InfoMatrix can be copied and its ipType can be changed with reset of all data.
       InfoMatrix can be converted to 2D numpy array for visualization in IFieldMatrixGui.
    """

    #==========================================================================
    # Static variables & methods
    #--------------------------------------------------------------------------

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, name):
        """Calls constructor of InfoMatrix of respective name.
           Constructor initializes all public and private data structures of InfoMatrix.
           Constructor does not initialize points in InfoMatrix nor set ipType,
           it is expected that they will be added later.
        """

        logger.debug(f"InfoMatrix.constructor: {name}")

        #----------------------------------------------------------------------
        # Public datove polozky triedy
        #----------------------------------------------------------------------
        self.name         = name     # Name of the InfoMatrix
        self.ipType       = None     # Type of the InfoPoint in this InfoMatrix
        self.staticEdge   = False    # Static edge means value of the edge points is fixed in some methods
        self.points       = []       # List of InfoPoints

        self.actVal       = None     # Key of the current InfoPoint's dat value
        self.actSubIdxs   = {}       # Current active submatrix definition as dict of freezed axesKeys with values
        self.actList      = []       # Current active list of points in submatrix
        self.actChanged   = True     # Current sub settings was changed and actSubMatrix needs refresh

        #----------------------------------------------------------------------
        # Private datove polozky triedy, menia sa v metode init()
        #----------------------------------------------------------------------
        self._cnts        = {}       # Number of InfoPoints in respective axes
        self._origs       = {}       # Origin's coordinates of the InfoMatrix for respective axes in lambda units
        self._rects       = {}       # Lenghts of the InfoMatrix for respective axes in lambda units
        self._diffs       = {}       # Distance between two points in respective axes in lambda units

        self._subProducts = []       # List of subproducts of _cnts [1, A, AB, ABC, ...]
        self._lastPos     = None     # Last position used in pointByPos for faster access

        #----------------------------------------------------------------------
        # Inicializacia
        #----------------------------------------------------------------------

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.constructor: done")

    #--------------------------------------------------------------------------
    def __str__(self):
        """Returns string representation of this InfoMatrix.
        """

        return self.info()['msg']

    #--------------------------------------------------------------------------
    def __array__(self) -> np.array:
        """Returns active submatrix of the InfoMatrix as 2D numpy array.
           Value of the array is defined by self.actVal as key of the InfoPoint's dat value.
           This method is used for visualization of InfoMatrix in IFieldMatrixGui.

           This method is not good defined, FIX IN THE FUTURE
        """

        mtrx = self.actSubmatrix(keyVal=self.actVal)

        #----------------------------------------------------------------------
        # Kontrola existencie vybranej 2D matice
        #----------------------------------------------------------------------
        if mtrx is None:
            logger.error(f"{self.name}.__array__: actMatrix is None")
            return None

        #----------------------------------------------------------------------
        # Vratim skonvertovane do np.array
        #----------------------------------------------------------------------
        return np.array(mtrx)

     #--------------------------------------------------------------------------
    def setIpType(self, ipType:str, force:bool=False):
        """Set ipType of this InfoMatrix and reset all data.
           If not force, ipType is set only if it is different from the current one,
           otherwise warning is logged and ipType is not changed nor points are destroyed.
           If force or ipType is different than actual self.ipType, set self.ipType to ipType
           and set structures _cnts, _origs, _rects and _diffs to empty dict {}.
           Destroy all points in this InfoMatrix.
        """

        logger.info(f"{self.name}.setIpType: ipType='{ipType}', force={force}")

        #----------------------------------------------------------------------
        # Kontrola zmeny ipType
        #----------------------------------------------------------------------
        if (self.ipType == ipType) and (not force):
            logger.warning(f"{self.name}.setIpType: ipType was not changed, no need to reset")
            return

        #----------------------------------------------------------------------
        # Reset all InfoMatrix's data
        #----------------------------------------------------------------------
        self.points.clear()        # List of rows of lists of InfoPoints
        self.ipType     = ipType
        self.staticEdge = False    # Static edge means value of the edge nodes is fixed

        self.actVal     = None     # Key of the InfoPoint's current dat value
        self.actSubIdxs = {}       # Current active submatrix defined as dict of freezed axesKeys with values
        self.actList    = []       # Current active submatrix/subvector
        self.actChanged = True     # Current sub settings was changed and actSubMatrix needs refresh

        self._cnts      = {}       # Number of InfoPoints in respective axes
        self._origs     = {}       # Origin's coordinates of the InfoMatrix for respective axes in lambda units
        self._rects     = {}       # Lenghts of the InfoMatrix for respective axes in lambda units
        self._diffs     = {}       # Distance between two points in respective axes in lambda units

        #----------------------------------------------------------------------
        logger.warning(f"{self.name}.setIpType: ipType was set to '{ipType}' and InfoMatrix was reset")

   #--------------------------------------------------------------------------
    def info(self, indent=0, full=False) -> dict:
        """Creates info about this InfoMatrix.
           Identation is defined by indent as number of _IND for each line.
           If full is False, info contains only general info about this InfoMatrix.
           If full is True, info contains also info about all points in this InfoMatrix.
           Returns dict with keys 'res', 'dat' and 'msg' where
           'res' is 'OK' if info was created successfully,
           'dat' is dict of info data
           'msg' is string representation of info for printing.
        """

        dat = {}
        msg = ''

        #----------------------------------------------------------------------
        # info o celej strukture
        #----------------------------------------------------------------------
        dat['name'          ] = self.name
        dat['ipType'        ] = self.ipType
        dat['schema_axes'   ] = InfoPoint.getSchema(self.ipType)['axes']
        dat['schema_vals'   ] = InfoPoint.getSchema(self.ipType)['vals']
        dat['cnt of points' ] = self.count()
        dat['len(points)'   ] = len(self.points)
        dat['staticEdge'    ] = self.staticEdge

        dat['actVal'        ] = self.actVal
        dat['actSubIdxs'    ] = self.actSubIdxs
        dat['cnt of actList'] = len(self.actList)
        dat['actChanged'    ] = self.actChanged

        dat['cnts'          ] = self._cnts
        dat['origs'         ] = self._origs
        dat['rects'         ] = self._rects
        dat['diffs'         ] = self._diffs
        dat['subProducts'   ] = self._subProducts

        if indent == 0: msg = f"{indent*_IND}{60*'='}\n"

        for key, val in dat.items():
            msg += f"{indent*_IND}{key:<15}: {val}\n"

        #----------------------------------------------------------------------
        # info o vsetkych bodoch
        #----------------------------------------------------------------------
        if full:

            if indent == 0: msg += f"{indent*_IND}{60*'+'}\n"

            for pos, point in enumerate(self.points):
                idxs = self._idxsByPos(pos)
                msg += f"{pos:{_F_POS}} {idxs} {str(point)}\n"

            if indent == 0: msg += f"{indent*_IND}{60*'-'}\n"

        #----------------------------------------------------------------------
        return {'res':'OK', 'dat':dat, 'msg':msg}

    #--------------------------------------------------------------------------
    def count(self, check=True) -> int:
        """Returns Count of points in this InfoMatrix as sum of counts in respective
           axes as defined in _cnts.
           If check is True, checks if count of points is equal to len(points)
           and if not, logs warning and calls init() to recalculate count.
        """

        #----------------------------------------------------------------------
        # Pocet bodov podla _cnts
        #----------------------------------------------------------------------
        if len(self._cnts) == 0: toRet = 0

        else:
            toRet = 1
            for cnt in self._cnts.values():
                toRet *= cnt

        #----------------------------------------------------------------------
        # Kontrola, ci sa pocet bodov zhoduje s dlzkou zoznamu points
        #----------------------------------------------------------------------
        if check and (toRet != len(self.points)):
            logger.warning(f"{self.name}.count: Count of points {toRet} is not equal to len(points) {len(self.points)}, initialisation needed")
            self.init()

        #----------------------------------------------------------------------
        logger.debug(f"{self.name}.count: Count of points is {toRet} with check={check}")
        return toRet

    #--------------------------------------------------------------------------
    def copy(self, name) -> 'InfoMatrix':
        """Creates full copy of this InfoMatrix with new name.
        """

        logger.debug(f"{self.name}.copy: to {name}")

        #----------------------------------------------------------------------
        # Create new InfoMatrix with the same dimensions
        #----------------------------------------------------------------------
        toRet = InfoMatrix(name, self.ipType)

        toRet.points     = []                  # List of InfoPoints
        toRet.ipType     = self.ipType         # Type of the InfoPoint in this InfoMatrix
        toRet.staticEdge = self.staticEdge     # Static edge means value of the edge nodes is fixed

        toRet.actVal     = self.actVal         # Key of the InfoPoint's dat value
        toRet.actSubIdxs = self.actSubIdxs.copy()  # Current active submatrix defined as dict of freezed axesKeys with values
        toRet.actList    = []                  # Current active submatrix/subvector
        toRet.actChanged = True                # Current sub settings was changed and actSubMatrix needs refresh

        toRet._cnts      = self._cnts.copy()   # Number of InfoPoints in respective axes
        toRet._origs     = self._origs.copy()  # Origin's coordinates of the InfoMatrix
        toRet._rects     = self._rects.copy()  # Lengths of the InfoMatrix's axes
        toRet._diffs     = self._diffs.copy()  # Distance between two points in respective axes in lambda units

        #----------------------------------------------------------------------
        # Copy all points from this InfoMatrix to the new one
        #----------------------------------------------------------------------
        for point in self.points:
            toRet.points.append(self.copy())

        #----------------------------------------------------------------------
        return toRet

    #==========================================================================
    # Proxy tools for InfoPoint schema
    #--------------------------------------------------------------------------
    def clearSchema(self):
        """Clears schema of InfoPoint for respective ipType to {'axes':{}, 'vals':{}}.
           Destroys all points in this InfoMatrix.
        """

        InfoPoint.clearSchema(self.ipType)
        self.setIpType(self.ipType, force=True)

    #--------------------------------------------------------------------------
    def equalSchema(self, schema) -> dict:
        """Check if schema definition for ipType is equal to the testSchema as dict {ipType: {'axes':{}, 'vals':{}}}.
           Returns dict with keys 'exists', 'equalAxes', 'equalVals' and boolean values for respective checks.
        """

        return InfoPoint.equalSchema(self.ipType, schema)

    #--------------------------------------------------------------------------
    def isInSchema(self, *, axeKeys:list=None, valKeys:list=None) -> bool:
        """Returns True if schema has defined all provided axe keys and val keys in respective lists otherwise returns False
        """

        return InfoPoint.isInSchema(self.ipType, axeKeys=axeKeys, valKeys=valKeys)

    #--------------------------------------------------------------------------
    def getSchema(self) -> dict:
        """Returns copy of schema for respective InfoPoint type as dict {'axes':{}, 'vals':{}}
           If ipType is not defined in the schema yet, first create empty schema for this ipType.
        """

        return InfoPoint.getSchema(self.ipType)

    #--------------------------------------------------------------------------
    def setSchema(self, schema:dict):
        """Set schema for respective InfoPoint type as dict {'axes':{}, 'vals':{}}
           This method has no impact on InfoPoints of other ipTypes.
        """

        logger.warning(f"{self.name}.setSchema: schema={schema}")
        return InfoPoint.setSchema(self.ipType, schema)

    #--------------------------------------------------------------------------
    # Schema axes methods
    #--------------------------------------------------------------------------
    def getSchemaAxes(self) -> dict:
        """Returns axes keys and theirnames as dict {key: name} for respective ipType.
           If ipType is not defined in the schema yet, first create empty schema for this ipType.
        """

        return InfoPoint.getSchemaAxes(self.ipType)

    #--------------------------------------------------------------------------
    def setSchemaAxe(self, key, name):
        """Sets axe's key and name for respective ipType.
           If ipType is not defined in the schema yet, first create empty schema for this ipType.
           If axe exists in the schema already, redefine name.
           This method has no impact on InfoPoints of other ipTypes.
        """

        InfoPoint.setSchemaAxe(self.ipType, key, name)
        self.setIpType(self.ipType, force=True)

    #--------------------------------------------------------------------------
    def axeIdxByKey(self, key) -> int|None:
        """Returns axe's idx position in the dict of axes for respective key for respective ipType.
           If ipType is not defined in the schema, return None.
           If key is not defined in the schema for this ipType, return None.
        """

        return InfoPoint.axeIdxByKey(self.ipType, key)

    #--------------------------------------------------------------------------
    def axeKeyByIdx(self, idx) -> str|None:
        """Returns axe's key for respective idx position in the dict of axes for respective ipType.
           If ipType is not defined in the schema, return None.
           If idx is out of the range of axes for this ipType, return None.
        """

        return InfoPoint.axeKeyByIdx(self.ipType, idx)

    #--------------------------------------------------------------------------
    def axeNameByKey(self, key) -> str|None:
        """Returns axe's Name for respective key for respective ipType
           If ipType is not defined in the schema, return None.
           If key is not defined in the schema for this ipType, return None.
        """

        return InfoPoint.axeNameByKey(self.ipType, key)

     #--------------------------------------------------------------------------
    def axeKeyByName(self, name) -> str|None:
        """Returns axe's key for respective Name for respective ipType
           If ipType is not defined in the schema, return None.
           If name is not defined in the schema for this ipType, return None.
        """

        return InfoPoint.axeKeyByName(self.ipType, name)

    #--------------------------------------------------------------------------
    def axeCntByKey(self, key) -> int|None:
        """Returns axe's count of points for respective key.
           If key is not defined in the schema for this ipType, return None.
        """

        return self._cnts.get(key, None)

    #--------------------------------------------------------------------------
    # Schema vals methods
    #--------------------------------------------------------------------------
    def getSchemaVals(self) -> dict:
        """Returns values keys and names as dict {key: name} for respective ipType.
           If ipType is not defined in the schema yet, first create empty schema for this ipType.
        """

        return InfoPoint.getSchemaVals(self.ipType)

    #--------------------------------------------------------------------------
    def setSchemaVal(self, key, name):
        """Sets value key and name for respective ipType.
           If ipType is not defined in the schema, first create empty schema for this ipType.
           If value exists already, redefine name.
           This method has no impact on InfoPoints of other ipTypes.
        """

        return InfoPoint.setSchemaVal(self.ipType, key, name)

    #--------------------------------------------------------------------------
    def valIdxByKey(self, key) -> int|None:
        """Returns value's idx position in the dict of values for respective key for respective ipType.
           If ipType is not defined in the schema, return None.
           If key is not defined in the schema for this ipType, return None.
        """

        return InfoPoint.valIdxByKey(self.ipType, key)

    #--------------------------------------------------------------------------
    def valKeyByIdx(self, idx) -> str|None:
        """Returns value's key in the dict of values for respective idx position for respective ipType.
           If ipType is not defined in the schema, return None.
           If idx is not in the range, return None.
        """

        return InfoPoint.valKeyByIdx(self.ipType, idx)

    #--------------------------------------------------------------------------
    def valNameByKey(self, key) -> str|None:
        """Returns value's Name for respective key for respective ipType.
           If ipType is not defined in the schema, return None.
           If key is not defined in the schema for this ipType, return None.
        """

        return InfoPoint.valNameByKey(self.ipType, key)

    #--------------------------------------------------------------------------
    def valKeyByName(self, name) -> str|None:
        """Returns val's key for respective Name for respective ipType.
           If ipType is not defined in the schema, return None.
           If name is not defined in the schema for this ipType, return None.
        """

        return InfoPoint.valKeyByName(self.ipType, name)

    #--------------------------------------------------------------------------
    # Method's methods
    #--------------------------------------------------------------------------
    def mapShowMethods(self) -> dict:
        """Returns map of methods returning float number from keyed value mainly used to show the value of the point.
           Returns dict of {showMethodName: callable_function}.
        """

        return InfoPoint.mapShowMethods()

    #--------------------------------------------------------------------------
    def mapSetMethods(self) -> dict:
        """Returns map of methods for one InfoPoint setting keyed value to function value for respective parameters.
           Returns dict of {pointMethodName: {'pointMethod': callable_function, 'params':{paramName: defaultValue}, 'visible':True/False, 'type':'ask'/'noAsk'}}.
           params is dict of parameters for the method with default values.
           If type is 'ask', these parameters should be asked to user in GUI, if type is 'noAsk', these parameters are not asked to user and default values are used.
           If visible is False, this method should not be shown to user in GUI, if visible is True, this method should be shown to user in GUI.
        """

        methods = InfoPoint.mapSetMethods()

        methods['<Matrix Methods>'] = {'matrixMethod': self.nullMethod, 'pointMethod':None,  'params':{}                                        , 'visible':True, 'type':'ask'}
        methods['Move data'       ] = {'matrixMethod': self.moveData,   'pointMethod':None,  'params':{'axeKey':'x', 'startIdx':0, 'deltaIdx':1}, 'visible':True, 'type':'ask'}

        return methods

    #--------------------------------------------------------------------------
    def visibleMethodKeys(self) -> list:
        """Returns list of keys of mapped methods with 'visible'==True
        """

        methods = self.mapSetMethods()

        return [key for key, val in methods.items() if val.get('visible', True)]

    #==========================================================================
    # Internal tools for position and indices
    #--------------------------------------------------------------------------
    def _subPeriods(self, axeKey:str) -> tuple:
        """Returns period,serie & groups for respective axe"""

        logger.debug(f"{self.name}._subPeriods: axeKey={axeKey}")

        subs   = self._subProducts
        axePos = self.axeIdxByKey(axeKey)
        count  = self.count()

        #----------------------------------------------------------------------
        # Pocet Points v jednej grupe
        #----------------------------------------------------------------------
        serie  = subs[axePos  ]                            # Pocet Points v jednej grupe
        logger.debug(f"{self.name}._subPeriods: serie={serie} for axeKey={axeKey}")

        #----------------------------------------------------------------------
        # Perioda v akej sa opakuju grupy
        #----------------------------------------------------------------------
        if axePos+1>=len(subs): period = count
        else                  : period = subs[axePos+1]    # Perioda v akej sa opakuju grupy
        logger.debug(f"{self.name}._subPeriods: period={period} for axeKey={axeKey}")

        #----------------------------------------------------------------------
        # Pocet grup s indexom axeIdx v osi axeKey
        #----------------------------------------------------------------------
        groups = self.count() // period                    # Pocet grup s indexom axeIdx v osi axeKey
        logger.debug(f"{self.name}._subPeriods: groups={groups} for axeKey={axeKey}")

        return period, serie, groups

    #--------------------------------------------------------------------------
    def _possByAxeIdx(self, axeKey:str, axeIdx:int) -> set:
        """Returns set of positions of Points belonging to the axe with respective index axeIdx
           in the axe with respective key axeKey.
        """

        logger.debug(f"{self.name}._possByAxeIdx: axeKey={axeKey}, axeIdx={axeIdx}")

        #----------------------------------------------------------------------
        # Zistim hodnoty serie, period a groups pre danu os axeKey
        #----------------------------------------------------------------------
        period, serie, groups = self._subPeriods(axeKey)
        toRet = set()

        #----------------------------------------------------------------------
        # Prejdem vsetky grupy
        #-----------------------------------------------------------------------
        for grp in range(groups):

            #------------------------------------------------------------------
            # Vypocitam zaciatok a koniec grupy
            #------------------------------------------------------------------
            start = (grp * period) + (axeIdx * serie)
            stop  = start + serie

            #------------------------------------------------------------------
            # Vlozim Points s indexom axeIdx do zoznamu toRet
            #------------------------------------------------------------------
            for pos in range(start, stop):
                toRet.add(pos)

        #-----------------------------------------------------------------------
        logger.debug(f"{self.name}._possByAxeIdx: Found {len(toRet)} positions for axeKey={axeKey}, axeIdx={axeIdx}")
        return toRet

    #--------------------------------------------------------------------------
    def _axeValByIdx(self, axeKey:str, axeIdx:int) -> float:
        """Returns value of the axe with respective index axeIdx in lambda units
        """

        logger.debug(f"{self.name}._axeValByIdx: axeKey={axeKey}, axeIdx={axeIdx}")

        #----------------------------------------------------------------------
        # Kontrola existencie osi
        #----------------------------------------------------------------------
        if axeKey not in self._cnts.keys():
            logger.error(f"{self.name}._axeValByIdx: Axe '{axeKey}' is not in InfoMatrix axes {list(self._cnts.keys())}")
            return None

        #----------------------------------------------------------------------
        # Vypocitam hodnotu osi
        #----------------------------------------------------------------------
        toRet = self._origs[axeKey] + (axeIdx * self._diffs[axeKey])

        logger.debug(f"{self.name}._axeValByIdx: axeVal={toRet} for axeKey={axeKey} and axeIdx={axeIdx}")
        return toRet

    #--------------------------------------------------------------------------
    def _idxByAxeVal(self, axeKey:str, axeVal:float) -> int|None:
        """Returns index in axe for respective coordinate.
           If axeKey is not in the schema, returns None.
           If coordinate is out of boundaries, return respective first or last axe value
        """

        #----------------------------------------------------------------------
        # Kontrola existencie osi
        #----------------------------------------------------------------------
        if axeKey not in self._cnts.keys():
            logger.error(f"{self.name}._idxByAxeVal: Axe '{axeKey}' is not in InfoMatrix axes {list(self._cnts.keys())}")
            return None

        #----------------------------------------------------------------------
        # Odstrihnem extremy pred a po min/max hodnatach
        #----------------------------------------------------------------------
        if   axeVal <= self._origs[axeKey]                      : toRet = 0
        elif axeVal >= self._origs[axeKey] + self._rects[axeKey]: toRet = self._cnts[axeKey]-1
        else:
            #------------------------------------------------------------------
            # Vypocitam index v osi podla (axeVal-axeOrig)/diff
            #------------------------------------------------------------------
            idx = (axeVal - self._origs[axeKey]) / self._diffs[axeKey]
            toRet = int(round(idx))

        #----------------------------------------------------------------------
        logger.debug(f"{self.name}._idxByAxeVal: axeKey={axeKey}, axeVal={axeVal} -> idx={toRet}")
        return toRet

    #--------------------------------------------------------------------------
    # One Point position tools
    #--------------------------------------------------------------------------
    def _posByIdxs(self, idxs:list) -> int|None:
        """Returns position of the InfoPoint in the list of points for respective indices.
           If idxs has more or less indices than number of axes, logs error and returns None. FIX IN THE FUTURE
        """

        subProd = self._subProducts

        pos = 0
        for i, idx in enumerate(idxs):
            pos += idx * subProd[i]

        logger.debug(f"{self.name}._posByIdxs: {idxs} -> pos={pos}")
        return pos

    #--------------------------------------------------------------------------
    def _idxsByPos(self, pos:int) -> list|None:
        """Returns indices of the InfoPoint for respective position in the list of points.
           If pos is out of range, logs error and returns None. FIX IN THE FUTURE
        """

        #----------------------------------------------------------------------
        # Inicializacia
        #----------------------------------------------------------------------
        toRet = []
        subs  = self._subProducts

        #----------------------------------------------------------------------
        # Prechadzam reverzne vsetky dimenzie
        #----------------------------------------------------------------------
        for sub in reversed(subs):

            #------------------------------------------------------------------
            # Zistim index a novu poziciu ako zostatok pre danu dimenziu
            #------------------------------------------------------------------
            idx = pos // sub
            pos = pos %  sub

            #------------------------------------------------------------------
            # Vlozim index na zaciatok zoznamu idxs
            #------------------------------------------------------------------
            toRet.insert(0, idx)

        #----------------------------------------------------------------------
        return toRet

    #==========================================================================
    # InfoPoint retrieval
    #--------------------------------------------------------------------------
    def lastPosIdxs(self) -> list|None:
        """Returns indices of the InfoPoint for last position used in pointByPos.
           If last position is not defined, logs error and returns None.
        """

        if self._lastPos is None:
            logger.error(f"{self.name}.lastPosIdxs: No lastPos stored")
            return None

        return self._idxsByPos(self._lastPos)

    #--------------------------------------------------------------------------
    def pointByPos(self, pos:int=None) -> InfoPoint|None:
        """Returns InfoPoint in list of points for respective position.
           Stores given pos into self._lastPos for faster access in future calls of lastPosIdxs.
           If pos is out of range or does not exist, logs error and returns None.
        """

        self._lastPos = pos

        if pos is None:
            logger.error(f"{self.name}.pointByPos: pos is None")
            return None

        if (pos<0) or (pos>=len(self.points)):
            logger.error(f"{self.name}.pointByPos: pos={pos} is out of range <0,{len(self.points)-1}>")
            return None

        toRet = self.points[pos]
        return toRet

    #--------------------------------------------------------------------------
    def pointByIdxs(self, idxs:list) -> InfoPoint|None:
        """Returns InfoPoint at respective indexes.
           If such points do not exist, logs error and returns None.
        """

        pos = self._posByIdxs(idxs)
        return self.pointByPos(pos)

    #--------------------------------------------------------------------------
    def pointByCoord(self, coord:dict) -> InfoPoint|None:
        """Returns nearest InfoPoint in field to respective coordinates.
           If coord is not compatible with the schema of this InfoMatrix, logs error and returns None. FIX IN THE FUTURE
        """

        logger.debug(f"{self.name}.pointByCoord: coord={coord} and actSubIdxs={self.actSubIdxs}")

        vals = []  # List of axe values for debugging
        idxs = []  # List of indices for respective axes

        #----------------------------------------------------------------------
        # Prejdem vsetky osi a vypocitam index pre kazdu os
        #----------------------------------------------------------------------
        for axe in self._cnts.keys():

            print(f"{self.name}.pointByCoord: axe={axe}, coord={coord}")

            #------------------------------------------------------------------
            # Ziskanie value pre danu os
            #------------------------------------------------------------------
            if axe in coord.keys() and coord[axe]:
                #--------------------------------------------------------------
                # Ak je dodana value pre danu os, pouzijem ju
                #--------------------------------------------------------------
                axeVal = coord[axe]
                logger.debug(f"{self.name}.pointByCoord: Axe '{axe}' found in coord, using value {axeVal}")

            elif axe in self.actSubIdxs.keys() and self.actSubIdxs[axe]:
                #--------------------------------------------------------------
                # Ak nie je dodana value pre danu os, pouzijem zmrazenu hodnotu pre danu os
                #--------------------------------------------------------------
                axeIdx = self.actSubIdxs[axe]
                axeVal = self._axeValByIdx(axeKey=axe, axeIdx=axeIdx)
                logger.warning(f"{self.name}.pointByCoord: Axe '{axe}' not in coord, using value {axeVal} for freezed index {axeIdx} ")

            else:
                #--------------------------------------------------------------
                # Ak nie je dodana value a ani nie je os zmrazena, pouzijem hodnotu z origu
                #--------------------------------------------------------------
                axeVal = self._origs[axe]
                logger.warning(f"{self.name}.pointByCoord: Axe '{axe}' is not in coord and not freezed, using origin value {axeVal}")

            #------------------------------------------------------------------
            # Z axeVal vypocitam index v osi a vlozim ho do zoznamu idxs
            #------------------------------------------------------------------
            vals.append(axeVal)  # For debugging purposes
            idxs.append(self._idxByAxeVal(axeKey=axe, axeVal=axeVal))

        #----------------------------------------------------------------------
        # Z idxs vypocitam poziciu v zozname bodov
        #----------------------------------------------------------------------
        pos = self._posByIdxs(idxs)

        #----------------------------------------------------------------------
        logger.debug(f"{self.name}.pointByCoord: coord={coord} -> vals={vals} -> idxs={idxs} -> pos={pos}")
        return self.pointByPos(pos)

    #==========================================================================
    # Active submatrix tools
    #--------------------------------------------------------------------------
    # Active submatrix definition
    #--------------------------------------------------------------------------
    def _actSubSet(self, actSubIdxs:dict):
        """Sets active submatrix definition as dict of freezed axesKeys with values.
           If actSubIdxs definition is different from current definition, sets actChanged to True.
        """

        oldActSubIdxs = self.actSubIdxs.copy()
        logger.debug(f"{self.name}._actSubSet: {oldActSubIdxs}->{actSubIdxs}")

        #----------------------------------------------------------------------
        # Kontrola zmeny definicie (self.actChanged moze mat hodnotu True z inych dovodov)
        #----------------------------------------------------------------------
        if self.actSubIdxs != actSubIdxs: self.actChanged = True
        else                            : self.actChanged = False

        #----------------------------------------------------------------------
        # Ak nie je submatica zmenena, vratim sa
        #----------------------------------------------------------------------
        if not self.actChanged:
            logger.debug(f"{self.name}._actSubSet: actSubIdxs definition was not changed, no need to update")
            return

        #----------------------------------------------------------------------
        # Kontrola novej definicie
        #----------------------------------------------------------------------
        for axe, axeIdx in actSubIdxs.items():

            if axe not in self._cnts.keys():
                logger.error(f"{self.name}._actSubSet: Axe '{axe}' is not in InfoMatrix axes {list(self._cnts.keys())}, change denied")
                return

        #----------------------------------------------------------------------
        # Nastavenie prazdnej aktivnej submatice
        #----------------------------------------------------------------------
        self.actSubIdxs  = actSubIdxs.copy()
        self.actList = []

        #----------------------------------------------------------------------
        logger.warning(f"{self.name}._actSubSet: definition was changed {oldActSubIdxs} -> {self.actSubIdxs}")

    #--------------------------------------------------------------------------
    # Active subsmatrix retrieval
    #--------------------------------------------------------------------------
    def actSubmatrix(self, actSubIdxs=None, force=False) -> list:
        """Returns active submatrix of InfoPoints as list of InfoPoints also stored in self.actList.
           Submatrix is defined by dict of freezed axesKeys with values.
           If actSubIdxs is NOT provided, whole matrix became active submatrix.
        """

        logger.debug(f"{self.name}.actSubmatrix: actSubIdxs={actSubIdxs}, force={force}")

        #----------------------------------------------------------------------
        # Nastavenie aktivnej submatice ak bola dodana definicia
        #----------------------------------------------------------------------
        if actSubIdxs is not None: self._actSubSet(actSubIdxs   )
        else                     : self._actSubSet(actSubIdxs={}) # Full matrix will be active submatrix

        #----------------------------------------------------------------------
        # Kontrola potreby obnovenia aktivnej submatice pri zmene definicie submatice
        #----------------------------------------------------------------------
        if (not self.actChanged) and (not force):
            logger.debug(f"{self.name}.actSubmatrix: subMatrix definition was not changed, no need to refresh")
            return self.actList

        #----------------------------------------------------------------------
        logger.debug(f"{self.name}.actSubmatrix: Refresh for actSubIdxs={self.actSubIdxs}, force={force}")

        #----------------------------------------------------------------------
        # Inicializujem mnozinu pozicii submatrixu vsetkymi bodmi
        #----------------------------------------------------------------------
        poss = set(range(self.count())) # Set of positions of InfoPoints in the active submatrix

        #----------------------------------------------------------------------
        # Prejdem vsetky osi so zmrazenou hodnotou idx
        #----------------------------------------------------------------------
        for axe, axeIdx in self.actSubIdxs.items():

            #------------------------------------------------------------------
            # Kontrola, ci je daná os freezed
            #------------------------------------------------------------------
            if axeIdx is None:
                logger.debug(f"{self.name}.actSubmatrix: Axe '{axe}' is not freezed, skipping")
                continue

            #------------------------------------------------------------------
            # Ziskam mnozinu pozicii bodov patriacich danej osi
            #------------------------------------------------------------------
            actPoss = self._possByAxeIdx(axeKey=axe, axeIdx=axeIdx)

            #------------------------------------------------------------------
            # Vytvorim prienik poss s touto mnozinou pozicii = odstranim body, ktore nepatria do danej osi
            #------------------------------------------------------------------
            poss = poss.intersection(actPoss)
            logger.debug(f"{self.name}.actSubmatrix: After axe '{axe}' with idx {axeIdx}, {len(poss)} positions remain in active submatrix")

        #----------------------------------------------------------------------
        # Create vector of InfoPoints for respective positions
        #----------------------------------------------------------------------
        self.actList.clear()  # Clear active list of points
        for pos in poss:
            self.actList.append(self.pointByPos(pos))

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.actSubmatrix: Found {len(self.actList)} positions in active submatrix for actSubIdxs={self.actSubIdxs}")
        return self.actList

    #==========================================================================
    # Structure/Value modification
    #--------------------------------------------------------------------------
    def clearPoints(self, *, defs:dict={}):
        """Set all InfoPoint's values to 0. No change of structure.
           If defs is provided, set values to these provided in defs dict {valKey: valDef}.
        """

        logger.debug(f"{self.name}.clearPoints: defs={defs}")
        pts = 0

        for point in self.points:
            point.clear(vals=defs)
            pts += 1

        logger.warning(f"{self.name}.clearPoints: {pts} InfoPoints was set to defs={defs}")

    #--------------------------------------------------------------------------
    def init(self, *, cnts:dict={}, origs:dict={}, rects:dict={} ) -> int|None:
        """Initialise InfoMatrix structure with already set parameters
           or You can provide new matrix structure parameters.

           cnts  is dict of {axeKey: cnt} where cnt is count of points in respective axe.
           origs is dict of {axeKey: orig} where orig is origin coordinate in lambda units for respective axe.
           rects is dict of {axeKey: rect} where rect is rectangle in lambda units for respective axe.

           If origs is not provided, origin for respective axe will be set to 0.
           If rects is not provided, rectangle for respective axe will be set to (cnt-1)*diff where diff
              is distance between two points in respective axe.

           Returns count of created InfoPoints or None if initialization failed due to incompatible parameters or undefined ipType.
        """

        #----------------------------------------------------------------------
        # Kontrola definicie ipType
        #----------------------------------------------------------------------
        if self.ipType is None:
            logger.error(f"{self.name}.init: InfoPoint type is not defined, cannot initialise InfoMatrix")
            return None

        #----------------------------------------------------------------------
        # Kontrola kompatibility definicie ipType a cnts
        #----------------------------------------------------------------------
        schAxes = InfoPoint.getSchemaAxes(self.ipType)

        if cnts.keys() != schAxes.keys():
            logger.error(f"{self.name}.init: InfoPoint type '{self.ipType}' axes {list(schAxes.keys())} are not compatible with cnts axes {list(cnts.keys())}, cannot initialise InfoMatrix")
            return None

        #----------------------------------------------------------------------
        # Priprava na init()
        #----------------------------------------------------------------------
        logger.info(f"{self.name}.init: {cnts}, {origs}, {rects}")
        self.points.clear()    # Clear all points in the InfoMatrix

        #----------------------------------------------------------------------
        # Set new Matrix structure parameters
        #----------------------------------------------------------------------
        if cnts : self._cnts  = cnts
        if origs: self._origs = origs
        if rects: self._rects = rects

        for key, cnt in self._cnts.items():

            if key not in self._origs.keys(): self._origs[key] = 0
            if key not in self._rects.keys(): self._rects[key] = cnt-1

        logger.debug(f"{self.name}.init: {self._cnts} points of type '{self.ipType}' on rect {self._rects} from origins {self._origs}")

        #----------------------------------------------------------------------
        # Vypocet subProducts
        #----------------------------------------------------------------------
        self._subProducts = [1]

        for cnt in self._cnts.values():
            self._subProducts.append( cnt * self._subProducts[-1] )

        self._subProducts.pop()  # Remove last element which is the product of all dimensions

        #----------------------------------------------------------------------
        # Vypocet diffs
        #----------------------------------------------------------------------
        for key, cnt in self._cnts.items():

            if cnt > 1: self._diffs[key] = self._rects[key]/(cnt-1)  # Distance between two points in respective axes in lambda units
            else      : self._diffs[key] = 0                         # If only one point, distance is zero

        #----------------------------------------------------------------------
        # Generate InfoPoints at respective positions
        #----------------------------------------------------------------------
        point = None
        for pos in range(self.count(check=False)):

            #------------------------------------------------------------------
            # Compute coordinates of the InfoPoint for respective position and indices
            #------------------------------------------------------------------
            idxs = self._idxsByPos(pos)          # Get indices of the InfoPoint for respective position
            coos = {}                            # Coordinates of the InfoPoint in lambda units

            for i, key in enumerate(self._cnts.keys()):
                coos[key] = self._origs[key] + (idxs[i] * self._diffs[key])

            #------------------------------------------------------------------
            # Create new InfoPoint at respective coordinates
            #------------------------------------------------------------------
            point = InfoPoint(self.ipType, pos=coos)
            self.points.append(point)

        #----------------------------------------------------------------------
        # Active subset je full matrix
        #----------------------------------------------------------------------
        self.actSubmatrix(actSubIdxs={}, force=True)

        #----------------------------------------------------------------------
        pts = len(self.points)
        logger.warning(f"{self.name}.init: Created {pts} InfoPoints")
        return pts

    #--------------------------------------------------------------------------

    #==========================================================================
    # Matrix methods
    #--------------------------------------------------------------------------
    def copyFrom(self, src, *, key=None, tgtSlice=(0,0,0,0), srcFrom=(0,0)) -> 'InfoMatrix':
        "Copy point's values from srcs 2D matrix into tgts 2D matrix"

        logger.debug(f"{self.name}.copyFrom: From {src.name} starting at {srcFrom} to nodes {tgtSlice} for key={key}")
        pts = 0

        #----------------------------------------------------------------------
        # Slice settings
        #----------------------------------------------------------------------
        tgtRowFrom = tgtSlice[0]
        tgtColFrom = tgtSlice[1]
        tgtRowTo   = tgtSlice[2] if tgtSlice[2] > 0 else self._rows-1
        tgtColTo   = tgtSlice[3] if tgtSlice[3] > 0 else self._cols-1

        srcRowFrom = srcFrom[0]
        srcColFrom = srcFrom[1]

        #----------------------------------------------------------------------
        # Target rows from tgtRowFrom to tgtRowTo
        #----------------------------------------------------------------------
        for tgtRow in range(tgtRowFrom, tgtRowTo+1):

            #------------------------------------------------------------------
            # Target columns from tgtColFrom to tgtColTo
            #------------------------------------------------------------------
            for tgtCol in range(tgtColFrom, tgtColTo+1):

                #--------------------------------------------------------------
                # Get target node
                #--------------------------------------------------------------
                tgtPoint = self.pointByIdxs([tgtRow, tgtCol])
                if tgtPoint is None:
                    logger.error(f"{self.name}.copyFrom: Target point[{tgtRow},{tgtCol}] does not exists")
                    break

                #--------------------------------------------------------------
                # Trying to get source node
                #--------------------------------------------------------------
                try:
                    srcPoint = src.pointByIdxs([srcRowFrom+tgtRow-tgtRowFrom, srcColFrom+tgtCol-tgtColFrom])
                except IndexError:
                    logger.error(f"{self.name}.copyFrom: Source point[{srcRowFrom+tgtRow-tgtRowFrom}, {srcColFrom+tgtCol-tgtColFrom}] does not exists")
                    break

                #--------------------------------------------------------------
                # Copy value from source to target node
                #--------------------------------------------------------------
                srcDat = srcPoint.get(key=key)
                tgtPoint.set(dat=srcDat)
                pts += 1

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.copyFrom: Copied {pts} points")
        return self

    #--------------------------------------------------------------------------
    def moveByAxe(self, axeKey, startIdx, deltaIdx, defVals={}) -> int:
        """Move whole matrix data by deltaIdx from start index in respective axe.
           Positive deltaIdx moves data to higher indices, negative to lower indices.
           Data moved out of matrix bounds are lost, new data positions are cleared to default values.
           Returns count of moved points.
        """
        logger.debug(f"{self.name}.moveByAxe: From {startIdx} by {deltaIdx} for axe key={axeKey}")
        pts = 0

        #----------------------------------------------------------------------
        # Kontrola existencie osi
        #----------------------------------------------------------------------
        if axeKey not in self._cnts.keys():
            logger.error(f"{self.name}.moveByAxe: Axe '{axeKey}' is not in InfoMatrix axes {list(self._cnts.keys())}, change denied")
            return pts

        #----------------------------------------------------------------------
        # Ziskam poziciu axeKey v liste indexov osi
        #----------------------------------------------------------------------
        axePos = self.axeIdxByKey(axeKey)

        #----------------------------------------------------------------------
        # Ak index zvysujem, iterujem od najvyssieho indexu osi, inak od najnizsieho
        #----------------------------------------------------------------------
        if deltaIdx > 0: rng = range(self.axeCntByKey(axeKey)-1, startIdx-1,         -1)
        else           : rng = range(startIdx + deltaIdx , self.axeCntByKey(axeKey),  1)

        #----------------------------------------------------------------------
        # Prejdem vsetky indexy osi podla urceneho poradia v rng
        #----------------------------------------------------------------------
        for axeIdx in rng:

            #------------------------------------------------------------------
            # Ak je cielovy index mimo rozsah, preskocim ho
            #------------------------------------------------------------------
            if (axeIdx < 0) or (axeIdx >= self.axeCntByKey(axeKey)): continue

            #------------------------------------------------------------------
            # Vypocitam index v osi, z ktoreho budem kopirovat data
            #------------------------------------------------------------------
            srcIdx = axeIdx - deltaIdx

            #------------------------------------------------------------------
            # Ziskam mnozinu pozicii cielovych bodov danej osi s indexom axeIdx
            #------------------------------------------------------------------
            poss = self._possByAxeIdx(axeKey=axeKey, axeIdx=axeIdx)

            #------------------------------------------------------------------
            # Prejdem cielove bodoy a skopirujem data zo zdrojovych bodov alebo clear
            #------------------------------------------------------------------
            for pos in poss:

                point = self.pointByPos(pos)  # Ziskam bod na danej pozicii
                idxs  = self._idxsByPos(pos)  # Ziskam indexy pre danu poziciu

                #------------------------------------------------------------------
                # Ak som dosiahol zaciatok moved zony, nastavim values na defVals
                #------------------------------------------------------------------
                if ((deltaIdx > 0) and (srcIdx < startIdx)) or ((deltaIdx < 0) and (srcIdx >= self.axeCntByKey(axeKey))):

                    point.clear(vals=defVals)

                else:
                    #----------------------------------------------------------
                    # Ziskam bod na srcIdx pozicii v osi axeKey
                    #----------------------------------------------------------
                    idxs[axePos] = srcIdx
                    srcPoint = self.pointByIdxs(idxs)

                    #----------------------------------------------------------
                    # Skopirujem data z povodneho bodu do noveho bodu
                    #----------------------------------------------------------
                    point.set(vals=srcPoint.val())

            #------------------------------------------------------------------
            pts += len(poss)
            logger.debug(f"{self.name}.moveByAxe: {len(poss)}:{axeIdx}<-{srcIdx}")

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.moveByAxe: From {startIdx} by {deltaIdx} for axe key={axeKey} moved {pts} InfoPoints")
        return pts

    #==========================================================================
    # Dynamic Methods application
    #--------------------------------------------------------------------------
    def applyMatrixMethod(self, methodKey:str, valueKey:str, params:dict=None) -> int|None:
        """Special matrix method for applying dynamic matrix methods.
               methodKey : Name of the method to apply
               valueKey  : Key of the value to be set by the method
               params    : Parameters for the method as dict
           Returns count of updated InfoPoints or None if initialization failed due to incompatible parameters or undefined ipType.
        """

        logger.warning(f"{self.name}.applyMatrixMethod: methodKey='{methodKey}', valueKey='{valueKey}', params={params}")
        pts = 0

        #----------------------------------------------------------------------
        # Ziskanie vykonavanej funkcie a jej parametrov
        #----------------------------------------------------------------------
        methods = self.mapSetMethods()

        if methodKey not in methods.keys():
            logger.error(f"{self.name}.applyMatrixMethod: '{methodKey}' is not in defined functions, command denied")
            return None

        else:
            method = methods[methodKey]

        #----------------------------------------------------------------------
        # Ak je definovana pointMethod, aplikujem ju pomocou applyPointMethod()
        #----------------------------------------------------------------------
        if 'pointMethod' in method.keys() and method['pointMethod'] is not None:

            pointMethod = method['pointMethod']
            logger.debug(f"{self.name}.applyMatrixMethod: {pointMethod.__name__}({params}) for value key='{valueKey}'")

            pts = self._applyPointMethod(pointMethod=pointMethod, valueKey=valueKey, params=params)

        #----------------------------------------------------------------------
        # Ak je definovana matrixMethod, aplikujem ju priamo
        #----------------------------------------------------------------------
        elif 'matrixMethod' in method.keys() and method['matrixMethod'] is not None:

            matrixMethod = method['matrixMethod']
            logger.debug(f"{self.name}.applyMatrixMethod: {matrixMethod.__name__}({params}) for value key='{valueKey}'")

            pts = matrixMethod(valueKey=valueKey, params=params)   # self uz bolo predane pri priradeni do premennej matrixMethod

        #----------------------------------------------------------------------
        # Nie je definovana ziadna metoda
        #----------------------------------------------------------------------
        else:
            logger.error(f"{self.name}.applyMatrixMethod: '{methodKey}' has neither pointMethod nor matrixMethod defined")
            return None

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.applyMatrixMethod: {pts} InfoPoints was updated for '{valueKey}'<-{methodKey}({params})")
        return pts

    #--------------------------------------------------------------------------
    def _applyPointMethod(self, pointMethod, valueKey:str, params:dict=None) -> int|None:
        """Special matrix method for applying Point methods to all or active subset of InfoPoints.
               pointMethod : Name of the Point method to apply
               valueKey    : Key of the value to be set by the method
               params      : Parameters for the method as dict
            Returns count of updated InfoPoints or None if initialization failed due to incompatible parameters or undefined ipType.
        """

        logger.debug(f"{self.name}._applyPointMethod: {pointMethod.__name__}({params}) for value key='{valueKey}'")
        pts = 0

        #----------------------------------------------------------------------
        # Ziskanie listu bodov na aplikovanie funkcie
        #----------------------------------------------------------------------
        if 'all' in params.keys() and params['all'] == True: tgtList = self.points
        else                                               : tgtList = self.actList

        #----------------------------------------------------------------------
        # Vykonanie funkcie
        #----------------------------------------------------------------------
        pts = 0  # Counter of points

        for point in tgtList:
            pointMethod(point, valueKey=valueKey, params=params)
            pts += 1

        #----------------------------------------------------------------------
        logger.info(f"{self.name}._applyPointMethod: {pts} InfoPoints was updated for '{valueKey}'<-{pointMethod.__name__}({params})")
        return pts

    #==========================================================================
    # Matrix methods to apply in Dynamics methods
    #--------------------------------------------------------------------------
    def nullMethod(self, valueKey:str, params:dict) -> int|None:
        """Default null method for InfoPoint for keyed value (do nothing)
               valueKey : Key of the value to be set by the method
               params   : Parameters for the method as dict
           Returns count of updated InfoPoints or None if initialization failed due to incompatible parameters or undefined ipType.
        """

        logger.debug(f"{self.name}.nullMethod: do nothing for key '{valueKey}' with params {params}")
        return 1

    #--------------------------------------------------------------------------
    def moveData(self, valueKey:str, params:dict) -> int|None:
        """Move data in matrix by deltaIdx from startIdx in axeKey
               valueKey : Key of the value to be set by the method
               params   : Parameters for the method as dict
           Returns count of updated InfoPoints or None if initialization failed due to incompatible parameters or undefined ipType.
        """

        logger.debug(f"{self.name}.moveData: for key '{valueKey}' with params {params}")
        return self.moveByAxe(axeKey=params['axeKey'], startIdx=params['startIdx'], deltaIdx=params['deltaIdx'])

    #--------------------------------------------------------------------------
    def normAbs(self, nods, norm=None) -> int|None:
        """Normalise set of the nodes by sum of absolute values.
               valueKey : Key of the value to be set by the method
               params   : Parameters for the method as dict
           Returns count of updated InfoPoints or None if initialization failed due to incompatible parameters or undefined ipType.
        """

        logger.info(f"{self.name}.normAbs: ")

        #----------------------------------------------------------------------
        # Initialisation
        #----------------------------------------------------------------------
        sumAbs = 0
        for node in nods: sumAbs += node['cP'].abs()

        #----------------------------------------------------------------------
        # If norm does exists will be sumAbs
        #----------------------------------------------------------------------
        if norm is None: norm = sumAbs

        #----------------------------------------------------------------------
        # Iterate over nodes and apply norm if possible
        #----------------------------------------------------------------------
        if norm > 0:
            for node in nods: node['cP'].c /= norm

        else: norm = 1

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.normAbs: norm = {norm} for {len(nods)} points")

    #==========================================================================
    # Persistency methods
    #--------------------------------------------------------------------------
    def toJson(self):
        "Converts node into json structure"

        logger.debug(f'{self.name}.toJson:')

        toRet = {}

        logger.debug(f'{self.name}.toJson: Converted')
        return toRet

#==============================================================================
# Inicializacia modulu
#------------------------------------------------------------------------------
print(f"InfoMatrix ver {_VER}")

if __name__ == '__main__':

    logger.info("Testing InfoMatrix class")

    #--------------------------------------------------------------------------
    # Test of the InfoMatrix class
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Vytvorenie, generovanie osi
    #--------------------------------------------------------------------------
    im = InfoMatrix('Test matrix')
    im.logger.setLevel('DEBUG')

    print(im)
    print(80*'-')
    input('Press Enter to continue...')


    im.init()
    print(im)
    print(80*'-')
    input('Press Enter to continue...')

    im.setIpType('ipTest')
    im.init(cnts={'a':5, 'b':4})
    print(im)
    print(80*'-')
    input('Press Enter to continue...')


    im.setSchemaAxe('a', 'Os A')
    im.setSchemaAxe('a', 'Os A')
    im.setSchemaAxe('b', 'Os B')
    print(im.info(full=True)['msg'])
    input('Press Enter to continue...')

    im.init(cnts={'a':5, 'b':4})
    print(im.info(full=True)['msg'])
    input('Press Enter to continue...')

    im.setSchemaVal('m', 'Hodnota M')
    print(im.info(full=True)['msg'])


    #--------------------------------------------------------------------------
    # generovanie hodnot
    #--------------------------------------------------------------------------
    im.logger.setLevel('DEBUG')
    im.applyMatrixMethod(methodKey='Bandom Bniform', valueKey='m', params={'min':0, 'max':5})
    im.applyMatrixMethod(methodKey='Random uniform', valueKey='m', params={'min':0, 'max':5})
    print(im.info(full=True)['msg'])
    input('Press Enter to continue...')

    #--------------------------------------------------------------------------
    # Submatrix
    #--------------------------------------------------------------------------



#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
