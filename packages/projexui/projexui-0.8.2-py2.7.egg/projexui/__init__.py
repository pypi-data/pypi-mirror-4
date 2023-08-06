#!/usr/bin/python

""" Provides a library of reusable user interface components. """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = [
    ('Yusuke Kamiyamane',
     'Fuque icon pack from findicons.com under Creative Commons.'),
    ('Alexey Egorov',
     'Checkbox icons for XTreeWidget from findicons.com under Freeware.'),
    ('Moment Icons',
     'Folder icons from findicons.com under Creative Commons.'),
]
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintanence information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

#------------------------------------------------------------------------------

# define version information (major,minor,maintanence)
__depends__        = ['projex']
__version_info__   = (0, 8, 2)
__version__        = '%i.%i.%i' % __version_info__

#------------------------------------------------------------------------------

from projexui.xcommands     import *
from projexui.xwidgetvalue  import *
from projexui.xdatatype     import *