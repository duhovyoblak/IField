#==============================================================================
#  SIQO Server object
#------------------------------------------------------------------------------
import asyncio
import sys
sys.path.append('lib')

from siqo_lib      import journal

#==============================================================================
# package's constants
#------------------------------------------------------------------------------

#==============================================================================
# package's tools
#------------------------------------------------------------------------------

#==============================================================================
# Server
#------------------------------------------------------------------------------
class SiqoServer:

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, name):
        "Call constructor of SiqoServer and initialise it"
       
        self.name       = name     # Nazov Servera
        self.state      = 'OFF'    # State of the server [ON, OFF]
        self.cycles     = 0        # Number of working cycles
        
        journal.M('{}: Server created'.format(self.name))
   
    #==========================================================================
    # API for users
    #--------------------------------------------------------------------------
    def info(self):
        "Starts the server"
        
        journal.M('{}: Server is in state {}'.format(self.name, self.state))
        journal.M('{}: cycles = {}'.format(self.name, self.cycles))

    #--------------------------------------------------------------------------
    def start(self):
        "Starts the server"
        
        journal.I('{}: Server is starting...'.format(self.name))
        self.state = 'ON'
        
        loopTask = asyncio.create_task(self.mainLoop())

        journal.O('{}: Server is in state {}'.format(self.name, self.state))

    #--------------------------------------------------------------------------
    def stop(self):
        "Stops the server"
        
        journal.M('{}: Server shutdown...'.format(self.name))
        self.state = 'OFF'

    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------

    #==========================================================================
    # Interna methods
    #--------------------------------------------------------------------------
    async def mainLoop(self):
        "Main server's loop of cycles"
        
        journal.I("{}: Loop is starting".format(self.name))
        
        while self.cycle():
            await asyncio.sleep(5)
        
        journal.O("{}: Loop done".format(self.name))
        
    #--------------------------------------------------------------------------
    def cycle(self):
        "Do one working cycle of the server"
        
        #----------------------------------------------------------------------
        # Test of user's input
        #----------------------------------------------------------------------
        if self.state=='OFF':
            journal.M("{}: User's commmand OFF. Server shutdown".format(self.name))
            return False
            
        #----------------------------------------------------------------------
        # One working cycle
        #----------------------------------------------------------------------
        self.cycles += 1
        journal.I('{}: Server is doing cycle {}'.format(self.name, self.cycles))

        journal.O('{}: Server cycle {} done'.format(self.name, self.cycles))
        return True

    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------
#==============================================================================
srv = SiqoServer('SIQO Server')
 
#==============================================================================
# Journal
#------------------------------------------------------------------------------
journal.M('Siqo server ver 0.01')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
