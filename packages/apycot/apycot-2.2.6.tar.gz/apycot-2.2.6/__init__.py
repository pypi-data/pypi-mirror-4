"""cubicweb-apycot"""
from cubicweb.schema import ETYPE_NAME_MAP
ETYPE_NAME_MAP['TestConfigGroup'] = 'TestConfig'


try:
    # development version
    import _apycotlib
except ImportError:
    pass
else:
    import sys
    sys.modules['apycotlib'] = _apycotlib
