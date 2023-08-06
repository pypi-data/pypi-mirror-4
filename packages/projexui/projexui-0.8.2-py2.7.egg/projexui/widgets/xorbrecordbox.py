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


#------------------------------------------------------------------------------

import logging

from projexui.qt import Signal, Property, PyObject, Slot

from projexui.widgets.xcombobox import XComboBox

logger = logging.getLogger(__name__)

try:
    from orb import Orb
except ImportError:
    logger.warning('Could not import the ORB library.')
    Orb = None

class XOrbRecordBox(XComboBox):
    """ Defines a combo box that contains records from the ORB system. """
    currentRecordChanged = Signal(PyObject)
    
    def __init__( self, parent = None ):
        super(XOrbRecordBox, self).__init__( parent )
        
        # define custom properties
        self._records           = []
        self._tableTypeName     = ''
        self._tableLookupIndex  = ''
        self._tableType         = None
        self._query             = None
        self._iconMapper        = None
        self._labelMapper       = str
        self._required          = True
        self._first             = True
        
        # create connections
        self.currentIndexChanged.connect( self.emitCurrentRecordChanged )
    
    def checkedRecords( self ):
        """
        Returns a list of the checked records from this combo box.
        
        :return     [<orb.Table>, ..]
        """
        indexes = self.checkedIndexes()
        return [self._records[index] for index in indexes]
    
    def currentRecord( self ):
        """
        Returns the record found at the current index for this combo box.
        
        :rerturn        <orb.Table> || None
        """
        index = self.currentIndex()
        
        if ( not self.isRequired() ):
            index -= 1
        
        if ( 0 <= index and index < len(self._records) ):
            return self._records[index]
        return None
    
    def emitCurrentRecordChanged( self ):
        """
        Emits the current record changed signal for this combobox, provided \
        the signals aren't blocked.
        """
        if ( not self.signalsBlocked() ):
            self.currentRecordChanged.emit(self.currentRecord())
    
    def iconMapper( self ):
        """
        Returns the icon mapping method to be used for this combobox.
        
        :return     <method> || None
        """
        return self._iconMapper
    
    def init( self ):
        """
        Initializes the records based on the query and other information the
        first time it is needed.
        """
        if ( self._first ):
            self.refresh()
    
    def isRequired( self ):
        """
        Returns whether or not this combo box requires the user to pick a
        selection.
        
        :return     <bool>
        """
        return self._required
    
    def labelMapper( self ):
        """
        Returns the label mapping method to be used for this combobox.
        
        :return     <method> || None
        """
        return self._labelMapper
    
    @Slot(PyObject)
    def lookupRecords(self, record):
        """
        Lookups records based on the inputed record.  This will use the 
        tableLookupIndex property to determine the Orb Index method to
        use to look up records.  That index method should take the inputed
        record as an argument, and return a list of records.
        
        :param      record | <orb.Table>
        """
        table_type = self.tableType()
        if not table_type:
            return
        
        index = getattr(table_type, self.tableLookupIndex(), None)
        if not index:
            return
        
        self.setRecords(index(record))
    
    def query( self ):
        """
        Returns the query used when querying the database for the records.
        
        :return     <Query> || None
        """
        return self._query
    
    def records( self ):
        """
        Returns the record list that ist linked with this combo box.
        
        :return     [<orb.Table>, ..]
        """
        if ( self._records is not None ):
            return self._records
        
        tableType = self.tableType()
        if ( not tableType ):
            return []
        
        self._records = list(tableType.select(where = self.query()))
        return self._records
    
    def refresh( self ):
        """
        Refreshs the current user interface to match the latest settings.
        """
        self._first     = False
        records         = self.records()
        label_mapper    = self.labelMapper()
        icon_mapper     = self.iconMapper()
        use_dummy       = not (self.isRequired() or self.isCheckable())
        
        self.blockSignals(True)
        self.clear()
        
        if ( use_dummy ):
            self.addItem('')
        
        self.addItems(map(label_mapper, records))
        
        if ( icon_mapper ):
            start = 0
            if ( use_dummy ):
                start = 1
            
            for i in range(start, len(records) + start):
                self.setItemIcon(i, icon_mapper(records[i - start]))
        
        self.blockSignals(False)
    
    def setCheckedRecords( self, records ):
        """
        Sets the checked off records to the list of inputed records.
        
        :param      records | [<orb.Table>, ..]
        """
        self.init()
        
        indexes = []
        
        for record in records:
            try:
                index = self._records.index(record)
            except ValueError:
                continue
            
            indexes.append(index)
        
        self.setCheckedIndexes(indexes)
    
    def setCurrentRecord( self, record ):
        """
        Sets the index for this combobox to the inputed record instance.
        
        :param      record      <orb.Table>
        
        :return     <bool> success
        """
        self.init()
        
        if ( not record in self._records ):
            return False
        
        index = self._records.index(record)
        if ( not self.isRequired() ):
            index += 1
        
        self.setCurrentIndex(index)
        return True
    
    def setIconMapper( self, mapper ):
        """
        Sets the icon mapping method for this combobox to the inputed mapper. \
        The inputed mapper method should take a orb.Table instance as input \
        and return a QIcon as output.
        
        :param      mapper | <method> || None
        """
        self._iconMapper = mapper
    
    def setLabelMapper( self, mapper ):
        """
        Sets the label mapping method for this combobox to the inputed mapper.\
        The inputed mapper method should take a orb.Table instance as input \
        and return a string as output.
        
        :param      mapper | <method>
        """
        self._labelMapper = mapper
    
    def setQuery( self, query ):
        """
        Sets the query for this record box for generating records.
        
        :param      query | <Query> || None
        """
        self._query     = query
        self._records   = None
    
    def setRecords( self, records ):
        """
        Sets the records on this combobox to the inputed record list.
        
        :param      records | [<orb.Table>, ..]
        """
        self._records = list(records)
        self.refresh()
    
    def setRequired( self, state ):
        """
        Sets the required state for this combo box.  If the column is not
        required, a blank record will be included with the choices.
        
        :param      state | <bool>
        """
        self._required = state
    
    def setTableLookupIndex(self, index):
        """
        Sets the name of the index method that will be used to lookup
        records for this combo box.
        
        :param    index | <str>
        """
        self._tableLookupIndex = str(index)
    
    def setTableType( self, tableType ):
        """
        Sets the table type for this record box to the inputed table type.
        
        :param      tableType | <orb.Table>
        """
        self._tableType     = tableType
        self._records       = None
        if tableType:
            self._tableTypeName = tableType.schema().name()
        else:
            self._tableTypeName = ''
    
    def setTableTypeName(self, name):
        """
        Sets the table type name for this record box to the inputed name.
        
        :param      name | <str>
        """
        self._tableTypeName = str(name)
        self._tableType = None
        self._records = None
    
    def setVisible( self, state ):
        """
        Updates the records for this instance based on it being visible.
        
        :param      state | <bool>
        """
        super(XOrbRecordBox, self).setVisible(state)
        
        if ( state ):
            self.init()
    
    def tableLookupIndex(self):
        """
        Returns the name of the index method that will be used to lookup
        records for this combo box.
        
        :return     <str>
        """
        return self._tableLookupIndex
    
    def tableType( self ):
        """
        Returns the table type for this instance.
        
        :return     <subclass of orb.Table> || None
        """
        if not self._tableType and self._tableTypeName:
            self._tableType = Orb.instance().model(str(self._tableTypeName))
        return self._tableType
    
    def tableTypeName(self):
        """
        Returns the table type name that is set for this combo box.
        
        :return     <str>
        """
        return self._tableTypeName
    
    x_required          = Property(bool, isRequired, setRequired)
    x_tableTypeName     = Property(str, tableTypeName, setTableTypeName)
    x_tableLookupIndex  = Property(str, tableLookupIndex, setTableLookupIndex)
    
__designer_plugins__ = [XOrbRecordBox]

# register save and load methods
import projexui
projexui.registerWidgetValue(XOrbRecordBox,
                lambda w: w.currentRecord(),
                lambda w, v: w.setCurrentRecord(v))