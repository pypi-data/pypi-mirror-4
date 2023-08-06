#!/usr/bin/python

""" Defines an indexing system to use when looking up records. """

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

import logging

from xml.etree import ElementTree

from projex import security

from orb.query import Query as Q
from orb import errors

logger = logging.getLogger(__name__)

class Index(object):
    """ 
    Defines an indexed way to lookup information from a database.
    Creating an Index generates an object that works like a method, however
    has a preset query built into it, along with caching options.
    """
    def __init__( self, 
                  name    = '', 
                  columns = None, 
                  unique  = False, 
                  order   = None, 
                  cached  = False ):
        
        if ( columns == None ):
            columns = []
        
        self.__name__       = name
        self._columnNames   = columns
        self._unique        = unique
        self._order         = order
        self._cached        = cached
        self._cache         = {}
        self._loaded        = False
    
    def __call__( self, cls, *values, **options ):
        from orb.table import Table
        from orb.recordset import RecordSet

        # make sure we have the right number of arguments
        if ( len(values) != len(self._columnNames) ):
            name        = self.__name__
            columnCount = len(self._columnNames)
            valueCount  = len(values)
            opts = (name, columnCount, valueCount)
            text = '%s() takes exactly %i arguments (%i given)' % opts
            raise TypeError(text)
        
        # returns the data from the cache if found
        if ( self._cached and values in self._cache ):
            return self._cache[values]
        
        # create the lookup query
        query = Q()
        for i, col in enumerate(self._columnNames):
            value = values[i]
            column = cls.schema().column(col)
            
            if Table.recordcheck(value) and not value.isRecord():
                if self._unique:
                    return None
                
                return RecordSet()
            
            if ( not column ):
                logger.warning(errors.ColumnNotFoundWarning(col))
                continue
            
            if ( column.isEncrypted() ):
                value = security.encrypt(value)
                
            query &= Q(col) == value
        
        # include additional where option selection
        if ( 'where' in options ):
            query &= options.get('where')
        
        order   = options.get('order', self._order)
        columns = options.get('columns', None)
        
        # selects the records from the database
        if ( self._unique ):
            results = cls.selectFirst( columns = columns,
                                       where = query)
        else:
            results = cls.select( columns = columns,
                                  where = query,
                                  order = order)
        
        # cache the results
        if ( self._cached ):
            self._cache[values] = results
        
        return results
    
    def cached( self ):
        """
        Returns whether or not the results for this index should be cached.
        
        :return     <bool>
        """
        return self._cached
    
    def clearCache( self ):
        """
        Clears out all the cached information for this index.
        """
        self._cache.clear()
    
    def columnNames( self ):
        """
        Returns the list of column names that this index will be expecting as \
        inputs when it is called.
        
        :return     [<str>, ..]
        """
        return self._columnNames
    
    def name( self ):
        """
        Returns the name of this index.
        
        :return     <str>
        """
        return self.__name__
    
    def setCached( self, state ):
        """
        Sets whether or not this index should cache the results of its query.
        
        :param      state | <bool>
        """
        self._cached = state
    
    def setColumnNames( self, columnNames ):
        """
        Sets the list of the column names that this index will use when \
        looking of the records.
        
        :param      columnNames | [<str>, ..]
        """
        self._columnNames = columnNames
    
    def setOrder( self, order ):
        """
        Sets the order information for this index for how to sort and \
        organize the looked up data.
        
        :param      order   | [(<str> field, <str> direction), ..]
        """
        self._order = order
    
    def setName( self, name ):
        """
        Sets the name for this index to this index.
        
        :param      name    | <str>
        """
        self.__name__ = str(name)
    
    def setUnique( self, state ):
        """
        Sets whether or not this index should find only a unique record.
        
        :param      state | <bool>
        """
        self._unique = state
    
    def unique( self ):
        """
        Returns whether or not the results that this index expects should be \
        a unique record, or multiple records.
        
        :return     <bool>
        """
        return self._unique
    
    def toXml( self, xparent ):
        """
        Saves the index data for this column to XML.
        
        :param      xparent     | <xml.etree.ElementTree.Element>
        
        :return     <xml.etree.ElementTree.Element>
        """
        xindex = ElementTree.SubElement(xparent, 'index')
        xindex.set( 'name', self.name() )
        xindex.set( 'columns', ','.join( self.columnNames() ) )
        xindex.set( 'unique', str(self.unique()))
        xindex.set( 'cached', str(self.cached()))
        
        return xindex
    
    @staticmethod
    def fromXml( xindex ):
        """
        Generates an index method descriptor from xml data.
        
        :param      xindex  | <xml.etree.Element>
        
        :return     <Index> || None
        """
        index = Index()
        index.setName(          xindex.get('name', '') )
        index.setColumnNames(   xindex.get('columns', '').split(',') )
        index.setUnique(        xindex.get('unique') == 'True' )
        index.setCached(        xindex.get('cached') == 'True' )
        
        return index