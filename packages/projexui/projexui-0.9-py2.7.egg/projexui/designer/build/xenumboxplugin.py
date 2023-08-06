#!/usr/bin/python

''' Auto-generated ui widget plugin '''

from projexui.qt.QtDesigner import QPyDesignerCustomWidgetPlugin
from projexui.qt.QtGui import QIcon

import projex.resources
from projexui.widgets.xenumbox import XEnumBox as Base

class XEnumBoxPlugin(QPyDesignerCustomWidgetPlugin):
    def __init__(self, parent=None):
        super(XEnumBoxPlugin, self).__init__(parent)
        
        self.initialized = False
    
    def initialize(self, core):
        if self.initialized:
            return
        
        self.initialized = True
    
    def isInitialized(self):
        return self.initialized
    
    def createWidget(self, parent):
        return Base(parent)
    
    def name(self):
        return getattr(Base, '__designer_name__', Base.__name__)
    
    def group(self):
        return getattr(Base, '__designer_group__', 'ProjexUI')
    
    def icon(self):
        default = projex.resources.find('img/logo_16.png')
        return QIcon(getattr(Base, '__designer_icon__', default))
    
    def toolTip( self ):
        docs = getattr(Base, '__doc__', '')
        if docs is None:
            docs = ''
        return getattr(Base, '__designer_tooltip__', docs)
    
    def whatsThis( self ):
        return ''
    
    def isContainer( self ):
        return getattr(Base, '__designer_container__', False)
    
    def includeFile( self ):
        return 'projexui.widgets.xenumbox'
    
    def domXml( self ):
        default = '<widget class="XEnumBox" name="XEnumBox"/>'
        return getattr(Base, '__designer_xml__', default)
