#==============================================================================
# Siqo class InfoMatrix
#------------------------------------------------------------------------------
import math
import cmath
import numpy                 as np
import random                as rnd

import siqo_ipoint            as ip
from   siqo_ipoint import InfoPoint

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_VER    = '3.02'
_IND    = '|  '       # Info indentation
_UPP    = 10          # distance units per period

_F_POS  =  8          # Format for position

#==============================================================================
# package's variables
#------------------------------------------------------------------------------


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
    def __init__(self, journal, name, ipType):
        "Calls constructor of InfoMatrix"

        self.journal = journal
        self.journal.I(f"InfoMatrix.constructor: {name}")
        
        #----------------------------------------------------------------------
        # Public datove polozky triedy
        #----------------------------------------------------------------------
        self.name       = name            # Name of the InfoMatrix
        self.ipType     = ipType          # Type of the InfoPoint in this InfoMatrix
        self.points     = []              # List of InfoPoints
        self.actVal     = None            # Key of the current InfoPoint's dat value
        self.act1D      = None            # Current active 1D submatrix (vector) defined as dict of freezed axesKeys with values
                                          #  {'x':x, 'y':y, ....] but ONE active axes missing
        self.act2D      = None            # Current active 2D submatrix defined as dict of freezed axesKeys with values
                                          #  {'x':x, 'y':y, ....] but TWO active axes missing
        self.staticEdge = False           # Static edge means value of the edge points is fixed in some methods
        
        #----------------------------------------------------------------------
        # Private datove polozky triedy
        #----------------------------------------------------------------------
        self._origs     = {}              # Origin's coordinates of the InfoMatrix for respective axes in lambda units
        self._cnts      = {}              # Number of InfoPoints in respective axes
        self._diffs     = {}              # Distance between two points in respective axes in lambda units

        #----------------------------------------------------------------------
        # Inicializacia
        #----------------------------------------------------------------------
        InfoPoint.setJournal(self.journal)

        self.journal.O(f"{self.name}.constructor: done")

    #--------------------------------------------------------------------------
    def __str__(self):
        "Prints info about this InfoMatrix"

        toRet = ''
        for line in self.info()['msg']: toRet += line +'\n'
        return toRet

    #--------------------------------------------------------------------------
    def __array__(self):
        "Returns InfoMatrix as 2D numpy array"
 
        mtrx = self.actMatrix(keyVal=self.actVal)

        #----------------------------------------------------------------------
        # Kontrola existencie vybranej 2D matice
        #----------------------------------------------------------------------
        if mtrx is None:
            self.journal.M(f"{self.name}.__array__: ERROR: actMatrix is None", True)
            return None

        #----------------------------------------------------------------------
        # Vratim skonvertovane do np.array
        #----------------------------------------------------------------------
        return np.array(mtrx)

    #--------------------------------------------------------------------------
    def reset(self, ipType=None):
        "Resets all InfoMatrix's data and destroys all points. Count of points will be 0"
        
        self.journal.I(f"{self.name}.reset: ipType={ipType}")
        
        if ipType is not None: self.ipType = ipType

        self.points     = []              # List of rows of lists of InfoPoints
        self.actVal     = None            # Key of the InfoPoint's current dat value
        self.act1D      = None            # Current active 1D submatrix (vector) defined as dict of freezed axesKeys with values
        self.act2D      = None            # Current active 2D submatrix defined as dict of freezed axesKeys with values
        self.staticEdge = False           # Static edge means value of the edge nodes is fixed        

        self._origs     = {}              # Origin's coordinates of the InfoMatrix
        self._cnts      = {}              # Number of InfoPoints in respective axes
        self._diffs     = {}              # Distance between two points in respective axes in lambda units
        
        self.journal.O()
        
    #--------------------------------------------------------------------------
    def info(self, indent=0):
        "Creates info about this InfoMatrix"
        
        dat = {}
        msg = []

        #----------------------------------------------------------------------
        # info o celej strukture
        #----------------------------------------------------------------------
        if indent == 0:
            msg.append(f"{indent*_IND}{60*'='}")
            dat['name'       ] = self.name
            dat['ipType'     ] = self.ipType
            dat['schema'     ] = InfoPoint.getSchema(self.ipType)
            dat['actVal'     ] = self.actVal
            dat['act1D'      ] = self.act1D
            dat['act2D'      ] = self.act2D
            dat['staticEdge' ] = self.staticEdge

            dat['origs'      ] = self._origs
            dat['cnts'       ] = self._cnts
            dat['len'        ] = len(self.points)
            dat['count'      ] = self.count()
            dat['subProducts'] = self._subProducts()
            dat['diffs'      ] = self._diffs

        for key, val in dat.items(): msg.append(f"{indent*_IND}{key:<15}: {val}")

        #----------------------------------------------------------------------
        # info o vsetkych bodoch
        #----------------------------------------------------------------------
        for pos, point in enumerate(self.points):
            idxs = self._idxByPos(pos)
            msg.append(f"{pos:{_F_POS}} {idxs} {str(point)}")
        
        #----------------------------------------------------------------------
        return {'res':'OK', 'dat':dat, 'msg':msg}
        
    #--------------------------------------------------------------------------
    def count(self):
        "Returns Count of points in this InfoMatrix"
        
        if len(self._cnts) == 0: return 0

        toRet = 1
        for cnt in self._cnts.values():
            toRet *= cnt

        return toRet

    #--------------------------------------------------------------------------
    def copy(self, name):
        "Creates copy of this InfoMatrix"
        
        self.journal.I(f"{self.name}.copy: to {name}")

        #----------------------------------------------------------------------
        # Create new InfoMatrix with the same dimensions
        #----------------------------------------------------------------------
        toRet = InfoMatrix(self.journal, name, self.ipType)

        toRet.points     = []                  # List of InfoPoints
        toRet.ipType     = self.ipType         # Type of the InfoPoint in this InfoMatrix
        toRet.actVal     = self.actVal         # Key of the InfoPoint's dat value
        toRet.act1D      = self.act1D          # Current active 1D submatrix (vector) defined as dict of freezed axesKeys with values
        toRet.act2D      = self.act2D          # Current active 2D submatrix defined as dict of freezed axesKeys with values
        toRet.staticEdge = self.staticEdge     # Static edge means value of the edge nodes is fixed

        toRet._origs     = self._origs.copy()  # Origin's coordinates of the InfoMatrix 
        toRet._cnts      = self._cnts.copy()   # Number of InfoPoints in respective axes
        toRet._diffs     = self._diffs.copy()  # Distance between two points in respective axes in lambda units

        #----------------------------------------------------------------------
        # Copy all points from this InfoMatrix to the new one
        #----------------------------------------------------------------------
        for point in self.points:
            toRet.points.append(self.copy())

        #----------------------------------------------------------------------
        self.journal.O()
        return toRet
        
    #==========================================================================
    # Proxy tools for InfoPoint schema
    #--------------------------------------------------------------------------
    def clearSchema(self):
        "Clears schema of InfoPoint for respective ipType to {'axes':{'None':'None'}, 'vals':{}}"
        return InfoPoint.clearSchema(self.ipType)
    
    #--------------------------------------------------------------------------
    def setAxe(self, key, name):
        "Sets axe key and name"
        return InfoPoint.setAxe(self.ipType, key, name)
    
    #--------------------------------------------------------------------------
    def getAxeIdx(self, key):
        "Returns axe's idx for respective key as position in the list of axes othewise None"
        return InfoPoint.getAxeIdx(self.ipType, key)
    
    #--------------------------------------------------------------------------
    def getAxeKey(self, idx):
        "Returns axe's key for respective position in the list of axes othewise None"
        return InfoPoint.getAxeKey(self.ipType, idx)

    #--------------------------------------------------------------------------
    def getAxeName(self, key):
        "Returns axe's Name for respective key as string othewise None"
        return InfoPoint.getAxeName(self.ipType, key)
    
    #--------------------------------------------------------------------------
    def setVal(self, key, name):
        "Sets value key and name"
        return InfoPoint.setVal(self.ipType, key, name)

    #--------------------------------------------------------------------------
    def getValIdx(self, key):
        "Returns value's idx for respective key as position in the list of axes othewise None"
        return InfoPoint.getValIdx(self.ipType, key)
    
    #--------------------------------------------------------------------------
    def getValKey(self, idx):
        "Returns value's key for respective position in the list of valus othewise None"
        return InfoPoint.getValKey(self.ipType, idx)

    #--------------------------------------------------------------------------
    def getValName(self, key):
        "Returns value's Name for respective key as string othewise None"
        return InfoPoint.getValName(self.ipType, key)
    
    #--------------------------------------------------------------------------
    def getSchema(self):
        "Returns schema for respective InfoPoint type as dict {'axes':{}, 'vals':{}}"
        return InfoPoint.getSchema(self.ipType)
    
    #--------------------------------------------------------------------------
    def getAxes(self):
        "Returns axes keys and names as dict {key: name}"
        return InfoPoint.getAxes(self.ipType)
    
    #--------------------------------------------------------------------------
    def getVals(self):
        "Returns values keys and names as dict {key: name}"
        return InfoPoint.getVals(self.ipType)

    #--------------------------------------------------------------------------
    def getFMethods(self):
        "Returns methods returning float value {key: InfoPoint.function}"
        return InfoPoint.floatMethods()

    #--------------------------------------------------------------------------
    def genMethods(self):
        "Returns methods generating keyed value"
        return InfoPoint.genMethods()

    #==========================================================================
    # Position and indices tools
    #--------------------------------------------------------------------------
    def _subProducts(self):
        "Returns list of subproducts of _cnts [1, A, AB, ABC, ...]"

        toRet = [1]

        for cnt in self._cnts.values():
            toRet.append( cnt * toRet[-1] )

        #----------------------------------------------------------------------
        # Remove last element which is the product of all dimensions
        #----------------------------------------------------------------------
        toRet.pop()

        return toRet

    #--------------------------------------------------------------------------
    def _posByIdx(self, idxs:list):
        "Returns position of the InfoPoint in the list for respective indices"

        subProd = self._subProducts()

        pos = 0
        for i, idx in enumerate(idxs):
            pos += idx * subProd[i]

        return pos

    #--------------------------------------------------------------------------
    def _idxByPos(self, pos:int):
        "Returns indices of the InfoPoint for respective position in the list"

        #----------------------------------------------------------------------
        # Inicializacia
        #----------------------------------------------------------------------
        toRet = []
        cnts  = list(self._cnts.values())
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

        return toRet

    #--------------------------------------------------------------------------
    def _1DposByIdx(self, idxs:list):
        """Returns list of pos for vector of respective indices with ONE
           question mark in the list [a, b, '?', 'c'].
           Question mark means all values in this dimension and defines vector."""

        self.journal.I(f"{self.name}._1DposByIdx: idxs={idxs}")
        toRet = []

        #----------------------------------------------------------------------
        # Prvy InfoPoint je urceny idxs kde '?' je nahradeny 0
        #----------------------------------------------------------------------
        startIdxs = []

        for i, idx in enumerate(idxs):

            if idx != '?': startIdxs.append(idx)
            else:
                startIdxs.append(0)
                vecDim = i

        #----------------------------------------------------------------------
        # Zistim pocet hodnot v hladanom vektore 
        #----------------------------------------------------------------------
        vecCnt = list(self._cnts.values())[vecDim]

        #----------------------------------------------------------------------
        # Zistim pos pre prvy InfoPoint v hladanom vektore
        #----------------------------------------------------------------------
        startPos = self._posByIdx(startIdxs)

        #----------------------------------------------------------------------
        # Zistim krok od startPos pre vsetky dalsie InfoPointy v hladanom vektore
        #----------------------------------------------------------------------
        step = self._subProducts()[vecDim]
        self.journal.M(f"{self.name}._1DposByIdx: startPos={startPos}, vecCnt={vecCnt} and step={step}")

        #----------------------------------------------------------------------
        # Vytvorim vsetky pozicie v hladanom vektore        
        #----------------------------------------------------------------------
        for pos in range(startPos, startPos + (vecCnt*step), step):
            toRet.append(pos)

        #----------------------------------------------------------------------
        self.journal.O(f"{self.name}._1DposByIdx: toRet={toRet}")
        return toRet

    #--------------------------------------------------------------------------
    def _2DposByIdx(self, idxs:list, struct:str):
        """Returns positons of InfoPoints for respective indices with TWO
           question marks in the list ['?', b, '?', 'c'].
           Question marks means all values in this dimension and  defines the matrix.
           Positions are returned in the list of vector's positions list
           [ [a, b, c], [d, e, f], ... ].
           """

        self.journal.I(f"{self.name}._2DposByIdx: Save points for idxs={idxs} into {struct}")
        toRet = []

        #----------------------------------------------------------------------
        # Zistim poziciu prveho '?' v idxs
        #----------------------------------------------------------------------
        rowDim = None
        for i, idx in enumerate(idxs):
            if idx == '?':
                rowDim = i
                break

        #----------------------------------------------------------------------
        # Zistim pocet hodnot v dimenzii rowDim
        #----------------------------------------------------------------------
        rowCnt = list(self._cnts.values())[rowDim]

        #----------------------------------------------------------------------
        # Vygenerujem idxs pre row-vektory
        #----------------------------------------------------------------------
        for i in range(rowCnt):

            #------------------------------------------------------------------
            # Vytvorim idxs pre row-vektor
            #------------------------------------------------------------------
            rowIdxs = list(idxs)
            rowIdxs[rowDim] = i

            #------------------------------------------------------------------
            # Vygenerujem pozicie pre row-vektor
            #------------------------------------------------------------------
            rowPos = self._1DposByIdx(rowIdxs)

            #------------------------------------------------------------------
            # Vlozim rowPos do matice pozicii toRet
            #------------------------------------------------------------------
            if   struct == 'matrix': toRet.append(rowPos) 
            elif struct == 'list'  : toRet.extend(rowPos)
            else:     
                self.journal.M(f"{self.name}._2DposByIdx: Unknown structure {struct}, command denied")
                self.journal.O()
                return None

        #----------------------------------------------------------------------
        self.journal.O(f"{self.name}._2DposByIdx: toRet={toRet}")
        return toRet

    #--------------------------------------------------------------------------
    def _actToIdxs(self, act:dict):
        """Converts active substructure defined by frozen axes (act1D, act2D)
           into list of indices with '?'
           Returns tuple (count_missing_axes_in_act, idxs_with_?)
        """

        freeDim = 0
        idxs    = []

        #----------------------------------------------------------------------
        # Prejdem vsetky dostupne osi v matrix
        #----------------------------------------------------------------------
        for key, val in self._cnts.items():

            if key not in act.keys():

                #--------------------------------------------------------------
                # Os ktora nie je v act je free dim oznacena '?' v indices
                #--------------------------------------------------------------
                idxs.append('?')
                freeDim += 1

            else:
                #--------------------------------------------------------------
                # Zafixujem polohu na tejto osi podla hodnoty v act
                #--------------------------------------------------------------
                idxs.append( act[key] )

        #----------------------------------------------------------------------
        self.journal.M(f"{self.name}._actToIdxs: {act} -> {idxs}({freeDim})")
        return (freeDim, idxs)

    #==========================================================================
    # InfoPoint retrieval
    #--------------------------------------------------------------------------
    def pointByPos(self, pos:int):
        "Returns InfoPoint in field for respective position"

        toRet = self.points[pos]

        return toRet

    #--------------------------------------------------------------------------
    def pointByIdx(self, idxs:list):
        "Returns InfoPoint in field at respective indexes"
        
        pos = self._posByIdx(idxs)
        return self.pointByPos(pos)
        
    #--------------------------------------------------------------------------
    def pointByCoords(self, coos:list):
        "Returns nearest InfoPoint in field for respective coordinates"

        self.journal.I(f"{self.name}.pointByPos: x={x}, y={y}")

        #----------------------------------------------------------------------
        # Searching for the row index for respective x
        #----------------------------------------------------------------------
        for row in range(self._rows):

            lstRow = row
            if self.points[row][0].pos[0] >= x: break

        #----------------------------------------------------------------------
        # Row index before or after x ?
        #----------------------------------------------------------------------
        if lstRow < self._rows-1:

            if abs(self.points[lstRow][0].pos[0]-x) > abs(self.points[lstRow+1][0].pos[0]-x):
                lstRow += 1

        #----------------------------------------------------------------------
        # Searching for the col index for respective y
        #----------------------------------------------------------------------
        for col in range(self._cols):

            lstCol = col
            if self.points[0][col].pos[1] >= y: break
        
        #----------------------------------------------------------------------
        # Col index before or after y ? 
        #----------------------------------------------------------------------
        if lstCol < self._cols-1:

            if abs(self.points[0][lstCol].pos[1]-y) > abs(self.points[0][lstCol+1].pos[1]-y):
                lstCol += 1

        #----------------------------------------------------------------------
        # Final 
        #----------------------------------------------------------------------
        self.journal.O()
        return self.points[lstRow][lstCol]
      
    #==========================================================================
    # Substructure retrieval
    #--------------------------------------------------------------------------
    def actVector(self, *, keyVal:str=None, sub1D=None):
        """Returns vector of InfoPoints in field for respective act1D settings
           If keyVal is not None then returns vector of keyed values.
           If keyVal is     None then returns vector of InfoPoints."""
        
        self.journal.I(f"{self.name}.actVector: keyVal={keyVal}, sub1D={sub1D}")
        toRet = []

        if sub1D is not None: self.act2D = sub1D

        #----------------------------------------------------------------------
        # Ak nie je act1D nastaveny, vyber je cela InfoMatrix
        #----------------------------------------------------------------------
        if self.act1D is None: self.act1D = {}    
        
        #----------------------------------------------------------------------
        # Ziskam idxs podla act1D a pre kontrolu aj pocet volnych dimenzii
        #----------------------------------------------------------------------
        freeDim, idxs = self._actToIdxs(self.act1D)

        if freeDim != 1:
            self.journal.M(f"{self.name}.actVector: ERROR: act1D {self.act1D} is not 1D substructure but {freeDim} dim", True)
            self.journal.O()
            return toRet

        #----------------------------------------------------------------------
        # Ziskam list pozicii bodov patriacich hladanemu vektoru
        #----------------------------------------------------------------------
        poss = self._1DposByIdx(idxs)
        
        #----------------------------------------------------------------------
        # Create vector of InfoPoints/Values for respective positions
        #----------------------------------------------------------------------
        for pos in poss:
            toRet.append(self.pointByPos(pos).get(key=keyVal))

        #----------------------------------------------------------------------
        self.journal.O()
        return toRet    
    
    #--------------------------------------------------------------------------
    def actMatrix(self, *, keyVal:str=None, sub2D=None, struct:str='list'):
        """Returns matrix of InfoPoints in field for respective act2D settings 
           If keyVal is not None then returns matrix of keyed values.
           If keyVal is     None then returns matrix of InfoPoints."""

        self.journal.I(f"{self.name}.actMatrix: keyVal={keyVal}, sub2D={sub2D} into structure {struct}")
        toRet = []

        if sub2D is not None: self.act2D = sub2D

        #----------------------------------------------------------------------
        # Ak nie je act2D nastaveny, vyber je cela InfoMatrix
        #----------------------------------------------------------------------
        if self.act2D is None: self.act2D = {}    
        
        #----------------------------------------------------------------------
        # Ziskam idxs podla act2D a pre kontrolu aj pocet volnych dimenzii
        #----------------------------------------------------------------------
        freeDim, idxs = self._actToIdxs(self.act2D)

        if freeDim != 2:
            self.journal.M(f"{self.name}.actMatrix: ERROR: act2D {self.act2D} is not 2D substructure but {freeDim} dim", True)
            self.journal.O()
            return toRet

        #----------------------------------------------------------------------
        # Ziskam maticu pozicii bodov patriacich hladanej matici
        #----------------------------------------------------------------------
        mtrx  = self._2DposByIdx(idxs, struct)

        if mtrx is None:
            self.journal.M(f"{self.name}.actMatrix: ERROR: Can not obtain positions for desired subset and structure", True)
            self.journal.O()
            return toRet
        
        #----------------------------------------------------------------------
        # Create otput for respective structure settings
        #----------------------------------------------------------------------
        if struct=='matrix':

            #------------------------------------------------------------------
            # Create marix of InfoPoints for respective positions
            #------------------------------------------------------------------
            for row in mtrx:

                rowVec = []

                #--------------------------------------------------------------
                # Create row-vector of InfoPoints/Values for respective positions
                #--------------------------------------------------------------
                for pos in row:
                    rowVec.append(self.pointByPos(pos).get(key=keyVal))

                #--------------------------------------------------------------
                # Vlozim riadok do matice
                #--------------------------------------------------------------
                toRet.append(rowVec)

        elif struct == 'list':

            #------------------------------------------------------------------
            # Create list of InfoPoints for respective positions
            #------------------------------------------------------------------
            for pos in mtrx:
                toRet.append(self.pointByPos(pos).get(key=keyVal))

        else:
            self.journal.M(f"{self.name}.actMatrix: Unknown structure {struct}, command denied")
            self.journal.O()
            return None

        #----------------------------------------------------------------------
        self.journal.O()
        return toRet    

    #==========================================================================
    # Value modification
    #--------------------------------------------------------------------------
    def clear(self, *, defs:dict={}):
        "Set all InfoPoint's values to default value"
        
        self.journal.M(f"{self.name}.clear: defs={defs}")

        for point in self.points: point.clear(dat=defs)

    #--------------------------------------------------------------------------
    def gener(self, *, cnts:dict, origs:dict, rect:dict, ipType:str=None, vals:dict=None, defs:dict={} ):
        "Creates InfoMatrix with respective settings"
        
        if ipType is not None: self.ipType = ipType
        self.journal.I(f"{self.name}.gener: {cnts} points of type {self.ipType} on rect {rect} from {origs}")

        self.points.clear()                    # Clear all points in the InfoMatrix

        #----------------------------------------------------------------------
        # Set InfoPoint's schema Axes
        #----------------------------------------------------------------------
        self.clearSchema()                     # Clear schema for this InfoPoint type
        mins = []                              # List of minimum values for respective axes

        for key, val in cnts.items():

            self.setAxe(key, f"os {key}")    
            mins.append(val)

        #----------------------------------------------------------------------
        # Set InfoPoint's schema Values if vals is not None 
        #----------------------------------------------------------------------
        if vals is not None:

            for key, name in vals.items():
                self.setVal(key, name)

            if len(vals) == 1: self.actVal = list(vals.keys())[0]

        #----------------------------------------------------------------------
        # InfoMatrix settings
        #----------------------------------------------------------------------
        self._cnts     = cnts.copy()              # List of number of InfoPoints in respective axes     
        self._origs    = origs.copy()             # List of origin's coordinates of the InfoMatrix

        self._diffs    = {}                       # List of distances between two points in respective axes in lambda units
        for key, cnt in self._cnts.items():
            self._diffs[key] = rect[key]/(cnt-1)  # Distance between two points in respective axes in lambda units
                
        self.actCol    = None                     # Current axes in role of the columns for 2D matrix
        self.actRow    = None                     # Current axes in role of the rows for 2D matrix
        if len(self._cnts) <= 1: self.actRow = list(self._cnts.keys())[0]
        if len(self._cnts) == 2: self.actCol = list(self._cnts.keys())[1]   

        #----------------------------------------------------------------------
        # Generate InfoPoints at respective positions
        #----------------------------------------------------------------------
        point = None
        for pos in range(self.count()):

            #------------------------------------------------------------------
            # Compute coordinates of the InfoPoint for respective position and indices
            #------------------------------------------------------------------
            idxs = self._idxByPos(pos)          # Get indices of the InfoPoint for respective position
            coos = {}

            for i, key in enumerate(self._cnts.keys()):
                coos[key] = self._origs[key] + (idxs[i] * self._diffs[key])

            #------------------------------------------------------------------
            # Create new row of InfoPoint at respective coordinates
            #------------------------------------------------------------------
            point = InfoPoint(self.ipType, pos=coos, dat=defs)
            self.points.append(point)
            
        #----------------------------------------------------------------------
        # Final adjustments
        #----------------------------------------------------------------------
        self.journal.O()
        
    #--------------------------------------------------------------------------

    #==========================================================================
    # Methods application
    #--------------------------------------------------------------------------
    def copyFrom(self, src, *, key=None, tgtSlice=(0,0,0,0), srcFrom=(0,0)):
        "Copy point's values from srcs 2D matrix into tgts 2D matrix"
        
        self.journal.I(f"{self.name}.copyFrom: From {src.name} starting at {srcFrom} to nodes {tgtSlice} for key={key}")

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
                tgtPoint = self.pointByIdx([tgtRow, tgtCol])
                if tgtPoint is None:
                    self.journal.M(f"{self.name}.copyFrom: ERROR Target point[{tgtRow},{tgtCol}] does not exists", True)
                    break
                
                #--------------------------------------------------------------
                # Trying to get source node
                #--------------------------------------------------------------
                try:
                    srcPoint = src.pointByIdx([srcRowFrom+tgtRow-tgtRowFrom, srcColFrom+tgtCol-tgtColFrom])
                except IndexError:
                    self.journal.M(f"{self.name}.copyFrom: ERROR Source point[{srcRowFrom+tgtRow-tgtRowFrom}, {srcColFrom+tgtCol-tgtColFrom}] does not exists", True)
                    break   
                
                #--------------------------------------------------------------
                # Copy value from source to target node
                #--------------------------------------------------------------
                srcDat = srcPoint.get(key=key)
                tgtPoint.set(dat=srcDat)
                i += 1

        #----------------------------------------------------------------------
        self.journal.O(f"{self.name}.copyFrom: Copied {i} points")
        return self
        
    #--------------------------------------------------------------------------
    def applyPointFunction(self, function, key:str, par:dict=None, slice=(0,0,0,0)):
        "Apply respective function for all points in slices"

        #----------------------------------------------------------------------
        # Slice settings
        #----------------------------------------------------------------------
        rowFrom = slice[0]
        colFrom = slice[1]
        rowTo   = slice[2] if slice[2] > 0 else self._rows-1
        colTo   = slice[3] if slice[3] > 0 else self._cols-1
        
        self.journal.I(f"{self.name}.applyPointFunction: {function.__name__}(key={key}, par={par}) from [{rowFrom}:{colFrom}] to [{rowTo}:{colTo}]")
        
        pts = 0  # Counter of points to be processed
        aps = 0  # Counter of points processed by function   

        #----------------------------------------------------------------------
        # rows from rowFrom to rowTo
        #----------------------------------------------------------------------
        for row in range(rowFrom, rowTo+1): 
            
            #------------------------------------------------------------------
            # columns from colFrom to colTo
            #------------------------------------------------------------------
            for col in range(colFrom, colTo+1):
                
                #--------------------------------------------------------------
                # Get node to apply function
                #--------------------------------------------------------------
                point = self.pointByIdx([row, col])
                if point is None:
                    self.journal.M(f"{self.name}.applyPointFunction: ERROR Target point[{row},{col}] does not exists", True)
                    break

                pts += 1

                #--------------------------------------------------------------
                # Apply function to point
                #--------------------------------------------------------------
                if function(point=point, key=key, par=par): aps += 1

                #--------------------------------------------------------------
                # Number of points should be number of applied functions
                #--------------------------------------------------------------
                if pts != aps: 
                    self.journal.M(f"{self.name}.applyPointFunction: ERROR: function {function.__name__} failed for point[{row},{col}]", True)
                    self.journal.O()
                    return False

        #----------------------------------------------------------------------
        self.journal.O(f"{self.name}.applyPointFunction: {function.__name__} was applied to {aps}/{pts} nodes")
        return True

    #==========================================================================
    # Normalisation methods
    #--------------------------------------------------------------------------
    def normAbs(self, nods, norm=None):
        "Normalise set of the nodes by sum of absolute values"
        
        self.journal.I(f"{self.name}.normAbs: ")
        
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
        self.journal.O(f"{self.name}.normAbs: norm = {norm} for {len(nods)} points")

    #==========================================================================
    # Tki API
    #--------------------------------------------------------------------------
    def getNPdata(self, *, keyCol, keyU=None, keyV=None, sub2D:dict={}):
        "Returns numpy arrays of axeX, axeY, values, re and im for respective subset of InfoMatrix"
    
        self.journal.I(f"{self.name}.getData: valueColor={keyCol}, quiverRe={keyU}, quiverIm={keyV} from sub2D={sub2D}")

        #----------------------------------------------------------------------
        # Ziskam pozadovany subset
        #----------------------------------------------------------------------
        subM = self.actMatrix(keyVal=None)
        for row in mtrx: 
            for point in row: print(point)


        #----------------------------------------------------------------------
        self.journal.O()
        return toRet

    #--------------------------------------------------------------------------
    #==========================================================================
    # Persistency methods
    #--------------------------------------------------------------------------
    def toJson(self):
        "Converts node into json structure"
        
        self.journal.I(f'{self.name}.toJson:')
        
        toRet = {}

        self.journal.O(f'{self.name}.toJson: Converted')
        return toRet

#------------------------------------------------------------------------------
print(f"InfoMatrix ver {_VER}")

if __name__ == '__main__':

    from   siqolib.journal          import SiqoJournal
    journal = SiqoJournal('IMatrix component test', debug=3)

    #--------------------------------------------------------------------------
    # Test of the InfoMatrix class
    #--------------------------------------------------------------------------
    journal.M('Test of InfoMatrix class')

    im1 = InfoMatrix(journal, 'Test matrix', ipType='ipTest')
    print(im1)

    im1.gener(cnts={'a':5}, origs={'a':0.0}, rect={'a':1.0})
    print(im1)

    im1.gener(cnts={'a':4}, origs={'a':0.0}, rect={'a':1.0}, vals={'v':'Value'})
    print(im1)

    im1.gener(cnts={'a':3}, origs={'a':0.0}, rect={'a':1.0}, vals={'v':'Value'}, defs={'v':0.0})
    print(im1)

    im2 = InfoMatrix(journal, 'Test matrix', ipType='ipTest')
    im2.gener(cnts={'a':3, 'b':4}, origs={'a':0.0, 'b':0}, rect={'a':10, 'b':10}, vals={'v':'Value'}, defs={'v':3.0})
    print(im2)

    im3 = InfoMatrix(journal, 'Test matrix', ipType='ipTest')
    im3.gener(cnts={'a':3, 'b':4, 'c':2}, origs={'a':0.0, 'b':0, 'c':0}, rect={'a':1.0, 'b':2, 'c':3}, vals={'v':'Value'}, defs={'v':0.0})
    print(im3)

    print('point')
    print('pos=16 ', im3.pointByPos(16))
    print()

    print('[1, 3, 0] ', im3.pointByIdx([1, 3, 0]))
    print()


    print("_actToIdxs({'b':3})", im3._actToIdxs({'b':3}))
    print("_actToIdxs({'b':3, 'c':1})", im3._actToIdxs({'b':3, 'c':1}))
    print()

    if False:
        print('vector')
        im3.act1D = {'b':2, 'c':1}
        print(im3._1DposByIdx(['?', 2, 1]))
        vec = im3.actVector(keyVal=None)
        for point in vec: print(point)  
        print()

    if False:
        print('matrix tki API')
        print(im2)
        mtrx = im2.actMatrix(keyVal=None)
        for row in mtrx: 
            for point in row: print(point)
        print()

    if True:
        print('matrix subset')
        print('list  :', im3._2DposByIdx([ '?', '?', 1], struct='list'   ))
        print('matrix:', im3._2DposByIdx([ '?', '?', 1], struct='matrix' ))

        im3.act2D = {'c':1}
        mtrx = im3.actMatrix(keyVal=None, struct='list')
        for point in mtrx: print(point)
        print('point.')
        print()

        mtrx = im3.actMatrix(keyVal=None, struct='matrix')
        for row in mtrx: 
            for point in row: print(point)
        print()

    if False:
        print('matrix __array__')
        print(im3.__array__())
        print()

    if False:
        print('matrix np')
        im3.act2D = {'c':1}
        mtrx = im3.actMatrix(keyVal='v')
        for row in mtrx: 
            for point in row: print(point)
        print()

#    im1.applyPointFunction(ip.abs, key='v')
#    print(im1)

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------