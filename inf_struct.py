#==============================================================================
# Siqo class IStruct
#------------------------------------------------------------------------------
# from  datetime import datetime, timedelta

import  siqo_general     as     gen
import  inf_lib          as     lib

from    inf_object       import IObject

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_DELTA_MAX  =  100  # Max delta for autoidentity
_OUT_MAX    =   80  # Max characters per output
_ID_LEN     =   12  # Max length of objId

#==============================================================================
# package's variables
#------------------------------------------------------------------------------

#==============================================================================
# IStruct
#------------------------------------------------------------------------------
class IStruct:

    #==========================================================================
    # Static variables & methods
    #--------------------------------------------------------------------------
    journal = None   # Pointer to global journal

    #--------------------------------------------------------------------------
    @staticmethod
    def infoAll():
        "Returns info about Structs"

        info = {}
        msg  = []
        
        msg.append('{} {}'.format(90*'=', 'Objects:'))
        
        for objId, obj in IStruct.objs.items():
            info[objId] = obj.objVal[:_OUT_MAX]
            
        #----------------------------------------------------------------------
        # Output
        for key, val in info.items(): msg.append(f'{key.ljust(_ID_LEN+3)} = {val}')

        #----------------------------------------------------------------------
        return {'res':'OK', 'info':info, 'msg':msg, 'obj':None}

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, name):
        "Calls constructor of IStruct"

        IStruct.journal.I(f"IStruct({name}).constructor:")

        #----------------------------------------------------------------------
        # datove polozky triedy
        #----------------------------------------------------------------------
        self.name    = name   # 
        self.status  = 'I'    # Actual status of this structure ['I'nitialised, 'A'nalysed]

        self.objs    = []     # List of IObject/IStruct constituing this structure
        self.alias   = ''     # Mnemotechnic alias for this structure
        self.len     = 0      # Total length of the object
        self.iterPos = -1     # Position of the iterator of this structure
        self.iterSub = None   # Iterator of the sub-object
        
        #----------------------------------------------------------------------
        # Update zoznamov a indexov
        #----------------------------------------------------------------------
        
        #----------------------------------------------------------------------
        # inicializacia Objektu
        #----------------------------------------------------------------------

        IStruct.journal.O(f'{self.name}.constructor: done with status {self.status}')

    #--------------------------------------------------------------------------
    def __str__(self):
        "Prints info about this object"

        toRet = ''
        for line in self.info()['msg']: toRet += line +'\n'

        return toRet

    #--------------------------------------------------------------------------
    def __iter__(self):
        "Creates iterator for this object"
        
        self.iterPos = 0
        self.iterSub = None
        return self

    #--------------------------------------------------------------------------
    def __next__(self):
        "Returns next item in ongoing iteration of this structure"
        
        #----------------------------------------------------------------------
        # Ak existuje inicializovany iterator sub-objektu z minuleho prechodu
        #----------------------------------------------------------------------
        if self.iterSub is not None:

            #------------------------------------------------------------------
            # Skusim vratit next value of the sub-iterator
            #------------------------------------------------------------------
            try                 : nxt = next(self.iterSub)
            #------------------------------------------------------------------
            # Ak som dosiahol koniec sub-objektu tak resetnem subIter
            #------------------------------------------------------------------
            except StopIteration: self.iterSub = None

        #----------------------------------------------------------------------
        # Ak som dosiahol koniec listu
        #----------------------------------------------------------------------
        if self.iterPos >= len(self.objs): raise StopIteration

        #----------------------------------------------------------------------
        # Nacitam nasledujuci objekt
        #----------------------------------------------------------------------
        obj = self.objs[self.iterPos]
        self.iterPos += 1
            
        # Ak je objekt base objekt, vratim jeho hodnotu:
        if obj.isBase(): return obj.cont
        
        #----------------------------------------------------------------------
        # Ak je objekt IStruct:
        #----------------------------------------------------------------------
        else:
            #------------------------------------------------------------------
            # Inicializujem iterator sub-objektu
            #------------------------------------------------------------------
            self.iterSub = iter(obj)
            #------------------------------------------------------------------
            # Vratim nex value of the sub-object's iterator
            #------------------------------------------------------------------
            return next(self.iterSub)
        
    #--------------------------------------------------------------------------
    def isBase(self):
        "Returns False because IStruct can not be base object"
        
        return False
        
    #--------------------------------------------------------------------------
    def idStr(self):
        "Returns string representation of object's IDs"
        
        ids = [x.objId for x in self.objs]
        
        return ';'.join(ids)
        
    #--------------------------------------------------------------------------
    def alStr(self):
        "Returns string representation of object's aliases"
        
        return self.alias
        
    #--------------------------------------------------------------------------
    def info(self):
        "Returns info about this Object"

        info = {}
        msg  = []
        
        info['name'     ] = self.name

        #----------------------------------------------------------------------
        # Histogram

        #----------------------------------------------------------------------
        # Output
        for key, val in info.items(): msg.append(f'{key.ljust(_ID_LEN)} = {val}')

        return {'res':'OK', 'info':info, 'msg':msg, 'obj':self}

    #==========================================================================
    # API
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
    def append(self, obj):
        "Append object to this structure structure"
        
        self.objs.append(obj)

    #--------------------------------------------------------------------------
    def encode(self, string):
        "Append string encoded into structure (from list of IObjects) into this structure"
        
        IStruct.journal.I(f"{self.name}.encode: '{string[:_OUT_MAX]}...'")
        
        #----------------------------------------------------------------------
        # Prejdem vsetky charaktery stringu
        #----------------------------------------------------------------------
        for char in string:
            
            newStruct = self.encodeChar(char)
            self.append(newStruct)
        
        IStruct.journal.O(f'{self.name}.encode: ')
    
    #--------------------------------------------------------------------------

    #==========================================================================
    # Internal Methods
    #--------------------------------------------------------------------------
    def encodeChar(self, char):
        "Encode char into an IStruct"
        
        IStruct.journal.I(f"{self.name}.encodeChar: '{char}'")
        
        i = ord(char)
        bs = gen.
        #----------------------------------------------------------------------
        # Prejdem vsetky pozicie v objVal
        #----------------------------------------------------------------------
        





        IStruct.journal.O('')
    
    #--------------------------------------------------------------------------
    #==========================================================================
    # Persistency methods
    #--------------------------------------------------------------------------
    def fromJson(self, json):
        "Loads Object from json structure"

        IStruct.journal.I(f'{self.objId}.fromJson:')

        #----------------------------------------------------------------------
        IStruct.journal.O(f'{self.objId}.fromJson: Loaded')

    #--------------------------------------------------------------------------
    def toJson(self):
        "Converts Object into json structure"
        
        IStruct.journal.I(f'{self.objId}.toJson:')
        
        toRet = {}

        IStruct.journal.O(f'{self.objId}.toJson: Converted')
        return toRet

#------------------------------------------------------------------------------
print('IStruct ver 0.01')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------