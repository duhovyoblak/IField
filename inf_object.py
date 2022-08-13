#==============================================================================
# Siqo class IObject
#------------------------------------------------------------------------------
# from  datetime import datetime, timedelta

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_ID_LEN   = 12  # Max length of objId

#==============================================================================
# package's variables
#------------------------------------------------------------------------------

#==============================================================================
# IObject
#------------------------------------------------------------------------------
class IObject:

    #==========================================================================
    # Static variables & methods
    #--------------------------------------------------------------------------
    journal = None   # Pointer to global journal
    objs    = {}     # Zoznam objektov      {objId : obj}
    vals    = {}     # Zoznam values        {objVal: obj}
    vidx    = {}     # Index ID podla dzlky {valLen: #count_of_objects}

    #--------------------------------------------------------------------------
    @staticmethod
    def infoAll():
        "Returns info about Objects"

        info = {}
        out  = []
        
        out.append('{} {}'.format(90*'=', 'Objects:'))
        
        for objId, obj in IObject.objs.items():
            info[objId] = obj.objVal
            
        #----------------------------------------------------------------------
        # Output
        for key, val in info.items(): out.append(f'{key.ljust(_ID_LEN+3)} = {val}')

        #----------------------------------------------------------------------
        return {'res':'OK', 'info':info, 'out':out, 'obj':None}

    #--------------------------------------------------------------------------
    @staticmethod
    def isObj(objVal):
        "Returns True if Object with respective objVal exists"

        # Check if such Object exists already
        if objVal in IObject.vals.keys(): return True
        else                            : return False

    #--------------------------------------------------------------------------
    @staticmethod
    def getObj(objVal, create=True):
        "Returns Object with respective objVal if exists, else returns None or creates new Object"

        IObject.journal.I(f"IObject.getObj: '{objVal}'")
        toRet = None

        #----------------------------------------------------------------------
        # Check if such Object exists already
        #----------------------------------------------------------------------
        if IObject.isObj(objVal): toRet =  IObject.vals[objVal]

        #----------------------------------------------------------------------
        # Decision about creating new Object
        #----------------------------------------------------------------------
        else:
            if create: toRet = IObject(objVal)
            else     : toRet = None
        
        if toRet is None: objId = 'None'
        else            : objId = toRet.objId

        IObject.journal.O(f"IObject.getObj: Returns Object '{objId}'")
        return toRet

    #--------------------------------------------------------------------------
    @staticmethod
    def cntOfLen(vLen):
        "Returns number of Objects with respective length of objVal"
        
        if vLen in IObject.vidx.keys(): cnt = IObject.vidx[vLen]
        else                          : cnt = 0
        
        return cnt

    #--------------------------------------------------------------------------
    @staticmethod
    def valToId(objVal):
        "Returns or creates objId for respective objVal"

        # Check if such Object exists already
        if objVal in IObject.vals.keys(): return IObject.vals[objVal].objId

        vLen = len(objVal)

        # Trivial solution
        if vLen<=_ID_LEN: return objVal

        # Composite ID: A<1234567>-<123456>
        cnt = IObject.cntOfLen(vLen)
        return 'A{:07n}-{:06n}'.format(vLen, cnt)

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, objVal):
        "Calls constructor of IObject and initialise it"

        IObject.journal.I(f'IObject.constructor: |{objVal}|')

        #----------------------------------------------------------------------
        # datove polozky triedy
        #----------------------------------------------------------------------
        self.objVal  = objVal                   # String of raw data constitiuing this Object
        self.objId   = IObject.valToId(objVal)  # String contains unique object Id
        self.objPrp  = {}                       # Objects properties
        
        self.status  = 'I'    # Actual status of this Objects ['I'nitialised, 'A'nalysed]

        self.prtLst  = []     # List of Objects IDs constituing objects
        self.prtHist = {}     # histogram of valId objects count

        #----------------------------------------------------------------------
        # Update zoznamov a indexov
        #----------------------------------------------------------------------
        IObject.objs[self.objId      ] = self
        IObject.vals[self.objVal     ] = self
        
        cnt = IObject.cntOfLen(len(self.objVal))
        
        if cnt==0: IObject.vidx[len(self.objVal)]  = 1
        else     : IObject.vidx[len(self.objVal)] += 1
        
        #----------------------------------------------------------------------
        # inicializacia Objektu
        #----------------------------------------------------------------------
        self.encode()

        IObject.journal.O(f'{self.objId}.constructor: done with status {self.status}')

    #--------------------------------------------------------------------------
    def __str__(self):
        "Prints info about this object"

        toRet = ''
        for line in self.info()['out']: toRet += line +'\n'

        return toRet

    #==========================================================================
    # API
    #--------------------------------------------------------------------------
    def info(self):
        "Returns info about this Object"

        info = {}
        out  = []
        
        info['objId'     ] = self.objId
        info['objVal'    ] = self.objVal[:800]
        info['prtIds'    ] = self.prtIdStr()
        info['prtVals'   ] = self.prtValStr()
            
        #----------------------------------------------------------------------
        # Histogram

        #----------------------------------------------------------------------
        # Output
        for key, val in info.items(): out.append(f'{key.ljust(_ID_LEN)} = {val}')

        return {'res':'OK', 'info':info, 'out':out, 'obj':self}

    #--------------------------------------------------------------------------
    def prtIdStr(self):
        "Returns string of objId's constituing this Object"
        
        idLst = [obj.objId for obj in self.prtLst]
        return ','.join(idLst)[:90]
    
    #--------------------------------------------------------------------------
    def prtValStr(self):
        "Returns string of objVal's constituing this Object"
        
        valLst = [obj.objVal for obj in self.prtLst]
        return '|'.join(valLst)[:90]
    
    #--------------------------------------------------------------------------
    def isBase(self):
        "Returns True if this Object is base object"
        
        if self.objId==self.objVal: return True
        else                      : return False
    
    #--------------------------------------------------------------------------
    def isValid(self):
        "Returns True if this Object is valid object"
        
        return self.valid
    
    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------

    #==========================================================================
    # Internal Methods
    #--------------------------------------------------------------------------
    def encode(self):
        "Encode objVal into prtLst using existing/new Objects in objs"
        
        IObject.journal.I(f'{self.objId}.encode: {self.objVal[:80]}')
        
        self.prtLst.clear()
        
        #----------------------------------------------------------------------
        # Prejdem vsetky pozicie v objVal
        #----------------------------------------------------------------------
        pos   =  0
        vLen  =  len(self.objVal)
        
        while pos < vLen:
            
            # Najdem njdlhsiu sekvenciu ktora sa nachadza vo vals
            val = ''
            while (val=='' or IObject.isObj(val) ) and (pos < vLen):
                val += self.objVal[pos]
                pos += 1
            
            # Korekcia posledneho znaku ak existuje aspon jednoznakova sekvencia
            if len(val)>1:
                val = val[:-1]
                pos -= 1
                
            # Ziskam objekt s prislusnou objVal
            part = IObject.getObj(val, create=True)
        
            # Vlozim partObject do zoznamu
            self.prtLst.append(part)
        
        IObject.journal.O(f'{self.objId}.encode: ')
    
    #--------------------------------------------------------------------------
    def analyse(self, objVal=None):
        "Analyses objVal and creates prtLst. Returns number of identified parts"

        if objVal is not None: self.objVal = objVal

        IObject.journal.I(f'{self.objId}.analyse: {self.objVal[:70]}...')

        if self.objVal=='': self.valid = False
        else:
            self.valid = True
            self.encode()
        
        IObject.journal.O(f'{self.objId}.analyse: Identified {len(self.prtLst)} parts')
        return len(self.prtLst)
        
    #==========================================================================
    # Persistency methods
    #--------------------------------------------------------------------------
    def fromJson(self, json):
        "Loads Object from json structure"

        IObject.journal.I(f'{self.objId}.fromJson:')

        #----------------------------------------------------------------------
        IObject.journal.O(f'{self.objId}.fromJson: Loaded')

    #--------------------------------------------------------------------------
    def toJson(self):
        "Converts Object into json structure"
        
        IObject.journal.I(f'{self.objId}.toJson:')
        
        toRet = {}

        IObject.journal.O(f'{self.objId}.toJson: Converted')
        return toRet

#------------------------------------------------------------------------------
print('IObject ver 0.01')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------