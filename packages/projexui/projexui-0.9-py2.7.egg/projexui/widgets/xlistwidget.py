#!/usr/bin/python

""" 
Extends the base QTreeWidget class with additional methods.
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

#------------------------------------------------------------------------------

import re
import weakref

from projexui.qt        import Slot
from projexui.qt.QtGui  import QListWidget,\
                               QListWidgetItem

import projex.text
from projexui import resources

DATATYPE_FILTER_EXPR = re.compile('((\w+):([\w,\*]+|"[^"]+"?))')

class XListWidgetItem(QListWidgetItem):
    def __init__( self, *args ):
        super(XListWidgetItem, self).__init__(*args)
        
        self._filterData = {}
    
    def filterData( self, key ):
        """
        Returns the filter data for the given key.
        
        :param      key | <str>
        
        :return     <str>
        """
        return self._filterData.get(key, '')
    
    def setFilterData( self, key, value ):
        """
        Sets the filtering information for the given key to the inputed value.
        
        :param      key | <str>
                    value | <str>
        """
        self._filterData[str(key)] = str(value)

#------------------------------------------------------------------------------

class XListWidget(QListWidget):
    """ Advanced QTreeWidget class. """
    
    __designer_icon__ = resources.find('img/ui/listbox.png')
    
    def __init__( self, *args ):
        super(XListWidget, self).__init__(*args)
        
        self._filteredDataTypes = []
    
    def __filterItems( self, 
                       terms, 
                       autoExpand = True, 
                       caseSensitive = False ):
        """
        Filters the items in this tree based on the inputed keywords.
        
        :param      terms           | {<str> dataType: [<str> term, ..], ..}
                    autoExpand      | <bool>
                    caseSensitive   | <bool>
        
        :return     <bool> | found
        """
        found = False
        items = []
        
        # collect the items to process
        for i in range(self.count()):
            items.append(self.item(i))
        
        for item in items:
            # if there is no filter keywords, then all items will be visible
            if ( not any(terms.values()) ):
                found = True
                item.setHidden(False)
            
            else:
                # match all generic keywords
                generic         = terms.get('*', [])
                generic_found   = dict((key, False) for key in generic)
                
                # match all specific keywords
                dtype_found  = dict((col, False) for col in terms if col != '*')
                
                # look for any matches for any data type
                mfound = False
                
                for dataType in self._filteredDataTypes:
                    # determine the check text based on case sensitivity
                    if ( caseSensitive ):
                        check = str(item.filterData(dataType))
                    else:
                        check = str(item.filterData(dataType)).lower()
                    
                    specific = terms.get(dataType, [])
                    
                    # make sure all the keywords match
                    for key in generic + specific:
                        if ( not key ):
                            continue
                        
                        # look for exact keywords
                        elif ( key.startswith('"') and key.endswith('"') ):
                            if ( key.strip('"') == check ):
                                if ( key in generic ):
                                    generic_found[key] = True
                                
                                if ( key in specific ):
                                    dtype_found[dataType] = True
                        
                        # look for ending keywords
                        elif ( key.startswith('*') and not key.endswith('*') ):
                            if ( check.endswith(key.strip('*')) ):
                                if ( key in generic ):
                                    generic_found[key] = True
                                if ( key in specific ):
                                    dtype_found[dataType] = True
                        
                        # look for starting keywords
                        elif ( key.endswith('*') and not key.startswith('*') ):
                            if ( check.startswith(key.strip('*')) ):
                                if ( key in generic ):
                                    generic_found[key] = True
                                if ( key in specific ):
                                    dtype_found[dataType] = True
                        
                        # look for generic keywords
                        elif ( key.strip('*') in check ):
                            if ( key in generic ):
                                generic_found[key] = True
                            if ( key in specific ):
                                dtype_found[dataType] = True
                    
                    mfound = all(dtype_found.values()) and \
                             all(generic_found.values())
                    if ( mfound ):
                        break
                
                item.setHidden(not mfound)
                
                if ( mfound ):
                    found = True
        
        return found
    
    def filteredDataTypes( self ):
        """
        Returns the data types that are used for filtering for this tree.
        
        :return     [<str>, ..]
        """
        return self._filteredDataTypes
    
    @Slot(str)
    def filterItems( self, 
                     terms, 
                     autoExpand = True, 
                     caseSensitive = False ):
        """
        Filters the items in this tree based on the inputed text.
        
        :param      terms           | <str> || {<str> datatype: [<str> opt, ..]}
                    autoExpand      | <bool>
                    caseSensitive   | <bool>
        """
        # create a dictionary of options
        if ( type(terms) != dict ):
            terms = {'*': str(terms)}
        
        # validate the "all search"
        if ( '*' in terms and type(terms['*']) != list ):
            sterms = str(terms['*'])
            
            if ( not sterms.strip() ):
                terms.pop('*')
            else:
                dtype_matches = DATATYPE_FILTER_EXPR.findall(sterms)
                
                # generate the filter for each data type
                for match, dtype, values in dtype_matches:
                    sterms = sterms.replace(match, '')
                    terms.setdefault(dtype, [])
                    terms[dtype] += values.split(',')
                
                keywords = sterms.replace(',', '').split()
                while ( '' in keywords ):
                    keywords.remove('')
                
                terms['*'] = keywords
        
        # filter out any data types that are not being searched
        filtered_dtypes = self.filteredDataTypes()
        filter_terms = {}
        for dtype, keywords in terms.items():
            if ( dtype != '*' and not dtype in filtered_dtypes ):
                continue
            
            if ( not caseSensitive ):
                keywords = [str(keyword).lower() for keyword in keywords]
            else:
                keywords = map(str, keywords)
            
            filter_terms[dtype] = keywords
        
        self.__filterItems(filter_terms, autoExpand, caseSensitive)
    
    def setFilteredDataTypes( self, dataTypes ):
        """
        Sets the data types that will be used for filtering of this 
        tree's items.
        
        :param      data types | [<str>, ..]
        """
        self._filteredDataTypes = dataTypes
    
# define the designer properties
__designer_plugins__ = [XListWidget]