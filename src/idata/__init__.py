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
# Konfiguracia schem
#------------------------------------------------------------------------------
from .ipoint import InfoPoint

ipTypeFName = Path(__file__).with_name('ipTypeConfig.json')

with ipTypeFName.open(encoding='utf-8') as config_file:
    _ipTypeConfig = json.load(config_file)

for _ipType, _schema in _ipTypeConfig.items():
    InfoPoint.setSchema(_ipType, _schema)

logger.info(f"Loaded {len(_ipTypeConfig)} InfoPoint type schemas from '{ipTypeFName.name}'")

#==============================================================================
# Inicializacia modulu
#------------------------------------------------------------------------------
print(f'IDataPackage ver {_VER}')

if __name__ == '__main__':

    logger.info("Testing IDataPackage")

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------