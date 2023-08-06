#!/usr/bin/python

""" Creates reusable Qt window components. """

# define authorship information:
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintanence information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

#---------------------------------------------------------------------------

import logging
import os.path
import shutil
import zipfile

from projexui.qt.QtCore import QSize, QDir, Qt
from projexui.qt.QtGui import QIcon,\
                              QTreeWidgetItem,\
                              QApplication

import projexui.resources

logger = logging.getLogger(__name__)

TITLE_MAP = {
    'functions':    'All Functions',
    'classes':      'All Classes',
    'modules':      'All Modules',
    'api':          'API Manual',
    'user':         'User Manual'
}

class XdkEntryItem(QTreeWidgetItem):
    def __init__( self, parent, filepath ):
        super(XdkEntryItem, self).__init__(parent)
        
        # set custom properties
        self._isFolder = os.path.isdir(filepath)
        self._filepath = str(filepath).replace('\\', '/')
        self._url      = ''
        self._loaded   = False
        
        # define custom properties
        if ( self._isFolder ):
            icon = projexui.resources.find('img/folder.png')
            self.setChildIndicatorPolicy(self.ShowIndicator)
        else:
            icon = projexui.resources.find('img/file.png')
            self._url    = 'file:///%s' % self._filepath
            self._loaded = True
        
        # set default properties
        self.setIcon(0,     QIcon(icon))
        self.setSizeHint(0, QSize(20, 18))
        self.setText(0,     self.titleForFilepath(self._filepath))
    
    def __lt__( self, other ):
        if ( not isinstance(other, XdkEntryItem) ):
            return super(XdkEntryItem, self).__lt__(other)
        
        sfolder = self.isFolder()
        ofolder = other.isFolder()
        
        if ( sfolder and not ofolder ):
            return True
            
        elif ( ofolder and not sfolder ):
            return False
        
        return super(XdkEntryItem, self).__lt__(other)
    
    def filepath( self ):
        """
        Returns the filepath for this item.
        
        :return     <str>
        """
        return self._filepath
    
    def isFolder( self ):
        """
        Returns whether or not this instance is a folder.
        
        :return     <bool>
        """
        return self._isFolder
    
    def isLoaded( self ):
        """
        Return whether or not this item is currently loaded.
        
        :return     <bool>
        """
        return self._loaded
    
    def load( self ):
        """
        Loads this item.
        """
        if ( self._loaded ):
            return
        
        self._loaded = True
        self.setChildIndicatorPolicy(self.DontShowIndicatorWhenChildless)
        
        if ( self.isFolder() ):
            for name in os.listdir(self.filepath()):
                # ignore 'hidden' folders
                if ( name.startswith('_') and not name.startswith('__') ):
                    continue
                
                # ignore special cases (only want modules for this)
                if ( '-' in name ):
                    continue
                
                # use the index or __init__ information
                if ( name in ('index.html', '__init__.html') ):
                    self._url = 'file:///%s/%s' % (self.filepath(), name)
                    continue
                
                # otherwise, load a childitem
                XdkEntryItem(self, os.path.join(self.filepath(), name))
    
    def url( self ):
        """
        Returns the url for this instance.
        
        :return     <str>
        """
        return self._url
    
    def xdkItem( self ):
        root = self
        while ( root.parent() ):
            root = root.parent()
        
        if ( isinstance(root, XdkItem) ):
            return root
        return None
    
    @staticmethod
    def titleForFilepath( url ):
        """
        Returns a gui title for this url.
        
        :return     <str>
        """
        title       = str(url).split('/')[-1].split('.')[0]
        title_splt  = title.split('-')
        
        if ( title_splt[-1] == 'allmembers' ):
            title = 'List of All Members for %s' % title_splt[-2]
        elif ( title_splt[-1] == 'source' ):
            title = 'Source Code for %s' % title_splt[-2]
        else:
            title = title_splt[-1]
        
        # don't reuse things like 'api' since these will be module names as well
        if ( len(str(url).split('/')) <= 2 ):
            return TITLE_MAP.get(title, title)
        return title
    
#------------------------------------------------------------------------------

class XdkItem(XdkEntryItem):
    """ """
    def __init__( self, sdk_filename ):
        # creates the new XdkItem
        name     = os.path.basename(str(sdk_filename)).split('.')[0]
        temppath = str(QDir.tempPath())
        filepath = os.path.join(temppath, 'xdocs/%s' % name)
        
        # create the new XdkItem
        super(XdkItem, self).__init__(None, filepath)
        
        # define custom properties
        self._sdkFilename   = str(sdk_filename)
        self._searchurls    = {}
        
        # set the options
        self.setIcon(0, QIcon(projexui.resources.find('img/sdk.png')))
    
    def load( self ):
        # extract the data to the temp location
        if ( self.isLoaded() ):
            return
        
        # load the files to the temp location
        temp_path = self.filepath()
        if ( os.path.exists(temp_path) ):
            shutil.rmtree(temp_path)
        
        if ( not os.path.exists(temp_path) ):
            os.makedirs(temp_path)
        
        # extract the zip files to the temp location
        QApplication.setOverrideCursor(Qt.WaitCursor)
        zfile = zipfile.ZipFile(self.sdkFilename(), 'r')
        zfile.extractall(temp_path)
        zfile.close()
        QApplication.restoreOverrideCursor()
        
        # load the url information for this entry
        super(XdkItem, self).load()
    
    def indexlist( self ):
        """
        Returns the list of files in alphabetical order for index lookups.
        
        :return     [(<str> name, <str> url), ..]
        """
        # load the index information from the filename
        zfile = zipfile.ZipFile(self.sdkFilename(), 'r')
        namelist = zfile.namelist()
        zfile.close()
        
        # extract the index information
        output = []
        for name in namelist:
            name_splt = os.path.basename(name).split('.')[0].split('-')
            
            # ignore undesired information
            if ( name_splt[-1] in ('allmembers', 'source') ):
                continue
            
            # ignore any private information
            ignore = False
            for part in name_splt:
                if ( part.startswith('_') ):
                    ignore = True
                    break
            
            if ( ignore ):
                continue
            
            if ( name_splt[-1] in ('index.html', '__init__.html') ):
                title = name_splt[-2]
            else:
                title = name_splt[-1]
            
            url = 'file:///%s/%s' % (self.filepath(), name)
            output.append((title, url))
        
        return output
    
    def sdkFilename( self ):
        """
        Returns the filename for this Xdk source item.
        
        :return     <str>
        """
        return self._sdkFilename
    
    def search( self, terms ):
        """
        Seraches the documents for the inputed terms.
        
        :param      terms
        
        :return     [{'url': <str>, 'title': <str>', 'strength': <int>}]
        """
        if ( not self._searchurls ):
            prefix = 'file:///' + self.filepath().rstrip('/') + '/'
            # load the html contents
            zfile = zipfile.ZipFile(self.sdkFilename(), 'r')
            for name in zfile.namelist():
                self._searchurls[prefix + name] = zfile.read(name)
            zfile.close()
        
        # search for the contents
        output = [] # [(<int> strength>
        term_list = str(terms).split(' ')
        for url, html in self._searchurls.items():
            title           = self.titleForFilepath(url)
            strength        = 0
            all_title_found = True
            all_found       = True
            
            for term in term_list:
                if ( term == title ):
                    strength += 5
                
                elif ( term.lower() == title.lower() ):
                    strength += 4
                    
                elif ( term in title ):
                    strength += 3
                
                elif ( term.lower() in title.lower() ):
                    strength += 2
                
                else:
                    all_title_found = False
                
                if ( not term in html ):
                    all_found = False
                else:
                    strength += 1
            
            if ( all_title_found ):
                strength += len(terms) * 2
            
            if ( all_found ):
                strength += len(terms)
            
            # determine the strength
            if ( strength ):
                output.append({'url': url, 
                               'title': self.titleForFilepath(url),
                               'strength': strength})
        
        return output