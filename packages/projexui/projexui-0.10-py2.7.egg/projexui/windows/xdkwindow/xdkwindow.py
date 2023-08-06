#!/usr/bin/python

""" Creates reusable Qt window components. """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintanence information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

#---------------------------------------------------------------------------

import os.path

from projexui.qt.QtCore import Qt, QDir, QUrl

from projexui.qt.QtGui import QApplication,\
                              QFileDialog,\
                              QMainWindow,\
                              QTreeWidgetItem

from projexui.qt.QtWebKit import QWebView, \
                                 QWebPage

import projexui

from projexui.windows.xdkwindow.xdkitem         import XdkItem, XdkEntryItem
#from projexui.windows.xdkwindow.xcontentwidget  import XContentWidget

SEARCH_HTML = """
<html>
    <head>
        <style>
            * { outline: none !important; }
            
            body {
                margin: 0.5em;
                padding: 0.5em;
                font-family: Arial, Verdana !important;
                font-size: 14px !important;
                width:100%%;
                height:95%%;
            }

            table   { font-size: 14px; } 
            h1      { font-size: 20px; }
            h2      { font-size: 16px; }
            h3      { font-size: 14px; }
            small   { font-size: 11px; color: gray; }
            
            a {
                color: rgb(40,100,150);
                font-weight: bold;
                text-decoration: none;
            }
            a:hover {
                color: rgb(60,120,250);
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        %s
    </body>
</html>
"""

class XdkWindow(QMainWindow):
    """ """
    def __init__( self, parent = None ):
        super(XdkWindow, self).__init__( parent )
        
        # load the user interface
        projexui.loadUi(__file__, self)
        
        # define custom properties
        self._currentContentsIndex = -1
        
        # set default properties
        self.uiContentsTREE.sortByColumn(0, Qt.AscendingOrder)
        self.setAttribute( Qt.WA_DeleteOnClose )
        self.uiFindNextBTN.setDefaultAction(self.uiFindNextACT)
        self.uiFindPrevBTN.setDefaultAction(self.uiFindPrevACT)
        self.uiFindWIDGET.setVisible(False)
        self.uiIndexTXT.setHint('filter index by...')
        self.uiSearchWEB.page().setLinkDelegationPolicy(
                                            QWebPage.DelegateAllLinks)
        
        
        self.refreshUi()
        
        # connect widgets
        self.uiContentsTAB.currentChanged.connect(self.refreshUi)
        self.uiContentsTAB.tabCloseRequested.connect(self.closeContentsWidget)
        self.uiContentsTREE.itemExpanded.connect(self.loadItem)
        self.uiContentsTREE.itemSelectionChanged.connect(self.refreshContents)
        self.uiSearchTXT.returnPressed.connect(self.search)
        self.uiSearchWEB.linkClicked.connect(self.gotoUrl)
        self.uiIndexTXT.textChanged.connect(self.filterIndex)
        self.uiIndexTREE.itemSelectionChanged.connect(self.refreshFromIndex)
        
        # connect find actions
        self.uiBackACT.triggered.connect(self.goBack)
        self.uiForwardACT.triggered.connect(self.goForward)
        self.uiHomeACT.triggered.connect(self.goHome )
        self.uiFindTXT.textChanged.connect( self.findNext )
        self.uiFindTXT.returnPressed.connect( self.findNext )
        self.uiFindNextACT.triggered.connect( self.findNext )
        self.uiFindPrevACT.triggered.connect( self.findPrev )
        self.uiFindACT.triggered.connect(self.showFind)
        self.uiFindCloseBTN.clicked.connect(self.uiFindWIDGET.hide)
        self.uiCopyTextACT.triggered.connect( self.copyText )
        
        # connect zoom actions
        self.uiZoomResetACT.triggered.connect( self.zoomReset )
        self.uiZoomInACT.triggered.connect( self.zoomIn )
        self.uiZoomOutACT.triggered.connect( self.zoomOut )
        
        # connect file actions
        self.uiLoadACT.triggered.connect( self.loadFilename )
        self.uiNewTabACT.triggered.connect( self.addContentsWidget )
        self.uiCloseTabACT.triggered.connect( self.closeContentsWidget )
        self.uiQuitACT.triggered.connect( self.close )
    
    def addContentsWidget( self ):
        """
        Adds a new contents widget tab into the contents tab.
        
        :return     <QWebView>
        """
        curr_widget = self.currentContentsWidget()
        widget = QWebView(self)
            
        self.uiContentsTAB.blockSignals(True)
        self.uiContentsTAB.addTab(widget, 'SDK')
        self.uiContentsTAB.setCurrentIndex(self.uiContentsTAB.count() - 1)
        self.uiContentsTAB.blockSignals(False)
        
        self._currentContentsIndex = self.uiContentsTAB.count() - 1
        
        if ( curr_widget ):
            widget.setUrl(curr_widget.url())
        
        widget.titleChanged.connect(self.refreshUi)
        
        return widget
    
    def closeContentsWidget( self ):
        """
        Closes the current contents widget.
        """
        widget = self.currentContentsWidget()
        if ( not widget ):
            return
            
        widget.close()
        widget.setParent(None)
        widget.deleteLater()
    
    def copyText( self ):
        """
        Copies the selected text to the clipboard.
        """
        widget = self.uiContentsTAB.currentWidget()
        view = widget.findChildren(QWebView)[0]
        QApplication.clipboard().setText(view.page().selectedText())
    
    def currentContentsIndex( self ):
        """
        Returns the last index used for the contents widgets.
        
        :return     <int>
        """
        return self._currentContentsIndex
    
    def currentContentsWidget( self, autoadd = False ):
        """
        Returns the current contents widget based on the cached index.  If \
        no widget is specified and autoadd is True, then a new widget will \
        be added to the tab.
        
        :param      autoadd | <bool>
        
        :return     <QWebView>
        """
        widget = self.uiContentsTAB.widget(self.currentContentsIndex())
        if ( not isinstance(widget, QWebView) ):
            widget = None
        
        if ( not widget and autoadd ):
            widget = self.addContentsWidget()
        
        return widget
    
    def filterIndex( self ):
        """
        Filters the tree items in the index based on the current index text.
        """
        text        = str(self.uiIndexTXT.text()).lower()
        anywhere    = text.startswith('*') and text.endswith('*')
        endswith    = text.startswith('*')
        text        = text.strip('*')
        
        self.uiIndexTREE.setUpdatesEnabled(False)
        self.uiIndexTREE.blockSignals(True)
        
        for i in range(self.uiIndexTREE.topLevelItemCount()):
            item = self.uiIndexTREE.topLevelItem(i)
            title = str(item.text(0)).lower()
            
            if ( not text ):
                item.setHidden(False)
            elif ( anywhere and text in title ):
                item.setHidden(False)
            elif ( endswith and title.endswith(text) ):
                item.setHidden(False)
            elif ( title.startswith(text) ):
                item.setHidden(False)
            else:
                item.setHidden(True)
                
        self.uiIndexTREE.setUpdatesEnabled(True)
        self.uiIndexTREE.blockSignals(False)
    
    def findNext( self ):
        """
        Looks for the previous occurance of the current search text.
        """
        text = self.uiFindTXT.text()
        widget = self.uiContentsTAB.currentWidget()
        view = widget.findChildren(QWebView)[0]
        
        options =  QWebPage.FindWrapsAroundDocument
        
        if ( self.uiCaseSensitiveCHK.isChecked() ):
            options |= QWebPage.FindCaseSensitively
        
        view.page().findText(text, options)
    
    def findPrev( self ):
        """
        Looks for the previous occurance of the current search text.
        """
        text = self.uiFindTXT.text()
        widget = self.uiContentsTAB.currentWidget()
        view = widget.findChildren(QWebView)[0]
        
        options =  QWebPage.FindWrapsAroundDocument
        options |= QWebPage.FindBackward
        
        if ( self.uiCaseSensitiveCHK.isChecked() ):
            options |= QWebPage.FindCaseSensitively
        
        view.page().findText(text, options)
    
    def findXdk( self, name ):
        """
        Looks up the xdk item based on the current name.
        
        :param      name | <str>
        
        :return     <XdkItem> || None
        """
        for i in range(self.uiContentsTREE.topLevelItemCount()):
            item = self.uiContentsTREE.topLevelItem(i)
            if ( item.text(0) == name ):
                return item
        return None
    
    def goBack( self ):
        widget = self.currentContentsWidget()
        if ( widget ):
            widget.page().history().back()
    
    def goForward( self ):
        widget = self.currentContentsWidget()
        if ( widget ):
            widget.page().history().forward()
    
    def goHome( self ):
        widget = self.currentContentsWidget()
        if ( widget ):
            widget.history().goHome()
    
    def gotoUrl( self, url ):
        if ( not QApplication.keyboardModifiers() == Qt.ControlModifier ):
            widget = self.currentContentsWidget(autoadd = True)
        else:
            widget = self.addContentsWidget()
        
        self.uiContentsTAB.setCurrentIndex(self.uiContentsTAB.indexOf(widget))
        widget.setUrl(QUrl(url))
    
    def loadItem( self, item ):
        """
        Loads the inputed item.
        
        :param      item | <QTreeWidgetItem>
        """
        if ( isinstance(item, XdkEntryItem) ):
            item.load()
    
    def loadedFilenames( self ):
        """
        Returns a list of all the xdk files that are currently loaded.
        
        :return     [<str>, ..]
        """
        output = []
        for i in range(self.uiContentsTREE.topLevelItemCount()):
            item = self.uiContentsTREE.topLevelItem(i)
            output.append(str(item.sdkFilename()))
        return output
    
    def loadFilename( self, filename = '' ):
        """
        Loads a new XDK file into the system.
        
        :param      filename | <str>
        
        :return     <bool> | success
        """
        if ( not (filename and isinstance(filename, basestring)) ):
            filename = QFileDialog.getOpenFileName( self,
                                                    'Open XDK File',
                                                    QDir.currentPath(),
                                                    'XDK Files (*.xdk)' )
            
            if type(filename) == tuple:
                filename = str(filename[0])
            
            if ( not filename ):
                return False
        
        if ( not (filename and os.path.exists(filename)) ):
            return False
        
        elif ( filename in self.loadedFilenames() ):
            return False
        
        item = XdkItem(filename)
        
        # add the xdk content item
        self.uiContentsTREE.addTopLevelItem(item)
        
        # add the index list items
        self.uiIndexTREE.blockSignals(True)
        self.uiIndexTREE.setUpdatesEnabled(False)
        for name, url in item.indexlist():
            item = QTreeWidgetItem([name])
            item.setToolTip(0, url)
            self.uiIndexTREE.addTopLevelItem(item)
        self.uiIndexTREE.blockSignals(False)
        self.uiIndexTREE.setUpdatesEnabled(True)
        self.uiIndexTREE.sortByColumn(0, Qt.AscendingOrder)
            
        return True
    
    def refreshFromIndex( self ):
        """
        Refreshes the documentation from the selected index item.
        """
        item = self.uiIndexTREE.currentItem()
        if ( not item ):
            return
        
        self.gotoUrl(item.toolTip(0))
    
    def refreshContents( self ):
        """
        Refreshes the contents tab with the latest selection from the browser.
        """
        item = self.uiContentsTREE.currentItem()
        if ( not isinstance(item, XdkEntryItem) ):
           return
        
        item.load()
        url = item.url()
        if ( url ):
            self.gotoUrl(url)
    
    def refreshUi( self ):
        """
        Refreshes the interface based on the current settings.
        """
        widget      = self.uiContentsTAB.currentWidget()
        is_content  = isinstance(widget, QWebView)
        
        if ( is_content ):
            self._currentContentsIndex = self.uiContentsTAB.currentIndex()
            history = widget.page().history()
        else:
            history = None
        
        self.uiBackACT.setEnabled(is_content and history.canGoBack())
        self.uiForwardACT.setEnabled(is_content and history.canGoForward())
        self.uiHomeACT.setEnabled(is_content)
        self.uiNewTabACT.setEnabled(is_content)
        self.uiCopyTextACT.setEnabled(is_content)
        self.uiCloseTabACT.setEnabled(is_content and
                                      self.uiContentsTAB.count() > 2)
        
        for i in range(1, self.uiContentsTAB.count()):
            widget = self.uiContentsTAB.widget(i)
            self.uiContentsTAB.setTabText(i, widget.title())
    
    def search( self ):
        """
        Looks up the current search terms from the xdk files that are loaded.
        """
        QApplication.instance().setOverrideCursor(Qt.WaitCursor)
        
        terms = str(self.uiSearchTXT.text())
        
        html = []
        
        entry_html = '<a href="%(url)s">%(title)s</a><br/>'\
                     '<small>%(url)s</small>'
        
        for i in range(self.uiContentsTREE.topLevelItemCount()):
            item = self.uiContentsTREE.topLevelItem(i)
            
            results = item.search(terms)
            results.sort(lambda x, y: cmp(y['strength'], x['strength']))
            for item in results:
                html.append( entry_html % item )
        
        if ( not html ):
            html.append('<b>No results were found for %s</b>' % terms)
        
        self.uiSearchWEB.setHtml(SEARCH_HTML % '<br/><br/>'.join(html))
        
        QApplication.instance().restoreOverrideCursor()
    
    def showFind( self ):
        self.uiFindWIDGET.show()
        self.uiFindTXT.setFocus()
        self.uiFindTXT.selectAll()
    
    def zoomIn( self ):
        widget = self.uiContentsTAB.currentWidget()
        view = widget.findChildren(QWebView)[0]
        view.setZoomFactor(view.zoomFactor() + 0.1)
    
    def zoomOut( self ):
        widget = self.uiContentsTAB.currentWidget()
        view = widget.findChildren(QWebView)[0]
        view.setZoomFactor(view.zoomFactor() - 0.1)
    
    def zoomReset( self ):
        widget = self.uiContentsTAB.currentWidget()
        view = widget.findChildren(QWebView)[0]
        view.setZoomFactor(1)
    
    @staticmethod
    def browse( parent, filename = '' ):
        """
        Creates a new XdkWidnow for browsing an XDK file.
        
        :param      parent      | <QWidget>
                    filename    | <str>
        """
        dlg = XdkWindow(parent)
        dlg.show()
        
        if ( filename ):
            dlg.loadFilename(filename)