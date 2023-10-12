#==============================================================================
# Siqo class CompplexField
#------------------------------------------------------------------------------
import sys
sys.path.append('..\siqo_lib')

import math
import cmath
import numpy                 as np
import random                as rnd

from siqo_cpoint import ComplexPoint

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_IND    = '|  '       # Info indentation
_DPL    = 10          # Default dots per lambda
_LIN    = 'linear'    # Default type of offsets
_LOG    = 'log10'
_LN2    = 'log2'

#==============================================================================
# package's variables
#------------------------------------------------------------------------------


#==============================================================================
# ComplexField
#------------------------------------------------------------------------------
class ComplexField:

    #==========================================================================
    # Static variables & methods
    #--------------------------------------------------------------------------
    @staticmethod
    def genOffset(journal, count, offMin, offMax, offType):
        "Generates offsets (coordinates from origin) for respective setting"
        
        journal.I(f"ComplexField.genOffset: {count} for <{offMin:7.2f}...{offMax:7.2f}> offType {offType}")

        #----------------------------------------------------------------------
        # Creating parameters
        #----------------------------------------------------------------------
        if offType==_LIN: 
            lb = offMin
            lk = (           offMax  - lb) / (count-1)
        
        elif offType==_LOG: 
            eb = math.log10(offMin)
            ek = (math.log10(offMax) - eb) / (count-1)
        
        #----------------------------------------------------------------------
        # Creating offsets using parameters
        #----------------------------------------------------------------------
        offs = {}
        for i in range(count):

            if   offType==_LIN: off =              (lb + lk * i)
            elif offType==_LOG: off = math.pow(10, (eb + ek * i) )
            
            offs[i] = off

        journal.O()
        return offs

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, journal, name):
        "Calls constructor of ComplexField"

        self.journal = journal
        self.journal.I(f"ComplexField.constructor: {name}")
        
        #----------------------------------------------------------------------
        # Public datove polozky triedy
        #----------------------------------------------------------------------
        self.name      = name    # Name of the whole structure
        self.dimName   = ''      # Name of this dimension
        
        self.origPos   = []      # point's position to which is attached this subfield
        self.offMin    = 0       # Min offset distance in lambda from mother dimension
        self.offMax    = 1       # Max offset distance in lambda from mother dimension
        self.offType   = _LIN    # offType of offsets of nodes
        
        self.nodes     = []      # List of nodes {ComplexPoint, ComplexFields}
        
        #----------------------------------------------------------------------
        # Private datove polozky triedy
        #----------------------------------------------------------------------
        self.iterNodes = []      # List of nodes for iteration
        self.iterPos   = 0       # Iterator's position in self.iterNodes[]
        self.iterCut   = []      # Definition of cut applied in iterator
                                 # as list <1..dimMax> of selected indices <0..count-1>
                                 # indice's value -1 means ALL nodes selected for respective dimension

        self.journal.O(f"{self.name}.constructor: done")

    #--------------------------------------------------------------------------
    def dim(self):
        "Returns to which dimension belongs this ComplexField"
        
        return len(self.origPos)+1

    #--------------------------------------------------------------------------
    def dimMax(self, deep=0):
        "Returns max dimension of whole structure"
        
        # Ak prvy node neobsahuje dalsie cF ukoncim pocitanie dimenzii
        if self.nodes[0]['cF'] is None: return deep+1
        else                          : return self.nodes[0]['cF'].dimMax(deep+1)

    #--------------------------------------------------------------------------
    def count(self):
        "Returns Count of nodes in this ComplexField"
        
        return len(self.nodes)

    #--------------------------------------------------------------------------
    def copy(self, name):
        "Creates copy of this ComplexField"
        
        self.journal.I(f"{self.name}.copy: {name}")
        

        self.journal.O()
        
    #--------------------------------------------------------------------------
    def info(self, indent=0):
        "Creates info about this ComplexField"
        
        dat = {}
        msg = []

        #----------------------------------------------------------------------
        # info o cele strukture
        #----------------------------------------------------------------------
        if indent == 0:
            msg.append(f"{indent*_IND}{90*'='}")
            dat['name'       ] = self.name
            dat['dimensions' ] = self.dimMax()
    
        #----------------------------------------------------------------------
        # info o dimenzii
        #----------------------------------------------------------------------
        msg.append(f"{indent*_IND}{90*'-'}")
        
        dat['dim'        ] = self.dim()
        dat['dimName'    ] = self.dimName
        dat['count'      ] = self.count()
        dat['origPos'    ] = self.origPos
        dat['offMin'     ] = self.offMin
        dat['offMax'     ] = self.offMax
        dat['offType'    ] = self.offType
        dat['iterCut'    ] = self.iterCut

        for key, val in dat.items(): msg.append("{}{:<15}: {}".format(indent*_IND, key, val))

        #----------------------------------------------------------------------
        # info
        #----------------------------------------------------------------------
        for node in self.nodes:
        
            if node['cF'] is None: subMsg = node['cP'].info(indent+1)['msg']
            else                 : subMsg = node['cF'].info(indent+1)['msg']
            msg.extend(subMsg)
        
        #----------------------------------------------------------------------
        return {'res':'OK', 'dat':dat, 'msg':msg}
        
    #--------------------------------------------------------------------------
    def __str__(self):
        "Prints info about this ComplexField"

        toRet = ''
        for line in self.info()['msg']: toRet += line +'\n'
        return toRet

    #==========================================================================
    # Iterator's node's generator and named cuts settings
    #--------------------------------------------------------------------------
    def cutToNodes(self, cut=None):
        "Creates list of nodes for respective cut's definition for iteration"
        
        #----------------------------------------------------------------------
        # Inicializacia
        #----------------------------------------------------------------------
        if cut is None:
            
            self.journal.I(f"{self.name}.cutToNodes: Cut is {self.iterCut}")
            root = True
            cut  = self.iterCut
            
        else: root = False
        
        #----------------------------------------------------------------------
        # Vycistim zoznam iter Nodes a pripravim si cut left for next recursion
        #----------------------------------------------------------------------
        self.iterNodes = []
        cutLeft = list(cut[1:])

        #----------------------------------------------------------------------
        # Prejdem vsetky pozicie v cF
        #----------------------------------------------------------------------
        for pos in range(self.count()):
            
            #------------------------------------------------------------------
            # Skontrolujem, ci je pozicia selected v cut definicii
            #------------------------------------------------------------------
            if  (cut[0] == -1) or (cut[0] == pos):
                
                #--------------------------------------------------------------
                # Vyberiem node na pos pozicii
                #--------------------------------------------------------------
                node = self.nodes[pos]

                #--------------------------------------------------------------
                # Ak zostala este dalsia dimenzia v cut, vnorim sa hlbsie do rekurzie
                #--------------------------------------------------------------
                if len(cutLeft) > 0: self.iterNodes.extend( node['cF'].cutToNodes(cutLeft) )
                
                # Ak nezostala ziadna cutLeft, trivialne riesenie je vlozit tento node do iterNodes
                else               : self.iterNodes.append(node)
            #------------------------------------------------------------------
        
        #----------------------------------------------------------------------
        # Finalizacia
        #----------------------------------------------------------------------
        if root:
            self.journal.O(f"{self.name}.cutToNodes: iterNodes are {len(self.iterNodes)}")
        
        #----------------------------------------------------------------------
        return self.iterNodes
        
    #--------------------------------------------------------------------------
    def cutZeros(self):
        "Returns cut's definition for pplaceholders 0 for all points"
        
        self.iterCut  = [0 for i in range(self.dimMax())]
        
        self.journal.M(f"{self.name}.cutZeros: Cut is {self.iterCut}")
        return self.iterCut
        
    #--------------------------------------------------------------------------
    def cutAll(self):
        "Returns cut's definition for all points in max dimension"
        
        self.iterCut  = [-1 for i in range(self.dimMax())]
 
        self.journal.M(f"{self.name}.cutAll: Cut is {self.iterCut}")
        return self.iterCut
        
    #--------------------------------------------------------------------------
    def cutDim(self, dim):
        "Returns cut's definition for all points in respective dimension"
        
        self.iterCut  = [-1 for i in range(dim)]

        self.journal.M(f"{self.name}.cutDim: For dim={dim} is {self.iterCut}")
        return self.iterCut
        
    #==========================================================================
    # Iterator based on cut[[]] definition
    #--------------------------------------------------------------------------
    def __iter__(self):
        "Creates iterator for this ComplexField"
        
        # Reset iterator's position and generate list of nodes for iteration
        self.iterPos = 0
        self.cutToNodes()
        
        return self

    #--------------------------------------------------------------------------
    def __next__(self):
        "Returns next node in ongoing iteration"
        
        #----------------------------------------------------------------------
        # If there is one more node in list of nodes left
        #----------------------------------------------------------------------
        if self.iterPos < len(self.iterNodes):
                
            # Get current node in list of nodes
            node = self.iterNodes[self.iterPos]
            
            # Move to the next node
            self.iterPos += 1
            
            return node

        #----------------------------------------------------------------------
        # There is no more node in list of nodes left
        #----------------------------------------------------------------------
        else: raise StopIteration
            
    #==========================================================================
    # Structure modification
    #--------------------------------------------------------------------------
    def reset(self):
        "Clears ComplexField and reset it to dimension=1"
        
        self.journal.I(f"{self.name}.reset:")
        
        self.nodes.clear()        # Odstranenie vsetkych poli

        self.origIdx = []         # Reset of the origin point indices
        self.offMin  =  0
        self.offMax  =  1
        self.offType = _LIN       # offType of offsets in underlying field
        
        self.iterCut = []         # Definition of cut applied in iterator
        
        self.journal.O()
        
    #--------------------------------------------------------------------------
    def gener(self, dimName, count, offMin, offMax, offType=_LIN, origPos=[]):
        "Creates 1D ComplexField with respective settings"
        
        self.journal.I(f"{self.name}.gener: '{dimName}': {count} nodes between {offMin}...{offMax} from {origPos}")

        self.nodes.clear()

        #----------------------------------------------------------------------
        # ComplexField settings
        #----------------------------------------------------------------------
        self.dimName = dimName
        self.origPos = origPos
        self.offMin  = offMin
        self.offMax  = offMax
        self.offType = offType
        
        #----------------------------------------------------------------------
        # Creating dict of offsets positions and add one dimension to origPos
        #----------------------------------------------------------------------
        offs   = ComplexField.genOffset(self.journal, count, self.offMin, self.offMax, self.offType)
        actPos = list(origPos)
        actPos.append(0)

        #----------------------------------------------------------------------
        # Generate <count> nodes in cF at position actPos = [origPos, offset]
        #----------------------------------------------------------------------
        for i, offset in offs.items():
            
            #------------------------------------------------------------------
            # Create copy of the <pos> list and add <offset> coordinate
            #------------------------------------------------------------------
            actPos[-1] = offset
            
            cP = ComplexPoint(actPos)
            
            #------------------------------------------------------------------
            # Pridam do ComplexFiled { complexPoint, None subfield }
            #------------------------------------------------------------------
            self.nodes.append( {'cP':cP, 'cF':None} )
            
        #----------------------------------------------------------------------
        # Final adjustments
        #----------------------------------------------------------------------
        self.journal.O()
        
    #--------------------------------------------------------------------------
    def extend(self, dimName, count, offMin=None, offMax=None, offType=_LIN):
        "Assigns to each node of this ComplexField new ComplexField subfield"
        
        self.journal.I(f"{self.name}.extend: {dimName}: {count} in offset <{offMin} - {offMax}> by {offType}")
        
        #----------------------------------------------------------------------
        # Select all leaves nodes of the tree
        #----------------------------------------------------------------------
        self.cutAll()

        #----------------------------------------------------------------------
        # Iterate through all leaves nodes of the tree and add ComplexField to them
        #----------------------------------------------------------------------
        for node in self:
            
            actPos = node['cP'].pos
            
            subField = ComplexField(self.journal, f"{self.name}_sub")
            subField.gener(dimName=dimName, count=count, offMin=offMin, offMax=offMax, offType=offType, origPos=actPos)

            # Assign subfield to respective node
            node['cF'] = subField
            
        #----------------------------------------------------------------------
        self.journal.O()

    #==========================================================================
    # ComplexPoint value modification
    #--------------------------------------------------------------------------
    def getPointByIdx(self, idx):
        "Returns ComplexPoint in field at respective position"
        
        #idx = [x1, x2, x3, ...]
        
        if len(idx) > 1: return self.nodes[idx[0]]['cF'].getPointByIdx(idx[1:])
        else           : return self.nodes[idx[0]]['cP']

    #--------------------------------------------------------------------------
    def getPointByPos(self, coord, deep=0):
        "Returns nearest Point in field for respective coordinates"

        idx  = -1            # Indices of the nearest point
        srch = coord[deep]   # Coordinate of the searched point in respective dimension
        
        self.journal.I(f"{self.name}.getPointByPos: coord={coord}, srch={srch}, deep={deep}")

        #----------------------------------------------------------------------
        # Initialise distance to previous point (e.g., first)
        #----------------------------------------------------------------------
        i = 0
        dltPrev = self.nodes[i]['cP'].pos[deep] - srch
        i += 1

        #----------------------------------------------------------------------
        # Iterate over all next points
        #----------------------------------------------------------------------
        while i < self.count():
            
            # Distance to actual (i-th) point
            dltAct = self.nodes[i]['cP'].pos[deep] - srch

            #------------------------------------------------------------------
            #  If the actual point has greater coord than <srch>
            #------------------------------------------------------------------
            if dltAct >= 0:
                
                #--------------------------------------------------------------
                # Return nearer point: Previous or Actual
                #--------------------------------------------------------------
                if abs(dltAct) <= abs(dltPrev): idx = i
                else                          : idx = i-1
                
                break

            #------------------------------------------------------------------
            # Move to the next point
            #------------------------------------------------------------------
            dltPrev = dltAct
            i += 1

        #----------------------------------------------------------------------
        # If pos was not set then set it to last point
        #----------------------------------------------------------------------
        if idx == -1: idx = i-1
        
        #----------------------------------------------------------------------
        # Prepare return value
        #----------------------------------------------------------------------
        lstPos = [idx]
        
        #----------------------------------------------------------------------
        # If there are not-yet-resolved coordinates left then recursive
        #----------------------------------------------------------------------
        if len(coord) > (deep+1):
            
            # field to be searched 
            sF = self.nodes[idx]['cF']
            
            lstPos.extend( sF.getPointByPos(coord, deep+1) )
                    
        self.journal.O()

        #----------------------------------------------------------------------
        # If deep == 0 the return point on position lstPos
        #----------------------------------------------------------------------
        if deep == 0: return self.getData(cut=lstPos)[-1]['arr'][0]
        
        #----------------------------------------------------------------------
        # If deep != 0 then return list of indices of the nearest point
        #----------------------------------------------------------------------
        return lstPos
      
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
    def clear(self):
        "Clear all ComplexPoint values"
        
        self.cutAll()
        for node in self: node['cP'].clear()

        self.journal.M(f"{self.name}.clear:")
        
    #--------------------------------------------------------------------------
    def copyTo(self, srcCut, cutPos):
        "Copy ComplexPoint values from srcCut to next dimension at cutPos"
        
        self.journal.I(f"{self.name}.copyTo: from {srcCut} to position {cutPos}")

        #----------------------------------------------------------------------
        # Iterate over srcCut nodes
        #----------------------------------------------------------------------
        self.iterCut = srcCut
        i        = 0

        for idx, node in self: 
            
            # Source complex value at position
            srcVal = node['cP'].c
            
            # Target position is actPos with added cutPos
            tgtPos = list(srcPos)
            tgtPos.append(cutPos)
            
            self.journal.M(f"{self.name}.copyTo: From {srcPos} to {tgtPos}")
            
            # Assign value from source to the target value
            self.getPointByPos(tgtPos).c = srcVal
            
            i += 1
        
        self.journal.O(f"{self.name}.copyTo: Copied {i} nodes")
        
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
    def normalise(self, dim):
        "Normalise ComplexPoint values of the <dim> dimension"
        
        self.journal.I(f"{self.name}.normalise: dim {dim}")
        
        sumSqr = 0
        
        #----------------------------------------------------------------------
        # Prepare list of all points in dimesion
        #----------------------------------------------------------------------
        self.cutDim(dim)
        
        #----------------------------------------------------------------------
        # Iterate over points and accumulate sum of abs's squares
        #----------------------------------------------------------------------
        i = 0
        for node in self:
            sumSqr += node['cP'].abs()
            i += 1

        #----------------------------------------------------------------------
        # Iterate over points and apply norm if possible
        #----------------------------------------------------------------------
        if sumSqr > 0:
            
            norm = 1/sumSqr    #/i
            norm =1
            
            for node in self: node['cP'].c *= norm
            
        else: norm = 1

        #----------------------------------------------------------------------
        self.journal.O(f"{self.name}.normalise: norm = {norm} for {i} points")

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
        srcs = []
        self.cutDim(dimLower)
        for node in self: srcs.append(node)
        
        #----------------------------------------------------------------------
        # Prepare cut for target points
        #----------------------------------------------------------------------
        self.iterCut.append(-1)

        #----------------------------------------------------------------------
        # Iterate over srcs points
        #----------------------------------------------------------------------
        toRet = []
        for src in srcs:
        
            srcP = src['cP']
        
            #------------------------------------------------------------------
            # Iterate over target points
            #------------------------------------------------------------------
            for tgt in self:
                
                tgtP = tgt['cP']
                
                # Get coordinates of source point and target point
                dlts = srcP.deltasTo(tgtP)
                dx1  = dlts[0]
                dx2  = tgtP.pos[1]
                
                # Compute distance in periods
                r = math.sqrt( (dx1*dx1) + (dx2*dx2) )
                            
                # Period's fraction defines amplitude phase
                phase = (r % 1) * 2 * math.pi
                
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
                        r = math.sqrt( (dx1*dx1) + (dx2*dx2) )
                            
                        # Period's fraction defines amplitude phase
                        phase = (r % 1) * 2 * math.pi
                
                        # Phase defines rotation of amplitude
                        rot = cmath.exp(rotDir * phase)
            
                        #--------------------------------------------------------------
                        # Superpose srcP * rot to tgtP or backward
                        #--------------------------------------------------------------
                        if forward: tgtP.c += srcP.c * rot
                        else      : srcP.c += tgtP.c * rot

                toRet.append({'src':src['cP'], 'tgt':tgt['cP'], 'dx1':dx1, 'dx2':dx2})
                
        #----------------------------------------------------------------------
        # Normalise
        #----------------------------------------------------------------------
        if forward: self.normalise(dimLower+1)
        else      : self.normalise(dimLower)

        #----------------------------------------------------------------------
        self.journal.O(f"{self.name}.getRays: creates {len(toRet)} rays")
        return toRet

    #--------------------------------------------------------------------------
    def evolve(self, cut, start=0, stop=0):
        "Evolve state in <cut> and historise it in nex dimension"
        
        srcDim = len(cut)
        tgtCnt = self.dimCount(srcDim+1)
        self.journal.I(f"{self.name}.evolve: cut={cut} {tgtCnt} times")
        
        #----------------------------------------------------------------------
        # Prepare list of source points
        #----------------------------------------------------------------------
        srcs = []
        self.iterCut = cut
        for node in self: srcs.append(node)
        
        #----------------------------------------------------------------------
        # Iterate evolving for dimNext.count times
        #----------------------------------------------------------------------
        for tgtPos in range(tgtCnt):
            
            #------------------------------------------------------------------
            # Historise actual state of dimLower to dimNext at coord j
            #------------------------------------------------------------------
            self.copyTo(cut, tgtPos)
            


        #----------------------------------------------------------------------
        self.journal.O(f"{self.name}.evolve: evolved ")

    #--------------------------------------------------------------------------
    def getLstCF(self, deep=0):
        "Returns list of all ComplexFields"
        
        self.journal.I(f"{self.name}.getLstCF: {deep}")
        
        toRet = []
        #----------------------------------------------------------------------
        # Add self
        #----------------------------------------------------------------------
        if deep==0: toRet.append(self)
        
        #----------------------------------------------------------------------
        # Add all underlying ComplexFields
        #----------------------------------------------------------------------
        for node in self.nodes:
            
            if node['cF'] is not None:
                
                toRet.append( node['cF']                  )
                toRet.extend( node['cF'].getLstCF(deep+1) )
        
        #----------------------------------------------------------------------
        self.journal.O()
        return toRet
        
    #==========================================================================
    # API
    #--------------------------------------------------------------------------
    def getData(self, cut=None):
        "Returns dict of numpy arrays as a cut from ComplexField"
    
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
print('ComplexField ver 2.03')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------