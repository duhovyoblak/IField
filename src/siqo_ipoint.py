#==============================================================================
# Siqo class InfoPoint
#------------------------------------------------------------------------------
import math
import cmath
import random                 as rnd
#import siqo_general          as gen

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_IND      = '|  '                      # Info indentation
_F_TOTAL  = 5                          # Total number of digits in float number
_F_DECIM  = 3                          # Number of digits after decimal point in float number
_F_FORMAT = f"{_F_TOTAL}.{_F_DECIM}f"  # Format for float number

#==============================================================================
# package's variables
#------------------------------------------------------------------------------

#==============================================================================
# InfoPoint
#------------------------------------------------------------------------------
class InfoPoint:

    #==========================================================================
    # Static variables & methods
    #--------------------------------------------------------------------------
    _journal = None                # Journal for logging

    #--------------------------------------------------------------------------
    @staticmethod
    def setJournal(journal):
        "Sets journal for logging"
        
        InfoPoint._journal = journal

    #--------------------------------------------------------------------------
    @staticmethod
    def journal(msg, force=False):
        ""
        if InfoPoint._journal is not None:
            InfoPoint._journal.M(msg, force)

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, *, pos={}, dat={}):
        "Calls constructor of InfoPoint on respective position"
        
        self.pos = pos         # Dict of real numbers for position coordinates
        self.dat = dat         # Dict of values of this InfoPoint

    #--------------------------------------------------------------------------
    def __str__(self):
        "Prints info about this InfoPoint"

        toRet = ''
        for line in self.info()['msg']: toRet += line
        return toRet

    #--------------------------------------------------------------------------
    def info(self, indent=0):
        "Creates info about this InfoPoint"
        
        msg = (f"{indent*_IND}{self.posStr()}: {self.datStr()}")

        return {'res':'OK', 'dat':self.dat, 'msg':msg}
        
    #--------------------------------------------------------------------------
    def format(self, val):
        "Creates string representation of the value for respective format settings"

        if   type(val) == int    : toRet = f"{val:#{_F_TOTAL}}"
        elif type(val) == float  : toRet = f"{val:#{_F_TOTAL}.{_F_DECIM}f}"
        elif type(val) == complex: toRet = f"({val.real:#{_F_TOTAL}.{_F_DECIM}f} {val.imag:#{_F_TOTAL}.{_F_DECIM}f}j)"
        else                     : toRet = f"{val:<{_F_TOTAL}}"

        return toRet
    
    #--------------------------------------------------------------------------
    def posStr(self):
        "Creates string representation of the position of this InfoPoint"

        toRet = '['
        
        i = 0
        for key, val in self.pos.items():
            
            if i == 0: toRet +=  f"{key}={self.format(val)}"
            else     : toRet += f"|{key}={self.format(val)}"
            i += 1

        toRet += ']'
        return toRet
    
    #--------------------------------------------------------------------------
    def datStr(self):
        "Creates string representation of the data of this InfoPoint"

        toRet = '{'
        
        i = 0
        for key, val in self.dat.items():

            if i == 0: toRet +=  f"{key}={self.format(val)}"
            else     : toRet += f"|{key}={self.format(val)}"
            i += 1  

        toRet += '}'
        return toRet
    
    #--------------------------------------------------------------------------
    def copy(self):
        "Creates copy of this InfoPoint"

        toRet = InfoPoint()

        toRet.pos = self.pos.copy()
        toRet.dat = self.dat.copy()

        return toRet
        
    #==========================================================================
    # Dat Value modification
    #--------------------------------------------------------------------------
    def clear(self, *, dat={}):
        "Sets complex number to default value and clears state variables"
        
        self.dat = dat

        return self

    #--------------------------------------------------------------------------
    def rndBit(self, prob:float):
        "Sets real value 0/1 with respective probability and imaginary value sets to 0"

        x = rnd.randint(0, 9999)
        
        if x <= prob*10000: self.c = complex(1, 0)
        else              : self.c = complex(0, 0)

        return self
        
    #--------------------------------------------------------------------------
    def rndPhase(self, r=1):
        "Sets random phase <0, 2PI> and radius r. If r==0 then r will be preserved"
        
        if r==0: r = self.c.abs()

        phi    = 2*cmath.pi*rnd.random()
        self.c = cmath.rect(r, phi)

        return self

    #==========================================================================
    # Complex Value methods; expects complex value with key 'c' in dat dict
    #--------------------------------------------------------------------------
    def setCompVal(self, c:complex):
        "Sets complex number to respective complex value"
        
        self.dat['c'] = c
        return self
        
    #--------------------------------------------------------------------------
    def setCompRect(self, re:float, im:float):
        "Sets complex number given by rectangular coordinates (real, imag)"
        
        self.dat['c'] = complex(re, im)
        return self
        
    #--------------------------------------------------------------------------
    def setCompPolar(self, mod:float, phi:float):
        "Sets complex number given by polar coordinates (modulus, phase)"
        
        self.dat['c'] = cmath.rect(mod, phi)
        return self
        
    #--------------------------------------------------------------------------
    def real(self):
        "Returns real part of complex number"
        
        return self.dat['c'].real

    #--------------------------------------------------------------------------
    def imag(self):
        "Returns imaginary part of complex number"
        
        return self.dat['c'].imag

    #--------------------------------------------------------------------------
    def polar(self):
        "Returns polar coordinates of complex number as a tuple. Phase in <-pi, pi> from +x axis"
        
        return cmath.polar(self.dat['c'])

    #--------------------------------------------------------------------------
    def abs(self):
        "Returns absolute value = modulus of complex number"
        
        return abs(self.dat['c'])

    #--------------------------------------------------------------------------
    def phase(self):
        "Returns phase in <-pi, pi> from +x axis"
        
        return cmath.phase(self.dat['c'])

    #--------------------------------------------------------------------------
    def conjugate(self):
        "Returns conjugate complex number"
        
        return self.dat['c'].conjugate()

    #--------------------------------------------------------------------------
    def sqrComp(self):
        "Returns square of complex number"
        
        return self.dat['c'] * self.dat['c']

    #--------------------------------------------------------------------------
    def sqrAbs(self):
        "Returns square of the absolute value of complex value"
        
        return (self.dat['c'].real * self.dat['c'].real) + (self.dat['c'].imag * self.dat['c'].imag )

    #==========================================================================
    # Two-points methods
    #--------------------------------------------------------------------------
    def deltasTo(self, toP):
        "Returns list of differences between coordinates for respective InfoPoint"
        
        #----------------------------------------------------------------------
        # Check if both InfoPoints have the same number of coordinates and create pairs of them
        #----------------------------------------------------------------------
        pairs = []

        try:
            for key, val in self.pos.items():
                pairs.append( (val, toP.pos[key]) )

        except KeyError:
            self.journal(f"Error: InfoPoints have different number of coordinates!", True)
            return None
            
        #----------------------------------------------------------------------
        # Cretess list of differences between coordinates for respective InfoPoint
        #----------------------------------------------------------------------
        toRet = [pair[1] - pair[0] for pair in pairs]
        return toRet

    #--------------------------------------------------------------------------
    def distSqrTo(self, toP):
        "Returns square of the distance to respective InfoPoint"
        
        dlts  = self.deltasTo(toP)
        toRet = 0
        
        for dlt in dlts: toRet += dlt*dlt
        
        return toRet

    #--------------------------------------------------------------------------
    def distTo(self, toP):
        "Returns the distance to respective InfoPoint"
        
        sqrDist = self.distSqrTo(toP)
        return math.sqrt(sqrDist)
    
#==============================================================================
# One-Point associated methods
#------------------------------------------------------------------------------
def abs(point:InfoPoint, par:dict):
    "Returns the absolute value of the value on the position valKey"

    #--------------------------------------------------------------------------
    # Parameters checking
    #--------------------------------------------------------------------------
    if 'valKey' in par.keys(): valKey = par['valKey']
    else:
        p.journal(f"abs : Error Key '{valKey}' not found in parameters", True)
        return False 
    
    #--------------------------------------------------------------------------
    # Apply function
    #--------------------------------------------------------------------------
    point.dat[valKey] = math.fabs(point.dat[valKey])
    return True
 
#------------------------------------------------------------------------------
print('InfoPoint ver 3.01')

if __name__ == '__main__':

    print('Test of InfoPoint class')
    print('_IND      =', _IND) 

    p1 = InfoPoint()
    print(p1)

    p2 = InfoPoint(pos={'x':1, 'y':1.2}, dat={'a':3, 'b':4.567891234})
    print(p2)
    
    p3 = InfoPoint(pos={'x':1, 'y':2}, dat={'a':-3, 'b':4.567891234, 'c':complex(1,-2.3456789)})
    print(p3)

    abs(p3, par={'valKey':'a'})
    print(p3)

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------