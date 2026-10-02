#==============================================================================
# Idata package - Data structures for Information Field
#------------------------------------------------------------------------------
import json
from pathlib import Path

from  siqolib.logger         import SiqoLogger

#==============================================================================
# Package's constants
#------------------------------------------------------------------------------
_VER  = '1.1.1'

#==============================================================================
# Package's variables
#------------------------------------------------------------------------------
logger = SiqoLogger(name='IDataPackage')   # Logger for IDataPackage
logger.setLevel('INFO')

#------------------------------------------------------------------------------
# Nacitanie InfoData typov
#------------------------------------------------------------------------------
iDataTypes = {}
iDataTypeFName = Path(__file__).with_name('iDataTypeConfig.json')

with iDataTypeFName.open(encoding='utf-8') as config_file:
    iDataTypes = json.load(config_file)

logger.info(f"Loaded {len(iDataTypes)} InfoData types from '{iDataTypeFName.name}'")

#==============================================================================
# Inicializacia modulu
#------------------------------------------------------------------------------
print(f'IDataPackage ver {_VER}')

if __name__ == '__main__':

    logger.info("Testing IDataPackage")

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------