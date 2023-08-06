__all__=['wxTerminal','version',"wxTerminalMP"]

from wxTerminal import *

try:
	from version import __version__
except ImportError:
    __version__="Unknown"

	