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
    def __init__(self, name, ipType):
        "Calls constructor of InfoMatrix"

        self.logger = SiqoLogger(name, level='DEBUG')
        self.logger.info(f"InfoMatrix.constructor: {name}")

        #----------------------------------------------------------------------
        # Public datove polozky triedy
        #----------------------------------------------------------------------
        self.name       = name     # Name of the InfoMatrix
        self.ipType     = ipType   # Type of the InfoPoint in this InfoMatrix
        self.staticEdge = False    # Static edge means value of the edge points is fixed in some methods
        self.points     = []       # List of InfoPoints

        self.actVal     = None     # Key of the current InfoPoint's dat value
        self.actSub     = {}       # Current active submatrix definition as dict of freezed axesKeys with values
        self.actList    = []       # Current active list of points in submatrix
        self.actChanged = True     # Current sub settings was changed and actSub needs refresh

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
        InfoPoint.checkSchema(ipType)

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
    def reset(self, ipType=None):
        "Resets all InfoMatrix's data and destroys all points. Count of points will be 0"

        self.logger.warning(f"{self.name}.reset: ipType={ipType}")

        #----------------------------------------------------------------------
        # Reset ipType if it is not None
        #----------------------------------------------------------------------
        if ipType is not None:

            self.ipType = ipType
            InfoPoint.checkSchema(ipType)
            self.logger.warning(f"{self.name}.reset: ipType changed to {self.ipType}")

        #----------------------------------------------------------------------
        # Reset all InfoMatrix's data
        #----------------------------------------------------------------------
        self.points     = []       # List of rows of lists of InfoPoints
        self.staticEdge = False    # Static edge means value of the edge nodes is fixed

        self.actVal     = None     # Key of the InfoPoint's current dat value
        self.actSub     = {}       # Current active submatrix defined as dict of freezed axesKeys with values
        self.actList    = []       # Current active submatrix/subvector
        self.actChanged = True     # Current sub settings was changed and actSub needs refresh

        self._cnts      = {}       # Number of InfoPoints in respective axes
        self._origs     = {}       # Origin's coordinates of the InfoMatrix
        self._rects     = {}       # Lenghts of the InfoMatrix for respective axes in lambda units
        self._diffs     = {}       # Distance between two points in respective axes in lambda units

        self.logger.info(f"{self.name}.reset: done")

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
        dat['actSub'        ] = self.actSub
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
            self.logger.critical(f"{self.name}.count: Count of points {toRet} is not equal to len(points) {len(self.points)}, Matrix terminated")
            self.reset()
            toRet = 0

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
        toRet.actSub     = self.actSub.copy()  # Current active submatrix defined as dict of freezed axesKeys with values
        toRet.actList    = []                  # Current active submatrix/subvector
        toRet.actChanged = True                # Current sub settings was changed and actSub needs refresh

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

        self.reset()
        return InfoPoint.clearSchema(self.ipType)

    #--------------------------------------------------------------------------
    def isInSchema(self, *, axes:list=None, vals:list=None) -> bool:

        return InfoPoint.isInSchema(self.ipType, axes=axes, vals=vals)

    #--------------------------------------------------------------------------
    def getSchema(self) -> dict:
        "Returns schema for respective InfoPoint type as dict {'axes':{}, 'vals':{}}"
        return InfoPoint.getSchema(self.ipType)

    #--------------------------------------------------------------------------
    # Schema axes methods
    #--------------------------------------------------------------------------
    def getAxes(self) -> dict:
        "Returns axes keys and names as dict {key: name}"
        return InfoPoint.getAxes(self.ipType)

    #--------------------------------------------------------------------------
    def setAxe(self, key, name):
        "Add axe key and name"

        if key not in self._cnts. keys(): self._cnts [key] = 0
        if key not in self._origs.keys(): self._origs[key] = 0
        if key not in self._rects.keys(): self._rects[key] = 0
        if key not in self._diffs.keys(): self._origs[key] = 0

        return InfoPoint.setAxe(self.ipType, key, name)

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
    def mapSetMethods(self) -> dict:
        "Returns map of methods setting keyed value to function value for respective parameters"
        return InfoPoint.mapSetMethods()

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

        self.logger.debug(f"{self.name}.pointByCoord: coord sent={coord}")

        vals = []  # List of axe values for debugging
        idxs = []  # List of indices for respective axes

        #----------------------------------------------------------------------
        # Prejdem vsetky osi a vypocitam index pre kazdu os
        #----------------------------------------------------------------------
        for axe in self._cnts.keys():

            #------------------------------------------------------------------
            # Ak je os zmrazena, pouzijem zmrazenu hodnotu ako jeden z koordinatov
            #------------------------------------------------------------------
            if axe in self.actSub.keys() and self.actSub[axe]: axeVal = self.actSub[axe]
            else                                             : axeVal = coord[axe]

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
    def _actSubSet(self, actSub:dict):
        """Sets active submatrix definition as dict of freezed axesKeys with values.
           If actSub definition changed from current definition, sets actChanged to True.
        """

        self.logger.info(f"{self.name}._actSubSet: To {actSub}")

        #----------------------------------------------------------------------
        # Kontrola zmeny definicie
        #----------------------------------------------------------------------
        if self.actSub == actSub:
            self.logger.debug(f"{self.name}._actSubSet: actSub definition was not changed")
            return

        #----------------------------------------------------------------------
        # Kontrola novej definicie
        #----------------------------------------------------------------------
        for axe, axeIdx in actSub.items():

            if axe not in self._cnts.keys():
                self.logger.error(f"{self.name}._actSubSet: Axe '{axe}' is not in InfoMatrix axes {list(self._cnts.keys())}, change denied")
                return

        #----------------------------------------------------------------------
        # Nastavenie aktivnej submatice
        #----------------------------------------------------------------------
        self.actSub     = actSub.copy()
        self.actList    = []
        self.actChanged = True

        #----------------------------------------------------------------------
        self.logger.debug(f"{self.name}._actSubSet: definition was changed to {self.actSub}")

    #--------------------------------------------------------------------------
    # Active subsmatrix retrieval
    #--------------------------------------------------------------------------
    def actSubmatrix(self, actSub=None, force=False) -> list:
        """Returns active submatrix of InfoPoints as list of InfoPoints
        """

        self.logger.info(f"{self.name}.actSubmatrix: actSub={actSub}, force={force}")

        #----------------------------------------------------------------------
        # Nastavenie aktivnej submatice ak bola dodana definicia
        #----------------------------------------------------------------------
        if actSub is not None: self._actSubSet(actSub)

        #----------------------------------------------------------------------
        # Kontrola potreby obnovenia
        #----------------------------------------------------------------------
        if not self.actChanged and not force:
            self.logger.debug(f"{self.name}.actSubmatrix: subMatrix definition was not changed, no need to refresh")
            return self.actList

        #----------------------------------------------------------------------
        self.logger.info(f"{self.name}.actSubmatrix: Refresh for actSub={self.actSub}, force={force}")

        #----------------------------------------------------------------------
        # Prejdem vsetky osi s definovanou hodnotou idx
        #----------------------------------------------------------------------
        poss  = set()  # Set of positions of InfoPoints in the active submatrix
        first = True   # Flag for first axe

        for axe, axeIdx in self.actSub.items():

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
            # Ak uz existuje nejaka mnozina pozicii, vytvorim prienik s touto mnozinou
            #------------------------------------------------------------------
            if first:
                #----------------------------------------------------------------
                # Prva os, nastavim mnozinu pozicii na tuto mnozinu
                #----------------------------------------------------------------
                poss  = actPoss
                first = False

            else:
                #----------------------------------------------------------------
                # Dalsia os, vytvorim prienik s touto poss mnozinou
                #----------------------------------------------------------------
                poss = poss.intersection(actPoss)

        #----------------------------------------------------------------------
        # Create vector of InfoPoints for respective positions
        #----------------------------------------------------------------------
        self.actList.clear()  # Clear active list of points
        for pos in poss:
            self.actList.append(self.pointByPos(pos))

        #----------------------------------------------------------------------
        self.logger.info(f"{self.name}.actSubmatrix: Found {len(self.actList)} positions in active submatrix for actSub={self.actSub}")
        return self.actList

    #==========================================================================
    # Value modification
    #--------------------------------------------------------------------------
    def clear(self, *, defs:dict={}):
        "Set all InfoPoint's values to default value"

        self.logger.info(f"{self.name}.clear: defs={defs}")

        for point in self.points: point.clear(dat=defs)

    #--------------------------------------------------------------------------
    def gener(self, *, cnts:dict, origs:dict, rects:dict, ipType:str=None, defs:dict={} ):
        """Creates new InfoMatrix with respective cnts, origs and rect. Expecting valid
           ipType scheme. If ipType is not in arguments, uses existing ipType"""

        if ipType is not None: self.ipType = ipType
        self.logger.info(f"{self.name}.gener: {cnts} points of type {self.ipType} on rect {rects} from {origs} with values {defs}")

        #----------------------------------------------------------------------
        # Check validity of InfoPoint's schema
        #--- -------------------------------------------------------------------
        if not self.isInSchema(axes=list(cnts.keys()), vals=list(defs.keys())):
            self.logger.error(f"{self.name}.gener: Schema for {self.ipType} is not comaptible with arguments")
            return

        #----------------------------------------------------------------------
        # Destroy old data
        #----------------------------------------------------------------------
        self.points.clear()                    # Clear all points in the InfoMatrix

        #----------------------------------------------------------------------
        # InfoMatrix settings
        #----------------------------------------------------------------------
        self._cnts     = cnts.copy()              # List of number of InfoPoints in respective axes
        self._origs    = origs.copy()             # List of origin's coordinates of the InfoMatrix
        self._rects    = rects.copy()             # List of lenghts of the InfoMatrix's axes

        self._diffs    = {}                       # List of distances between two points in respective axes in lambda units
        for key, cnt in self._cnts.items():
            self._diffs[key] = self._rects[key]/(cnt-1)  # Distance between two points in respective axes in lambda units

        self.actCol    = None                     # Current axes in role of the columns for 2D matrix
        self.actRow    = None                     # Current axes in role of the rows for 2D matrix
        if len(self._cnts) <= 1: self.actRow = list(self._cnts.keys())[0]
        if len(self._cnts) == 2: self.actCol = list(self._cnts.keys())[1]

        #----------------------------------------------------------------------
        # Generate InfoPoints at respective positions
        #----------------------------------------------------------------------
        point = None
        for pos in range(self.count(check=False)):

            #------------------------------------------------------------------
            # Compute coordinates of the InfoPoint for respective position and indices
            #------------------------------------------------------------------
            idxs = self._idxsByPos(pos)          # Get indices of the InfoPoint for respective position
            coos = {}

            for i, key in enumerate(self._cnts.keys()):
                coos[key] = self._origs[key] + (idxs[i] * self._diffs[key])

            #------------------------------------------------------------------
            # Create new row of InfoPoint at respective coordinates
            #------------------------------------------------------------------
            point = InfoPoint(self.ipType, pos=coos, vals=defs)
            self.points.append(point)

        #----------------------------------------------------------------------
        # Final adjustments
        #----------------------------------------------------------------------
        self.logger.info(f"{self.name}.gener: Created {len(self.points)} InfoPoints")

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

    #--------------------------------------------------------------------------
    def pointSetFunction(self, keyFtion:str, key:str, par:dict=None) -> bool:
        "Apply respective function for all points or points in active substructure to set the value for key"

        self.logger.info(f"{self.name}.pointSetFunction: {keyFtion}(key={key}, par={par}) for {len(self.actList)} active Points]")

        #----------------------------------------------------------------------
        # Ziskanie vykonavanej funkcie
        #----------------------------------------------------------------------
        if keyFtion in self.mapSetMethods().keys():
            function = self.mapSetMethods()[keyFtion]['ftion']

        else:
            self.logger.error(f"{self.name}.pointSetFunction: '{keyFtion}' is not in defined functions")
            return False

        #----------------------------------------------------------------------
        # Ziskanie listu bodov na aplikovanie funkcie
        #----------------------------------------------------------------------
        if 'all' in par.keys() and par['all'] == True:
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
            function(self=point, key=key, par=par)
            pts += 1

        #----------------------------------------------------------------------
        self.logger.info(f"{self.name}.pointSetFunction: {keyFtion} was applied to {tgtStr} {pts} InfoPoints")
        return True

    #==========================================================================
    # Normalisation methods
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
    im = InfoMatrix('Test matrix', ipType='ipTest')
    im.logger.debug('Test of InfoMatrix class')


    print(im)
    input('Press Enter to continue...')

    im.gener(cnts={'a':5}, origs={'a':0.0}, rects={'a':1.0})
    print(im.info(full=True)['msg'])
    input('Press Enter to continue...')

    im.setAxe('a', 'Os A')
    im.setAxe('a', 'Os A')
    print(im.info(full=True)['msg'])
    input('Press Enter to continue...')

    im.gener(cnts={'a':3}, origs={'a':0.0}, rects={'a':1.0})
    print(im.info(full=True)['msg'])
    input('Press Enter to continue...')

    im.setAxe('b', 'Os B')
    im.gener(cnts={'a':3, 'b':4}, origs={'a':0.0, 'b':0}, rects={'a':10, 'b':10})
    print(im.info(full=True)['msg'])
    input('Press Enter to continue...')

    im.setAxe('c', 'Os C')
    im.gener(cnts={'a':3, 'b':4, 'c':2}, origs={'a':0.0, 'b':0, 'c':0}, rects={'a':1.0, 'b':2, 'c':3})
    im.setVal('v', 'Rýchlosť')
    im.setVal('m', 'Hmotnosť')
    input('Press Enter to continue...')
    print()

    im.logger.setLevel('DEBUG')

    print(im.info(full=True)['msg'])
    print('possA0', im._possByAxeIdx(axeKey='a', axeIdx=0))
    print('possA1', im._possByAxeIdx(axeKey='a', axeIdx=1))
    print()
    print('possB0', im._possByAxeIdx(axeKey='b', axeIdx=0))
    print('possB1', im._possByAxeIdx(axeKey='b', axeIdx=1))
    print()
    print('possC0', im._possByAxeIdx(axeKey='c', axeIdx=0))
    print('possC1', im._possByAxeIdx(axeKey='c', axeIdx=1))
    input('Press Enter to continue...')
    print()

    im.actSubmatrix({'a':0, 'b':1, 'c':None})
    print(im.actList)

    #--------------------------------------------------------------------------
    # generovanie hodnot
    #--------------------------------------------------------------------------
    im.pointSetFunction('BRandom fuuniform', 'm', par={'all':True, 'min':0, 'max':5})
    im.pointSetFunction('Random uniform', 'm', par={'all':True, 'min':0, 'max':5})
    print(im.info(full=True)['msg'])
    input('Press Enter to continue...')

    #--------------------------------------------------------------------------
    # generovanie hodnot
    #--------------------------------------------------------------------------
    print('point')
    print('pos=16 ', im.pointByPos(16))
    input('Press Enter to continue...')


    print('[1, 3, 0] ', im.pointByIdxs([1, 3, 0]))
    input('Press Enter to continue...')

    #--------------------------------------------------------------------------
    # Submatrix
    #--------------------------------------------------------------------------



#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------