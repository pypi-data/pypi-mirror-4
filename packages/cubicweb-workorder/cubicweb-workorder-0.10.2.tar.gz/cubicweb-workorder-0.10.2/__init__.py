"""cubicweb-workorder"""

# EOrder was renamed Order with version 0.5.0
from cubicweb import ETYPE_NAME_MAP
ETYPE_NAME_MAP['EOrder'] = 'Order'
