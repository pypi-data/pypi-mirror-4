""" Defines the grouping class for the orb tree widget. """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintenance information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

from projexui.qt.QtCore import QSize, Qt
from projexui.qt.QtGui  import QTreeWidgetItem, QIcon, QApplication

import projexui.resources

from orb import RecordSet

class XOrbGroupItem( QTreeWidgetItem ):
    def __init__( self, parent, groupName, records = None ):
        super(XOrbGroupItem, self).__init__(parent)
        
        # define custom properties
        self._loaded    = False
        self._recordSet = None
        
        # set local properties
        self.setText(0, str(groupName))
        self.setFirstColumnSpanned(True)
        self.setChildIndicatorPolicy(self.ShowIndicator)
        self.setSizeHint(0, QSize(150, 20))
        
        self.updateIcon()
        
        # load the records for this group
        if ( isinstance(records, RecordSet) ):
            self.setRecordSet(records)
        elif ( type(records) in (dict, list, tuple) ):
            self.loadRecords(records)
    
    def loadRecords( self, records ):
        """
        Loads the inputed records as children to this item.
        
        :param      records | [<orb.Table>, ..] || {<str> sub: <variant>, .. }
        """
        self.setChildIndicatorPolicy(self.DontShowIndicatorWhenChildless)
        
        self._loaded = True
        
        # load a child set of groups
        if ( type(records) == dict ):
            cls = self.treeWidget().createGroupItem
            for subgroup, subrecords in records.items():
                cls(self, subgroup, subrecords)
        
        # load records
        else:
            cls = self.treeWidget().createRecordItem
            for record in records:
                cls(self, record)
    
    def load( self ):
        """
        Loads the records from the query set linked with this item.
        """
        if ( self._loaded ):
            return
        
        rset = self.recordSet()
        
        QApplication.setOverrideCursor(Qt.WaitCursor)
        
        if ( not rset ):
            self.loadRecords([])
        elif ( rset.isGrouped() ):
            self.loadRecords(rset.grouped())
        else:
            self.loadRecords(rset.all())
        
        QApplication.restoreOverrideCursor()
    
    def recordSet( self ):
        """
        Returns the record set that is linked with this grouping item.
        
        :return     <orb.RecordSet>
        """
        return self._recordSet
    
    def setRecordSet( self, recordSet ):
        """
        Sets the record set that is linked with this grouping item.
        
        :param      recordSet | <orb.RecordSet>
        """
        self._recordSet = recordSet
    
    def updateIcon( self, recursive = False ):
        """
        Updates the icon to reflect the expanded state of this item.
        """
        if ( self.isExpanded() ):
            icon = projexui.resources.find('img/folder_open.png')
        else:
            icon = projexui.resources.find('img/folder_close.png')
        
        self.setIcon(0, QIcon(icon))