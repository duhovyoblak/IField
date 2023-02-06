#==============================================================================
# Siqo class ComplexPoint and CompplexField
#------------------------------------------------------------------------------
import sys
sys.path.append('..\siqo_lib')

import math
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
    def gener(journal, name, dim, count, offMin, offMax, spread=_LIN, pos=[], deep=0):
        "Creates ComplexField with respective settings"
        
        journal.I(f"ComplexField.gener: {name} dim={dim}, count={count}")

        #----------------------------------------------------------------------
        # Creating ComplexField object
        #----------------------------------------------------------------------
        toRet = ComplexField(journal, name)
        
        toRet.dim    = 1 + deep
        toRet.offset = offMin
        toRet.spread = spread
        
        if dim == (deep+1): toRet.leaf = True
        else              : toRet.leaf = False
        
        # Correction if this is root dimension e.g., deep=0
        if deep == 0:
            
            toRet.offset = 0
            toRet.spread = _LIN

        #----------------------------------------------------------------------
        # Creating offsets
        #----------------------------------------------------------------------
        offs = ComplexField.offsetLst(journal, count, toRet.offset, offMax, toRet.spread)

        #----------------------------------------------------------------------
        # Generate <count> objects in cF
        #----------------------------------------------------------------------
        for i, offset in offs.items():
            
            # Create copy of the <pos> list and add <offset> coordinate
            actPos = list(pos)
            actPos.append(offset)
            
            cP = ComplexPoint(actPos)
            
            #------------------------------------------------------------------
            # Ak to nie je listie stromu vytvorim aj subField
            #------------------------------------------------------------------
            if toRet.leaf: subField = None
            else         : subField = ComplexField.gener(journal, f"{name}_{i}", dim, count, offMin, offMax, actPos, spread, deep+1)
            
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
        self.dim     = 1          # Dimension of the field
        self.leaf    = True       # Flag if this is leaf object of the tree
        self.offset  = 0          # Offset distance in lambda from mother dimension
        self.spread  = _LIN       # Spread of offsets in underlying field
        self.count   = 0          # Count of underlyings fields
        
        self.cF      = []         # List of ComplexPoint/ComplexFields
        
        #----------------------------------------------------------------------
        # Private datove polozky triedy
        #----------------------------------------------------------------------
        self.itPos   = 0          # Iterator's position in self.cF list
        self.subIter = None       # Iterator over subField

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
        dat['offset'     ] = self.offset
        dat['spread'     ] = self.spread
        dat['count'      ] = self.count

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
        # Iterate over cF list until itPos < count
        #----------------------------------------------------------------------
        if self.itPos < self.count: 
            
            #------------------------------------------------------------------
            # If leaf the simply return ComplexPoint at itPos
            #------------------------------------------------------------------
            if self.leaf:

                obj = self.cF[self.itPos]
                self.itPos += 1

                return obj
            
            #------------------------------------------------------------------
            # If not leaf then iterate over underlying ComplexFields
            #------------------------------------------------------------------
            else:
                
                #--------------------------------------------------------------
                # If not yet initialised, initialise iterator over subField
                #--------------------------------------------------------------
                if self.subIter is None:
                    
                    subField     = self.cF[self.itPos]['cF']
                    self.subIter = iter(subField)

                #--------------------------------------------------------------
                # Return the next value from underlying ComplexFields
                #--------------------------------------------------------------
                try:
                     return next(self.subIter)
                    
                except StopIteration:
                    #----------------------------------------------------------
                    # Reset subPosition and move to the next object in cF list
                    #----------------------------------------------------------
                    self.subIter = None
                    self.itPos  += 1
                    
                    return next(self)
        
        #----------------------------------------------------------------------
        # There is no more object in Cf list left
        #----------------------------------------------------------------------
        else: raise StopIteration
            
    #--------------------------------------------------------------------------
    def dotToPos(self, dots):
        "Evaluates distance from dots"
        
        return dots/self.dpl * math.pi

    #--------------------------------------------------------------------------
    def copy(self, name):
        "Creates copy of this ComplexField"
        
        self.journal.I(f"{self.name}.copy: {name}")
        

        self.journal.O()
        
    #--------------------------------------------------------------------------
    def clear(self):
        "Clears content of cF of this field"
        
        self.journal.I(f"{self.name}.clear:")
        
        #----------------------------------------------------------------------
        # First recursive clearing to clear all underlying structures
        #----------------------------------------------------------------------
        if self.dim > 1:
            for subField in self.cF: subField.clear()

        #----------------------------------------------------------------------
        # Finally trivial clearing of this list
        #----------------------------------------------------------------------
        self.cF.clear()
        self.count   = 0
        
        self.journal.O()
        
    #--------------------------------------------------------------------------
    def reset(self, inset=None, offset=None, dpl=None, spread=None):
        "Clears complex field and reset it to dimension=0"
        
        self.journal.I(f"{self.name}.reset:")
        
        self.dim     = 1            # Dimension of the field
        self.spread  = _LIN         # Spread of offsets in underlying field
        self.clear()                # Clear of the context
        
        if inset  is not None: self.inset  = inset
        if offset is not None: self.offset = offset
        if dpl    is not None: self.dpl    = dpl
        if spread is not None: self.spread = spread

        self.journal.O()
        
    #==========================================================================
    # API
    #--------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------
    def extend(self, count, offMin=None, offMax=None, spread=_LIN):
        "Generate new ComplexField with one more dimension based on this ComplexField"
        
        self.journal.I(f"{self.name}.extend: By {count} complex fields")
        
        #----------------------------------------------------------------------
        # Iterate through all leaves objects of the tree
        #----------------------------------------------------------------------
        for obj in self:
            
            subField = ComplexField.gener(self.journal, f"{self.name}_ex", self.dim+1, count, offMin, offMax, spread, obj['cP'].pos, deep=self.dim)
            
            obj['cF'] = subField
            
        #----------------------------------------------------------------------
        # Final adjustments
        #----------------------------------------------------------------------
        self.leaf = False

        self.journal.O()

    #--------------------------------------------------------------------------
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