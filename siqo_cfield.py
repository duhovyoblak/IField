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
        
        return self.c * self.c.conjugate()

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
        self.leaf    = True       # Flag if this is leaf object of the InformationStructure
        self.offMin  = 0          # Min offset distance in lambda from mother dimension
        self.offMax  = 1          # Max offset distance in lambda from mother dimension
        self.offType = _LIN       # offType of offsets of objects
        self.count   = 0          # Count of objects in this ComplexField
        
        self.cF      = []         # List of ComplexPoint/ComplexFields
        
        #----------------------------------------------------------------------
        # Private datove polozky triedy
        #----------------------------------------------------------------------
        self.itPos   = 0          # Iterator's position in self.cF list
        self.subIter = None       # Iterator over subField
        self.cut     = [-1]       # Definition of cut applied in iterator

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
        dat['count'      ] = self.count
        dat['offType'    ] = self.offType

        for key, val in dat.items(): msg.append("{}{:<15}: {}".format(indent*_IND, key, val))

        #----------------------------------------------------------------------
        # info
        #----------------------------------------------------------------------
        for obj in self.cF:
        
            if self.leaf: subMsg = obj['cP'].info(indent+1)['msg']
            else        : subMsg = obj['cF'].info(indent+1)['msg']
            msg.extend(subMsg)
        
        #----------------------------------------------------------------------
        return {'res':'OK', 'dat':dat, 'msg':msg}
        
    #--------------------------------------------------------------------------
    def __str__(self):
        "Prints info about this object"

        toRet = ''
        for line in self.info()['msg']: toRet += line +'\n'
        return toRet

    #--------------------------------------------------------------------------
    def __iter__(self):
        "Creates iterator for this object"
        
        # Reset iterator's position
        self.itPos   = 0
        self.subIter = None
        
        return self

    #--------------------------------------------------------------------------
    def __next__(self):
        "Returns next item in ongoing iteration for applied filters"
        
        #----------------------------------------------------------------------
        # If cut is defined (!=-1) then return respective cut only
        #----------------------------------------------------------------------
        if self.cut[0] != -1:

            # Get desired cut e.g., object in cF list
            obj = self.cF[self.cut[0]]
            
            #------------------------------------------------------------------
            # If there is cut definition left, start underlying iterator
            #------------------------------------------------------------------
            if len(self.cut)>1:
                
                #--------------------------------------------------------------
                # If not yet initialised, initialise iterator over subField with sub-cut
                #--------------------------------------------------------------
                if self.subIter is None:
                    
                    subField     = obj['cF']
                    subField.cut = self.cut[1:]
                    self.subIter = iter(subField)

                #--------------------------------------------------------------
                # Return the next value from underlying ComplexFields until exception
                #--------------------------------------------------------------
                return next(self.subIter)
            
            #------------------------------------------------------------------
            # If there is no cut definition left, return current object
            #------------------------------------------------------------------
            else:
                #--------------------------------------------------------------
                # Check if this was already returned
                #--------------------------------------------------------------
                if self.itPos == -1: raise StopIteration
                else:
                    self.itPos = -1
                    return obj
        
        #----------------------------------------------------------------------
        # If cut is not defined then Iterate over cF list until itPos < count
        #----------------------------------------------------------------------
        else:
            
            if self.itPos < self.count: 
                
                # Get current object in cF list
                obj = self.cF[self.itPos]
                
                #--------------------------------------------------------------
                # If there is cut definition left, start underlying iterator
                #--------------------------------------------------------------
                if len(self.cut)>1:
                    
                    #----------------------------------------------------------
                    # If not yet initialised, initialise iterator over subField with sub-cut
                    #----------------------------------------------------------
                    if self.subIter is None:
                    
                        subField     = obj['cF']
                        subField.cut = self.cut[1:]
                        self.subIter = iter(subField)

                    #----------------------------------------------------------
                    # Return the next value from underlying ComplexFields
                    #----------------------------------------------------------
                    try:
                        return next(self.subIter)

                    except StopIteration:
                        #------------------------------------------------------
                        # Reset subIterator and move to the next object in cF list
                        #------------------------------------------------------
                        self.subIter = None
                        self.itPos  += 1
                        return next(self)
                  
                #--------------------------------------------------------------
                # If there is no cut definition left, return Point and move to next point
                #--------------------------------------------------------------
                else: 
                    self.itPos += 1
                    return obj
                    
            #------------------------------------------------------------------
            # There is no more object in Cf list left
            #------------------------------------------------------------------
            else: raise StopIteration
            
    #==========================================================================
    # Structure modification
    #--------------------------------------------------------------------------
    def clear(self):
        "Recursively clear content of cF of this ComplexField"
        
        self.journal.I(f"{self.name}.clear:")
        
        #----------------------------------------------------------------------
        # First recursive clearing to clear all underlying structures
        #----------------------------------------------------------------------
        if not self.leaf:
            for obj in self.cF: obj['cF'].clear()

        #----------------------------------------------------------------------
        # Finally trivial clearing of this list
        #----------------------------------------------------------------------
        self.cF.clear()
        self.count   = 0
        
        self.journal.O()
        
    #--------------------------------------------------------------------------
    def reset(self, inset=None, offset=None, offType=None):
        "Clears ComplexField and reset it to dimension=1"
        
        self.journal.I(f"{self.name}.reset:")
        
        self.clear()           # Clear of the context
        self.dim     = 1       # Reset dimension of the field
        self.offType = _LIN    # offType of offsets in underlying field
        
        if inset   is not None: self.inset   = inset
        if offset  is not None: self.offset  = offset
        if offType is not None: self.offType = offType

        self.journal.O()
        
    #--------------------------------------------------------------------------
    def gener(self, count, offMin, offMax, offType=_LIN, dimPrev=0, posPrev=[]):
        "Creates ComplexField with respective settings"
        
        self.journal.I(f"{self.name}.gener: dim={dimPrev+1}, count={count}")

        self.cF.clear()

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
        # Generate <count> objects in cF at position actPos = [posPrev, offset]
        #----------------------------------------------------------------------
        for i, offset in offs.items():
            
            #------------------------------------------------------------------
            # Create copy of the <pos> list and add <offset> coordinate
            #------------------------------------------------------------------
            actPos = list(posPrev)
            actPos.append(offset)
            
            cP = ComplexPoint(actPos)
            
            #------------------------------------------------------------------
            # Pridam do ComplexFiled { complexPoint, subfield }
            #------------------------------------------------------------------
            self.cF.append( {'cP':cP, 'cF':None} )
            
        #----------------------------------------------------------------------
        # Final adjustments
        #----------------------------------------------------------------------
        self.count = len(self.cF)

        self.journal.O()
        
    #--------------------------------------------------------------------------
    def extend(self, count, offMin=None, offMax=None, offType=_LIN):
        "Assigns to each ComplexPoint of this ComplexField new ComplexField subfield"
        
        self.journal.I(f"{self.name}.extend: {count} in offset <{offMin} - {offMax}> by {offType}")
        
        #----------------------------------------------------------------------
        # Prepare all leaves objects of the tree
        #----------------------------------------------------------------------
        self.cut = [-1 for i in range(self.getDimMax())]

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
        dltPrev = self.cF[i]['cP'].pos[deep] - srch
        i += 1

        #----------------------------------------------------------------------
        # Iterate over all next points
        #----------------------------------------------------------------------
        while i < self.count:
            
            # Distance to actual (i-th) point
            dltAct = self.cF[i]['cP'].pos[deep] - srch

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
            sF = self.cF[pos]['cF']
            
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
        
        if len(self.cF)==0 or self.cF[0]['cF'] is None: return deep+1
        else                                          : return self.cF[0]['cF'].getDimMax(deep+1)

    #--------------------------------------------------------------------------
    def XgetDimSettings(self, dim):
        "Returns ComplexField settings for respective dimension"

        if dim < 0: return None
        
        if dim < 1: return self
        else      : return self.cF[0]['cF'].getDimSettings(dim-1)

    #--------------------------------------------------------------------------
    def getDimCount(self, dim):
        "Returns count of members for respective dimension"

        if dim < 1: return None
        
        # Dimension of this cF is desired dimension
        if self.dim == dim: 
            
            return self.count
        
        else: 
            if self.cF[0]['cF'] is not None: return self.cF[0]['cF'].getDimCount(dim)
            else                           : return None
        
    #--------------------------------------------------------------------------
    def Xamp(self):
        "Returns amplitude of the Object"

        if self.isBase(): return self.objVal
        else            : return self.objVal.amp()

    #--------------------------------------------------------------------------
    def Xprob(self):
        "Returns probability of the amplitude of the Object"

        if self.isBase(): return self.objVal * self.objVal.conjugate()
        else            : return self.objVal.prob()

    #==========================================================================
    # Methods application
    #--------------------------------------------------------------------------
    def rndBit(self, prob):
        "Sets all values to random bit with respective probability"
        
        for obj in self:
            obj['cP'].rndBit(prob)
        
    #--------------------------------------------------------------------------
    def normalise(self, dim):
        "Normalise values of the <dim> dimension"
        
        self.journal.I(f"{self.name}.normalise: dim {dim}")
        
        sumSqr = 0
        
        #----------------------------------------------------------------------
        # Prepare list of all points in dimesion
        #----------------------------------------------------------------------
        cut = [-1 for i in range(dim)]
        self.cut = cut
        
        #----------------------------------------------------------------------
        # Iterate over points and accumulate sum of abs's squares
        #----------------------------------------------------------------------
        for obj in self:
            sumSqr += obj['cP'].sqrAbs()

        #----------------------------------------------------------------------
        # Iterate over points and apply norm
        #----------------------------------------------------------------------
        for obj in self:
            obj['cP'].c /= sumSqr

        self.journal.O(f"{self.name}.normalise: sumSqr = {sumSqr}")

    #--------------------------------------------------------------------------
    def applyRays(self, dimStart, start=0, stop=0, forward=True, torus=False):
        "Apply rays from <dimStart> to next dimension"
        
        self.journal.I(f"{self.name}.getRays: from dim {dimStart} with torus={torus}")
        
        if forward: rotDir = -1j
        else      : rotDir =  1j
        
        dltOff = (self.offMax-self.offMin) * (self.count+1)/self.count
        
        #----------------------------------------------------------------------
        # Prepare list of source points
        #----------------------------------------------------------------------
        cut = [0 for i in range(dimStart)]
        cut[-1] = -1
        self.cut = cut

        srcs = []
        for obj in self: srcs.append(obj)
        
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
        self.normalise(dimStart+1)

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
        for obj in self.cF:
            
            if obj['cF'] is not None:
                
                toRet.append( obj['cF']                  )
                toRet.extend( obj['cF'].getLstCF(deep+1) )
        
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
        for obj in self:
            
            cP = obj['cP']
            
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
        "Converts Object into json structure"
        
        self.journal.I(f'{self.name}.toJson:')
        
        toRet = {}

        self.journal.O(f'{self.name}.toJson: Converted')
        return toRet

#------------------------------------------------------------------------------
print('ComplexField ver 2.01')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------