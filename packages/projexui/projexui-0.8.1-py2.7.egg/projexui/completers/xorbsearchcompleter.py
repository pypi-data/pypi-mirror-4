#!/usr/bin/python

""" 
Defines a completer for searching ORB records and returning the resulting
matches as a completion, similar to the hints provided during a google search.
"""

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintanence information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

#----------------------------------------------------------

from projexui.qt.QtCore import Qt, SIGNAL
from projexui.qt.QtGui import QCompleter,\
                              QStringListModel

class XOrbSearchCompleter(QCompleter):
    def __init__( self, tableType, widget ):
        super(XOrbSearchCompleter, self).__init__(widget)
        
        # set default properties
        self.setModel(QStringListModel(self))
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        
        # define custom properties
        self._currentRecord = None
        self._records   = []
        self._tableType = tableType
        self._baseQuery = None
        self._order     = None
        self._cache     = {}
        self._limit     = 10 # limited number of search results
        self._pywidget  = widget # need to store the widget as the parent
                                 # to avoid pyside crashing - # EKH 02/01/13
    
    def baseQuery(self):
        """
        Returns the base query that is used for filtering these results.
        
        :return     <orb.Query> || None
        """
        return self._baseQuery
    
    def currentRecord(self):
        """
        Returns the current record based on the active index from the model.
        
        :return     <orb.Table> || None
        """
        completion = str(self._pywidget.text())
        options    = map(str, self.model().stringList())
        
        try:
            index = options.index(completion)
        except ValueError:
            return None
        
        return self._records[index]
    
    def eventFilter(self, object, event):
        """
        Sets the completion prefor this instance, triggering a search query
        for the search query.
        
        :param      prefix | <str>
        """
        result = super(XOrbSearchCompleter, self).eventFilter(object, event)
        
        # update the search results
        if event.type() == event.KeyPress:
            table   = self.tableType()
            search  = str(self._pywidget.text())
            if search in self._cache:
                records = self._cache[search]
            else:
                records = table.select(where = self.baseQuery(),
                                       order = self.order(),
                                       limit = self.limit())
                records = list(records.search(search))
                self._cache[search] = records
                
            self._records = records
            self.model().setStringList(map(str, self._records))
        
        return result
        
    def limit(self):
        """
        Returns the limit for the search results for this instance.
        
        :return     <int>
        """
        return self._limit
    
    def order(self):
        """
        Returns the order that the results will be returned from the search.
        
        :return     [(<str> columnName, <str> asc|desc), ..]
        """
        return self._order
    
    def setBaseQuery(self, query):
        """
        Sets the base query for this completer to the inputed query.
        
        :param      query | <orb.Query>
        """
        self._baseQuery = query
    
    def setLimit(self, limit):
        """
        Sets the limit of results to be pulled for this instance.
        
        :param      limit | <int>
        """
        self._limit = limit
    
    def setOrder(self, order):
        """
        Sets the order for this search to the inputed order.
        
        :param      order | [(<str> columnName, <str> asc|desc), ..] || None
        """
        self._order = order
    
    def setTableType(self, tableType):
        """
        Sets the table type for this instance to the inputed type.
        
        :param      tableType | <subclass of orb.Table>
        """
        self._tableType = tableType
    
    def tableType(self):
        """
        Returns the table type that will be used for this completion mechanism.
        
        :return     <subclass of orb.Table>
        """
        return self._tableType