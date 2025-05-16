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
        self.actRow     = None            # Current axes in role of the rows for 2D matrix
        self.actCol     = None            # Current axes in role of the columns for 2D matrix
        self.actVal     = None            # Key of the current InfoPoint's dat value
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
 
        #----------------------------------------------------------------------
        # Kontrola nastavenia vybranej osi pre row
        #----------------------------------------------------------------------
        if self.actRow is None:    
            self.journal.M(f"{self.name}.__array__: ERROR: actRow is None", True)
            return None

        #----------------------------------------------------------------------
        # Kontrola nastavenia vybranej osi pre col
        #----------------------------------------------------------------------
        if self.actCol is None:    
            self.journal.M(f"{self.name}.__array__: ERROR: actCol is None", True)
            return None

        #----------------------------------------------------------------------
        # Kontrola nastavenia vybranej hodnoty
        #----------------------------------------------------------------------
        if self.actVal is None:    
            self.journal.M(f"{self.name}.__array__: ERROR: actVal is None", True)
            return None

        #----------------------------------------------------------------------
        # Prejdem vsetky riadky
        #----------------------------------------------------------------------
        array2D = [[]]
        for row in self.points:

            arrayRow = []

            #------------------------------------------------------------------
            # Prejdem vsetky body v riadku
            #------------------------------------------------------------------
            for point in row:

                val = point.dat[self.actVal]
                if val is None:
                    self.journal.M(f"{self.name}.__array__: ERROR: point.dat[{self.actVal}] is None", True)
                    return None
                
                arrayRow.append(val)

            #------------------------------------------------------------------
            # Vlozim riadok do c2D
            #------------------------------------------------------------------
            array2D.append(arrayRow)

        #----------------------------------------------------------------------
        return np.array(array2D)

    #--------------------------------------------------------------------------
    def reset(self, ipType=None):
        "Resets all InfoMatrix's data and destroys all points. Count of points will be 0"
        
        self.journal.I(f"{self.name}.reset: ipType={ipType}")
        
        if ipType is not None: self.ipType = ipType

        self.points     = []              # List of rows of lists of InfoPoints
        self.actRow     = None            # Current axes in role of the rows for 2D matrix
        self.actCol     = None            # Current axes in role of the columns for 2D matrix
        self.actVal     = None            # Key of the InfoPoint's current dat value
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
            dat['actRow'     ] = self.actRow
            dat['actCol'     ] = self.actCol
            dat['actVal'     ] = self.actVal
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
        toRet.actRow     = self.actRow         # Current axes in role of the rows for 2D matrix
        toRet.actCol     = self.actCol         # Current axes in role of the columns for 2D matrix
        toRet.actVal     = self.actVal         # Key of the InfoPoint's dat value
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
    def _vectorPosByIdx(self, idxs:list):
        """Returns list of pos for vector of respective indices with one
           question mark in yhe list [a, b, '?', 'c'].
           Question mark means all values in this dimension and defines vector."""

        self.journal.I(f"{self.name}._vectorPosByIdx: idxs={idxs}")
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
        self.journal.M(f"{self.name}._vectorPosByIdx: startPos={startPos}, vecCnt={vecCnt} and step={step}")

        #----------------------------------------------------------------------
        # Vytvorim vsetky pozicie v hladanom vektore        
        #----------------------------------------------------------------------
        for pos in range(startPos, startPos + (vecCnt * step), step):
            toRet.append(pos)

        #----------------------------------------------------------------------
        self.journal.O(f"{self.name}._vectorPosByIdx: toRet={toRet}")
        return toRet

    #--------------------------------------------------------------------------
    def _matrixPosByIdx(self, idxs:list):
        """Returns positons of InfoPoints for respective indices with two
           question marks in the list ['?', b, '?', 'c'].
           Question marks means all values in this dimension and  defines 
           the matrix. Positions are returned in the list of vector's positions list
           [ [a, b, c], [d, e, f], ... ].
           """

        self.journal.I(f"{self.name}._matrixPosByIdx: idxs={idxs}")
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
            rowPos = self._vectorPosByIdx(rowIdxs)

            #------------------------------------------------------------------
            # Vlozim rowPos do matice pozicii toRet
            #------------------------------------------------------------------
            toRet.append(rowPos)       

        #----------------------------------------------------------------------
        self.journal.O(f"{self.name}._matrixPosByIdx: toRet={toRet}")
        return toRet

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
        return self.points[lstRow][lstCol]
      
    #==========================================================================
    # Substructure retrieval
    #--------------------------------------------------------------------------
    def vectorByIdx(self, idxs:list, keyVal:str=None):
        """Returns vector of InfoPoints in field for respective indexes with 
           one '?' in the list.
           If keyVal is not None then returns vector of keyed values.
           If keyVal is     None then returns vector of InfoPoints."""
        
        #----------------------------------------------------------------------
        # Get list of positions for respective indices
        #----------------------------------------------------------------------
        poss = self._vectorPosByIdx(idxs)
        
        #----------------------------------------------------------------------
        # Create vector of InfoPoints/Values for respective positions
        #----------------------------------------------------------------------
        toRet = []
        for pos in poss:
            toRet.append(self.pointByPos(pos).get(key=keyVal))

        return toRet    
    
    #--------------------------------------------------------------------------
    def matrixByIdx(self, idxs:list, keyVal:str=None):
        """Returns matrix of InfoPoints in field for respective indexes with 
           two '?' in the list.
           If keyVal is not None then returns matrix of keyed values.
           If keyVal is     None then returns matrix of InfoPoints."""

        #----------------------------------------------------------------------
        # Get matrix of positions for respective indices
        #----------------------------------------------------------------------
        mtrx = self._matrixPosByIdx(idxs)
        
        #----------------------------------------------------------------------
        # Create marix of InfoPoints for respective positions
        #----------------------------------------------------------------------
        toRet = []
        for row in mtrx:

            rowVec = []

            #------------------------------------------------------------------
            # Create row-vector of InfoPoints/Values for respective positions
            #------------------------------------------------------------------
            for pos in row:
                rowVec.append(self.pointByPos(pos).get(key=keyVal))

            #------------------------------------------------------------------
            # Vlozim riadok do matice
            #------------------------------------------------------------------
            toRet.append(rowVec)

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
        InfoPoint.clearSchema(self.ipType)     # Clear schema for this InfoPoint type
        mins = []                              # List of minimum values for respective axes

        for key, val in cnts.items():

            InfoPoint.setAxe(self.ipType, key, f"os {key}")    
            mins.append(val)

        #----------------------------------------------------------------------
        # Set InfoPoint's schema Values if vals is not None 
        #----------------------------------------------------------------------
        if vals is not None:

            for key, name in vals.items():
                InfoPoint.setVal(self.ipType, key, name)

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
    def copyValues(self, src, *, key=None, tgtSlice=(0,0,0,0), srcFrom=(0,0)):
        "Copy point's values from srcs to tgts points"
        
        self.journal.I(f"{self.name}.copyValues: From {src.name} starting at {srcFrom} to nodes {tgtSlice} for key={key}")

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
                tgtPoint = self.pointByIdx(tgtRow, tgtCol)
                if tgtPoint is None:
                    self.journal.M(f"{self.name}.copyValues: ERROR Target point[{tgtRow},{tgtCol}] does not exists", True)
                    break
                
                #--------------------------------------------------------------
                # Trying to get source node
                #--------------------------------------------------------------
                try:
                    srcPoint = src[srcRowFrom+tgtRow-tgtRowFrom][srcColFrom+tgtCol-tgtColFrom]
                except IndexError:
                    self.journal.M(f"{self.name}.copyValues: ERROR Source point[{srcRowFrom+tgtRow-tgtRowFrom}][{srcColFrom+tgtCol-tgtColFrom}] does not exists", True)
                    break   
                
                #--------------------------------------------------------------
                # Copy value from source to target node
                #--------------------------------------------------------------
                srcDat = srcPoint.get(key=key)
                tgtPoint.set(dat=srcDat)
                i += 1

        #----------------------------------------------------------------------
        self.journal.O(f"{self.name}.copyValues: Copied {i} points")
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
                point = self.pointByIdx(row, col)
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

    #--------------------------------------------------------------------------
    def applyRays(self, dimLower, start=0, stop=0, forward=True, torus=False):
        "Apply rays from <dimLower> to next higher dimension"
        
        self.journal.I(f"{self.name}.getRays: from dim {dimLower} with torus={torus}")
        
        if forward: rotDir = -1j
        else      : rotDir =  1j
        
        # Compute constant length of torus-like dimension
        count = self.count()
        
        dltOff = (self.offMax-self.offMin) * (count+1)/count
        
        #----------------------------------------------------------------------
        # Prepare list of source points
        #----------------------------------------------------------------------
        actCut = self.cutDim(dimLower)
        srcs = self.cutToNodes()
        
        #----------------------------------------------------------------------
        # Prepare of target points
        #----------------------------------------------------------------------
        actCut.append('*')
        tgts = self.cutToNodes(actCut)

        #----------------------------------------------------------------------
        # Iterate over srcs points
        #----------------------------------------------------------------------
        toRet = []
        for src in srcs:
        
            srcP = src['cP']
        
            #------------------------------------------------------------------
            # Iterate over target points
            #------------------------------------------------------------------
            for tgt in tgts:
                
                tgtP = tgt['cP']
                
                #--------------------------------------------------------------
                # Get coordinates of source point and target point
                #--------------------------------------------------------------
                dlts = srcP.deltasTo(tgtP)
                dx1  = dlts[0]              # Rozdiel 1 suradnic bodov srcP a tgtP
                dx2  = tgtP.pos[1]          # Bod srcP nema 2 suradnicu, povazujeme ju za 0
                
                #--------------------------------------------------------------
                # Compute distance in periods
                #--------------------------------------------------------------
                r = math.sqrt( (dx1*dx1) + (dx2*dx2) )  # in distance units
                            
                # phase shift
                phase = (r / _UPP) * 2 * math.pi        # in radians
                
                # Phase defines rotation of amplitude
                rot = cmath.exp(rotDir * phase)
            
                #--------------------------------------------------------------
                # Superpose srcP * rot to tgtP or backward
                #--------------------------------------------------------------
                if forward: tgtP.c += srcP.c * rot
                else      : srcP.c += tgtP.c * rot
                
                #--------------------------------------------------------------
                # If torus then superpose secondary ray
                #--------------------------------------------------------------
                if torus:
                    
                    if dx1 != 0:
                        
                        dx1 = dltOff - abs(dx1)
                        
                        # Compute distance in periods
                        r = math.sqrt( (dx1*dx1) + (dx2*dx2) )   # in distance units
                            
                        # phase shift
                        phase = (r / _UPP) * 2 * math.pi        # in radians
                
                        # Phase defines rotation of amplitude
                        rot = cmath.exp(rotDir * phase)
            
                        #--------------------------------------------------------------
                        # Superpose srcP * rot to tgtP or backward
                        #--------------------------------------------------------------
                        if forward: tgtP.c += srcP.c * rot
                        else      : srcP.c += tgtP.c * rot

                toRet.append({'src':src['cP'], 'tgt':tgt['cP'], 'dx1':dx1, 'dx2':dx2})
                
        #----------------------------------------------------------------------
        # Normalisation
        #----------------------------------------------------------------------
        if forward: self.normAbs(nods=tgts)
        else      : self.normAbs(nods=srcs)

        #----------------------------------------------------------------------
        self.journal.O(f"{self.name}.getRays: creates {len(toRet)} rays")
        return toRet

    #--------------------------------------------------------------------------
    def evolve(self, srcCut, inf=0, start=0, stop=0):
        "Evolve state in <srcCut> and historise it in nex dimension"
        
        self.journal.I(f"{self.name}.evolve: srcCut={srcCut} from {start} to {stop}")
        
        #----------------------------------------------------------------------
        # Prepare list of nodes for evolution
        #----------------------------------------------------------------------
        srcs = self.cutToNodes(srcCut)
        
        #----------------------------------------------------------------------
        # Prepare definition of the target cut
        #----------------------------------------------------------------------
        tgtCut = list(srcCut)
        tgtCut.append(start)
        
        #----------------------------------------------------------------------
        # Copy original srcs into tgts
        #----------------------------------------------------------------------
        tgts = self.cutToNodes(tgtCut)
        self.copyValues(srcs, tgts)

        #----------------------------------------------------------------------
        # Iterate over states from <start> to <stop>
        #----------------------------------------------------------------------
        i = 0
        for time in range(start+1, stop+1):
            
            #------------------------------------------------------------------
            # Retrieve list of target nodes
            #------------------------------------------------------------------
            tgtCut[-1] = time
            tgts = self.cutToNodes(tgtCut)
    
            #------------------------------------------------------------------
            # Evolve one state
            #------------------------------------------------------------------
            self.evolveStateBase(srcs, tgts, a=time, b=time+inf)
            
            #------------------------------------------------------------------
            # Copy evolved state into srcs
            #------------------------------------------------------------------
            self.copyValues(tgts, srcs)
            
            i += 1
            
        #----------------------------------------------------------------------
        self.journal.O(f"{self.name}.evolve: evolved {i} states")

    #--------------------------------------------------------------------------
    def evolveStateBase(self, srcs, tgts, a, b=None):
        "Evolve state of the srcs nodes into tgts nodes"
        
        if b is None: b = a
        self.journal.I(f"{self.name}.evolveStateBase: For Sources relative to the target {a}..{b}")

        #----------------------------------------------------------------------
        # Doability check
        #----------------------------------------------------------------------
        if a > b: 
            self.journal.M(f"{self.name}.evolveStateBase: Bounadries ERROR: {a} > {b}", True)
            self.journal.O()
            return

        #----------------------------------------------------------------------
        # Phase rotation between two points - static data
        #----------------------------------------------------------------------
        rotDist  = (self.offMax - self.offMin) / (self.count()-1)  # distance in units
        rotPhase = (rotDist/_UPP) * 2 * math.pi                    # distance in radians
        self.journal.M(f"{self.name}.evolveStateBase: Phase between two points: {rotPhase:5.4} rad")

        #----------------------------------------------------------------------
        # Iteration prep
        #----------------------------------------------------------------------
        rotDir   = -1j                              # Direction of amplitude's rotation
        rotCoeff = cmath.exp(rotDir * rotPhase)     # rotation coefficient
        self.journal.M(f"{self.name}.evolveStateBase: Rot coeff: {rotCoeff:5.4}, abs = {abs(rotCoeff):5.4}")
        
        #----------------------------------------------------------------------
        # Preprae global aggregates
        #----------------------------------------------------------------------
        srcsSumAbs = 0
        for src in srcs: srcsSumAbs += src['cP'].abs()
        
        #----------------------------------------------------------------------
        # Iteration over tgts
        #----------------------------------------------------------------------
        posT = 0
        for tgtNode in tgts:
            
            cumAmp = complex(0,0)

            #------------------------------------------------------------------
            # Accumulation over srcs LEFT
            #------------------------------------------------------------------
            xL = posT - b
            yL = posT - a
            if xL  < 0   : xL  = 0  # pretecenie pred zaciatok
            
            for posS in range(xL, yL+1):

                srcNode = srcs[posS]
                
                #--------------------------------------------------------------
                # Rotate srcAmp by abs(posT-posS)*rotPhase
                #--------------------------------------------------------------
                rot    = cmath.exp(rotDir * abs(posT-posS) * rotPhase)
                srcAmp = srcNode['cP'].c * rot

                #--------------------------------------------------------------
                # Cumulate rotated srcAmp to cumAmp
                #--------------------------------------------------------------
                if True:          # Dvojite zapocitanie srcs[posT]
                
                    cumAmp += srcAmp
                    self.journal.M(f"{self.name}.evolveStateBase: Accumulation LEFT: {posS} -> {posT}")
            
            #------------------------------------------------------------------
            # Accumulation over srcs RIGHT
            #------------------------------------------------------------------
            xL = posT + a
            yL = posT + b
            if yL >= len(srcs): yL = len(srcs)-1  # pretecenie za koniec
            
            for posS in range(xL, yL+1):

                srcNode = srcs[posS]
                
                #--------------------------------------------------------------
                # Rotate srcAmp by abs(posT-posS)*rotPhase
                #--------------------------------------------------------------
                rot    = cmath.exp(rotDir * abs(posT-posS) * rotPhase)
                srcAmp = srcNode['cP'].c * rot

                #--------------------------------------------------------------
                # Cumulate rotated srcAmp to cumAmp
                #--------------------------------------------------------------
                if posT != posS:          # Dvojite zapocitanie srcs[posT]
                
                    cumAmp += srcAmp
                    self.journal.M(f"{self.name}.evolveStateBase: Accumulation RIGHT: {posT} <- {posS}")
            
            #------------------------------------------------------------------
            # Set target node value
            #------------------------------------------------------------------
            tgtNode['cP'].c = cumAmp

            #------------------------------------------------------------------
            # Move to the next tgt node
            #------------------------------------------------------------------
            posT += 1
            
        self.journal.M(f"{self.name}.evolveStateBase: srcsSumAbs: {srcsSumAbs:5.2}")

        #----------------------------------------------------------------------
        # Normalisation
        #----------------------------------------------------------------------
        self.normAbs(nods=tgts, norm=srcsSumAbs)

        #----------------------------------------------------------------------
        self.journal.O()

    #--------------------------------------------------------------------------
    def evolveState(self, srcs, tgts):
        "Evolve state of the srcs nodes into tgts nodes"
        
        self.journal.I(f"{self.name}.evolveState:")

        #----------------------------------------------------------------------
        # Phase rotation between two points - static data
        #----------------------------------------------------------------------
        rotDist  = (self.offMax - self.offMin) / (self.count()-1)  # distance in units
        rotPhase = (rotDist/_UPP) * 2 * math.pi                    # distance in radians
        self.journal.M(f"{self.name}.evolveState: Phase between two points: {rotPhase} rad")

        #----------------------------------------------------------------------
        # Iteration over tgts from left
        #----------------------------------------------------------------------
        rotDir   = -1j                              # Direction of amplitude's rotation
        rotCoeff = cmath.exp(rotDir * rotPhase)     # rotation coefficient
        self.journal.M(f"{self.name}.evolveState: Rot coeff: {rotCoeff}, abs = {abs(rotCoeff)}")
        
        cumAmp   = complex(0,0)                     # Cumulative amplitude

        #----------------------------------------------------------------------
        # Iteration over tgts from left
        #----------------------------------------------------------------------
        pos = 0
        for tgtNode in tgts:
            
            #------------------------------------------------------------------
            # Rotate cumulative amplitude by rotPhase angle (multiple by rotCoeff)
            #------------------------------------------------------------------
            cumAmp *= rotCoeff
            
            #------------------------------------------------------------------
            # Retrieve current source's amplitude
            #------------------------------------------------------------------
            srcAmp = srcs[pos]['cP'].c
            
            #------------------------------------------------------------------
            # Accumulate srcAmp to cumAmp
            #------------------------------------------------------------------
            cumAmp += srcAmp

            #------------------------------------------------------------------
            # Set target amplitude - ORIGINAL TARGET VALUE IS (0,0)
            #------------------------------------------------------------------
            tgtNode['cP'].c = cumAmp
            print(f"{pos:3} cum {cumAmp.real:7.3f} {cumAmp.imag:7.3f}j   src {srcAmp.real:7.3f} {srcAmp.imag:7.3f}j")
            
            #------------------------------------------------------------------
            # Move to the next right node
            #------------------------------------------------------------------
            pos += 1

        #----------------------------------------------------------------------
        # Iteration over tgts from right
        #----------------------------------------------------------------------
        print()
        rotDir   = -1j                              # Direction of amplitude's rotation
        rotCoeff = cmath.exp(rotDir * rotPhase)     # rotation coefficient
        
        cumAmp   = complex(0,0)                     # Cumulative amplitude
        
        #----------------------------------------------------------------------
        # Iteration over tgts from right
        #----------------------------------------------------------------------
        pos = len(tgts)-1
        for tgtNode in reversed(tgts):
            
            #------------------------------------------------------------------
            # Rotate cumulative amplitude by rotPhase angle (multiple by rotCoeff)
            #------------------------------------------------------------------
            cumAmp *= rotCoeff
            
            #------------------------------------------------------------------
            # Retrieve current source's amplitude
            #------------------------------------------------------------------
            srcAmp = srcs[pos]['cP'].c
            
            #------------------------------------------------------------------
            # Accumulate srcAmp to cumAmp
            #------------------------------------------------------------------
            cumAmp += srcAmp

            #------------------------------------------------------------------
            # Set target amplitude - ORIGINAL TARGET VALUE IS SETTED FROM LEFT ITERATION
            #------------------------------------------------------------------
            tgtNode['cP'].c += cumAmp
            print(f"{pos:3} cum {cumAmp.real:7.3f} {cumAmp.imag:7.3f}j   src {srcAmp.real:7.3f} {srcAmp.imag:7.3f}j")
            
            #------------------------------------------------------------------
            # Move to the next left node
            #------------------------------------------------------------------
            pos -= 1

        #----------------------------------------------------------------------
        self.journal.O()

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
    # API
    #--------------------------------------------------------------------------
    def getData(self, cut=None):
        "Returns numpy arrays as a cut from InfoMatrix"
    
        self.journal.I(f"{self.name}.getData: cut = {cut}")
    

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
print('InfoMatrix ver 3.01')

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
    im2.gener(cnts={'a':3, 'b':4}, origs={'a':0.0, 'b':0}, rect={'a':1.0, 'b':2}, vals={'v':'Value'}, defs={'v':3.0})
    print(im2)

    im3 = InfoMatrix(journal, 'Test matrix', ipType='ipTest')
    im3.gener(cnts={'a':3, 'b':4, 'c':2}, origs={'a':0.0, 'b':0, 'c':0}, rect={'a':1.0, 'b':2, 'c':3}, vals={'v':'Value'}, defs={'v':0.0})
    print(im3)

    print('pos=16 ', im3.pointByPos(16))
    print()

    print('[1, 3, 0] ', im3.pointByIdx([1, 3, 0]))
    print()

    print('vector')
    print(im3._vectorPosByIdx(['?', 2, 1]))
    vecs = im3.vectorByIdx(['?', 2, 1])
    for vec in vecs: print(vec)  
    print()

    print(im3._matrixPosByIdx([ 0, '?', '?']))
    print()




    print(im3._vectorPosByIdx([ 2, '?', 1]))
    print(im3._vectorPosByIdx([ 1, 0, '?']))


#    im1.applyPointFunction(ip.abs, key='v')
#    print(im1)

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------