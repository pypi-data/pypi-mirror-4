"""cubicweb-email"""

from cubicweb import ETYPE_NAME_MAP
ETYPE_NAME_MAP['Emailpart'] = 'EmailPart'
ETYPE_NAME_MAP['Emailthread'] = 'EmailThread'

try:
    from cubicweb.devtools import VIEW_VALIDATORS
    VIEW_VALIDATORS['headers'] = None
except ImportError:
    pass
