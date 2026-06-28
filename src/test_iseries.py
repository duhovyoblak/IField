#==============================================================================
#  IField: main file
#------------------------------------------------------------------------------
import tkinter                  as tk

from   siqolib.logger           import SiqoLogger
from   idata.iseries            import ISeries
from   idata.idata_gui          import InfoDataGui

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_VALS_MAX  = 100000

#==============================================================================
# package's tools
#------------------------------------------------------------------------------

#==============================================================================
# Functions
#------------------------------------------------------------------------------
if __name__ =='__main__':

    logger = SiqoLogger(name='ISeries', level='INFO')
    logger.frameDepth = 2
    print(f'logger.frameDepth = {logger.frameDepth}')

    #--------------------------------------------------------------------------
    # Test of the ISeries class
    #--------------------------------------------------------------------------
    win = tk.Tk()
    win.configure(bg='silver', highlightthickness=2, highlightcolor='green')
    win.title('Test of ISeries class')
    #win.maxsize(width=1200, height=800)
    win.minsize(width=600, height=300)
    win.config(highlightbackground = "green", highlightcolor= "green")

    #--------------------------------------------------------------------------
    # Zaciatok testu
    #--------------------------------------------------------------------------
    data = ISeries('ISeries')

    logger.setLevel('INFO')
    logger.info('Test of ISeries class')

    print(data.info(full=False)['msg'])

    dataGui = InfoDataGui(container=win, data=data)
    dataGui.pack(fill=tk.BOTH, expand=True, side=tk.TOP, anchor=tk.N)

    logger.setLevel('INFO')
    win.mainloop()
    logger.info('Stop of ISeries test')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
