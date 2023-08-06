#!/usr/bin/python

""" Defines common commands that can be used to streamline ui development. """

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


import os.path
import sys

from projexui.qt          import QtGui, wrapVariant

from projexui.qt.QtCore   import Qt,\
                                 QDir

from projexui.qt.QtGui    import QAction,\
                                 QApplication,\
                                 QPixmap,\
                                 QColor,\
                                 QSystemTrayIcon,\
                                 QMenu

from projexui.qt import uic
from projexui.widgets.xloggersplashscreen import XLoggerSplashScreen

def ancestor( qobject, classType ):
    """
    Looks up the ancestor of the inputed QObject based on the given class type.
    
    :param      qobject   | <QObject>
                classType | <subclass of QObject>
    
    :return     <subclass of QObject> || None
    """
    parent = qobject
    while ( parent and not isinstance(parent, classType) ):
        parent = parent.parent()
    return parent

def findUiActions( widget ):
    """
    Looks up actions for the inputed widget based on naming convention.
    
    :param      widget | <QWidget>
    
    :return     [<QAction>, ..]
    """
    output = []
    for action in widget.findChildren(QAction):
        name = str(action.objectName()).lower()
        if ( name.startswith('ui') and name.endswith('act') ):
            output.append(action)
    return output

def localizeShortcuts(widget):
    """
    Shifts all action shortcuts for the given widget to us the
    WidgetWithChildrenShortcut context, effectively localizing it to this
    widget.
    
    :param      widget | <QWidget>
    """
    for action in widget.findChildren(QAction):
        action.setShortcutContext(Qt.WidgetWithChildrenShortcut)

def loadUi(modulefile, inst, uifile = None):
    """
    Load the ui file based on the module file location and the inputed class.
    
    :param      modulefile  | <str>
                inst        | <subclass of QWidget>
                uifile      | <str> || None
    
    :return     <QWidget>
    """
    currpath = QDir.currentPath()
    
    if ( not uifile ):
        uifile = uiFile(modulefile, inst)
    
    # normalize the path
    uifile = os.path.normpath(uifile)
    QDir.setCurrent(os.path.dirname(uifile))
    widget = uic.loadUi(uifile, inst)
    QDir.setCurrent(currpath)
    
    widget.addActions(findUiActions(widget))
    
    return widget

def exec_( window, data ):
    """
    Executes the startup data for the given main window.  This method needs to 
    be called in conjunction with the setup method.
    
    :sa     setup
    
    :param      window  | <QWidget>
                data    | { <str> key: <variant> value, .. }
    
    :return     <int> err
    """
    if ( 'splash' in data ):
        data['splash'].finish(window)
    
    if ( 'app' in data ):
        # setup application information
        data['app'].setPalette(window.palette())
        data['app'].setWindowIcon(window.windowIcon())
        
        # create the tray menu
        if not window.windowIcon().isNull():
            menu   = QMenu(window)
            action = menu.addAction('Quit')
            action.triggered.connect( window.close )
            
            # create the tray icon
            tray_icon = QSystemTrayIcon(window)
            tray_icon.setObjectName('trayIcon')
            tray_icon.setIcon(window.windowIcon())
            tray_icon.setContextMenu(menu)
            tray_icon.setToolTip(data['app'].applicationName())
            tray_icon.show()
        
        return data['app'].exec_()
    
    return 0

def setup( applicationName,
           applicationType = None,
           style = 'plastique',
           splash = '',
           splashType = None,
           splashTextColor = 'white',
           splashTextAlign = Qt.AlignLeft | Qt.AlignBottom ):
    """
    Wrapper system for the QApplication creation process to handle all proper
    pre-application setup.  This method will verify that there is no application
    running, creating one if necessary.  If no application is created, a None
    value is returned - signaling that there is already an app running.  If you
    need to specify your own QApplication subclass, you can do so through the 
    applicationType parameter.
    
    :note       This method should always be used with the exec_ method to 
                handle the post setup process.
    
    :param      applicationName | <str>
                applicationType | <subclass of QApplication> || None
                style    | <str> || <QStyle> | style to use for the new app
                splash   | <str> | filepath to use for a splash screen
                splashType   | <subclass of QSplashScreen> || None
                splashTextColor   | <str> || <QColor>
                splashTextAlign   | <Qt.Alignment>
    
    :usage      |import projexui
                |
                |def main(argv):
                |   # initialize the application
                |   data = projexui.setup()
                |   
                |   # do some initialization code
                |   window = MyWindow()
                |   window.show()
                |   
                |   # execute the application
                |   projexui.exec_(window, data)
    
    :return     { <str> key: <variant> value, .. }
    """
    output = {}
    
    # check to see if there is a qapplication running
    if ( not QApplication.instance() ):
        # make sure we have a valid QApplication type
        if ( applicationType is None ):
            applicationType = QApplication
        
        app = applicationType([applicationName])
        app.setApplicationName(applicationName)
        app.setStyle(style)
        
        # utilized with the projexui.config.xschemeconfig
        app.setProperty('useScheme', wrapVariant(True))
        output['app'] = app
    
    # create a new splash screen if desired
    if ( splash ):
        if ( not splashType ):
            splashType = XLoggerSplashScreen
        
        pixmap = QPixmap(splash)
        screen = splashType(pixmap)
        
        screen.setTextColor(QColor(splashTextColor))
        screen.setTextAlignment(splashTextAlign)
        screen.show()
        
        QApplication.instance().processEvents()
        
        output['splash'] = screen
    
    return output

def topWindow():
    """
    Returns the very top window for all Qt purposes.
    
    :return     <QWidget> || None
    """
    window = QApplication.instance().activeWindow()
    parent = window.parent()
    
    while ( parent ):
        window = parent
        parent = window.parent()
        
    return window

def testWidget( widgetType ):
    """
    Creates a new instance for the widget type, settings its properties \
    to be a dialog and parenting it to the base window.
    
    :param      widgetType  | <subclass of QWidget>
    """
    window = QApplication.instance().activeWindow()
    widget = widgetType(window)
    widget.setWindowFlags( Qt.Dialog )
    widget.show()
    
    return widget

def uiFile( modulefile, inst ):
    """
    Returns the ui file for the given instance and module file.
    
    :param      moduleFile | <str>
                inst       | <QWidget>
    
    :return     <str>
    """
    clsname     = inst.__class__.__name__.lower()
    basepath    = os.path.dirname(str(modulefile))
    uifile      = os.path.join(basepath, 'ui/%s.ui' % clsname)
    return uifile