#==============================================================================
# Siqo class ComplexPoint and CompplexField
#------------------------------------------------------------------------------
#import math
import cmath
import random                as rnd
#import siqo_general          as gen

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_IND    = '|  '       # Info indentation

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
    def __init__(self, *, pos=[], c=complex(0,0)):
        "Calls constructor of ComplexPoint on respective position"
        
        self.pos = list(pos)      # Vector of real numbers for position coordinates
        self.c   = c              # Complex value of this ComplexPoint

    #--------------------------------------------------------------------------
    def __str__(self):
        "Prints info about this ComplexPoint"

        toRet = ''
        for line in self.info()['msg']: toRet += line
        return toRet

    #--------------------------------------------------------------------------
    def info(self, indent=0):
        "Creates info about this ComplexPoint"
        
        dat = {}
        msg = []

        dat['c'  ] = self.c
        dat['pos'] = self.pos

        msg.append(f"{indent*_IND}{self.posStr()} : {self.cStr()}")

        return {'res':'OK', 'dat':dat, 'msg':msg}
        
    #--------------------------------------------------------------------------
    def posStr(self):
        "Creates string representation of the position of this ComplexPoint"

        toRet = 'X['
        
        i = 0
        for coor in self.pos:
            
            if i == 0: toRet +=   f"{coor:7.2f}"
            else     : toRet += f" |{coor:7.2f}"
            i += 1

        toRet += ']'

        return toRet
    
    #--------------------------------------------------------------------------
    def cStr(self):
        "Creates string representation of the complex value of this ComplexPoint"

        return f"({self.c.real:7.3f} {self.c.imag:7.3f}j)"
    
    #--------------------------------------------------------------------------
    def copy(self):
        "Creates copy of this ComplexPoint"

        toRet = ComplexPoint(pos=self.pos, c=self.c)
        return toRet
        
    #==========================================================================
    # Value modification
    #--------------------------------------------------------------------------
    def clear(self):
        "Sets complex number to (0+0j)"
        
        self.c = complex(0,0)
        return self
    #--------------------------------------------------------------------------
    def setComp(self, c):
        "Sets complex number to respective complex value"
        
        self.c = c
        return self
        
    #--------------------------------------------------------------------------
    def setRect(self, re, im):
        "Sets complex number given by rectangular coordinates (real, imag)"
        
        self.c = complex(re, im)
        return self
        
    #--------------------------------------------------------------------------
    def setPolar(self, mod, phi):
        "Sets complex number given by polar coordinates (modulus, phase)"
        
        self.c = cmath.rect(mod, phi)
        return self
        
    #--------------------------------------------------------------------------
    def rndBit(self, prob):
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

#------------------------------------------------------------------------------
print('ComplexPoint ver 3.01')

if __name__ == '__main__':

    print('Test of ComplexPoint class')

    # Test of ComplexPoint class
    p1 = ComplexPoint()
    print(p1)

    p2 = ComplexPoint(c=complex(3, 4))
    print(p2)
    
    p1.setComp(complex(1, 2))
    p2.setComp(complex(3, 4))

    print(p1)
    print(p2)

    print(p1.distSqrTo(p2))

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------