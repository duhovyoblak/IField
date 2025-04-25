#==============================================================================
# Siqo class ComplexMatrix
#------------------------------------------------------------------------------
import math
import cmath
import numpy                 as np
import random                as rnd

from siqo_cpoint import ComplexPoint

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_IND    = '|  '       # Info indentation
_UPP    = 10          # distance units per period

#==============================================================================
# package's variables
#------------------------------------------------------------------------------


#==============================================================================
# ComplexMatrix
#------------------------------------------------------------------------------
class ComplexMatrix:

    #==========================================================================
    # Static variables & methods
    #--------------------------------------------------------------------------

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, journal, name):
        "Calls constructor of ComplexMatrix"

        self.journal = journal
        self.journal.I(f"ComplexMatrix.constructor: {name}")
        
        #----------------------------------------------------------------------
        # Public datove polozky triedy
        #----------------------------------------------------------------------
        self.name       = name        # Name of the ComplexMatrix
        self.dims       = ['x', 'y']  # List of dimensions of the ComplexMatrix
        self.orig       = [0, 0]      # List of origin's coordinates of the ComplexMatrix in lambda units
        self.nodes      = [[]]        # List of rows of complex vectors {ComplexPoint}
        self.staticEdge = False       # Static edge means value of the edge nodes is fixed
        
        #----------------------------------------------------------------------
        # Private datove polozky triedy
        #----------------------------------------------------------------------
        self._rows      = 0           # Number of rows in the ComplexMatrix
        self._cols      = 0           # Number of columns in the ComplexMatrix
        self._dx        = 0           # Distance between two points on axis X in lambda units
        self._dy        = 0           # Distance between two points on axis Y in lambda units
        self._iterPos   = 0           # Iterator's position in the ComplexMatrix

        self.journal.O(f"{self.name}.constructor: done")

    #--------------------------------------------------------------------------
    def __str__(self):
        "Prints info about this ComplexMatrix"

        toRet = ''
        for line in self.info()['msg']: toRet += line +'\n'
        return toRet

    #--------------------------------------------------------------------------
    def __array__(self):
        "Returns ComplexMatrix as 2D numpy array"
 
        c2D = [[]]

        #----------------------------------------------------------------------
        # Prejdem vsetky riadky
        #----------------------------------------------------------------------
        for row in self.nodes:

            cRow = []

            #------------------------------------------------------------------
            # Prejdem vsetky body v riadku
            #------------------------------------------------------------------
            for point in row:
                cRow.append(point.c)

            #------------------------------------------------------------------
            # Vlozim riadok do c2D
            #------------------------------------------------------------------
            c2D.append(cRow)

        #----------------------------------------------------------------------
        return np.array(c2D, dtype=complex)

    #--------------------------------------------------------------------------
    def info(self, indent=0):
        "Creates info about this ComplexMatrix"
        
        dat = {}
        msg = []

        #----------------------------------------------------------------------
        # info o celej strukture
        #----------------------------------------------------------------------
        if indent == 0:
            msg.append(f"{indent*_IND}{90*'='}")
            dat['name'       ] = self.name
            dat['dimensions' ] = self.dims
            dat['rows'       ] = self._rows
            dat['cols'       ] = self._cols
            dat['dx'         ] = self._dx
            dat['dy'         ] = self._dy
            dat['count'      ] = self.count()
            dat['orig'       ] = self.orig
            dat['staticEdge' ] = self.staticEdge

        for key, val in dat.items(): msg.append(f"{indent*_IND}{key:<15}: {val}")

        #----------------------------------------------------------------------
        # info o riadkoch
        #----------------------------------------------------------------------
        for node in self:

            row, col = self.idxByIter(self._iterPos)
            msg.append(f"Point[{row},{col}] {node.info()}")
        
        #----------------------------------------------------------------------
        return {'res':'OK', 'dat':dat, 'msg':msg}
        
    #--------------------------------------------------------------------------
    def count(self):
        "Returns Count of nodes in this ComplexMatrix"
        
        return self._rows * self._cols

    #--------------------------------------------------------------------------
    def copy(self, name):
        "Creates copy of this ComplexMatrix"
        
        self.journal.I(f"{self.name}.copy: to {name}")

        #----------------------------------------------------------------------
        # Create new ComplexMatrix with the same dimensions
        #----------------------------------------------------------------------
        toRet = ComplexMatrix(self.journal, name)

        toRet.dims       = self.dims.copy()  # List of dimensions of the ComplexMatrix
        toRet.orig       = self.orig.copy()  # List of origin's coordinates of the ComplexMatrix 
        toRet.nodes      = [[]]              # List of rows of complex vectors {ComplexPoint}
        toRet.rows       = self._rows        # Number of rows in the ComplexMatrix
        toRet.cols       = self._cols        # Number of columns in the ComplexMatrix
        toRet.dx         = self._dx          # Distance between two points on axis X in lambda units
        toRet.dy         = self._dy          # Distance between two points on axis Y in lambda units
        toRet.staticEdge = self.staticEdge   # Static edge means value of the edge nodes is fixed

        #----------------------------------------------------------------------
        # Copy all nodes from this ComplexMatrix to the new one
        #----------------------------------------------------------------------
        for row in self.nodes:
            
            copyRow = []

            for point in row:
                copyRow.append(point.copy())

            toRet.nodes.append(copyRow)

        #----------------------------------------------------------------------
        self.journal.O()
        return toRet
        
    #==========================================================================
    # Iterator for all nodes in ComplexMatrix
    #--------------------------------------------------------------------------
    def __iter__(self):
        "Creates iterator for this ComplexMatrix"
        
        # Reset iterator's position
        self._iterPos = 0
        
        return self

    #--------------------------------------------------------------------------
    def __next__(self):
        "Returns next node in ongoing iteration"
        
        #----------------------------------------------------------------------
        # If there is one more node in list of nodes left
        #----------------------------------------------------------------------
        if self._iterPos < self.count():
                
            #------------------------------------------------------------------
            # Get current node in list of nodes
            #------------------------------------------------------------------
            row, col = self.idxByIter(self._iterPos)
            node = self.nodes[row][col]
            
            #------------------------------------------------------------------
            # Move to the next node
            #------------------------------------------------------------------
            self._iterPos += 1
            
            return node

        #----------------------------------------------------------------------
        # There is no more node in list of nodes left
        #----------------------------------------------------------------------
        else: raise StopIteration
            
    #--------------------------------------------------------------------------
    def iterByIdx(self, row, col):
        "Returns iter position of the node in ComplexMatrix by index"
        
        return (row * self._cols) + col

    #--------------------------------------------------------------------------
    def idxByIter(self, pos):
        "Returns index of the node in ComplexMatrix by iter position"

        row = pos // self._cols
        col = pos  % self._cols

        return (row, col)

    #==========================================================================
    # Point retrieval
    #--------------------------------------------------------------------------
    def pointByIdx(self, row, col):
        "Returns ComplexPoint in field at respective indexes"
        
        try: toRet = self.nodes[row][col]
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
            if self.nodes[row][0].pos[0] >= x: break

        #----------------------------------------------------------------------
        # Row index before or after x ?
        #----------------------------------------------------------------------
        if lstRow < self._rows-1:

            if abs(self.nodes[lstRow][0].pos[0]-x) > abs(self.nodes[lstRow+1][0].pos[0]-x):
                lstRow += 1

        #----------------------------------------------------------------------
        # Searching for the col index for respective y
        #----------------------------------------------------------------------
        for col in range(self._cols):

            lstCol = col
            if self.nodes[0][col].pos[1] >= y: break
        
        #----------------------------------------------------------------------
        # Col index before or after y ? 
        #----------------------------------------------------------------------
        if lstCol < self._cols-1:

            if abs(self.nodes[0][lstCol].pos[1]-y) > abs(self.nodes[0][lstCol+1].pos[1]-y):
                lstCol += 1

        #----------------------------------------------------------------------
        # Final 
        #----------------------------------------------------------------------
        return self.nodes[lstRow][lstCol]
      
    #==========================================================================
    # Structure modification
    #--------------------------------------------------------------------------
    def reset(self):
        "Clears all ComplexMatrix's data. Count of nodes = 0"
        
        self.journal.I(f"{self.name}.reset:")
        
        self.dims      = ['x', 'y']  # List of dimensions of the ComplexMatrix
        self.orig      = [0, 0]      # List of origin's coordinates of the ComplexMatrix 
        self.nodes     = [[]]        # List of rows of complex vectors {ComplexPoint}

        self._rows     = 0           # Number of rows in the ComplexMatrix
        self._cols     = 0           # Number of columns in the ComplexMatrix
        self._dx       = 0           # Distance between two points on axis X in lambda units
        self._dy       = 0           # Distance between two points on axis Y in lambda units
        self._iterPos  = 0           # Iterator's position in the ComplexMatrix

        self.journal.O()
        
    #--------------------------------------------------------------------------
    def gener(self, nRow, nCol, c=complex(0,0), xMin=0, xMax=1, yMin=0, yMax=1, orig=[0, 0]):
        "Creates ComplexMatrix with respective settings"
        
        self.journal.I(f"{self.name}.gener: {nRow}*{nCol} nodes ({xMin}...{xMax}) x ({yMin}...{yMax}) from {orig}")

        self.reset()

        #----------------------------------------------------------------------
        # ComplexMatrix settings
        #----------------------------------------------------------------------
        self.orig      = orig.copy()           # List of origin's coordinates of the ComplexMatrix
        self._rows     = nRow                  # Number of rows in the ComplexMatrix       
        self._cols     = nCol                  # Number of columns in the ComplexMatrix
        self._dx       = (xMax-xMin)/(nRow-1)  # Distance between two points on axis X in lambda units
        self._dy       = (yMax-yMin)/(nCol-1)  # Distance between two points on axis Y in lambda units
        
        #----------------------------------------------------------------------
        # Generate nRow x nCol nodes at respective positions
        #----------------------------------------------------------------------
        for row in range(nRow):

            #------------------------------------------------------------------
            # Create new row of ComplexPoint at respective position
            #------------------------------------------------------------------
            self.nodes.append([])
            x = xMin + (row * self._dx)
            
            for col in range(nCol):
                
                #--------------------------------------------------------------
                # Create new ComplexPoint at respective position
                #--------------------------------------------------------------
                y = yMin + (col * self._dy)
                c = ComplexPoint(pos=[x,y], c=c)
                
                #--------------------------------------------------------------
                # Append new ComplexPoint to the list of nodes
                #--------------------------------------------------------------
                self.nodes[row].append(c)
            
        #----------------------------------------------------------------------
        # Final adjustments
        #----------------------------------------------------------------------
        self.journal.O()
        
    #==========================================================================
    # Value modification
    #--------------------------------------------------------------------------
    def clear(self, c=complex(0,0)):
        "Set all ComplexPoint's values to default value"
        
        for node in self:
            node.clear(c)           

        self.journal.M(f"{self.name}.clear:")
        
    #--------------------------------------------------------------------------

    #==========================================================================
    # Complex Field Information
    #--------------------------------------------------------------------------
    def Xamp(self):
        "Returns amplitude of the node"

        if self.isBase(): return self.objVal
        else            : return self.objVal.amp()

    #--------------------------------------------------------------------------
    def Xprob(self):
        "Returns probability of the amplitude of the node"

        if self.isBase(): return self.objVal * self.objVal.conjugate()
        else            : return self.objVal.prob()

    #==========================================================================
    # Methods application
    #--------------------------------------------------------------------------
    def copyValues(self, srcs, tgts):
        "Copy node's values from srcs to tgts nodes"
        
        self.journal.I(f"{self.name}.copyValues: from {len(srcs)} nodes to {len(tgts)} nodes")

        #----------------------------------------------------------------------
        # Iterate over src nodes
        #----------------------------------------------------------------------
        pos    = 0
        tgtLen = len(tgts)

        for srcNode in srcs: 
            
            # Trying retrieve target node
            if pos < tgtLen:
                
                tgtNode = tgts[pos]
                tgtNode['cP'].c = srcNode['cP'].c
                pos += 1
                
            else:
                self.journal.M(f"{self.name}.copyValues: WARNING Not enough target nodes", True)
                break
                
        #----------------------------------------------------------------------
        # Check if there are some tgtNodes left
        #----------------------------------------------------------------------
        if pos < tgtLen:
            self.journal.M(f"{self.name}.copyValues: WARNING Not enough source nodes", True)

        #----------------------------------------------------------------------
        self.journal.O(f"{self.name}.copyValues: Copied {pos} nodes")
        return pos
        
    #--------------------------------------------------------------------------
    def copySlice(self, dim, pos):
        "Copy values from higher dimension's slice to the lower dimension"
        
        self.journal.I(f"{self.name}.copySlice: from {dim} D[{pos}]")

        #----------------------------------------------------------------------
        # Target set
        #----------------------------------------------------------------------
        tgtCut = self.cutDim(dim-1)
        tgts   = self.cutToNodes(tgtCut)
        
        #----------------------------------------------------------------------
        # Source set
        #----------------------------------------------------------------------
        srcCut = list(tgtCut)
        srcCut.append(pos)
        srcs = self.cutToNodes(srcCut)
        
        #----------------------------------------------------------------------
        # Copy srcs into tgts
        #----------------------------------------------------------------------
        copied = self.copyValues(srcs, tgts)

        #----------------------------------------------------------------------
        self.journal.O(f"{self.name}.copySlice: Copied {copied} nodes")
        
    #--------------------------------------------------------------------------
    def rndBit(self, prob, srcCut=None):
        "Sets all ComplexPoint values to random bit with respective probability"

        if srcCut==None: self.cutAll()
        else           : self.iterCut = srcCut
        
        for node in self: node['cP'].rndBit(prob)

        self.journal.M(f"{self.name}.rndBit: Nodes in {self.iterCut} with prob={prob}")
        
    #--------------------------------------------------------------------------
    def rndPhase(self, r=1, srcCut=None):
        "Sets all ComplexPoint values to random phase with respective radius"

        if srcCut==None: self.cutAll()
        else           : self.iterCut = srcCut
        
        for node in self: node['cP'].rndPhase(r)

        self.journal.M(f"{self.name}.rndPhase: Nodes in {self.iterCut} with r={r}")
        
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
        "Returns dict of numpy arrays as a cut from ComplexMatrix"
    
        self.journal.I(f"{self.name}.getData: cut = {cut}")
    
        #----------------------------------------------------------------------
        # Applying cut
        #----------------------------------------------------------------------
        if cut is not None: self.iterCut = cut
        
        #----------------------------------------------------------------------
        # Prepare output for respective cut
        #----------------------------------------------------------------------
        dimMax = self.dimMax()
        data     = {}
        
        # Prepare all coordinate series
        for i in range(dimMax): data[f'x{i+1}'] = []
        
        # Prepare value series
        data['val'] = []
        
        #----------------------------------------------------------------------
        # Iterate over cP in field
        #----------------------------------------------------------------------
        for node in self:
            
            cP = node['cP']
            
            # Add X for coordinates
            i = 0
            for coor in cP.pos: 
                data[f'x{i+1}'].append(coor)
                i += 1
                
            # Add values
            data['val'].append(cP)

        #----------------------------------------------------------------------
        # Create toRet np-array for coordinates
        #----------------------------------------------------------------------
        toRet = []
        for key, arr in data.items():
            
            if key == 'val': toRet.append( {'key':key, 'arr':arr          } )
            else           : toRet.append( {'key':key, 'arr':np.array(arr)} )

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
print('ComplexMatrix ver 3.01')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------