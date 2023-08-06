__all__=['csFIFO','version']

from csFIFO import *

try:
	from version import __version__
except ImportError:
    __version__="Unknown"