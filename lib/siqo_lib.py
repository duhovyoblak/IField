#==============================================================================
# Siqo common library
#------------------------------------------------------------------------------
from  datetime import datetime
import json

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
 
#==============================================================================
# package's tools
#------------------------------------------------------------------------------

#==============================================================================
# Journal
#------------------------------------------------------------------------------
class SiqoJournal:

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, name):
        "Call constructor of SiqoJournal and initialise it with empty data"
       
        self.name       = name     # Nazov journalu
        self.usr        = ''       # Nazov usera, ktory pouziva journal
        self.debugLevel = 10       # Pocet vnoreni, ktore sa zobrazia
       
        self.indent     = 1        # Aktualne vnorenie
        self.fileOnly   = False    # Ci sa bude zapisovat IBA do suboru
        self.showAll    = False    # Overrride debugLevel. Ak True, bude sa vypisovat VSETKO
        self.out        = []       # Zoznam vypisanych riadkov, pre zapis na disk
       
        self.reset()
   
    #==========================================================================
    # API for users
    #--------------------------------------------------------------------------
    def M(self, mess, force=False, out=False, usr='', step='' ):
        "Vypise zaznam journalu do terminalu"
       
        # Upravim odsadenie podla step
        if step == 'IN': self.indent += 1
           
        # Head
        if usr != '': self.usr = usr
       
        head = '{} {}>'.format( datetime.now().time().strftime('%H:%M:%S'), self.usr )
       
        #----------------------------------------------------------------------
        # Vystup na obrazovku
		
        if not self.fileOnly:
           
            # Skontrolujem, ci su splnene podmienky na vystup
            if ((self.indent <= self.debugLevel) or self.showAll or force) and (self.debugLevel!=0):
           
                line = head
            
                if   step == 'IN' : line += (self.indent-2)*'|  ' + chr(691) + ' ' + mess
                elif step == 'OUT': line += (self.indent-2)*'|  ' + chr(746) + ' ' + mess
                else              : line += (self.indent-1)*'|  '                  + mess
                   
                print(line)
 
        #----------------------------------------------------------------------
        # Vystup do suboru podla argumentu <out>
       
        if out: self.out.append('{}{}'.format(head, mess))
 
        #----------------------------------------------------------------------
        # Upravim odsadenie podla step
        if step == 'OUT': self.indent -= 1
   
    #--------------------------------------------------------------------------
    def I(self, mess ):
 
        self.M( mess, step='IN' )
   
    #--------------------------------------------------------------------------
    def O(self, mess ):
   
        self.M(  mess, step='OUT' )
       
    #--------------------------------------------------------------------------
    def setDepth(self, debug):
        "Nastavi pocet vnoreni na zobrazenie"
 
        # Ak je zmena v nastaveni
        if self.debugLevel != debug:
           
            self.debugLevel = debug
            self.M('Journal setDepth: debug level={}'.format(self.debugLevel), True)
       
    #--------------------------------------------------------------------------
    def setShow(self):
        "Zacne vypisovat VSETKY spravy"
 
        self.showAll = True
        self.M('Journal setShow')
       
    #--------------------------------------------------------------------------
    def endShow(self):
        "Ukonci vypisovanie VSETKYCH sprav"
 
        self.showAll = False
        self.M('Journal endShow')
       
    #--------------------------------------------------------------------------
    def showOut(self):
        "Vypise zoznam perzistentnych sprav na obrazovku"
 
        for mess in self.out: print(mess)
       
    #--------------------------------------------------------------------------
    def dumpOut(self, fileName='' ):
        "Zapise journal na koniec suboru <fileName>"
 
        if fileName=='': fileName = '{}.json'.format(self.name)
       
        file = open(fileName, "a")
        json.dump(self.out, file, indent = 3)
        file.close()   
 
        self.M('Journal dumped to {}'.format(fileName))
       
    #--------------------------------------------------------------------------
    def reset(self, debug=10, usr='', fileOnly=False):
        "Resetne parametre journalu na default hodnoty"
 
        self.usr        = usr
        self.debugLevel = debug
       
        self.indent     = 1
        self.fileOnly   = fileOnly
        self.showAll    = False
        self.out.clear()
       
        self.M('Journal reset, debug level={} & fileOnly={}'.format(self.debugLevel, self.fileOnly), True)
       
        if self.debugLevel == 0: print("Journal '{}' will be quiet and will produce no output".format(self.name))
        if self.fileOnly       : print("Journal '{}' will will produce output to file ONLY".format(self.name))
 
#------------------------------------------------------------------------------
journal = SiqoJournal('Journal')
 
#==============================================================================
# Journal
#------------------------------------------------------------------------------
journal.M('Siqo common library ver 1.15')
 
#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
