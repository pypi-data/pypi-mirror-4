"""
LEAP Encryption Access Project
website: U{https://leap.se/}
"""

from leap import eip
from leap import baseapp
from leap import util
#from leap import soledad

__all__ = [eip, baseapp, util]
__version__ = "unknown"
try:
    from ._version import get_versions
    __version__ = get_versions()['version']
    del get_versions
except ImportError:
    #running on a tree that has not run
    #the setup.py setver
    pass

__appname__ = "unknown"
try:
    from leap._appname import __appname__
except ImportError:
    #running on a tree that has not run
    #the setup.py setver
    pass

__full_version__ = __appname__ + '/' + str(__version__)

try:
    from leap._branding import BRANDING as __branding
except ImportError:
    __branding = {}
