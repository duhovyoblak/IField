#==============================================================================
#  IField: main file
#------------------------------------------------------------------------------
import tkinter                  as tk

from   siqolib.logger           import SiqoLogger
from   siqo_imatrix_gui         import InfoMatrixGui
from   ifield_imatrix           import InfoFieldMatrix

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

    logger = SiqoLogger(name='IField', level='INFO')
    logger.frameDepth = 2
    print(f'logger.frameDepth = {logger.frameDepth}')

    #--------------------------------------------------------------------------
    # Test of the InfoMatrixGui class
    #--------------------------------------------------------------------------
    win = tk.Tk()
    win.configure(bg='silver', highlightthickness=2, highlightcolor='green')
    win.title('Test of InfoModelGui class')
    #win.maxsize(width=1200, height=800)
    win.minsize(width=600, height=300)
    win.config(highlightbackground = "green", highlightcolor= "green")

    #--------------------------------------------------------------------------
    # Zaciatok testu
    #--------------------------------------------------------------------------
    matrix = InfoFieldMatrix('IField')

    logger.setLevel('INFO')
    logger.info('Test of InfoMatrixGui class')

    matrix.setIpType('ipTest')
    matrix.setSchema({'axes': {'l': 'Lambda', 'e': 'Epoch'}, 'vals': {'s': 'State'}})
    matrix.init(cnts={'l':100, 'e':50})

    #logger.setLevel('DEBUG')

    matrix.applyMatrixMethod(methodKey='Real constant', valueKey='s', params={'const': 0.0})
    print(matrix.info(full=False)['msg'])

    matrixGui = InfoMatrixGui(container=win, dat=matrix)
    matrixGui.pack(fill=tk.BOTH, expand=True, side=tk.TOP, anchor=tk.N)

    logger.setLevel('INFO')
    win.mainloop()
    logger.info('Stop of InfoMatrixGui test')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
