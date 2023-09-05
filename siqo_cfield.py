#==============================================================================
# Siqo class ComplexPoint and CompplexField
#------------------------------------------------------------------------------
import sys
sys.path.append('..\siqo_lib')

import math
import cmath
import numpy                 as np
import random                as rnd
#import siqo_general          as gen

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
# ComplexPoint
#------------------------------------------------------------------------------
class ComplexPoint:

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, pos=[]):
        "Calls constructor of ComplexPoint on respective position"
        
        self.pos = list(pos)   # Vector of real numbers for position coordinates
        self.c   = complex()   # Complex value

    #--------------------------------------------------------------------------
    def copy(self):
        "Creates copy of this ComplexPoint"

        toRet    = ComplexPoint(self.pos)
        toRet.c  = self.c
        
        return toRet
        
    #--------------------------------------------------------------------------
    def posStr(self):
        "Creates string representation of the position of this ComplexPoint"

        toRet = '|'
        
        i = 0
        for coor in self.pos:
            toRet += "X[{}]={:7.2f} |".format(i+1, coor)
            i += 1

        return toRet
    
    #--------------------------------------------------------------------------
    def info(self, indent=0):
        "Creates info about this ComplexPoint"
        
        dat = {}
        msg = []

        dat['c'  ] = self.c
        dat['pos'] = self.pos

        msg.append(f"{indent*_IND}{self.posStr()} : {self.c}")

        return {'res':'OK', 'dat':dat, 'msg':msg}
        
    #--------------------------------------------------------------------------
    def __str__(self):
        "Prints info about this ComplexPoint"

        toRet = ''
        for line in self.info()['msg']: toRet += line
        return toRet

    #==========================================================================
    # Value modification
    #--------------------------------------------------------------------------
    def clear(self):
        "Sets complex number to (0+0j)"
        
        self.c = complex(0,0)
        
    #--------------------------------------------------------------------------
    def setComp(self, c):
        "Sets complex number to respective complex value"
        
        self.c = c
        
    #--------------------------------------------------------------------------
    def setRect(self, re, im):
        "Sets complex number given by rectangular coordinates (real, imag)"
        
        self.c = complex(re, im)
        
    #--------------------------------------------------------------------------
    def setPolar(self, mod, phi):
        "Sets complex number given by polar coordinates (modulus, phase)"
        
        self.c = cmath.rect(mod, phi)
        
    #--------------------------------------------------------------------------
    def rndBit(self, prob):
        "Sets real value 0/1 with respective probability and imaginary value sets to 0"

        x = rnd.randint(0, 9999)
        
        if x <= prob*10000: self.c = complex(1, 0)
        else              : self.c = complex(0, 0)

        return self.c
        
    #--------------------------------------------------------------------------
    def rndPhase(self, r=1):
        "Sets random phase <0, 2PI> and radius r. If r==0 then r will be preserved"
        
        if r==0: r = self.c.abs()

        phi    = 2*cmath.pi*rnd.random()
        self.c = cmath.rect(r, phi)

        return self.c

    #==========================================================================
    # Complex Value information
    #--------------------------------------------------------------------------
    def real(self):
        "Returns real part of complex number"
        
        return self.c.real

    #--------------------------------------------------------------------------
    def imag(self):
        "Returns imaginary part of complex number"
        
        return self.c.imag

    #--------------------------------------------------------------------------
    def polar(self):
        "Returns polar coordinates of complex number as a tuple. Phase in <-pi, pi> from +x axis"
        
        return cmath.polar(self.c)

    #--------------------------------------------------------------------------
    def abs(self):
        "Returns absolute value = modulus of complex number"
        
        return abs(self.c)

    #--------------------------------------------------------------------------
    def phase(self):
        "Returns phase in <-pi, pi> from +x axis"
        
        return cmath.phase(self.c)

    #--------------------------------------------------------------------------
    def conjugate(self):
        "Returns conjugate complex number"
        
        return self.c.conjugate()

    #--------------------------------------------------------------------------
    def sqrComp(self):
        "Returns square of complex number"
        
        return self.c * self.c

    #--------------------------------------------------------------------------
    def sqrAbs(self):
        "Returns square of the absolute value of complex value"
        
        return (self.c.real * self.c.real) + (self.c.imag * self.c.imag )

    #==========================================================================
    # Position information
    #--------------------------------------------------------------------------
    def deltasTo(self, toP):
        "Returns list of differences between coordinates for respective ComplexPoint"
        
        dlt = zip(self.pos, toP.pos)
        
        toRet = [pair[1] - pair[0] for pair in dlt]
        
        return toRet

    #--------------------------------------------------------------------------
    def distSqrTo(self, toP):
        "Returns square of the distance to respective ComplexPoint"
        
        dlts  = self.deltasTo(toP)
        toRet = 0
        
        for r in dlts: toRet += r*r
        
        return toRet

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
        
        journal.I(f"ComplexField.genOffset: {count} for <{offMin}, {offMax}> offType {offType}")

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
        self.name    = name       # Name of this complex field
        self.dim     = 1          # Dimension level of this field (Not dimension of the Space)
        self.leaf    = True       # Flag if this is leaf node of the InformationStructure
        self.offMin  = 0          # Min offset distance in lambda from mother dimension
        self.offMax  = 1          # Max offset distance in lambda from mother dimension
        self.offType = _LIN       # offType of offsets of nodes
        self.count   = 0          # Count of nodes in this ComplexField
        
        self.nodes   = []         # List of nodes {ComplexPoint, ComplexFields}
        
        #----------------------------------------------------------------------
        # Private datove polozky triedy
        #----------------------------------------------------------------------
        self.nodePos = 0          # Iterator's position in self.nodes list
        self.subIter = None       # Iterator over subField
        self.cut     = [-1]       # Definition of cut applied in iterator e.g., desired positions in cF list
                                  # If we want all nodes in cF list then cut for this dimensions is equal -1

        self.journal.O(f"{self.name}.constructor: done")

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

        msg.append(f"{indent*_IND}{90*'='}")
        dat['name'       ] = self.name
        dat['dim'        ] = self.dim
        dat['leaf'       ] = self.leaf
        dat['offMin'     ] = self.offMin
        dat['offMax'     ] = self.offMax
        dat['offType'    ] = self.offType
        dat['count'      ] = self.count

        for key, val in dat.items(): msg.append("{}{:<15}: {}".format(indent*_IND, key, val))

        #----------------------------------------------------------------------
        # info
        #----------------------------------------------------------------------
        for node in self.nodes:
        
            if self.leaf: subMsg = node['cP'].info(indent+1)['msg']
            else        : subMsg = node['cF'].info(indent+1)['msg']
            msg.extend(subMsg)
        
        #----------------------------------------------------------------------
        return {'res':'OK', 'dat':dat, 'msg':msg}
        
    #--------------------------------------------------------------------------
    def __str__(self):
        "Prints info about this ComplexField"

        toRet = ''
        for line in self.info()['msg']: toRet += line +'\n'
        return toRet

    #--------------------------------------------------------------------------
    def __iter__(self):
        "Creates iterator for this ComplexField"
        
        # Reset iterator's position
        self.nodePos = 0
        self.subIter = None
        
        return self

    #--------------------------------------------------------------------------
    def __next__(self):
        "Returns next node in ongoing iteration for applied filters"
        
        #----------------------------------------------------------------------
        # If cut for this dimension is defined then return respective cut only
        #----------------------------------------------------------------------
        if self.cut[0] != -1:

            # Get desired cut e.g., node in list of nodes
            node = self.nodes[self.cut[0]]
            
            #------------------------------------------------------------------
            # If there is cut definition left, start underlying iterator
            #------------------------------------------------------------------
            if len(self.cut)>1:
                
                #--------------------------------------------------------------
                # If not yet initialised, initialise iterator over subField with sub-cut
                #--------------------------------------------------------------
                if self.subIter is None:
                    
                    subField     = node['cF']
                    subField.cut = self.cut[1:]     # Odovzdanie definicie cut-u do sub-Fieldu
                    self.subIter = iter(subField)   # Inicializacia sub-iteracie

                #--------------------------------------------------------------
                # Return the next value from underlying ComplexFields until exception
                #--------------------------------------------------------------
                return next(self.subIter)
            
            #------------------------------------------------------------------
            # If there is no cut definition left, return current node
            #------------------------------------------------------------------
            else:
                #--------------------------------------------------------------
                # Check if this was already returned
                #--------------------------------------------------------------
                if self.nodePos == -1: raise StopIteration
                else:
                    self.nodePos = -1
                    return node
        
        #----------------------------------------------------------------------
        # If cut is not defined then Iterate over list of nodes until itPos < count
        #----------------------------------------------------------------------
        else:
            
            if self.nodePos < self.count: 
                
                # Get current node in list of nodes
                node = self.nodes[self.nodePos]
                
                #--------------------------------------------------------------
                # If there is cut definition left, start underlying iterator
                #--------------------------------------------------------------
                if len(self.cut)>1:
                    
                    #----------------------------------------------------------
                    # If not yet initialised, initialise iterator over subField with sub-cut
                    #----------------------------------------------------------
                    if self.subIter is None:
                    
                        subField     = node['cF']
                        subField.cut = self.cut[1:]     # Odovzdanie definicie cut-u do sub-Fieldu
                        self.subIter = iter(subField)   # Inicializacia sub-iteracie

                    #----------------------------------------------------------
                    # Return the next value from underlying ComplexFields
                    #----------------------------------------------------------
                    try:
                        return next(self.subIter)

                    except StopIteration:
                        #------------------------------------------------------
                        # Reset subIterator and move to the next node in list of nodes
                        #------------------------------------------------------
                        self.subIter  = None
                        self.nodePos += 1
                        return next(self)
                  
                #--------------------------------------------------------------
                # If there is no cut definition left, return Point and move to next point
                #--------------------------------------------------------------
                else: 
                    self.nodePos += 1
                    return node
                    
            #------------------------------------------------------------------
            # There is no more node in list of nodes left
            #------------------------------------------------------------------
            else: raise StopIteration
            
    #==========================================================================
    # Named cuts settings
    #--------------------------------------------------------------------------
    def cutAll(self):
        "Returns cut's definition for all points"
        
        cut = [-1 for i in range(self.getDimMax())]
 
        self.journal.M(f"{self.name}.cutAll: Cut is {cut}")
        return cut
        
    #--------------------------------------------------------------------------
    def cutDimension(self, dim):
        "Returns cut's definition for all points in respective dimension"
        
        cut = [-1 for i in range(dim)]

        self.journal.M(f"{self.name}.cutDimension: For dim={dim} is {cut}")
        return cut
        
    #--------------------------------------------------------------------------
    def cutLeaves(self):
        "Returns cut's definition for all leave's points"
        
        cut = [-1 for i in range(self.getDimMax())]
 
        self.journal.M(f"{self.name}.cutLeaves: Cut is {cut}")
        return cut
        
    #--------------------------------------------------------------------------
    def cutSources(self, dim):
        "Returns cut's definition for all sources points in demension"
    
        cut = [0 for i in range(dim)]
        cut[-1] = -1
        
        self.journal.M(f"{self.name}.cutSources: For dim={dim} is {cut}")
        return cut

    #==========================================================================
    # Structure modification
    #--------------------------------------------------------------------------
    def reset(self):
        "Clears ComplexField and reset it to dimension=1"
        
        self.journal.I(f"{self.name}.reset:")
        
        self.nodes.clear()        # Odstranenie vsetkych poli
        self.count   = 0          # Nastavenie poctu nodov
        self.leaf    = True       # Flag if this is leaf node of the InformationStructure

        self.dim     = 1          # Reset dimension of the field
        self.offType = _LIN       # offType of offsets in underlying field
        self.cut     = [-1]       # Definition of cut applied in iterator
        
        self.journal.O()
        
    #--------------------------------------------------------------------------
    def gener(self, count, offMin, offMax, offType=_LIN, dimPrev=0, posPrev=[]):
        "Creates ComplexField with respective settings"
        
        self.journal.I(f"{self.name}.gener: dim={dimPrev+1}, count={count}")

        self.nodes.clear()

        #----------------------------------------------------------------------
        # ComplexField settings
        #----------------------------------------------------------------------
        self.dim     = dimPrev + 1
        self.offMin  = offMin
        self.offMax  = offMax
        self.offType = offType
        
        #----------------------------------------------------------------------
        # Correction if this is root dimension e.g., toRet.dim=1
        #----------------------------------------------------------------------
        if self.dim == 1: self.offset  = 0

        #----------------------------------------------------------------------
        # Set leaf flag to True
        #----------------------------------------------------------------------
        self.leaf = True
        
        #----------------------------------------------------------------------
        # Creating offsets
        #----------------------------------------------------------------------
        offs = ComplexField.genOffset(self.journal, count, self.offMin, self.offMax, self.offType)

        #----------------------------------------------------------------------
        # Generate <count> nodes in cF at position actPos = [posPrev, offset]
        #----------------------------------------------------------------------
        for i, offset in offs.items():
            
            #------------------------------------------------------------------
            # Create copy of the <pos> list and add <offset> coordinate
            #------------------------------------------------------------------
            actPos = list(posPrev)
            actPos.append(offset)
            
            cP = ComplexPoint(actPos)
            
            #------------------------------------------------------------------
            # Pridam do ComplexFiled { complexPoint, None subfield }
            #------------------------------------------------------------------
            self.nodes.append( {'cP':cP, 'cF':None} )
            
        #----------------------------------------------------------------------
        # Final adjustments
        #----------------------------------------------------------------------
        self.count = len(self.nodes)

        self.journal.O()
        
    #--------------------------------------------------------------------------
    def extend(self, count, offMin=None, offMax=None, offType=_LIN):
        "Assigns to each ComplexPoint of this ComplexField new ComplexField subfield"
        
        self.journal.I(f"{self.name}.extend: {count} in offset <{offMin} - {offMax}> by {offType}")
        
        #----------------------------------------------------------------------
        # Prepare all leaves nodes of the tree
        #----------------------------------------------------------------------
        self.cut = self.cutLeaves()

        #----------------------------------------------------------------------
        # Iterate through all leaves nodes of the tree
        #----------------------------------------------------------------------
        i = 0
        for node in self:
            
            actPos = node['cP'].pos

            subField = ComplexField(self.journal, f"{self.name}_ext{i}")
            subField.gener(count=count, offMin=offMin, offMax=offMax, offType=offType, dimPrev=self.dim, posPrev=actPos)

            # Assign subfield to respective ComplexPoint
            node['cF'] = subField
            
        #----------------------------------------------------------------------
        # Set leaf = False to all ComplexFields with cf.dim=dimPrev
        #----------------------------------------------------------------------
        cfLst = self.getLstCF()
        
        for cf in cfLst:
            if cf.dim == self.dim: cf.leaf = False

        #----------------------------------------------------------------------
        self.journal.O()

    #==========================================================================
    # ComplexPoint value modification
    #--------------------------------------------------------------------------
    def getPointByCoord(self, coord, deep=0):
        "Returns nearest Point in field for respective coordinates"

        pos  = -1            # Indices of the nearest point
        srch = coord[deep]   # Coordinate of the searched point in respective dimension
        
        self.journal.I(f"{self.name}.getPointByCoord: coord={coord}, srch={srch}, deep={deep}")

        #----------------------------------------------------------------------
        # Initialise distance to previous point (e.g., first)
        #----------------------------------------------------------------------
        i = 0
        dltPrev = self.nodes[i]['cP'].pos[deep] - srch
        i += 1

        #----------------------------------------------------------------------
        # Iterate over all next points
        #----------------------------------------------------------------------
        while i < self.count:
            
            # Distance to actual (i-th) point
            dltAct = self.nodes[i]['cP'].pos[deep] - srch

            #------------------------------------------------------------------
            #  If the actual point has greater coord than <srch>
            #------------------------------------------------------------------
            if dltAct >= 0:
                
                #--------------------------------------------------------------
                # Return nearer point: Previous or Actual
                #--------------------------------------------------------------
                if abs(dltAct) <= abs(dltPrev): pos = i
                else                          : pos = i-1
                
                break

            #------------------------------------------------------------------
            # Move to the next point
            #------------------------------------------------------------------
            dltPrev = dltAct
            i += 1

        #----------------------------------------------------------------------
        # If pos was not set then set it to last point
        #----------------------------------------------------------------------
        if pos == -1: pos = i-1
        
        #----------------------------------------------------------------------
        # Prepare return value
        #----------------------------------------------------------------------
        lstPos = [pos]
        
        #----------------------------------------------------------------------
        # If there are not-yet-resolved coordinates left then recursive
        #----------------------------------------------------------------------
        if len(coord) > (deep+1):
            
            # field to be searched 
            sF = self.nodes[pos]['cF']
            
            lstPos.extend( sF.getPointByCoord(coord, deep+1) )
                    
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
    def getDimMax(self, deep=0):
        "Returns max dimension of whole space"
        
        if len(self.nodes)==0 or self.nodes[0]['cF'] is None: return deep+1
        else                                                : return self.nodes[0]['cF'].getDimMax(deep+1)

    #--------------------------------------------------------------------------
    def XgetDimSettings(self, dim):
        "Returns ComplexField settings for respective dimension"

        if dim < 0: return None
        
        if dim < 1: return self
        else      : return self.nodes[0]['cF'].getDimSettings(dim-1)

    #--------------------------------------------------------------------------
    def getDimCount(self, dim):
        "Returns count of members for respective dimension"

        if dim < 1: return None
        
        # Dimension of this cF is desired dimension
        if self.dim == dim: 
            
            return self.count
        
        else: 
            if self.nodes[0]['cF'] is not None: return self.nodes[0]['cF'].getDimCount(dim)
            else                              : return None
        
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
        "Clear all values"
        
        self.cut = self.cutAll()
        for node in self: node['cP'].clear()

        self.journal.M(f"{self.name}.clear:")
        
    #--------------------------------------------------------------------------
    def rndBit(self, prob):
        "Sets all values to random bit with respective probability"

        self.cut = self.cutAll()
        for node in self: node['cP'].rndBit(prob)

        self.journal.M(f"{self.name}.rndBit: prob={prob}")
        
    #--------------------------------------------------------------------------
    def rndPhase(self, r=1):
        "Sets all values to random phase with respective radius"

        self.cut = self.cutAll()
        for node in self: node['cP'].rndPhase(r)

        self.journal.M(f"{self.name}.rndPhase: r={r}")
        
    #--------------------------------------------------------------------------
    def normalise(self, dim):
        "Normalise values of the <dim> dimension"
        
        self.journal.I(f"{self.name}.normalise: dim {dim}")
        
        sumSqr = 0
        
        #----------------------------------------------------------------------
        # Prepare list of all points in dimesion
        #----------------------------------------------------------------------
        self.cut = self.cutDimension(dim)
        
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
        dltOff = (self.offMax-self.offMin) * (self.count+1)/self.count
        
        #----------------------------------------------------------------------
        # Prepare list of source points
        #----------------------------------------------------------------------
        srcs = []
        self.cut = self.cutSources(dimLower)
        for node in self: srcs.append(node)
        
        #----------------------------------------------------------------------
        # Prepare cut for target points
        #----------------------------------------------------------------------
        self.cut.append(-1)

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
        if cut is not None: self.cut = cut
        
        #----------------------------------------------------------------------
        # Prepare output for respective cut
        #----------------------------------------------------------------------
        dimMax = self.getDimMax()
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
print('ComplexField ver 2.02')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------