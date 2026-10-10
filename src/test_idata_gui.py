#==============================================================================
#  IField: Test file for IFieldMatrixGui class
#------------------------------------------------------------------------------
import tkinter                  as tk

from   siqolib.logger           import SiqoLogger

from   idata.idata              import InfoData
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

    logger = SiqoLogger(name='IData', level='INFO')
    logger.frameDepth = 2
    print(f'logger.frameDepth = {logger.frameDepth}')

    #--------------------------------------------------------------------------
    # Test of the InfoDataGui class
    #--------------------------------------------------------------------------
    win = tk.Tk()
    win.configure(bg='silver', highlightthickness=2, highlightcolor='green')
    win.title('Test of InfoDataGui class')
    #win.maxsize(width=1200, height=800)
    win.minsize(width=600, height=300)
    win.config(highlightbackground = "green", highlightcolor= "green")

    #--------------------------------------------------------------------------
    # Zaciatok testu
    #--------------------------------------------------------------------------
    data = InfoData('IDataGuiTest')

    logger.setLevel('INFO')
    logger.info('Test of InfoDataGui class')

    print(data.info(full=False)['msg'])

    dataGui = InfoDataGui(container=win)
    dataGui.pack(fill=tk.BOTH, expand=True, side=tk.TOP, anchor=tk.N)

    logger.setLevel('INFO')
    win.mainloop()
    logger.info('Stop of InfoDataGui test')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
