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
_F_SCHEMA = 1                          # Format for ipType
_F_TOTAL  = 5                          # Total number of digits in float number
_F_DECIM  = 3                          # Number of digits after decimal point in float number
_F_FORMAT = f"{_F_TOTAL}.{_F_DECIM}f"  # Format for float number

_SCHEMA   = {'ipReal   ':{'axes':{'None':'None'}
                         ,'vals':{}
                         }
            ,'ipComplex':{'axes':{'None':'None', 'x':'os X', 'y':'os Y'}
                         ,'vals':{'r':'real Value'}
                         }
            }                          # Default built-in Schema for InfoPoint

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
    _journal = None                                # Journal for logging
    _schema  = _SCHEMA.copy()                      # Schema for InfoPoint

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

    #--------------------------------------------------------------------------
    @staticmethod
    def resetSchema():
        "Resets schema of InfoPoint to default values"
        
        InfoPoint._schema = _SCHEMA.copy()

    #--------------------------------------------------------------------------
    @staticmethod
    def clearSchema(ipType):
        "Clears schema of InfoPoint for respective ipType to {'axes':{'None':'None'}, 'vals':{}}"
        
        InfoPoint._schema[ipType] = {'axes':{'None':'None'}, 'vals':{}}

    #--------------------------------------------------------------------------
    @staticmethod
    def setAxe(ipType, key, name):
        "Sets axe key and name"
        
        if ipType not in InfoPoint._schema.keys(): InfoPoint._schema[ipType] = {'axes':{'None':'None'}, 'vals':{}} 

        InfoPoint._schema[ipType]['axes'][key] = name

    #--------------------------------------------------------------------------
    @staticmethod
    def getAxeIdx(ipType, key):
        "Returns axe's idx for respective key as position in the list of axes othewise None"

        #----------------------------------------------------------------------
        # Check if ipType is defined    
        #----------------------------------------------------------------------        
        if ipType not in InfoPoint._schema.keys(): 
            logger.info(f"InfoPoint.getAxeIdx: ipType '{ipType}' is not defined InfoPoint type")
            return None 

        #----------------------------------------------------------------------
        # Find index of the axe's key  
        #----------------------------------------------------------------------
        for i, keyAxe in enumerate(InfoPoint._schema[ipType]['axes'].keys()):
            if key==keyAxe: return i

        #----------------------------------------------------------------------
        # Key not found     
        #----------------------------------------------------------------------
        logger.info(f"InfoPoint.getAxeIdx: Key '{key}' not found in axes {InfoPoint._schema[ipType]['axes']}")
        return None
    
    #--------------------------------------------------------------------------
    @staticmethod
    def getAxeKey(ipType, idx):
        "Returns axe's key for respective position in the list of axes othewise None"

        #----------------------------------------------------------------------
        # Check if ipType is defined    
        #----------------------------------------------------------------------        
        if ipType not in InfoPoint._schema.keys(): 
            logger.info(f"InfoPoint.getAxeKey: ipType '{ipType}' is not defined InfoPoint type")
            return None 

        #----------------------------------------------------------------------
        # Check if idx is not out of the range   
        #----------------------------------------------------------------------        
        if idx >= len(InfoPoint._schema[ipType]['axes'].keys()): 
            logger.info(f"InfoPoint.getAxeKey: Idx '{idx}' is out of the range in {InfoPoint._schema[ipType]['axes']}")
            return None 

        #----------------------------------------------------------------------
        # Find key for index  
        #----------------------------------------------------------------------
        key = list(InfoPoint._schema[ipType]['axes'].keys())[idx]
        return key
    
    #--------------------------------------------------------------------------
    @staticmethod
    def getAxeName(ipType, key):
        "Returns axe's Name for respective key as string othewise None"

        #----------------------------------------------------------------------
        # Check if ipType is defined    
        #----------------------------------------------------------------------        
        if ipType not in InfoPoint._schema.keys(): 
            logger.info(f"InfoPoint.getAxeName: ipType '{ipType}' is not defined InfoPoint type")
            return None 

        #----------------------------------------------------------------------
        # Find name of the axe's key  
        #----------------------------------------------------------------------
        if key not in InfoPoint._schema[ipType]['axes'].keys():
            logger.info(f"InfoPoint.getAxeName: Key '{key}' not found in axes {InfoPoint._schema[ipType]['axes']}")
            return None
        
        else:
            return InfoPoint._schema[ipType]['axes'][key]
    
    #--------------------------------------------------------------------------
    @staticmethod
    def setVal(ipType, key, name):
        "Sets value key and name"
        
        if ipType not in InfoPoint._schema.keys(): InfoPoint._schema[ipType] = {'axes':{}, 'vals':{}} 

        InfoPoint._schema[ipType]['vals'][key] = name

    #--------------------------------------------------------------------------
    @staticmethod
    def getValIdx(ipType, key):
        "Returns value's idx for respective key as position in the list of axes othewise None"

        #----------------------------------------------------------------------
        # Check if ipType is defined    
        #----------------------------------------------------------------------        
        if ipType not in InfoPoint._schema.keys(): 
            logger.info(f"InfoPoint.getValIdx: ipType '{ipType}' is not defined InfoPoint type")
            return None 

        #----------------------------------------------------------------------
        # Find index of the value's key  
        #----------------------------------------------------------------------
        for i, keyVal in enumerate(InfoPoint._schema[ipType]['vals'].keys()):
            if key==keyVal: return i

        #----------------------------------------------------------------------
        # Key not found     
        #----------------------------------------------------------------------
        logger.info(f"InfoPoint.getValIdx: Key '{key}' not found in valus {InfoPoint._schema[ipType]['vals']}")
        return None
    
    #--------------------------------------------------------------------------
    @staticmethod
    def getValKey(ipType, idx):
        "Returns value's key for respective position in the list of valus othewise None"

        #----------------------------------------------------------------------
        # Check if ipType is defined    
        #----------------------------------------------------------------------        
        if ipType not in InfoPoint._schema.keys(): 
            logger.info(f"InfoPoint.getValKey: ipType '{ipType}' is not defined InfoPoint type")
            return None 

        #----------------------------------------------------------------------
        # Check if idx is not out of the range   
        #----------------------------------------------------------------------        
        if idx >= len(InfoPoint._schema[ipType]['vals'].keys()): 
            logger.info(f"InfoPoint.getValKey: Idx '{idx}' is out of the range in {InfoPoint._schema[ipType]['vals']}")
            return None 

        #----------------------------------------------------------------------
        # Find key for index  
        #----------------------------------------------------------------------
        key = list(InfoPoint._schema[ipType]['vals'].keys())[idx]
        return key
    
    #--------------------------------------------------------------------------
    @staticmethod
    def getValName(ipType, key):
        "Returns value's Name for respective key as string othewise None"

        #----------------------------------------------------------------------
        # Check if ipType is defined    
        #----------------------------------------------------------------------        
        if ipType not in InfoPoint._schema.keys(): 
            logger.info(f"InfoPoint.getValName: ipType '{ipType}' is not defined InfoPoint type")
            return None 

        #----------------------------------------------------------------------
        # Find name of the value's key  
        #----------------------------------------------------------------------
        if key not in InfoPoint._schema[ipType]['vals'].keys():
            logger.info(f"InfoPoint.getValName: Key '{key}' not found in valus {InfoPoint._schema[ipType]['vals']}")
            return None
        
        else:
            return InfoPoint._schema[ipType]['vals'][key]
    
    #--------------------------------------------------------------------------
    @staticmethod
    def getSchema(ipType):
        "Returns schema for respective InfoPoint type as dict {'axes':{}, 'vals':{}}"
        
        if ipType not in InfoPoint._schema.keys(): InfoPoint._schema[ipType] = {'axes':{}, 'vals':{}}

        return InfoPoint._schema[ipType].copy()
    
    #--------------------------------------------------------------------------
    @staticmethod
    def getAxes(ipType):
        "Returns axes keys and names as dict {key: name}"
        
        if ipType not in InfoPoint._schema.keys():
            logger.info(f"InfoPoint.getAxes: ipType '{ipType}' is not defined InfoPoint type")
            return None 

        return InfoPoint._schema[ipType]['axes'].copy()
    
    #--------------------------------------------------------------------------
    @staticmethod
    def getVals(ipType):
        "Returns values keys and names as dict {key: name}"

        if ipType not in InfoPoint._schema.keys():
            logger.info(f"InfoPoint.getVals: ipType '{ipType}' is not defined InfoPoint type")
            return None

        return InfoPoint._schema[ipType]['vals'].copy()

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, ipType:str, *, pos=None, dat=None):
        "Calls constructor of InfoPoint on respective position"
        
        self._ipType = ipType # Type of InfoPoint (ipReal, ipComplex, ...)
        self._pos    = {}     # Dict of real numbers for position coordinates {'row':5, 'col':6, ...} defined by schema
        self._dat    = {}     # Dict of values of this InfoPoint defined by schema

        self.set(pos=pos, dat=dat)

    #--------------------------------------------------------------------------
    def __str__(self):
        "Prints info about this InfoPoint"

        toRet = ''
        for line in self.info()['msg']: toRet += line
        return toRet

    #--------------------------------------------------------------------------
    def _format(self, val):
        "Creates string representation of the value for respective format settings"

        if   val is None         : toRet = 'None'.ljust(_F_TOTAL)
        elif type(val) == int    : toRet = f"{val:#{_F_TOTAL}}"
        elif type(val) == float  : toRet = f"{val:#{_F_TOTAL}.{_F_DECIM}f}"
        elif type(val) == complex: toRet = f"({val.real:#{_F_TOTAL}.{_F_DECIM}f} {val.imag:#{_F_TOTAL}.{_F_DECIM}f}j)"
        else                     : toRet = f"{val:{_F_TOTAL}}"

        return toRet
    
    #--------------------------------------------------------------------------
    def _posStr(self):
        "Creates string representation of the position of this InfoPoint"

        toRet = '['
        
        i = 0
        for axe, axeName in InfoPoint._schema[self._ipType]['axes'].items():

            # Axe 'None' preskocim
            if axe == 'None': continue

            #----------------------------------------------------------------------
            # Retrieve position of this InfoPoint for axe with key 'axe'
            #----------------------------------------------------------------------
            if axe in self._pos.keys(): val = self._pos[axe]
            else                      : val = None

            #----------------------------------------------------------------------
            # Create string representation of the position of this InfoPoint
            #----------------------------------------------------------------------
            if i == 0: toRet +=  f"{axeName}={self._format(val)}"
            else     : toRet += f"|{axeName}={self._format(val)}"
            i += 1
 
        toRet += ']'
        return toRet
    
    #--------------------------------------------------------------------------
    def _datStr(self):
        "Creates string representation of the data of this InfoPoint"

        toRet = '{'
        
        i = 0
        for valKey, valName in InfoPoint._schema[self._ipType]['vals'].items():
            
            if valKey in self._dat.keys(): val = self._dat[valKey]
            else                         : val = None

            #----------------------------------------------------------------------
            # Create string representation of the data of this InfoPoint
            #----------------------------------------------------------------------
            if i == 0: toRet +=  f"{valKey}={self._format(val)}"
            else     : toRet += f"|{valKey}={self._format(val)}"
            i += 1  

        toRet += '}'
        return toRet
    
    #--------------------------------------------------------------------------
    def info(self, indent=0):
        "Creates info about this InfoPoint"
        
        msg = f"{indent*_IND}{self._ipType:{_F_SCHEMA}}{self._posStr()}: {self._datStr()}"

        return {'res':'OK', 'dat':self._dat, 'msg':msg}
        
    #--------------------------------------------------------------------------
    def copy(self):
        "Creates copy of this InfoPoint"

        toRet = InfoPoint(self._ipType)

        toRet._pos = self._pos.copy()
        toRet._dat = self._dat.copy()

        return toRet
        
    #==========================================================================
    # Dat Value retrieval
    #--------------------------------------------------------------------------
    def get(self, key:str=None):
        "Returns value of this InfoPoint for respective key"
        
        #----------------------------------------------------------------------
        # Return this InfoPoint for key is None
        #----------------------------------------------------------------------
        if key is None: return self

        #----------------------------------------------------------------------
        # Key check
        #----------------------------------------------------------------------
        if key not in InfoPoint._schema[self._ipType]['vals'].keys():
            logger.debug(f"InfoPoint.get: Key '{key}' not found in values {InfoPoint._schema[self._ipType]['vals']}")
            return None

        #----------------------------------------------------------------------
        # Return value of this InfoPoint for respective key
        #----------------------------------------------------------------------
        return self._dat[key]

    #==========================================================================
    # Dat Value modification
    #--------------------------------------------------------------------------
    def set(self, *, pos=None, dat=None):
        "Sets position and data of this InfoPoint"
        
        #----------------------------------------------------------------------
        # Set position of this InfoPoint
        #----------------------------------------------------------------------
        if pos is not None:

            try:
                # Zapisem poziciu vo vsetkych osiach schemy okrem NONE
                for key in InfoPoint._schema[self._ipType]['axes'].keys():
                    if key != 'None': self._pos[key] = pos[key]

            except KeyError:
                logger.debug(f"InfoPoint.set: Key '{key}' not found in positions {pos} ERROR")
                return False
            
        #----------------------------------------------------------------------
        # Set values of this InfoPoint
        #----------------------------------------------------------------------
        if dat is not None:

            for key, val in dat.items():

                if key in InfoPoint._schema[self._ipType]['vals'].keys():
                    self._dat[key] = val    

                else:
                    logger.debug(f"InfoPoint.set: Key '{key}' not found in values {InfoPoint._schema[self._ipType]['vals']}")
                    return False
                
        #----------------------------------------------------------------------
        return True
    
    #--------------------------------------------------------------------------
    def clear(self, *, dat:dict=None):
        "Sets data to default values"
        
        if (dat is not None) and (len(dat) > 0):

            for key, val in dat.items():

                if key in InfoPoint._schema[self._ipType]['vals'].keys():
                    self._dat[key] = val    

                else:
                    logger.debug(f"InfoPoint.set: Key '{key}' not found in values {InfoPoint._schema[self._ipType]['vals']}")
                    return False

        else: self._dat = {}

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
            for key, val in self._pos.items():
                pairs.append( (val, toP._pos[key]) )

        except KeyError:
            logger.debug(f"Error: InfoPoints have different number of coordinates!")
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
def abs(point:InfoPoint, key:str, par:dict=None):
    "Returns the absolute value of the value on the position valKey"

    #--------------------------------------------------------------------------
    # Key check
    #--------------------------------------------------------------------------
    if key not in InfoPoint._schema[point._ipType]['vals'].keys():
        logger.info(f"abs: Key '{key}' was not found in values {InfoPoint._schema[point._ipType]['vals']}")
        return False

    #--------------------------------------------------------------------------
    # Apply function
    #--------------------------------------------------------------------------
    point._dat[key] = math.fabs(point._dat[key])
    return True
 
#------------------------------------------------------------------------------
print('InfoPoint ver 3.01')

if __name__ == '__main__':

    from   siqolib.journal          import SiqoJournal
    journal = SiqoJournal('InfoPoint component test', debug=3)

    journal.I('InfoPoint test')

    InfoPoint.setJournal(journal)

    InfoPoint.setAxe('ipTest', 'x', 'os X')    
    InfoPoint.setAxe('ipTest', 'y', 'os Y')    
    InfoPoint.setVal('ipTest', 'm', 'hmotnost')
    InfoPoint.setVal('ipTest', 'v', 'rychlost')

    print('Test of InfoPoint class')
    print('_IND      =', _IND)
    print('schema    =', InfoPoint._schema)
    print('axes      =', InfoPoint.getAxes('ipTest'))   
    print('vals      =', InfoPoint.getVals('ipTest')) 

    p1 = InfoPoint('ipTest')
    print(p1)

    p2 = InfoPoint('ipTest', pos={'x':1, 'y':1.2}, dat={'m':3, 'v':-4.567891234})
    print(p2)

    print('m =', p2.get('m'))
    print('v2 =', p2.get('v2'))  
    print('no key', p2.get())  
    print()
    
    print('schema tools')
    print('idx for keyAxe x =', InfoPoint.getAxeIdx('ipTest', 'x'))
    print('key for keyAxe 0 =', InfoPoint.getAxeKey('ipTest', 0 ))
    print('idx for keyAxe y =', InfoPoint.getAxeIdx('ipTest', 'y'))
    print('key for keyAxe 1 =', InfoPoint.getAxeKey('ipTest', 1 ))
    print('idx for keyAxe z =', InfoPoint.getAxeIdx('ipTest', 'z'))
    print('key for keyAxe 2 =', InfoPoint.getAxeKey('ipTest', 2 ))

    print('idx for keyVal x =', InfoPoint.getValIdx('ipTest', 'x'))
    print('key for keyVal 0 =', InfoPoint.getValKey('ipTest', 0))
    print('idx for keyVal v =', InfoPoint.getValIdx('ipTest', 'v'))
    print('key for keyVal 1 =', InfoPoint.getValKey('ipTest', 1))
    print('key for keyVal 2 =', InfoPoint.getValKey('ipTest', 2))
    print()


    print('name for keyAxe x =', InfoPoint.getAxeName('ipTest', 'x'))
    print('name for keyAxe y =', InfoPoint.getAxeName('ipTest', 'y'))
    print('name for keyAxe z =', InfoPoint.getAxeName('ipTest', 'z'))
    print('name for keyVal x =', InfoPoint.getValName('ipTest', 'x'))
    print('name for keyVal v =', InfoPoint.getValName('ipTest', 'v'))
    print()

    abs(p2, key='v')
    print('abs v ', p2)


    pc = p2.copy()
    print('Copied ', pc)

    pc = pc.clear()
    print('Cleared ', pc)

    pc = pc.clear(dat={'m':3})
    print('Cleared ', pc)

    pc = pc.clear(dat={})
    print('Cleared ', pc)

    pc = pc.clear(dat={'r':4})
    print('Cleared ', pc)

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------