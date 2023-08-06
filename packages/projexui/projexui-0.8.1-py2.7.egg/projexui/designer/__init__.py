#!/usr/bin/python

""" Auto-generates Qt ui designer plugins. """

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

import glob
import logging
import os
import sys

import projex
import projexui

logger = logging.getLogger(__name__)

WIDGET_PATH = os.path.pathsep.join((
                os.path.dirname(projexui.__file__) + '/widgets',
                os.environ.get('PROJEXUI_DESIGNER_WIDGETPATH', '')))
                
BUILD_PATH  = os.environ.get('PROJEXUI_DESIGNER_BUILDPATH', 
                             os.path.dirname(__file__) + '/build')

PLUGIN_DEF = """\
#!/usr/bin/python

''' Auto-generated ui widget plugin '''

from projexui.qt.QtDesigner import QPyDesignerCustomWidgetPlugin
from projexui.qt.QtGui import QIcon

from %(module)s import %(class)s as WidgetClass

class %(class)sPlugin( QPyDesignerCustomWidgetPlugin ):
    def __init__( self, parent = None ):
        super(%(class)sPlugin, self).__init__( parent )
        
        self.initialized = False
    
    def initialize( self, core ):
        if ( self.initialized ):
            return
        
        self.initialized = True
    
    def isInitialized( self ):
        return self.initialized
    
    def createWidget( self, parent ):
        return WidgetClass(parent)
    
    def name( self ):
        if ( hasattr( WidgetClass, '__designer_name__' ) ):
            return WidgetClass.__designer_name__
        return WidgetClass.__name__
    
    def group( self ):
        if ( hasattr( WidgetClass, '__designer_group__' ) ):
            return WidgetClass.__designer_group__
        return 'ProjexUI'
    
    def icon( self ):
        if ( hasattr( WidgetClass, '__designer_icon__' ) ):
            return QIcon(WidgetClass.__designer_icon__)
        return QIcon()
    
    def toolTip( self ):
        if ( hasattr( WidgetClass, '__designer_tooltip__' ) ):
            return WidgetClass.__designer_tooltip__
        elif ( hasattr( WidgetClass, '__doc__' ) ):
            return str(WidgetClass.__doc__)
        return ''
    
    def whatsThis( self ):
        return ''
    
    def isContainer( self ):
        if ( hasattr( WidgetClass, '__designer_container__' ) ):
            return WidgetClass.__designer_container__
        return False
    
    def includeFile( self ):
        return '%(module)s'
    
    def domXml( self ):
        if ( hasattr( WidgetClass, '__designer_xml__' ) ):
            return WidgetClass.__designer_xml__
        
        return '<widget class="%(class)s" name="%(class)s"/>'
"""

def generatePlugins(widgetPath = None, buildPath = None):
    """
    Generates all the plugin files for the system and imports them.
    
    :param      widgetPath | <str> || None
                buildPath  | <str> || None
    """
    if ( widgetPath is None ):
        widgetPath = WIDGET_PATH
        
    if ( buildPath is None ):
        buildPath = BUILD_PATH
    
    for basepath in widgetPath.split(os.path.pathsep):
        if ( not basepath ):
            continue
            
        # load packaged widgets
        for filepath in glob.glob(os.path.join(basepath, '*/__init__.py')):
            generatePlugin(filepath, buildPath)
        
        # load module widgets
        for filepath in glob.glob(os.path.join(basepath, '*.py')):
            if ( filepath.endswith('__init__.py') ):
                continue
                
            generatePlugin(filepath, buildPath)

def generatePlugin(sourcePath, buildPath = None):
    """
    Generates a particular ui plugin for ths system and imports it.
    
    :param      widgetPath  | <str>
                buildPath   | <str> || None
    """
    if ( buildPath is None ):
        buildPath = BUILD_PATH
        
    pkg_name = projex.packageFromPath(sourcePath)
    # load a package
    if ( not sourcePath.endswith('__init__.py') ):
        pkg_name += '.' + os.path.basename(sourcePath).split('.')[0]
    
    try:
        __import__(pkg_name)
    except ImportError, e:
        logging.exception(e)
        return
    
    module = sys.modules.get(pkg_name)
    if ( not module ):
        return
        
    if ( not hasattr(module, '__designer_plugins__' ) ):
        logger.warning('%s has no __designer_plugins__ defined.' % pkg_name)
        return
    
    if ( not os.path.exists(buildPath) ):
        os.mkdir(buildPath)
    
    for plug in module.__designer_plugins__:
        output_path = os.path.join(buildPath, 
                                   '%splugin.py' % plug.__name__.lower())
        
        # generate the options
        options = {}
        options['module'] = pkg_name
        options['class']  = plug.__name__
        
        # save the plugin
        f = open(output_path, 'w')
        f.write(PLUGIN_DEF % options)
        f.close()

if ( __name__ == '__main__' ):
    logging.basicConfig()
    generatePlugins()