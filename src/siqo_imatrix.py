#==============================================================================
# Siqo class InfoMatrix
#------------------------------------------------------------------------------
import functools
import math
import cmath
import numpy                  as np
import random                 as rnd

from   siqolib.logger         import SiqoLogger
from   siqo_ipoint            import InfoPoint

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_VER    = '3.03'
_IND    = '|  '       # Info indentation
_UPP    = 10          # distance units per period

_F_POS  =  8          # Format for position

#==============================================================================
# package's variables
#------------------------------------------------------------------------------

#==============================================================================
# Only when matrix is not empty
#------------------------------------------------------------------------------
def noEmptyMatrix(function):
    "Assures matrix is not empty before calling decorated function"

    #--------------------------------------------------------------------------
    # Interna wrapper funkcia
    #--------------------------------------------------------------------------
    @functools.wraps(function)
    def wrapper(*args, **kwargs):

        #----------------------------------------------------------------------
        # Before decorated function
        #----------------------------------------------------------------------
        self = args[0]
        self.logger.debug(f"{self.name}.noEmptyMatrix: {function.__name__}")
        resp = None

        #----------------------------------------------------------------------
        # Kontrola existencie bodov v InfoMatrix
        #----------------------------------------------------------------------
        if self.count() > 0: resp = function(*args, **kwargs)
        else               : self.logger.warning(f"{self.name}.noEmptyMatrix: Matrix is empty, function {function.__name__} denied")

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

    #==========================================================================
    # Static variables & methods
    #--------------------------------------------------------------------------

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, name):
        "Calls constructor of InfoMatrix"

        self.logger = SiqoLogger(name, level='DEBUG')
        self.logger.info(f"InfoMatrix.constructor: {name}")

        #----------------------------------------------------------------------
        # Public datove polozky triedy
        #----------------------------------------------------------------------
        self.name       = name     # Name of the InfoMatrix
        self.ipType     = None     # Type of the InfoPoint in this InfoMatrix
        self.staticEdge = False    # Static edge means value of the edge points is fixed in some methods
        self.points     = []       # List of InfoPoints

        self.actVal     = None     # Key of the current InfoPoint's dat value
        self.actSubIdxs = {}       # Current active submatrix definition as dict of freezed axesKeys with values
        self.actList    = []       # Current active list of points in submatrix
        self.actChanged = True     # Current sub settings was changed and actSubMatrix needs refresh

        #----------------------------------------------------------------------
        # Private datove polozky triedy
        #----------------------------------------------------------------------
        self._cnts      = {}       # Number of InfoPoints in respective axes
        self._origs     = {}       # Origin's coordinates of the InfoMatrix for respective axes in lambda units
        self._rects     = {}       # Lenghts of the InfoMatrix for respective axes in lambda units
        self._diffs     = {}       # Distance between two points in respective axes in lambda units

        #----------------------------------------------------------------------
        # Inicializacia
        #----------------------------------------------------------------------

        #----------------------------------------------------------------------
        self.logger.info(f"{self.name}.constructor: done")

    #--------------------------------------------------------------------------
    def __str__(self):
        "Prints info about this InfoMatrix"

        return self.info()['msg']

    #--------------------------------------------------------------------------
    def __array__(self):
        "Returns InfoMatrix as 2D numpy array"

        mtrx = self.actSubmatrix(keyVal=self.actVal)

        #----------------------------------------------------------------------
        # Kontrola existencie vybranej 2D matice
        #----------------------------------------------------------------------
        if mtrx is None:
            self.logger.error(f"{self.name}.__array__: actMatrix is None")
            return None

        #----------------------------------------------------------------------
        # Vratim skonvertovane do np.array
        #----------------------------------------------------------------------
        return np.array(mtrx)

     #--------------------------------------------------------------------------
    def setIpType(self, ipType:dict, force:bool=False):
        "Apply InfoPoint.schema to internal structures _cnts, _origs, _rects for respective ipType"

        self.logger.warning(f"{self.name}.setIpType: ipType={ipType}")

        #----------------------------------------------------------------------
        # Kontrola zmeny ipType
        #----------------------------------------------------------------------
        if (self.ipType == ipType) and (not force):
            self.logger.warning(f"{self.name}.setIpType: ipType was not changed, no need to reset")
            return

        #----------------------------------------------------------------------
        # Reset all InfoMatrix's data
        #----------------------------------------------------------------------
        self.ipType     = ipType
        self.points     = []       # List of rows of lists of InfoPoints
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
        # Nastavenie axes
        #----------------------------------------------------------------------
        for key in InfoPoint.getAxes(self.ipType).keys():

            self._cnts [key] = 5
            self._origs[key] = 0
            self._rects[key] = 1

        #----------------------------------------------------------------------
        # Vypocet diffs
        #----------------------------------------------------------------------
        for key, cnt in self._cnts.items():

            if cnt > 1: self._diffs[key] = self._rects[key]/(cnt-1)  # Distance between two points in respective axes in lambda units
            else      : self._diffs[key] = 0                         # If only one point, distance is zero

   #--------------------------------------------------------------------------
    def info(self, indent=0, full=False):
        "Creates info about this InfoMatrix"

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
        dat['subProducts'   ] = self._subProducts()

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
    def count(self, check=True):
        "Returns Count of points in this InfoMatrix"

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
            self.logger.warning(f"{self.name}.count: Count of points {toRet} is not equal to len(points) {len(self.points)}, initialisation needed")
            self.init()

        #----------------------------------------------------------------------
        self.logger.debug(f"{self.name}.count: Count of points is {toRet}")
        return toRet

    #--------------------------------------------------------------------------
    def copy(self, name):
        "Creates copy of this InfoMatrix"

        self.logger.debug(f"{self.name}.copy: to {name}")

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
        "Clears schema of InfoPoint for respective ipType to {'axes':{'None':'None'}, 'vals':{}}"

        InfoPoint.clearSchema(self.ipType)
        self.setIpType(self.ipType, force=True)

    #--------------------------------------------------------------------------
    def equalSchema(self, schema) -> bool:
        "Check if schema is equal to the schema of respective InfoPoint type"

        return InfoPoint.equalSchema(self.ipType, schema)

    #--------------------------------------------------------------------------
    def isInSchema(self, *, axes:list=None, vals:list=None) -> bool:

        return InfoPoint.isInSchema(self.ipType, axes=axes, vals=vals)

    #--------------------------------------------------------------------------
    def getSchema(self) -> dict:
        "Returns schema for respective InfoPoint type as dict {'axes':{}, 'vals':{}}"

        return InfoPoint.getSchema(self.ipType)

    #--------------------------------------------------------------------------
    def setSchema(self, schema:dict):
        "Set schema for respective InfoPoint type as dict {'axes':{}, 'vals':{}}"

        return InfoPoint.setSchema(self.ipType, schema)

    #--------------------------------------------------------------------------
    # Schema axes methods
    #--------------------------------------------------------------------------
    def getAxes(self) -> dict:
        "Returns axes keys and names as dict {key: name}"

        return InfoPoint.getAxes(self.ipType)

    #--------------------------------------------------------------------------
    def setAxe(self, key, name):
        "Add axe key and name"

        InfoPoint.setAxe(self.ipType, key, name)
        self.setIpType(self.ipType, force=True)

    #--------------------------------------------------------------------------
    def axeIdxByKey(self, key) -> int:
        "Returns axe's idx for respective key as position in the list of axes othewise None"

        return InfoPoint.axeIdxByKey(self.ipType, key)

    #--------------------------------------------------------------------------
    def axeKeyByIdx(self, idx) -> str:
        "Returns axe's key for respective position in the list of axes othewise None"

        return InfoPoint.axeKeyByIdx(self.ipType, idx)

    #--------------------------------------------------------------------------
    def axeNameByKey(self, key) -> str:
        "Returns axe's Name for respective key as string othewise None"

        return InfoPoint.axeNameByKey(self.ipType, key)

     #--------------------------------------------------------------------------
    def axeKeyByName(self, name) -> str:
        "Returns axe's key for respective Name, othewise None"

        return InfoPoint.axeKeyByName(self.ipType, name)

    #--------------------------------------------------------------------------
    # Schema vals methods
    #--------------------------------------------------------------------------
    def getVals(self) -> dict:
        "Returns values keys and names as dict {key: name}"

        return InfoPoint.getVals(self.ipType)

    #--------------------------------------------------------------------------
    def setVal(self, key, name):
        "Sets value key and name"

        return InfoPoint.setVal(self.ipType, key, name)

    #--------------------------------------------------------------------------
    def valIdxByKey(self, key) -> int:
        "Returns value's idx for respective key as position in the list of axes othewise None"

        return InfoPoint.valIdxByKey(self.ipType, key)

    #--------------------------------------------------------------------------
    def valKeyByIdx(self, idx) -> str:
        "Returns value's key for respective position in the list of valus othewise None"

        return InfoPoint.valKeyByIdx(self.ipType, idx)

    #--------------------------------------------------------------------------
    def valNameByKey(self, key) -> str:
        "Returns value's Name for respective key as string othewise None"

        return InfoPoint.valNameByKey(self.ipType, key)

    #--------------------------------------------------------------------------
    def valKeyByName(self, name) -> str:
        "Returns val's key for respective Name, othewise None"

        return InfoPoint.valKeyByName(self.ipType, name)

    #--------------------------------------------------------------------------
    # Method's methods
    #--------------------------------------------------------------------------
    def mapShowMethods(self) -> dict:
        "Returns map of methods returning float number from keyed value"

        return InfoPoint.mapShowMethods()

    #--------------------------------------------------------------------------
    def mapMethods(self) -> dict:
        "Returns map of methods setting keyed value to function value for respective parameters"

        methods = InfoPoint.mapMethods()

        methods['<Matrix Methods>'] = {'matrixMethod': self.nullMethod, 'pointMethod':None,  'params':{}}

        return methods

    #==========================================================================
    # Position and indices tools
    #--------------------------------------------------------------------------
    def _subProducts(self) -> list:
        "Returns list of subproducts of _cnts [1, A, AB, ABC, ...]"

        toRet = [1]

        for cnt in self._cnts.values():
            toRet.append( cnt * toRet[-1] )

        #----------------------------------------------------------------------
        # Remove last element which is the product of all dimensions
        #----------------------------------------------------------------------
        toRet.pop()

        #----------------------------------------------------------------------
        self.logger.debug(f"{self.name}._subProducts: {toRet}")
        return toRet

    #--------------------------------------------------------------------------
    def _subPeriods(self, axeKey:str) -> tuple:
        "Returns period,serie & groups for respective axe"

        self.logger.debug(f"{self.name}._subPeriods: axeKey={axeKey}")

        subs   = self._subProducts()
        axePos = self.axeIdxByKey(axeKey)
        count  = self.count()

        #----------------------------------------------------------------------
        # Pocet Points v jednej grupe
        #----------------------------------------------------------------------
        serie  = subs[axePos  ]                            # Pocet Points v jednej grupe
        self.logger.debug(f"{self.name}._subPeriods: serie={serie} for axeKey={axeKey}")

        #----------------------------------------------------------------------
        # Perioda v akej sa opakuju grupy
        #----------------------------------------------------------------------
        if axePos+1>=len(subs): period = count
        else                  : period = subs[axePos+1]    # Perioda v akej sa opakuju grupy
        self.logger.debug(f"{self.name}._subPeriods: period={period} for axeKey={axeKey}")

        #----------------------------------------------------------------------
        # Pocet grup s indexom axeIdx v osi axeKey
        #----------------------------------------------------------------------
        groups = self.count() // period                    # Pocet grup s indexom axeIdx v osi axeKey
        self.logger.debug(f"{self.name}._subPeriods: groups={groups} for axeKey={axeKey}")

        return period, serie, groups

    #--------------------------------------------------------------------------
    def _possByAxeIdx(self, axeKey:str, axeIdx:int) -> set:
        "Returns set of positions of Points belonging to the axe with respective index axeIdx"

        self.logger.debug(f"{self.name}._possByAxeIdx: axeKey={axeKey}, axeIdx={axeIdx}")

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
        self.logger.debug(f"{self.name}._possByAxeIdx: Found {len(toRet)} positions for axeKey={axeKey}, axeIdx={axeIdx}")
        return toRet

    #--------------------------------------------------------------------------
    def _axeValByIdx(self, axeKey:str, axeIdx:int) -> float:
        "Returns value of the axe with respective index axeIdx in lambda units"

        self.logger.debug(f"{self.name}._axeValByIdx: axeKey={axeKey}, axeIdx={axeIdx}")

        #----------------------------------------------------------------------
        # Kontrola existencie osi
        #----------------------------------------------------------------------
        if axeKey not in self._cnts.keys():
            self.logger.error(f"{self.name}._axeValByIdx: Axe '{axeKey}' is not in InfoMatrix axes {list(self._cnts.keys())}")
            return None

        #----------------------------------------------------------------------
        # Vypocitam hodnotu osi
        #----------------------------------------------------------------------
        toRet = self._origs[axeKey] + (axeIdx * self._diffs[axeKey])

        self.logger.debug(f"{self.name}._axeValByIdx: axeVal={toRet} for axeKey={axeKey} and axeIdx={axeIdx}")
        return toRet

    #--------------------------------------------------------------------------
    def _idxByAxeVal(self, axeKey:str, axeVal:float) -> int:
        "Returns index in axe for respective coordinate"

        #----------------------------------------------------------------------
        # Kontrola existencie osi
        #----------------------------------------------------------------------
        if axeKey not in self._cnts.keys():
            self.logger.error(f"{self.name}._idxByAxeVal: Axe '{axeKey}' is not in InfoMatrix axes {list(self._cnts.keys())}")
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
        self.logger.debug(f"{self.name}._idxByAxeVal: axeKey={axeKey}, axeVal={axeVal} -> idx={toRet}")
        return toRet

    #--------------------------------------------------------------------------
    # One Point position tools
    #--------------------------------------------------------------------------
    def _posByIdxs(self, idxs:list) -> int:
        "Returns position of the InfoPoint in the list for respective indices"

        subProd = self._subProducts()

        pos = 0
        for i, idx in enumerate(idxs):
            pos += idx * subProd[i]

        self.logger.debug(f"{self.name}._posByIdxs: {idxs} -> pos={pos}")
        return pos

    #--------------------------------------------------------------------------
    def _idxsByPos(self, pos:int) -> list:
        "Returns indices of the InfoPoint for respective position in the list"

        #----------------------------------------------------------------------
        # Inicializacia
        #----------------------------------------------------------------------
        toRet = []
        subs  = self._subProducts()

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
    def pointByPos(self, pos:int) -> InfoPoint:
        "Returns InfoPoint in field for respective position"

        if (pos<0) or (pos>=len(self.points)):
            self.logger.error(f"{self.name}.pointByPos: pos={pos} is out of range <0,{len(self.points)-1}>")
            return None

        toRet = self.points[pos]
        return toRet

    #--------------------------------------------------------------------------
    def pointByIdxs(self, idxs:list) -> InfoPoint:
        "Returns InfoPoint in field at respective indexes"

        pos = self._posByIdxs(idxs)
        return self.pointByPos(pos)

    #--------------------------------------------------------------------------
    def pointByCoord(self, coord:dict) -> InfoPoint:
        "Returns nearest InfoPoint in field to respective coordinates"

        self.logger.debug(f"{self.name}.pointByCoord: coord sent={coord} and actSubIdxs={self.actSubIdxs}")

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
                self.logger.debug(f"{self.name}.pointByCoord: Axe '{axe}' found in coord, using value {axeVal}")

            elif axe in self.actSubIdxs.keys() and self.actSubIdxs[axe]:
                #--------------------------------------------------------------
                # Ak nie je dodana value pre danu os, pouzijem zmrazenu hodnotu pre danu os
                #--------------------------------------------------------------
                axeIdx = self.actSubIdxs[axe]
                axeVal = self._axeValByIdx(axeKey=axe, axeIdx=axeIdx)
                self.logger.warning(f"{self.name}.pointByCoord: Axe '{axe}' not in coord, using value {axeVal} for freezed index {axeIdx} ")

            else:
                #--------------------------------------------------------------
                # Ak nie je dodana value a ani nie je os zmrazena, pouzijem hodnotu z origu
                #--------------------------------------------------------------
                axeVal = self._origs[axe]
                self.logger.warning(f"{self.name}.pointByCoord: Axe '{axe}' is not in coord and not freezed, using origin value {axeVal}")

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
        self.logger.debug(f"{self.name}.pointByCoord: coord={coord} -> vals={vals} -> idxs={idxs} -> pos={pos}")
        return self.pointByPos(pos)

    #==========================================================================
    # Active submatrix tools
    #--------------------------------------------------------------------------
    # Active submatrix definition
    #--------------------------------------------------------------------------
    def _actSubSet(self, actSubIdxs:dict):
        """Sets active submatrix definition as dict of freezed axesKeys with values.
           If actSubIdxs definition changed from current definition, sets actChanged to True.
        """

        self.logger.info(f"{self.name}._actSubSet: To {actSubIdxs}")
        oldActSubIdxs = self.actSubIdxs.copy()

        #----------------------------------------------------------------------
        # Kontrola zmeny definicie
        #----------------------------------------------------------------------
        if self.actSubIdxs == actSubIdxs:

            self.actChanged = False
            self.logger.debug(f"{self.name}._actSubSet: actSubIdxs definition was not changed")
            return

        else: self.actChanged = True

        #----------------------------------------------------------------------
        # Kontrola novej definicie
        #----------------------------------------------------------------------
        for axe, axeIdx in actSubIdxs.items():

            if axe not in self._cnts.keys():
                self.logger.error(f"{self.name}._actSubSet: Axe '{axe}' is not in InfoMatrix axes {list(self._cnts.keys())}, change denied")
                return

        #----------------------------------------------------------------------
        # Nastavenie prazdnej aktivnej submatice
        #----------------------------------------------------------------------
        self.actSubIdxs  = actSubIdxs.copy()
        self.actList = []

        #----------------------------------------------------------------------
        self.logger.warning(f"{self.name}._actSubSet: definition was changed {oldActSubIdxs} -> {self.actSubIdxs}")

    #--------------------------------------------------------------------------
    # Active subsmatrix retrieval
    #--------------------------------------------------------------------------
    def actSubmatrix(self, actSubIdxs=None, force=False) -> list:
        """Returns active submatrix of InfoPoints as list of InfoPoints
        """

        self.logger.info(f"{self.name}.actSubmatrix: actSubIdxs={actSubIdxs}, force={force}")

        #----------------------------------------------------------------------
        # Nastavenie aktivnej submatice ak bola dodana definicia
        #----------------------------------------------------------------------
        if actSubIdxs is not None: self._actSubSet(actSubIdxs)

        #----------------------------------------------------------------------
        # Kontrola potreby obnovenia
        #----------------------------------------------------------------------
        if not self.actChanged and not force:
            self.logger.debug(f"{self.name}.actSubmatrix: subMatrix definition was not changed, no need to refresh")
            return self.actList

        #----------------------------------------------------------------------
        self.logger.info(f"{self.name}.actSubmatrix: Refresh for actSubIdxs={self.actSubIdxs}, force={force}")

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
                self.logger.debug(f"{self.name}.actSubmatrix: Axe '{axe}' is not freezed, skipping")
                continue

            #------------------------------------------------------------------
            # Ziskam mnozinu pozicii bodov patriacich danej osi
            #------------------------------------------------------------------
            actPoss = self._possByAxeIdx(axeKey=axe, axeIdx=axeIdx)

            #------------------------------------------------------------------
            # Vytvorim prienik poss s touto mnozinou pozicii
            #------------------------------------------------------------------
            poss = poss.intersection(actPoss)

        #----------------------------------------------------------------------
        # Create vector of InfoPoints for respective positions
        #----------------------------------------------------------------------
        self.actList.clear()  # Clear active list of points
        for pos in poss:
            self.actList.append(self.pointByPos(pos))

        #----------------------------------------------------------------------
        self.logger.info(f"{self.name}.actSubmatrix: Found {len(self.actList)} positions in active submatrix for actSubIdxs={self.actSubIdxs}")
        return self.actList

    #==========================================================================
    # Structure/Value modification
    #--------------------------------------------------------------------------
    def clear(self, *, defs:dict={}):
        "Set all InfoPoint's values to default value"

        self.logger.info(f"{self.name}.clear: defs={defs}")

        for point in self.points: point.clear(dat=defs)

    #--------------------------------------------------------------------------
    def init(self, defs:dict={} ):
        """Initialise InfoMatrix data to default values."""

        if self.ipType is None:
            self.logger.error(f"{self.name}.init: InfoPoint type is not defined, cannot initialise InfoMatrix")
            return

        self.logger.info(f"{self.name}.init: {self._cnts} points of type {self.ipType} on rect {self._rects} from {self._origs} with values {defs}")

        #----------------------------------------------------------------------
        # Destroy old data
        #----------------------------------------------------------------------
        self.points.clear()                     # Clear all points in the InfoMatrix

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
            point = InfoPoint(self.ipType, pos=coos, vals=defs)
            self.points.append(point)

        #----------------------------------------------------------------------
        # Final adjustments
        #----------------------------------------------------------------------
        self.logger.info(f"{self.name}.init: Created {len(self.points)} InfoPoints")

    #--------------------------------------------------------------------------

    #==========================================================================
    # Methods application
    #--------------------------------------------------------------------------
    def copyFrom(self, src, *, key=None, tgtSlice=(0,0,0,0), srcFrom=(0,0)) -> 'InfoMatrix':
        "Copy point's values from srcs 2D matrix into tgts 2D matrix"

        self.logger.info(f"{self.name}.copyFrom: From {src.name} starting at {srcFrom} to nodes {tgtSlice} for key={key}")

        #----------------------------------------------------------------------
        # Slice settings
        #----------------------------------------------------------------------
        tgtRowFrom = tgtSlice[0]
        tgtColFrom = tgtSlice[1]
        tgtRowTo   = tgtSlice[2] if tgtSlice[2] > 0 else self._rows-1
        tgtColTo   = tgtSlice[3] if tgtSlice[3] > 0 else self._cols-1

        srcRowFrom = srcFrom[0]
        srcColFrom = srcFrom[1]

        i = 0

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
                    self.logger.error(f"{self.name}.copyFrom: Target point[{tgtRow},{tgtCol}] does not exists")
                    break

                #--------------------------------------------------------------
                # Trying to get source node
                #--------------------------------------------------------------
                try:
                    srcPoint = src.pointByIdxs([srcRowFrom+tgtRow-tgtRowFrom, srcColFrom+tgtCol-tgtColFrom])
                except IndexError:
                    self.logger.error(f"{self.name}.copyFrom: Source point[{srcRowFrom+tgtRow-tgtRowFrom}, {srcColFrom+tgtCol-tgtColFrom}] does not exists")
                    break

                #--------------------------------------------------------------
                # Copy value from source to target node
                #--------------------------------------------------------------
                srcDat = srcPoint.get(key=key)
                tgtPoint.set(dat=srcDat)
                i += 1

        #----------------------------------------------------------------------
        self.logger.info(f"{self.name}.copyFrom: Copied {i} points")
        return self

    #==========================================================================
    # Dynamic Methods application
    #--------------------------------------------------------------------------
    def applyMatrixMethod(self, methodKey:str, valueKey:str, params:dict=None) -> bool:
        """Special matrix method for applying dynamic matrix methods.
           pointMethod : Name of the Point method to apply
           valueKey    : Key of the value to be set by the method
           params      : Parameters for the method as dict
        """

        self.logger.info(f"{self.name}.applyMatrixMethod: {methodKey}(params={params})")

        #----------------------------------------------------------------------
        # Ziskanie vykonavanej funkcie a parametrov
        #----------------------------------------------------------------------
        methods = self.mapMethods()

        if methodKey not in methods.keys():
            self.logger.error(f"{self.name}.applyMatrixMethod: '{methodKey}' is not in defined functions")
            return False

        else:
            method = methods[methodKey]

        #----------------------------------------------------------------------
        # Ak je definovana pointMethod, aplikujem ju pomocou applyPointMethod()
        #----------------------------------------------------------------------
        if 'pointMethod' in method.keys() and method['pointMethod'] is not None:

            pointMethod = method['pointMethod']
            self.logger.info(f"{self.name}.applyMatrixMethod: Applying pointMethod '{pointMethod.__name__}'")

            self._applyPointMethod(pointMethod=pointMethod, valueKey=valueKey, params=params)

        #----------------------------------------------------------------------
        # Ak je definovana matrixMethod, aplikujem ju priamo
        #----------------------------------------------------------------------
        elif 'matrixMethod' in method.keys() and method['matrixMethod'] is not None:

            matrixMethod = method['matrixMethod']
            self.logger.info(f"{self.name}.applyMatrixMethod: {matrixMethod.__name__}({params}) for value key='{valueKey}'")

            matrixMethod(valueKey=valueKey, params=params)   # self uz bolo predane pri priradeni do premennej matrixMethod

        #----------------------------------------------------------------------
        # Nie je definovana ziadna metoda
        #----------------------------------------------------------------------
        else:
            self.logger.error(f"{self.name}.applyMatrixMethod: '{methodKey}' has neither pointMethod nor matrixMethod defined")
            return False

        #----------------------------------------------------------------------
        self.logger.warning(f"{self.name}.applyMatrixMethod: {methodKey}({params}) for value key='{valueKey}' was applied to InfoMatrix")
        return True

    #--------------------------------------------------------------------------
    def _applyPointMethod(self, pointMethod, valueKey:str, params:dict=None) -> bool:
        """Special matrix method for applying Point methods to all or active subset of InfoPoints.
           pointMethod : Name of the Point method to apply
           valueKey    : Key of the value to be set by the method
           params      : Parameters for the method as dict
        """

        self.logger.info(f"{self.name}._applyPointMethod: {pointMethod.__name__}({params}) for value key='{valueKey}'")

        #----------------------------------------------------------------------
        # Ziskanie listu bodov na aplikovanie funkcie
        #----------------------------------------------------------------------
        if 'all' in params.keys() and params['all'] == True:
            tgtStr = 'all'
            tgtList = self.points

        else:
            tgtStr = 'active subset'
            tgtList = self.actList

        #----------------------------------------------------------------------
        # Vykonanie funkcie
        #----------------------------------------------------------------------
        pts = 0  # Counter of points

        for point in tgtList:
            pointMethod(self=point, valueKey=valueKey, params=params)
            pts += 1

        #----------------------------------------------------------------------
        self.logger.warning(f"{self.name}._applyPointMethod: {pointMethod.__name__} was applied to {tgtStr} {pts} InfoPoints")
        return True

    #==========================================================================
    # Matrix methods to apply in Dynamics methods
    #--------------------------------------------------------------------------
    def nullMethod(self, valueKey:str, params:dict):
        "Default null method for InfoPoint for keyed value (do nothing)"

        self.logger.debug(f"InfoPoint.nullMethod: do nothing for key '{valueKey}' with params {params}")

    #--------------------------------------------------------------------------
    def normAbs(self, nods, norm=None):
        "Normalise set of the nodes by sum of absolute values"

        self.logger.info(f"{self.name}.normAbs: ")

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
        self.logger.info(f"{self.name}.normAbs: norm = {norm} for {len(nods)} points")

    #==========================================================================
    # Persistency methods
    #--------------------------------------------------------------------------
    def toJson(self):
        "Converts node into json structure"

        self.logger.debug(f'{self.name}.toJson:')

        toRet = {}

        self.logger.debug(f'{self.name}.toJson: Converted')
        return toRet

#------------------------------------------------------------------------------
print(f"InfoMatrix ver {_VER}")

#==============================================================================
# Unit testy
#------------------------------------------------------------------------------
if __name__ == '__main__':

    #--------------------------------------------------------------------------
    # Test of the InfoMatrix class
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Vytvorenie, generovanie osi
    #--------------------------------------------------------------------------
    im = InfoMatrix('Test matrix')
    print(im)
    input('Press Enter to continue...')

    im.init()
    input('Press Enter to continue...')

    im.setIpType('ipTest')
    im.init()
    input('Press Enter to continue...')


    im.setAxe('a', 'Os A')
    im.setAxe('a', 'Os A')
    print(im.info(full=True)['msg'])
    input('Press Enter to continue...')

    im.init()
    print(im.info(full=True)['msg'])
    input('Press Enter to continue...')

    im.setVal('m', 'Hodnota M')
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