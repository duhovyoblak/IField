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
        
        self.pos    = list(pos)      # Vector of real numbers for position
        self.c      = complex()      # Complex value

    #--------------------------------------------------------------------------
    def posStr(self):
        "Creates string representation of position"

        toRet = '|'
        
        i = 0
        for coor in self.pos:
            toRet += "X[{}]={:10.2f} |".format(i, coor)
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
        for line in self.info()['msg']: toRet += line +'\n'
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
    #--------------------------------------------------------------------------
    @staticmethod
    def gener(journal, name, dim, count, offMin, offMax, pos=[], spread=_LIN):
        "Creates ComplexField with respective settings"
        
        journal.I(f"ComplexField.gener: {name} dim={dim}, count={count}")

        #----------------------------------------------------------------------
        # Creating ComplexField object
        #----------------------------------------------------------------------
        toRet = ComplexField(journal, name)
        
        toRet.dim    = dim
        toRet.offset = offMin
        toRet.spread = spread
        
        if toRet.dim==1: toRet.spread = _LIN

        #----------------------------------------------------------------------
        # Creating offsets
        #----------------------------------------------------------------------
        if   toRet.spread==_LIN: 
            lb = offMin
            lk = (           offMax  - lb) / (count-1)
        
        elif toRet.spread==_LOG: 
            eb = math.log10(offMin)
            ek = (math.log10(offMax) - eb) / (count-1)
        
        offs = {}
        for i in range(count):

            if   toRet.spread==_LIN: off =              (lb + lk * i)
            elif toRet.spread==_LOG: off = math.pow(10, (eb + ek * i) )
            
            offs[i] = off

        #----------------------------------------------------------------------
        # Generate <count> objects in cF
        #----------------------------------------------------------------------
        for i, offset in offs.items():
            
            # Create copy of the <pos> list and add <offset> coordinate
            actPos = list(pos)
            actPos.append(offset)
            
            if toRet.dim==1:
            
                cP = ComplexPoint(actPos)
                toRet.cF.append(cP)

            else:
                subField = ComplexField.gener(journal, f"{name}_{i}", dim-1, count, offMin, offMax, actPos, spread)
                toRet.cF.append(subField)
            
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
        self.dim     = 0          # Dimension of the field
        self.inset   = 0          # Inset distance in lambda
        self.offset  = 0          # Offset distance in lambda
        self.dpl     = _DPL       # Dots per lambda
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
        dat['inset'      ] = self.inset
        dat['offset'     ] = self.offset
        dat['dpl'        ] = self.dpl
        dat['spread'     ] = self.spread
        dat['count'      ] = self.count

        for key, val in dat.items(): msg.append("{}{:<15}: {}".format(indent*_IND, key, val))

        #----------------------------------------------------------------------
        # info
        #----------------------------------------------------------------------
        for obj in self.cF:
            
           subMsg = obj.info(indent+1)['msg']
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
            # Evaluate distance from origin point
            #------------------------------------------------------------------
            offsetPos = self.offset

            #------------------------------------------------------------------
            # If dim==1 the simply return ComplexPoint at itPos
            #------------------------------------------------------------------
            if self.dim == 1:

                cPoint = self.cF[self.itPos]
                self.itPos += 1

                return cPoint
            
            #------------------------------------------------------------------
            # If dim>1 then iterate over underlying ComplexFields
            #------------------------------------------------------------------
            else:
                
                #--------------------------------------------------------------
                # If not yet initialised, initialise iterator over subField
                #--------------------------------------------------------------
                if self.subIter is None:
                    
                    subField     = self.cF[self.itPos]
                    self.subIter = iter(subField)

                #--------------------------------------------------------------
                # Return the next value from underlying ComplexFields
                #--------------------------------------------------------------
                try:
                    cPoint = next(self.subIter)
                    return cPoint
                    
                except StopIteration:
                    #----------------------------------------------------------
                    # Reset subPosition and move to the next object in cF list
                    #----------------------------------------------------------
                    self.subIter = None
                    self.itPos += 1
        
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
    def extend(self, count, inset=None, offset=None, spread=None):
        "Generate new ComplexField with one more dimension based on this ComplexField"
        
        self.journal.I(f"{self.name}.extend: By {count} complex fields")
        
        toRet = self.copy()




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