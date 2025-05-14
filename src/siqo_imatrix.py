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
        self.orig       = {'x':0, 'y':0}  # Origin's coordinates of the InfoMatrix in lambda units
        self.points     = [[]]            # List of rows of lists of InfoPoints
        self.actKey     = None            # Key of the current InfoPoint's dat value
        self.staticEdge = False           # Static edge means value of the edge points is fixed in some methods
        
        #----------------------------------------------------------------------
        # Private datove polozky triedy
        #----------------------------------------------------------------------
        self._rows      = 0               # Number of rows in the InfoMatrix
        self._cols      = 0               # Number of columns in the InfoMatrix
        self._dx        = 0               # Distance between two points on axis X in lambda units
        self._dy        = 0               # Distance between two points on axis Y in lambda units
        self._iterPos   = 0               # Iterator's position in the InfoMatrix

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
        # Prejdem vsetky riadky
        #----------------------------------------------------------------------
        if self.actKey is None:    
            self.journal.M(f"{self.name}.__array__: ERROR: actKey is None", True)
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

                val = point.dat[self.actKey]
                if val is None:
                    self.journal.M(f"{self.name}.__array__: ERROR: point.dat[{self.actKey}] is None", True)
                    return None
                
                arrayRow.append(val)

            #------------------------------------------------------------------
            # Vlozim riadok do c2D
            #------------------------------------------------------------------
            array2D.append(arrayRow)

        #----------------------------------------------------------------------
        return np.array(array2D)

    #--------------------------------------------------------------------------
    def info(self, indent=0):
        "Creates info about this InfoMatrix"
        
        dat = {}
        msg = []

        #----------------------------------------------------------------------
        # info o celej strukture
        #----------------------------------------------------------------------
        if indent == 0:
            msg.append(f"{indent*_IND}{90*'='}")
            dat['name'       ] = self.name
            dat['ipType'     ] = self.ipType
            dat['orig'       ] = self.orig
            dat['rows'       ] = self._rows
            dat['cols'       ] = self._cols
            dat['dx'         ] = self._dx
            dat['dy'         ] = self._dy
            dat['count'      ] = self.count()
            dat['staticEdge' ] = self.staticEdge

        for key, val in dat.items(): msg.append(f"{indent*_IND}{key:<15}: {val}")

        #----------------------------------------------------------------------
        # info o riadkoch
        #----------------------------------------------------------------------
        for point in self:

            row, col = self._idxByIter(self._iterPos-1)
            msg.append(f"Point[{row:2},{col:2}] {point.info()['msg']}")
        
        #----------------------------------------------------------------------
        return {'res':'OK', 'dat':dat, 'msg':msg}
        
    #--------------------------------------------------------------------------
    def count(self):
        "Returns Count of nodes in this InfoMatrix"
        
        return self._rows * self._cols

    #--------------------------------------------------------------------------
    def copy(self, name):
        "Creates copy of this InfoMatrix"
        
        self.journal.I(f"{self.name}.copy: to {name}")

        #----------------------------------------------------------------------
        # Create new InfoMatrix with the same dimensions
        #----------------------------------------------------------------------
        toRet = InfoMatrix(self.journal, name, self.ipType)

        toRet.orig       = self.orig.copy()  # Origin's coordinates of the InfoMatrix 
        toRet.points     = [[]]              # List of rows of complex vectors {InfoPoint}
        toRet.actKey     = self.actKey       # Key of the InfoPoint's dat value
        toRet.staticEdge = self.staticEdge   # Static edge means value of the edge nodes is fixed

        toRet._rows      = self._rows        # Number of rows in the InfoMatrix
        toRet._cols      = self._cols        # Number of columns in the InfoMatrix
        toRet._dx        = self._dx          # Distance between two points on axis X in lambda units
        toRet._dy        = self._dy          # Distance between two points on axis Y in lambda units

        #----------------------------------------------------------------------
        # Copy all points from this InfoMatrix to the new one
        #----------------------------------------------------------------------
        for row in self.points:
            
            copyRow = []

            for point in row:
                copyRow.append(point.copy())

            toRet.points.append(copyRow)

        #----------------------------------------------------------------------
        self.journal.O()
        return toRet
        
    #==========================================================================
    # Iterator for all points in InfoMatrix
    #--------------------------------------------------------------------------
    def __iter__(self):
        "Creates iterator for this InfoMatrix"
        
        # Reset iterator's position
        self._iterPos = 0
        
        return self

    #--------------------------------------------------------------------------
    def __next__(self):
        "Returns next point in ongoing iteration"
        
        #----------------------------------------------------------------------
        # If there is one more node in list of nodes left
        #----------------------------------------------------------------------
        if self._iterPos < self.count():
                
            #------------------------------------------------------------------
            # Get current node in list of nodes
            #------------------------------------------------------------------
            row, col = self._idxByIter(self._iterPos)
            point = self.points[row][col]
            
            #------------------------------------------------------------------
            # Move to the next node
            #------------------------------------------------------------------
            self._iterPos += 1
            
            return point

        #----------------------------------------------------------------------
        # There is no more node in list of nodes left
        #----------------------------------------------------------------------
        else: raise StopIteration
            
    #--------------------------------------------------------------------------
    def _iterByIdx(self, row, col):
        "Returns iter position of the node in InfoMatrix by index"
        
        return (row * self._cols) + col

    #--------------------------------------------------------------------------
    def _idxByIter(self, pos):
        "Returns index of the node in InfoMatrix by iter position"

        row = pos // self._cols
        col = pos  % self._cols

        return (row, col)

    #==========================================================================
    # Point retrieval
    #--------------------------------------------------------------------------
    def pointByIdx(self, row, col):
        "Returns InfoPoint in field at respective indexes"
        
        try: toRet = self.points[row][col]
        except IndexError:
            self.journal.M(f"{self.name}.pointByIdx: ERROR: [{row},{col}] is out of range", True)
            return None
        
        return toRet
        
    #--------------------------------------------------------------------------
    def pointByPos(self, x, y):
        "Returns nearest Point in field for respective position"

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
    # Structure modification
    #--------------------------------------------------------------------------
    def reset(self, ipType=None):
        "Resets all InfoMatrix's data and destroys all points. Count of points will be 0"
        
        self.journal.I(f"{self.name}.reset: ipType={ipType}")
        
        if ipType is not None: self.ipType = ipType

        self.orig       = {'x':0, 'y':0}  # Origin's coordinates of the InfoMatrix 
        self.points     = [[]]            # List of rows of lists of InfoPoints
        self.actKey     = None            # Key of the InfoPoint's current dat value
        self.staticEdge = False           # Static edge means value of the edge nodes is fixed        

        self._rows      = 0               # Number of rows in the InfoMatrix
        self._cols      = 0               # Number of columns in the InfoMatrix
        self._dx        = 0               # Distance between two points on axis X in lambda units
        self._dy        = 0               # Distance between two points on axis Y in lambda units
        self._iterPos   = 0               # Iterator's position in the InfoMatrix

        self.journal.O()
        
    #--------------------------------------------------------------------------
    def gener(self, nRow:int, nCol:int, *, ipType=None, vals:dict, defs:dict={}, orig:dict={'x':0, 'y':0}, rect:tuple=(1,1) ):
        "Creates InfoMatrix with respective settings"
        
        self.journal.I(f"{self.name}.gener: {nRow}x{nCol} points on rect {rect[0]}x{rect[1]} from {orig}")
        self.reset(ipType=ipType)

        xDim = list(orig.keys()  )[0]
        xMin = list(orig.values())[0]

        yDim = list(orig.keys()  )[1]
        yMin = list(orig.values())[1]

        #----------------------------------------------------------------------
        # InfoMatrix settings
        #----------------------------------------------------------------------
        self.orig      = orig.copy()           # List of origin's coordinates of the InfoMatrix
        self._rows     = nRow                  # Number of rows in the InfoMatrix       
        self._cols     = nCol                  # Number of columns in the InfoMatrix
        self._dx       = rect[0]/(nRow-1)      # Distance between two points on axis X in lambda units
        self._dy       = rect[1]/(nCol-1)      # Distance between two points on axis Y in lambda units
        
        self.actKey    = key                   # Key of the InfoPoint's current dat value

        #----------------------------------------------------------------------
        # Set InfoPoint's schema 
        #----------------------------------------------------------------------
        InfoPoint.clearSchema(self.ipType)     # Clear schema for this InfoPoint type
       
        InfoPoint.setAxe(self.ipType, xDim, 'osa X')    
        InfoPoint.setAxe(self.ipType, yDim, 'osa Y')   

        for key, name in vals.items():
            InfoPoint.setVal(self.ipType, key, name) 

        #----------------------------------------------------------------------
        # Generate nRow x nCol nodes at respective positions
        #----------------------------------------------------------------------
        point = None
        for row in range(nRow):

            #------------------------------------------------------------------
            # Create new row of InfoPoint at respective position
            #------------------------------------------------------------------
            self.points.append([])
            x = xMin + (row * self._dx)
            
            for col in range(nCol):
                
                #--------------------------------------------------------------
                # Create new InfoPoint at respective position
                #--------------------------------------------------------------
                y = yMin + (col * self._dy)
                point = InfoPoint(self.ipType, pos={xDim:x, yDim:y}, dat=defs)
                
                #--------------------------------------------------------------
                # Append new InfoPoint to the list of nodes
                #--------------------------------------------------------------
                self.points[row].append(point)
            
        #----------------------------------------------------------------------
        # Final adjustments
        #----------------------------------------------------------------------
        if point is not None: point.setJournal(self.journal)
        self.journal.O()
        
    #==========================================================================
    # Value modification
    #--------------------------------------------------------------------------
    def clear(self, *, key=None, defs:dict={}):
        "Set all InfoPoint's values to default value"
        
        #----------------------------------------------------------------------
        # Clear all InfoPoint's values
        #----------------------------------------------------------------------
        for point in self:

            if key is None: point.clear()
            else          : point.clear(dat=defs)

        #----------------------------------------------------------------------
        # Clear InfoMatrix's settings
        #----------------------------------------------------------------------
        self.actKey   = key         # Key of the InfoPoint's current dat value

        self.journal.M(f"{self.name}.clear: key={key}, val={val}")
        
    #--------------------------------------------------------------------------

    #==========================================================================
    # Complex Field Information
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

    im = InfoMatrix(journal, 'Test matrix')
    print(im)

    im.gener(nRow=4, nCol=5, key='val', val=-5, xLen=1, yLen=1, orig={'a':5, 'b':7})
    print(im)

    im.applyPointFunction(ip.abs, key='v')
    print(im)

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------