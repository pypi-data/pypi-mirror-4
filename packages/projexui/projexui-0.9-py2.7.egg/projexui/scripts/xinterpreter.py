#!/usr/bin/python

""" Launches an XConsole application """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintanence information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

#------------------------------------------------------------------------------

# define version information (major,minor,maintanence)
__depends__        = ['projex']
__version_info__   = (0, 0, 0)
__version__        = '%i.%i.%i' % __version_info__

#------------------------------------------------------------------------------

import projex
projex.requires('projexui')

from projexui.qt.QtCore import Qt
from projexui.qt.QtGui import QApplication
from projexui.widgets.xconsoleedit import XConsoleEdit

if ( __name__ == '__main__' ):
    app = None
    if ( not QApplication.instance() ):
        app = QApplication([])
        app.setStyle('plastique')
    
    interpreter = XConsoleEdit(QApplication.instance().activeWindow())
    interpreter.setWindowTitle('XInterpreter')
    interpreter.setWindowFlags(Qt.Dialog)
    interpreter.show()
    
    if ( app ):
        app.exec_()