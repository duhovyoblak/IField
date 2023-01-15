#==============================================================================
# Siqo class IStruct
#------------------------------------------------------------------------------
# from  datetime import datetime, timedelta

from inf_object         import IObject

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_DELTA_MAX  =  100  # Max delta for autoidentity

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
        
        for objId, obj in IStruct.objs.items():
            info[objId] = obj.objVal[:_OUT_MAX]
            
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
        if objVal in IStruct.vals.keys(): return True
        else                            : return False

    #--------------------------------------------------------------------------
    @staticmethod
    def getObj(objVal, create=True):
        "Returns Object with respective objVal if exists, else returns None or creates new Object"

        IStruct.journal.I(f"IStruct.getObj: '{objVal[:80]}...'")
        toRet = None

        #----------------------------------------------------------------------
        # Check if such Object exists already
        #----------------------------------------------------------------------
        if IStruct.isObj(objVal): toRet =  IStruct.vals[objVal]

        #----------------------------------------------------------------------
        # Decision about creating new Object
        #----------------------------------------------------------------------
        else:
            if create: toRet = IStruct(objVal)
            else     : toRet = None
        
        if toRet is None: objId = 'None'
        else            : objId = toRet.objId

        IStruct.journal.O(f"IStruct.getObj: Returns Object '{objId}'")
        return toRet

    #--------------------------------------------------------------------------
    @staticmethod
    def cntOfLen(vLen):
        "Returns number of Objects with respective length of objVal"
        
        if vLen in IStruct.vidx.keys(): cnt = IStruct.vidx[vLen]
        else                          : cnt = 0
        
        return cnt

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, objVal):
        "Calls constructor of IStruct and initialise it"

        IStruct.journal.I(f"IStruct.constructor: '{objVal[:80]}...'")

        #----------------------------------------------------------------------
        # datove polozky triedy
        #----------------------------------------------------------------------
        self.objVal  = objVal                   # String of raw data constitiuing this Object
        self.objId   = IStruct.valToId(objVal)  # String contains unique object Id
        self.objPrp  = {}                       # Objects properties
        
        self.status  = 'I'    # Actual status of this Objects ['I'nitialised, 'A'nalysed]

        self.prtLst  = []     # List of Objects IDs constituing objects
        self.prtHist = {}     # histogram of valId objects count
        self.prtRank = {}     # Ranking of objects by count asc
        
        self.aidMat  = []     # AutoIdentity Matrix
        self.aidVec  = []     # AutoIdentity Vector
        
        self.prtVirt = {}     # List of virtual parts
        
        #----------------------------------------------------------------------
        # Update zoznamov a indexov
        #----------------------------------------------------------------------
        IStruct.objs[self.objId      ] = self
        IStruct.vals[self.objVal     ] = self
        
        cnt = IStruct.cntOfLen(len(self.objVal))
        
        if cnt==0: IStruct.vidx[len(self.objVal)]  = 1
        else     : IStruct.vidx[len(self.objVal)] += 1
        
        #----------------------------------------------------------------------
        # inicializacia Objektu
        #----------------------------------------------------------------------
        self.encode()
        self.histogram()

        IStruct.journal.O(f'{self.objId}.constructor: done with status {self.status}')

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
        info['objVal'    ] = self.objVal     [:_OUT_MAX]
        info['prtIds'    ] = self.prtIdStr() [:_OUT_MAX]
        info['prtVals'   ] = self.prtValStr()[:_OUT_MAX]
            
        #----------------------------------------------------------------------
        # Histogram

        #----------------------------------------------------------------------
        # Output
        for key, val in info.items(): out.append(f'{key.ljust(_ID_LEN)} = {val}')

        return {'res':'OK', 'info':info, 'out':out, 'obj':self}

    #--------------------------------------------------------------------------
    def infoAidMat(self):
        "Prints autoIdentityMatrix"
        
        for vec in self.aidMat:
            print(''.join([str(x) for x in vec]))
        
        
        
    #--------------------------------------------------------------------------
    def prtIdStr(self, a=0, b=None):
        "Returns string of objId's constituing this Object"
        
        if b is None: b = len(self.prtLst)
        
        idLst = [obj.objId for obj in self.prtLst[a:b]]
        return ','.join(idLst)
    
    #--------------------------------------------------------------------------
    def prtValStr(self, a=0, b=None):
        "Returns string of objVal's constituing this Object"
        
        if b is None: b = len(self.prtLst)
        
        valLst = [obj.objVal for obj in self.prtLst[a:b]]
        return '|'.join(valLst)
    
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
    def charVal(self, prtId):
        "Returns characteristics value of the particular Object"
        
        return self.prtRank[prtId]
        
    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------

    #==========================================================================
    # Internal Methods
    #--------------------------------------------------------------------------
    def encode(self):
        "Encode objVal into prtLst using existing/new Objects in objs"
        
        IStruct.journal.I(f"{self.objId}.encode: '{self.objVal[:80]}...'")
        
        self.prtLst.clear()
        
        #----------------------------------------------------------------------
        # Prejdem vsetky pozicie v objVal
        #----------------------------------------------------------------------
        pos   =  0
        vLen  =  len(self.objVal)
        
        while pos < vLen:
            
            # Najdem njdlhsiu sekvenciu ktora sa nachadza vo vals
            val = ''
            while (val=='' or IStruct.isObj(val) ) and (pos < vLen):
                val += self.objVal[pos]
                pos += 1
            
            # Korekcia posledneho znaku ak existuje aspon jednoznakova sekvencia
            if len(val)>1:
                val = val[:-1]
                pos -= 1
                
            # Ziskam objekt s prislusnou objVal
            part = IStruct.getObj(val, create=True)
        
            # Vlozim partObject do zoznamu
            self.prtLst.append(part)
        
        IStruct.journal.O(f'{self.objId}.encode: Identified {len(self.prtLst)} parts')
    
    #--------------------------------------------------------------------------
    def histogram(self):
        "From prtLst cretaes histogram vector and ranking"

        IStruct.journal.I(f'{self.objId}.histogram:')
        
        self.prtHist = {}
        self.prtRank = {}
        
        #----------------------------------------------------------------------
        # Histogram
        #----------------------------------------------------------------------
        for obj in self.prtLst:
            
            if obj.objId in self.prtHist.keys(): self.prtHist[obj.objId] += 1
            else                               : self.prtHist[obj.objId]  = 1
            
        # Normalizacia na percenta
        # for cnt in self.prtHist.values(): cnt /= len(self.prtLst)
            
        #----------------------------------------------------------------------
        # Ranking
        #----------------------------------------------------------------------
        pomDic = dict(sorted(self.prtHist.items(), key=lambda x: x[1], reverse=True))
        
        rank = 0
        for key in pomDic.keys():
            self.prtRank[key] = rank
            rank += 1
        
        IStruct.journal.O(f'{self.objId}.histogram:')
        
    #--------------------------------------------------------------------------
    def analyse(self):
        "From prtLst cretaes autoIdentity matrix"

        IStruct.journal.I(f'{self.objId}.analyse:')
        
        self.aidMat  = []
        self.aidVec  = []
        self.prtVirt = {}
        self.prtEim  = {}
        
        maxDelta = int(len(self.prtLst)/2)
        
        maxDelta = min(maxDelta, _DELTA_MAX)
        
        #----------------------------------------------------------------------
        # Prejdem delta t od 0 po maxDelta a pre kazde delta urcim identity vektor
        #----------------------------------------------------------------------
        for delta in range(1, maxDelta+1):
            
            if (delta%10)==0: IStruct.journal.M(f'{self.objId}.analyse: delta {delta}')

            #------------------------------------------------------------------
            # Ziskam autoIdentity vektor pre konkretnu delta
            #------------------------------------------------------------------
            aidVec = lib.vecIdent(self.prtLst, self.prtLst, delta)
            
            #------------------------------------------------------------------
            # Zapisem aidVec do AutiIdentity matrix
            #------------------------------------------------------------------
            self.aidMat.append(aidVec)
            
            #------------------------------------------------------------------
            # Zapisem sumu identit pre danu delta normovanu na dlzku prtVec
            #------------------------------------------------------------------
            self.aidVec.append( sum(aidVec) / len(self.prtLst) )
            
            #------------------------------------------------------------------
            # Z aidVec ziskam virtualne castice
            #------------------------------------------------------------------
            virts = lib.vecParts(aidVec)
            
            #------------------------------------------------------------------
            # Zapisem si virtualne castice do rankingu
            #------------------------------------------------------------------
            for virtInt in virts:
                prtVal = self.prtValStr(virtInt[0], virtInt[1])
                if prtVal not in self.prtVirt.keys(): self.prtVirt[prtVal]  = 1
                else                                : self.prtVirt[prtVal] += 1
                
            #------------------------------------------------------------------
            # 
            #------------------------------------------------------------------
            self.prtEim[delta] = {}  # dlzka:pocet_vyskytov




        #----------------------------------------------------------------------
        IStruct.journal.O(f'{self.objId}.analyse: Identified {len(self.prtLst)} parts')
        
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