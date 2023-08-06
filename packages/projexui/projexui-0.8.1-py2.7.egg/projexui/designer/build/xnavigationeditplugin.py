#!/usr/bin/python

''' Auto-generated ui widget plugin '''

from projexui.qt.QtDesigner import QPyDesignerCustomWidgetPlugin
from projexui.qt.QtGui import QIcon

from projexui.widgets.xnavigationedit import XNavigationEdit as WidgetClass

class XNavigationEditPlugin( QPyDesignerCustomWidgetPlugin ):
    def __init__( self, parent = None ):
        super(XNavigationEditPlugin, self).__init__( parent )
        
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
        return 'projexui.widgets.xnavigationedit'
    
    def domXml( self ):
        if ( hasattr( WidgetClass, '__designer_xml__' ) ):
            return WidgetClass.__designer_xml__
        
        return '<widget class="XNavigationEdit" name="XNavigationEdit"/>'
