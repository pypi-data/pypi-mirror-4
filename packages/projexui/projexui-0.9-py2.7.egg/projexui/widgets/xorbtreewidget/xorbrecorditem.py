#!/usr/bin/python

""" [desc] """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintenance information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

from projexui.qt import wrapVariant
from projexui.qt.QtCore   import QSize,\
                                 Qt,\
                                 QDate,\
                                 QDateTime,\
                                 QTime

from projexui.qt.QtGui    import QColor

import datetime

from projex.enum    import enum
from projexui.widgets.xtreewidget import XTreeWidgetItem

XOrbTreeWidget = None
def __lazy_load__():
    global XOrbTreeWidget
    if ( XOrbTreeWidget ):
        return
    
    from projexui.widgets.xorbtreewidget import XOrbTreeWidget

class XOrbRecordItem( XTreeWidgetItem ):
    State = enum('Normal', 'New', 'Removed', 'Modified')
    
    def __init__( self, parent, record ):
        super(XOrbRecordItem, self).__init__(parent)
        
        # sets whether or not this record is loaded
        self._record        = record
        self._loaded        = False
        self._recordState   = XOrbRecordItem.State.Normal
        
        # initialize the item
        self.setSizeHint(0, QSize(120, 20))
        self.setRecord(record)
        
#        if self.treeWidget().isEditable():
#            self.setFlags(self.flags() | Qt.ItemIsEditable)
    
    def addRecordState( self, state ):
        """
        Adds the inputed record state to the set for this item.
        
        :param      state | <XOrbRecordItem.State>
        """
        curr_state = self.recordState()
        self.setRecordState(curr_state | state)
    
    def findItemsByState( self, state ):
        """
        Looks up all the items within this record based on the state.
        
        :param      state | <XOrbRecordItem.State>
        
        :return     [<XOrbRecordItem>, ..]
        """
        out = []
        if ( self.hasRecordState(state) ):
            out.append(self)
        
        for c in range(self.childCount()):
            out += self.child(c).findItemsByState(state)
        
        return out
    
    def hasRecordState( self, state ):
        """
        Returns whether or not this items state contains the inputed state.
        
        :param      state | <XOrbRecordItem.State>
        
        :return     <bool>
        """
        return (self._recordState & state) != 0
    
    def load( self ):
        """
        Loads the children for this record item.
        
        :return     <bool> | changed
        """
        if ( self._loaded ):
            return False
        
        self._loaded = True
        self.setChildIndicatorPolicy(self.DontShowIndicatorWhenChildless)
        return True
    
    def record( self ):
        """
        Returns the record for this item.
        
        :return     <orb.Table>
        """
        return self._record
    
    def recordState( self ):
        """
        Returns the record state for this item.
        
        :return     <XOrbRecordItem.State>
        """
        return self._recordState
    
    def removeRecordState( self, state ):
        """
        Removes the state from this item.
        
        :param      state | <XOrbRecordItem.State>
        """
        curr_state = self.recordState()
        if ( curr_state & state ):
            self.setRecordState(curr_state ^ state)
    
    def setRecord( self, record ):
        """
        Sets the record instance for this item to the inputed record.
        
        :param      record | <orb.Table>
        """
        self._record = record
        self.updateRecordValues()
    
    def setRecordState( self, recordState ):
        """
        Sets the record state for this item to the inputed state.
        
        :param      recordState | <XOrbRecordItem.State>
        """
        self._recordState = recordState
        
        if ( not (self.treeWidget() and self.treeWidget().isColored()) ):
            return
        
        # determine the color for the item based on the state
        if ( recordState & XOrbRecordItem.State.Removed ):
            clr = self.treeWidget().colorSet().color('RecordRemoved')
        elif ( recordState & XOrbRecordItem.State.New ):
            clr = self.treeWidget().colorSet().color('RecordNew')
        elif ( recordState & XOrbRecordItem.State.Modified ):
            clr = self.treeWidget().colorSet().color('RecordModified')
        else:
            clr = QColor()
        
        # set the color based on the record state
        clr = QColor(clr)
        clr.setAlpha(40)
        for c in range(self.treeWidget().columnCount()):
            self.setBackground(c, clr)
    
    def updateRecordValues( self ):
        """
        Updates the ui to show the latest record values.
        """
        record = self.record()
        if ( not record ):
            return
        
        # update the record information
        __lazy_load__()
        tree = self.treeWidget()
        if ( not isinstance(tree, XOrbTreeWidget) ):
            return
        
        for column in record.schema().columns():
            c = tree.column(column.displayName())
            if ( c == -1 ):
                continue
            
            value = record.recordValue(column.name())
            
            if ( isinstance(value, datetime.date) ):
                value = QDate(value)
                self.setData(c, Qt.EditRole, wrapVariant(value))
            
            elif ( isinstance(value, datetime.time) ):
                value = QTime(value)
                self.setData(c, Qt.EditRole, wrapVariant(value))
            
            elif ( isinstance(value, datetime.datetime) ):
                value = QDateTime(value)
                self.setData(c, Qt.EditRole, wrapVariant(value))
            
            elif ( type(value) in (float, int) ):
                self.setData(c, Qt.EditRole, wrapVariant(value))
            
            elif ( value is not None ):
                self.setText(c, str(value))
            
            self.setSortData(c, value)
        
        # add custom columns based on the tree mappers
        for columnName, mapper in tree.columnMappers().items():
            c     = tree.column(columnName)
            value = mapper(record)
            self.setText(c, value)
        
        # update the record state information
        if ( not record.isRecord() ):
            self.addRecordState(XOrbRecordItem.State.New)
        
        elif ( record.isModified() ):
            self.addRecordState(XOrbRecordItem.State.Modified)
    
    def updateIcon( self ):
        """
        Updates the icon based on if this record is expanded or collapsed.
        """
        pass