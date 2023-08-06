#!/usr/bin python

""" Defines the menu that will be used when a ViewPanel is being modified. """

# define authorship information
__authors__     = ['Eric Hulser']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2011, Projex Software'

# maintanence information
__maintainer__  = 'Projex Software'
__email__       = 'team@projexsoftware.com'

from projexui.qt import wrapVariant, unwrapVariant
from projexui.qt.QtCore import Qt
from projexui.qt.QtGui import QActionGroup,\
                              QMenu,\
                              QIcon,\
                              QInputDialog,\
                              QLineEdit

from projexui import resources

class XViewPanelMenu( QMenu ):
    _instance = None
    
    def __init__( self, viewWidget, interfaceMode = False ):
        # initialize the super class
        super(XViewPanelMenu, self).__init__( viewWidget )
        
        # define custom properties
        self._viewWidget    = viewWidget
        self._currentPanel  = None
        self._interfaceMenu = None
        self._groupingMenu  = None
        self._panelGroup    = QActionGroup(self)
        self._groupingGroup = QActionGroup(self)
        
        # initialize the menu
        if ( not interfaceMode ):
            self.setTitle( 'Panel Options' )
            
            # create view grouping options
            self._groupingMenu = self.addMenu('Set Group')
            
            act = self._groupingMenu.addAction('No Grouping')
            act.setData(wrapVariant(0))
            act.setCheckable(True)
            self._groupingMenu.addSeparator()
            self._groupingGroup.addAction(act)
            
            for i in range(1, 6):
                act = self._groupingMenu.addAction('Group %i' % i)
                act.setData(wrapVariant(i))
                act.setCheckable(True)
                
                self._groupingGroup.addAction(act)
            
            self._groupingMenu.triggered.connect(self.assignGroup)
            
            self.addSeparator()
            
            act = self.addAction('Split Panel Left/Right')
            act.setIcon(QIcon(resources.find('img/view/split_horizontal.png')))
            act.triggered.connect( self.splitHorizontal )
            
            act = self.addAction('Split Panel Top/Bottom')
            act.setIcon(QIcon(resources.find('img/view/split_vertical.png')))
            act.triggered.connect( self.splitVertical )
            
#            act = self.addAction('Previous Panel Tab')
#            act.setIcon(QIcon(resources.find('img/view/back.png')))
#            act.triggered.connect( self.gotoPrevious )
#            
#            act = self.addAction('Next Panel Tab')
#            act.setIcon(QIcon(resources.find('img/view/forward.png')))
#            act.triggered.connect( self.gotoNext )
            
            self.addSeparator()
            
            act = self.addAction('Rename Tab')
            act.setIcon(QIcon(resources.find('img/edit.png')))
            act.triggered.connect( self.renamePanel )
            
            act = self.addAction('Detach Tab')
            act.setIcon(QIcon(resources.find('img/view/detach.png')))
            act.triggered.connect( self.detachPanel )
            
            act = self.addAction('Detach Tab (as a Copy)')
            act.setIcon(QIcon(resources.find('img/view/detach_copy.png')))
            act.triggered.connect( self.detachPanelCopy )
            
            act = self.addAction('Close Tab')
            act.setIcon(QIcon(resources.find('img/view/tab_remove.png')))
            act.triggered.connect( self.closeView )
            
            self.addSeparator()
            
#            act = self.addAction('Maximize Panel')
#            act.setIcon(QIcon(resources.find('img/view/maximize.png')))
#            act.triggered.connect( self.maximizePanel )
            
            act = self.addAction('Close Panel (Closes All Tabs)')
            act.setIcon(QIcon(resources.find('img/view/close.png')))
            act.triggered.connect( self.closePanel )
            
            act = self.addAction('Reset View (Closes All Panels)')
            act.setIcon(QIcon(resources.find('img/view/reset.png')))
            act.triggered.connect( self.reset )
            
            self.addSeparator()
            
            # create pane options menu
            set_tab_menu = self.addMenu( 'Switch View' )
            for viewType in viewWidget.viewTypes():
                act = set_tab_menu.addAction(viewType.viewName())
                act.setCheckable(True)
                self._panelGroup.addAction(act)
            set_tab_menu.triggered.connect( self.swapTabType )
            
            self._interfaceMenu = XViewPanelMenu(viewWidget, True)
            self.addMenu(self._interfaceMenu)
            
        else:
            self.setTitle( 'Add View' )
            
            for viewType in viewWidget.viewTypes():
                act = self.addAction(viewType.viewName())
                act.setIcon(QIcon(viewType.viewIcon()))
                
            self.triggered.connect( self.addView )
            self.addSeparator()
    
    def addPanel( self ):
        panel = self.currentPanel()
        if ( panel is not None ):
            return panel.addPanel()
        return None
    
    def addView( self, action ):
        panel = self.currentPanel()
        
        if ( panel is None ):
            return False
        
        viewType = self._viewWidget.viewType(action.text())
        return panel.addView(viewType)
    
    def assignGroup( self, action ):
        """
        Assigns the group for the given action to the current view.
        
        :param      action | <QAction>
        """
        grp  = unwrapVariant(action.data())
        view = self._currentPanel.currentWidget()
        view.setViewingGroup(grp)
    
    def closePanel( self ):
        """
        Closes the current panel within the view widget.
        """
        panel = self.currentPanel()
        if ( panel is not None ):
            return panel.closePanel()
        return False
    
    def closeView( self ):
        """
        Closes the current view within the panel.
        """
        panel = self.currentPanel()
        if ( panel is not None ):
            return panel.closeView()
        return False
    
    def currentPanel( self ):
        """
        Returns the current panel widget.
        
        :return     <XViewPanel>
        """
        return self._currentPanel
    
    def detachPanel( self ):
        """
        Detaches the current panel as a floating window.
        """
        from projexui.widgets.xviewwidget import XViewDialog
        
        dlg = XViewDialog(self._viewWidget, self._viewWidget.viewTypes())
        size = self._currentPanel.size()
        dlg.viewWidget().currentPanel().snagViewFromPanel(self._currentPanel)
        dlg.resize(size)
        dlg.show()
    
    def detachPanelCopy( self ):
        """
        Detaches the current panel as a floating window.
        """
        from projexui.widgets.xviewwidget import XViewDialog
        
        dlg = XViewDialog(self._viewWidget, self._viewWidget.viewTypes())
        size = self._currentPanel.size()
        view = self._currentPanel.currentWidget()
        
        # duplicate the current view
        if ( view ):
            new_view = view.duplicate(dlg.viewWidget().currentPanel())
            view_widget = dlg.viewWidget()
            view_panel = view_widget.currentPanel()
            view_panel.addTab(new_view, new_view.windowTitle())
            
        dlg.resize(size)
        dlg.show()
        
    def gotoNext( self ):
        """
        Goes to the next panel tab.
        """
        index = self._currentPanel.currentIndex() + 1
        if ( self._currentPanel.count() == index ):
            index = 0
            
        self._currentPanel.setCurrentIndex(index)
    
    def gotoPrevious( self ):
        """
        Goes to the previous panel tab.
        """
        index = self._currentPanel.currentIndex() - 1
        if ( index < 0 ):
            index = self._currentPanel.count() - 1
        
        self._currentPanel.setCurrentIndex(index)
    
    def newPanelTab( self ):
        """
        Creates a new panel with a copy of the current widget.
        """
        view = self._currentPanel.currentWidget()
        
        # duplicate the current view
        if ( view ):
            new_view = view.duplicate(self._currentPanel)
            self._currentPanel.addTab(new_view, new_view.windowTitle())
    
    def renamePanel( self ):
        """
        Prompts the user for a custom name for the current panel tab.
        """
        index = self._currentPanel.currentIndex()
        title = self._currentPanel.tabText(index)
        
        new_title, accepted = QInputDialog.getText( self,
                                                    'Rename Tab',
                                                    'Name:',
                                                    QLineEdit.Normal,
                                                    title )
        
        if ( accepted ):
            widget = self._currentPanel.currentWidget()
            widget.setWindowTitle(new_title)
            self._currentPanel.setTabText(index, new_title)
    
    def reset( self ):
        """
        Clears the current views from the system
        """
        self._viewWidget.reset()
    
    def setCurrentPanel( self, panel ):
        self._currentPanel = panel
        
        # update the current tab based on what view type it is
        viewType = ''
        grp = -1
        if ( panel is not None and panel.currentWidget() ):
            viewType = panel.currentWidget().viewName()
            grp = panel.currentWidget().viewingGroup()
        
        self._panelGroup.blockSignals(True)
        for act in self._panelGroup.actions():
            act.setChecked(viewType == act.text())
        self._panelGroup.blockSignals(False)
        
        self._groupingGroup.blockSignals(True)
        for act in self._groupingGroup.actions():
            act.setChecked(grp == unwrapVariant(act.data()))
        self._groupingGroup.blockSignals(False)
        
        if ( self._groupingMenu ):
            self._groupingMenu.setEnabled(grp != -1)
        
        if ( self._interfaceMenu ):
            self._interfaceMenu.setCurrentPanel(panel)
        
    def splitVertical( self ):
        panel = self.currentPanel()
        if ( panel is not None ):
            return panel.splitVertical()
        return None
        
    def splitHorizontal( self ):
        panel = self.currentPanel()
        if ( panel is not None ):
            return panel.splitHorizontal()
        return None
    
    def swapTabType( self, action ):
        """
        Swaps the current tab view for the inputed action's type.
        
        :param      action | <QAction>
        """
        # for a new tab, use the add tab slot
        if ( not self._currentPanel.count() ):
            self.addView(action)
            return
        
        # make sure we're not trying to switch to the same type
        viewType = self._viewWidget.viewType(action.text())
        view = self._currentPanel.currentWidget()
        if ( type(view) == viewType ):
            return
        
        # create a new view and close the old one
        self._currentPanel.setUpdatesEnabled(False)
        
        # create the new view
        new_view    = viewType.createInstance(self._currentPanel)
        index       = self._currentPanel.currentIndex()
        
        # cleanup the view
        view.destroyInstance(view)
        
        # add the new view
        self._currentPanel.insertTab(index - 1,
                                     new_view, 
                                     new_view.windowTitle())
        
        self._currentPanel.setUpdatesEnabled(True)