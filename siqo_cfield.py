#==============================================================================
# Siqo class ComplexPoint and CompplexField
#------------------------------------------------------------------------------
import sys
sys.path.append('..\siqo_lib')

import math
import numpy                 as np
import random                as rnd
import siqo_general          as gen

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_IND    = '|  '       # Info indentation
_DPL    = 10          # Default dots per lambda
_LIN    = 'linear'    # Default spread of offsets
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
        "Calls constructor of ComplexPoint"
        
        self.pos    = list(pos)      # Vector of real numbers for position in periods
        self.c      = complex()      # Complex value

    #--------------------------------------------------------------------------
    def posStr(self):
        "Creates string representation of position"

        toRet = '|'
        
        i = 0
        for coor in self.pos:
            toRet += "X[{}]={:10.2f} |".format(i+1, coor)
            i += 1

        return toRet
    
    #--------------------------------------------------------------------------
    def info(self, indent=0):
        "Creates info about this ComplexPoint"
        
        dat = {}
        msg = []

        dat['c'          ] = self.c
        dat['pos'        ] = self.pos

        msg.append(f"{indent*_IND}{self.posStr()} : {self.c}")

        return {'res':'OK', 'dat':dat, 'msg':msg}
        
    #--------------------------------------------------------------------------
    def __str__(self):
        "Prints info about this ComplexPoint"

        toRet = ''
        for line in self.info()['msg']: toRet += line
        return toRet

    #--------------------------------------------------------------------------
    def copy(self):
        "Creates copy of this ComplexPoint"

        toRet    = ComplexPoint(self.pos)
        toRet.c  = self.c
        
        return toRet
        
    #--------------------------------------------------------------------------
    def rndBit(self, prob):
        "Sets real value 0/1 with respective probability and imaginary value sets to 0"

        x = rnd.randint(0, 9999)
        
        if x <= prob*10000: self.c = complex(1, 0)
        else              : self.c = complex(0, 0)

        return self.c
        
#==============================================================================
# ComplexField
#------------------------------------------------------------------------------
class ComplexField:

    #==========================================================================
    # Static variables & methods
    #--------------------------------------------------------------------------
    @staticmethod
    def offsetLst(journal, count, offMin, offMax, spread):
        "Creates dict of offsets for respective setting"
        
        journal.I(f"ComplexField.offsetLst: {count} for <{offMin}, {offMax}> spreaded {spread}")

        #----------------------------------------------------------------------
        # Creating parameters
        #----------------------------------------------------------------------
        if spread==_LIN: 
            lb = offMin
            lk = (           offMax  - lb) / (count-1)
        
        elif spread==_LOG: 
            eb = math.log10(offMin)
            ek = (math.log10(offMax) - eb) / (count-1)
        
        #----------------------------------------------------------------------
        # Creating offsets using parameters
        #----------------------------------------------------------------------
        offs = {}
        for i in range(count):

            if   spread==_LIN: off =              (lb + lk * i)
            elif spread==_LOG: off = math.pow(10, (eb + ek * i) )
            
            offs[i] = off

        journal.O()
        return offs

    #--------------------------------------------------------------------------
    @staticmethod
    def gener(journal, name, count, offMin, offMax, dim, dimPrev=0, spread=_LIN, pos=[]):
        "Creates ComplexField with respective settings"
        
        journal.I(f"ComplexField.gener: {name} dim={dim}, count={count}")

        #----------------------------------------------------------------------
        # Creating ComplexField object
        #----------------------------------------------------------------------
        toRet = ComplexField(journal, name)
        
        toRet.dim    = dimPrev + 1
        toRet.offMin = offMin
        toRet.offMax = offMax
        toRet.spread = spread
        
        #----------------------------------------------------------------------
        # Correction if this is root dimension e.g., toRet.dim=1
        #----------------------------------------------------------------------
        if toRet.dim == 1:
            toRet.offset = 0
            toRet.spread = _LIN

        #----------------------------------------------------------------------
        # Set leaf if this is final dimension e.g., toRet.dim=dim
        #----------------------------------------------------------------------
        if toRet.dim == dim: toRet.leaf = True
        else               : toRet.leaf = False
        
        #----------------------------------------------------------------------
        # Creating offsets
        #----------------------------------------------------------------------
        offs = ComplexField.offsetLst(journal, count, toRet.offMin, toRet.offMax, toRet.spread)

        #----------------------------------------------------------------------
        # Generate <count> objects in cF
        #----------------------------------------------------------------------
        for i, offset in offs.items():
            
            #------------------------------------------------------------------
            # Create copy of the <pos> list and add <offset> coordinate
            #------------------------------------------------------------------
            actPos = list(pos)
            actPos.append(offset)
            
            cP = ComplexPoint(actPos)
            
            #------------------------------------------------------------------
            # Ak to nie je listie stromu vytvorim aj subField
            #------------------------------------------------------------------
            if toRet.leaf: subField = None
            else         : subField = ComplexField.gener(journal, f"{name}_{i}", count=count, 
                                      offMin=offMin, offMax=offMax, dim=dim, dimPrev=toRet.dim, spread=spread, pos=actPos)

            #------------------------------------------------------------------
            toRet.cF.append( {'cP':cP, 'cF':subField} )
            
        #----------------------------------------------------------------------
        # Final adjustments
        #----------------------------------------------------------------------
        toRet.count = len(toRet.cF)

        journal.O()
        return toRet
        
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
        self.leaf    = True       # Flag if this is leaf object of the tree
        self.offMin  = 0          # Min offset distance in lambda from mother dimension
        self.offMax  = 1          # Max offset distance in lambda from mother dimension
        self.count   = 0          # Count of objects in this field
        self.spread  = _LIN       # Spread of offsets of objects
        
        self.cF      = []         # List of ComplexPoint/ComplexFields
        
        #----------------------------------------------------------------------
        # Private datove polozky triedy
        #----------------------------------------------------------------------
        self.itPos   = 0          # Iterator's position in self.cF list
        self.subIter = None       # Iterator over subField
        self.cut     = [-1]       # Definition of cut applied in iterator

        self.journal.O(f"{self.name}.constructor: done")

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
        dat['spread'     ] = self.spread

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
        "Returns next item in ongoing iteration"
        
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
            
    #--------------------------------------------------------------------------
    def copy(self, name):
        "Creates copy of this ComplexField"
        
        self.journal.I(f"{self.name}.copy: {name}")
        

        self.journal.O()
        
    #--------------------------------------------------------------------------
    def getDimMax(self, deep=0):
        "Returns max dimension of whole space"
        
        if len(self.cF)==0 or self.cF[0]['cF'] is None: return deep+1
        else                                          : return self.cF[0]['cF'].getDimMax(deep+1)

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
        
    #--------------------------------------------------------------------------
    def clear(self):
        "Clears content of cF of this field"
        
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
    def reset(self, inset=None, offset=None, spread=None):
        "Clears complex field and reset it to dimension=0"
        
        self.journal.I(f"{self.name}.reset:")
        
        self.dim     = 1            # Dimension of the field
        self.spread  = _LIN         # Spread of offsets in underlying field
        self.clear()                # Clear of the context
        
        if inset  is not None: self.inset  = inset
        if offset is not None: self.offset = offset
        if spread is not None: self.spread = spread

        self.journal.O()
        
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
        data['re'] = []
        data['im'] = []
        
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
            data['re'].append(cP.c.real)
            data['im'].append(cP.c.imag)

        #----------------------------------------------------------------------
        # Create toRet np-array for populated data
        #----------------------------------------------------------------------
        toRet = []
        for key, arr in data.items():
            
            toRet.append( {'key':key, 'arr':np.array(arr)} )

        #----------------------------------------------------------------------
        self.journal.O()
        return toRet

    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------
    def extend(self, count, offMin=None, offMax=None, spread=_LIN):
        "Generate new ComplexField with one more dimension based on this ComplexField"
        
        self.journal.I(f"{self.name}.extend: {count} raster in <{offMin} - {offMax}> spread by {spread}")
        
        #----------------------------------------------------------------------
        # Prepare all leaves objects of the tree
        #----------------------------------------------------------------------
        leaves = []
        for obj in self:
            leaves.append(obj)
            
        origDim = len(leaves[0]['cP'].pos)

        #----------------------------------------------------------------------
        # Iterate through all leaves objects of the tree
        #----------------------------------------------------------------------
        for obj in leaves:
            
            name   = f"{self.name}_ex{origDim}"
            actPos = obj['cP'].pos
            
            subField = ComplexField.gener(self.journal, name, count, origDim+1, offMin, offMax, spread, origDim, actPos)
            obj['cF'] = subField
            
        #----------------------------------------------------------------------
        # Set leaf = False to all ComplexFields with dim=origDim
        #----------------------------------------------------------------------
        cfLst = self.getLstCF()
        
        for cf in cfLst:
            if cf.dim==origDim: cf.leaf = False

        self.journal.O()

    #--------------------------------------------------------------------------
    def rndBit(self, prob):
        "Sets all values to random bit with respective probability"
        
        for obj in self:
            obj['cP'].rndBit(prob)
        
    #--------------------------------------------------------------------------
    def amp(self):
        "Returns amplitude of the Object"

        if self.isBase(): return self.objVal
        else            : return self.objVal.amp()

    #--------------------------------------------------------------------------
    def prob(self):
        "Returns probability of the amplitude of the Object"

        if self.isBase(): return self.objVal * self.objVal.conjugate()
        else            : return self.objVal.prob()

    #--------------------------------------------------------------------------
    def toJson(self):
        "Converts Object into json structure"
        
        self.journal.I(f'{self.name}.toJson:')
        
        toRet = {}

        self.journal.O(f'{self.name}.toJson: Converted')
        return toRet

#------------------------------------------------------------------------------
print('ComplexField ver 0.01')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------