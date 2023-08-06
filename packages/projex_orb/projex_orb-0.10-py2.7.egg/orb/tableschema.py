#!/usr/bin/python

""" Defines the meta information for a Table class. """

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

import projex.text

from orb                 import errors
from orb                 import settings
from orb.column          import Column
from orb.index           import Index

logger = logging.getLogger(__name__)

Orb       = None
Table     = None
TableBase = None
def __lazy_import__():
    global Orb
    global Table
    global TableBase
    
    if ( Orb ):
        return
    
    from orb import Orb
    from orb.table import Table, TableBase

class TableSchema(object):
    """ 
    Contains meta data information about a table as it maps to a database.
    """
    
    TEMPLATE_PREFIXED = '[prefix::underscore::lower]_[name::underscore::lower]'
    TEMPLATE_TABLE    = '[name::underscore::lower]'
    
    _customHandlers = []
    
    def __init__( self ):
        self._abstract          = False
        self._autoPrimary       = True
        self._name              = ''
        self._databaseName      = ''
        self._groupName         = ''
        self._tableName         = ''
        self._inherits          = ''
        self._stringFormat      = ''
        self._namespace         = ''
        self._cacheEnabled      = False
        self._cacheExpireIn     = 0
        self._inheritedLoaded   = False
        self._columns           = []
        self._indexes           = []
        self._primaryColumns    = None
        self._model             = None
        self._properties        = {}
    
    def addColumn( self, column ):
        """
        Adds the inputed column to this table schema.
        
        :param      column  | <Column>
        """
        if ( column in self._columns ):
            return
        
        self._columns.append(column)
        
        # pylint: disable-msg=W0212
        if ( not column._schema ):
            column._schema = self
    
    def addIndex( self, index ):
        """
        Adds the inputed index to this table schema.
        
        :param      index   | <Index>
        """
        if ( index in self._indexes ):
            return
        
        self._indexes.append(index)
    
    def autoPrimary( self ):
        """
        Returns whether or not this schema auto-generates the primary key.  \
        This is useful when defining reusable schemas that could be applied \
        to various backends, for instance an auto-increment column for a \
        PostgreSQL database vs. a string column for a MongoDB.  By default, it \
        is recommended this value remain True.
        
        :return     <bool>
        """
        return self._autoPrimary
    
    def cacheExpireIn( self ):
        """
        Returns the number of minutes that the caching system will use before
        clearing its cache data.
        
        :return     <int> | <float>
        """
        return self._cacheExpireIn
    
    def column( self, name, recurse = True ):
        """
        Returns the column instance based on its name.  
        If error reporting is on, then the ColumnNotFoundError 
        error will be thrown the key inputed is not a valid 
        column name.
        
        :param      name | <str>
                    recurse | <bool>
        
        :return     <Column> || None
        """
        self.primaryColumns()
        
        for column in self.columns(recurse = recurse):
            if ( name in (column.name(),
                          column.fieldName(),
                          column.displayName()) ):
                return column
        return None
    
    def columnNames( self ):
        """
        Returns the list of column names that are defined for 
        this table schema instance.
        
        :return     <list> [ <str> columnName, .. ]
        """
        self.primaryColumns()
        return sorted([column.name() for column in self._columns])
    
    def columns( self, recurse = True ):
        """
        Returns the list of column instances that are defined
        for this table schema instance.
        
        :param      recurse | <bool>
        
        :return     <list> [ <Column>, .. ]
        """
        self.primaryColumns()
        
        __lazy_import__()
        
        # load the inherited columns
        if ( recurse and not self._inheritedLoaded and self._inherits ):
            names = self.columnNames()
            self._inheritedLoaded = True
            
            inherited = Orb.instance().schema(self._inherits)
            
            if ( not inherited ):
                warn = errors.MissingTableSchemaWarning(self._inherits)
                logger.warning( warn )
            else:
                for column in inherited.columns():
                    if ( column.name() in names ):
                        warn = errors.DuplicateColumnWarning(column.name())
                        logger.warning(warn)
                        continue
                        
                    self._columns.append(column)
        
        if ( recurse ):
            return self._columns[:]
        else:
            return [col for col in self._columns if col.schema() == self]
    
    def databaseName( self ):
        """
        Returns the name of the database that this schema will be linked to.
        
        :return     <str>
        """
        return self._databaseName
    
    def database( self ):
        """
        Returns the database that is linked with the current schema.
        
        :return     <Database> || None
        """
        __lazy_import__()
        return Orb.instance().database(self.databaseName())
    
    def generateModel( self ):
        """
        Generates the default model class for this table schema, if no \
        default model already exists.  The new generated table will be \
        returned.
        
        :return     <subclass of Table> || None
        """
        if ( self._model ):
            return self._model
        
        __lazy_import__()
        
        # generate the base models
        if ( self.inherits() ):
            inherits  = self.inherits()
            inherited = Orb.instance().schema(inherits)
            
            if ( not inherited ):
                logger.error('Could not find inherited model: %s' % inherits)
                base = None
            else:
                base = inherited.model(autoGenerate = True)
                
            if ( base ):
                bases = [base]
            else:
                bases = [Table]
        else:
            bases = [Table]
        
        # generate the attributes
        attrs   = { '__db_schema__': self }
        grp     = self.group()
        prefix  = ''
        if ( grp ):
            prefix = grp.modelPrefix()
        
        return TableBase( prefix + self.name(), tuple(bases), attrs )
    
    def generatePrimary( self ):
        """
        Auto-generates the primary column for this schema based on the \
        current settings.
        
        :return     [<Column>, ..] || None
        """
        if ( settings.EDIT_ONLY_MODE ):
            return None
        
        db = self.database()
        if ( not (db and db.connection()) ):
            return None
            
        # create the default primary column from the inputed type
        return [db.connection().defaultPrimaryColumn()]
    
    def groupName( self ):
        """
        Returns the name of the group that this schema is a part of in the \
        database.
        
        :return     <str>
        """
        return self._groupName
    
    def group( self ):
        """
        Returns the schema group that this schema is related to.
        
        :return     <OrbGroup> || None
        """
        __lazy_import__()
        return Orb.instance().group(self.groupName())
    
    def indexes( self, recurse = True ):
        """
        Returns the list of indexes that are associated with this schema.
        
        :return     [<Index>, ..]
        """
        return self._indexes[:]
        
    def inherits( self ):
        """
        Returns the name of the table schema that this class will inherit from.
        
        :return     <str>
        """
        return self._inherits
    
    def inheritsRecursive( self ):
        """
        Returns all of the tables that this table inherits from.
        
        :return     [<str>, ..]
        """
        __lazy_import__()
        
        output      = []
        inherits    = self.inherits()
        
        while ( inherits ):
            output.append(inherits)
            
            table = Orb.instance().schema(inherits)
            if ( not table ):
                break
            
            inherits = table.inherits()
            
        return output
    
    def isAbstract( self ):
        """
        Returns whether or not this schema is an abstract table.  Abstract \
        tables will not register to the database, but will serve as base \
        classes for inherited tables.
        
        :return     <bool>
        """
        return self._abstract
    
    def isCacheEnabled( self ):
        """
        Returns whether or not caching is enabled for this Table instance.
        
        :sa     setCacheEnabled
        
        :return     <bool>
        """
        return self._cacheEnabled
    
    def model( self, autoGenerate = False ):
        """
        Returns the default Table class that is associated with this \
        schema instance.
        
        :param      autoGenerate | <bool>
        
        :return     <subclass of Table>
        """
        if ( not self._model and autoGenerate ):
            self._model = self.generateModel()
            
        return self._model
    
    def name( self ):
        """
        Returns the name of this schema object.
        
        :return     <str>
        """
        return self._name
    
    def namespace( self ):
        """
        Returns the namespace of this schema object.  If no namespace is
        defined, then its group namespace is utilized.
        
        :return     <str>
        """
        if ( self._namespace ):
            return self._namespace
        
        grp = self.group()
        if ( grp ):
            return grp.namespace()
        else:
            db = self.database()
            if ( db ):
                return db.namespace()
            
            __lazy_import__()
            return Orb.instance().namespace()
    
    def primaryColumns( self ):
        """
        Returns the primary key columns for this table's
        schema.
        
        :return     <tuple> (<Column>,)
        """
        if ( self._primaryColumns ):
            return self._primaryColumns
        
        if ( self.autoPrimary() and not self._inherits ):
            cols = self.generatePrimary()
            
            if ( not cols is None ):
                for col in cols:
                    self.addColumn(col)
        else:
            cols = None
        
        # generate the primary column list the first time
        if ( cols is None and self._inherits ):
            __lazy_import__()
            
            inherited = Orb.instance().schema(self._inherits)
            
            if ( not inherited ):
                warn = errors.MissingTableSchemaWarning(self._inherits)
                logger.warn(warn)
            else:
                cols = inherited.primaryColumns()
        
        if ( not cols is None ):
            self._primaryColumns = cols[:]
            return self._primaryColumns
        else:
            return []
    
    def property( self, key, default = None ):
        """
        Returns the custom data that was stored on this table at the inputed \
        key.  If the key is not found, then the default value will be returned.
        
        :param      key         | <str>
                    default     | <variant>
        
        :return     <variant>
        """
        return self._properties.get(str(key), default)
    
    def removeColumn( self, column ):
        """
        Removes the inputed column from this table's schema.
        
        :param      column | <Column>
        """
        if ( column in self._columns ):
            self._columns.remove(column)
            column._schema = None
    
    def removeIndex( self, index ):
        """
        Removes the inputed index from this table's schema.
        
        :param      index | <Index>
        """
        if ( index in self._indexes ):
            self._indexes.remove(index)
    
    def searchableColumns(self):
        """
        Returns a list of the searchable columns for this schema.
        
        :return     <str>
        """
        return filter(lambda x: x.isSearchable(), self.columns())
    
    def setAbstract( self, state ):
        """
        Sets whether or not this table is abstract.
        
        :param      state | <bool>
        """
        self._abstract = state
    
    def setAutoPrimary( self, state ):
        """
        Sets whether or not this schema will use auto-generated primary keys.
        
        :sa         autoPrimary
        
        :return     <bool>
        """
        self._autoPrimary = state
    
    def setCacheEnabled( self, state ):
        """
        Sets whether or not to enable caching on the Table instance this schema
        belongs to.  When caching is enabled, all the records from the table
        database are selected the first time a select is called and
        then subsequent calls to the database are handled by checking what is
        cached in memory.  This is useful for small tables that don't change 
        often (such as a Status or Type table) and are referenced frequently.
        
        To have the cache clear automatically after a number of minutes, set the
        cacheExpireIn method.
        
        :param      state | <bool>
        """
        self._cacheEnabled = state
    
    def setCacheExpireIn( self, minutes ):
        """
        Sets the number of minutes that the table should clear its cached
        results from memory and re-query the database.  If the value is 0, then
        the cache will have to be manually cleared.
        
        :param      minutes | <int> || <float>
        """
        self._cacheExpireIn = minutes
    
    def setColumns( self, columns ):
        """
        Sets the columns that this schema uses.
        
        :param      columns     | [<Column>, ..]
        """
        self._columns = columns[:]
        
        # pylint: disable-msg=W0212
        for column in columns:
            if ( not column._schema ):
                column._schema = self
    
    def setProperty( self, key, value ):
        """
        Sets the custom data at the given key to the inputed value.
        
        :param      key     | <str>
                    value   | <variant>
        """
        self._properties[str(key)] = value
    
    def setDatabaseName( self, databaseName ):
        """
        Sets the database name that this schema will be linked to.
        
        :param      databaseName | <str>
        """
        self._databaseName = str(databaseName)
    
    def setModel( self, model ):
        """
        Sets the default Table class that is associated with this \
        schema instance.
        
        :param    model     | <subclass of Table>
        """
        self._model = model
    
    def setNamespace( self, namespace ):
        """
        Sets the namespace that will be used for this schema to the inputed
        namespace.
        
        :param      namespace | <str>
        """
        self._namespace = namespace
    
    def setIndexes( self, indexes ):
        """
        Sets the list of indexed lookups for this schema to the inputed list.
        
        :param      indexes     | [<Index>, ..]
        """
        self._indexes = indexes[:]
    
    def setInherits( self, name ):
        """
        Sets the name for the inherited table schema to the inputed name.
        
        :param      name    | <str>
        """
        self._inherits = name
    
    def setName( self, name ):
        """
        Sets the name of this schema object to the inputed name.
        
        :param      name    | <str>
        """
        self._name = name
    
    def setGroupName( self, groupName ):
        """
        Sets the group name that this table schema will be apart of.
        
        :param      groupName   | <str>
        """
        self._groupName = groupName
    
    def setStringFormat( self, format ):
        """
        Sets a string format to be used when rendering a table using the str()
        method.  This is a python string format with dictionary keys for the 
        column values that you want to display.
        
        :param      format | <str>
        """
        self._stringFormat = str(format)
    
    def setTableName( self, tableName ):
        """
        Sets the name that will be used in the actual database.  If the \
        name supplied is blank, then the default database name will be \
        used based on the group and name for this schema.
        
        :param      tableName  | <str>
        """
        self._tableName = tableName
    
    def stringFormat( self ):
        """
        Returns the string format style for this schema.
        
        :return     <str>
        """
        return self._stringFormat
    
    def tableName( self ):
        """
        Returns the name that will be used for the table in the database.
        
        :return     <str>
        """
        if ( not self._tableName ):
            self._tableName = self.defaultTableName( self.name(),
                                                     self.groupName() )
        return self._tableName
    
    def toXml( self, xparent ):
        """
        Saves this schema information to XML.
        
        :param      xparent     | <xml.etree.ElementTree.Element>
        
        :return     <xml.etree.ElementTree.Element>
        """
        xschema = ElementTree.SubElement(xparent, 'schema')
        
        # save the properties
        xschema.set( 'name',     self.name() )
        xschema.set( 'group',    self.groupName() )
        xschema.set( 'inherits', self.inherits() )
        xschema.set( 'dbname',   self.tableName() )
        xschema.set( 'autoPrimary',  str(self.autoPrimary()) )
        xschema.set( 'stringFormat', self.stringFormat())
        xschema.set( 'cacheEnabled', str(self.isCacheEnabled()))
        xschema.set( 'cacheExpire',  str(self.cacheExpireIn()))
        
        # save the properties
        if ( self._properties ):
            xprops = ElementTree.SubElement(xschema, 'properties')
            for prop, value in self._properties.items():
                xprop = ElementTree.SubElement(xprops, 'property')
                xprop.set('key', str(prop))
                xprop.set('value', str(value))
        
        # save the columns
        for column in self.columns(recurse = False):
            column.toXml( xschema )
        
        # save the indexes
        for index in self.indexes():
            index.toXml( xschema )
        
        return xschema
    
    @staticmethod
    def defaultTableName( name, prefix = '' ):
        """
        Returns the default database table name for the inputed name \
        and prefix.
        
        :param      name    | <str>
        :param      prefix  | <str>
        """
        if ( prefix ):
            templ = TableSchema.TEMPLATE_PREFIXED
        else:
            templ = TableSchema.TEMPLATE_TABLE
        
        options = { 'name': name, 'prefix': prefix }
        
        return projex.text.render( templ, options )
    
    @staticmethod
    def fromXml( xschema ):
        """
        Generates a new table schema instance for the inputed database schema \
        based on the given xml information.
        
        :param      xschema      | <xml.etree.Element>
        
        :return     <TableSchema> || None
        """
        from orb import TableSchema as cls
        
        tschema = cls()
        
        # load the properties
        tschema.setName(        xschema.get('name', '') )
        tschema.setGroupName(   xschema.get('group', '') )
        tschema.setInherits(    xschema.get('inherits', '') )
        tschema.setTableName(   xschema.get('dbname', '') )
        tschema.setAutoPrimary( xschema.get('autoPrimary') != 'False' )
        tschema.setStringFormat( xschema.get('stringFormat', '') )
        tschema.setCacheEnabled( xschema.get('cacheEnabled') == 'True' )
        tschema.setCacheExpireIn( int(xschema.get('cacheExpire', 0)) )
        
        # load the properties
        xprops = xschema.find('properties')
        if ( xprops is not None ):
            for xprop in xprops:
                tschema.setProperty(xprop.get('key'), xprop.get('value'))
        
        # load the columns
        for xcolumn in xschema.findall('column'):
            column = Column.fromXml( xcolumn )
            if ( column ):
                tschema.addColumn(column)
        
        # load the indexes
        for xindex in xschema.findall('index'):
            index = Index.fromXml( xindex )
            if ( index ):
                tschema.addIndex(index)
        
        return tschema