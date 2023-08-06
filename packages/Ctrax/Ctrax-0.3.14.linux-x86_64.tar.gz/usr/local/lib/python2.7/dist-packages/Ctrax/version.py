__version__ = "0.3.14"

DEBUG = False

DEBUG_ESTCONNCOMPS = False
DEBUG_REPEATABLE_BEHAVIOR = False
DEBUG_TRACKINGSETTINGS = False
DEBUG_CHOOSEORIENTATIONS = False

USE_AVBIN = True
import sys
if 'darwin' in sys.platform:
    # pyglet's avbin doesn't seem to work on Mac
    USE_AVBIN = False
