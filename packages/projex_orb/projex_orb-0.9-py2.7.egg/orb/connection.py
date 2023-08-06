#!/usr/bin/python

"""
Defines the base connection class that will be used for communication
to the backend databases.
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

# not using undefined variables is ok for abstract classes
# pylint: disable-msg=W0613

import glob
import os.path
import logging

import projex
from projex.decorators   import abstractmethod

import orb

from orb import errors
from orb import backends

logger = logging.getLogger(__name__)

class DatabaseOptions(object):
    """"
    Defines a unique instance of information that will be bundled when
    calling different methods within the connections class.
    """
    def __init__( self, **kwds ):
        self.namespace          = kwds.get('namespace')
        self.flags              = kwds.get('flags', 0)        
        self.dryRun             = kwds.get('dryRun', False)
        self.useCache           = kwds.get('useCache', False)
        self.inflateRecords     = kwds.get('inflated', 
                                  kwds.get('inflateRecords', True))

#------------------------------------------------------------------------------

class LookupOptions(object):
    """
    Defines a unique instance of information that will be bundled when
    calling different query based methods in the connection class.
    """
    def __init__( self, **kwds ):
        self.columns        = kwds.get('columns', None)
        self.where          = kwds.get('where',   None)
        self.order          = kwds.get('order',   None)
        self.start          = kwds.get('start',   None)
        self.limit          = kwds.get('limit',   None)

#------------------------------------------------------------------------------

class Connection(object):
    """ 
    Defines the base connection class type.  This class is used to handle
    database transactions and queries.  The Connection class needs to be
    subclassed to handle connection to a particular kind of database backend,
    the backends that are included with the orb package can be found in the
    orb.backends package.
    """
    backends = {}
    
    # define the options class that will be used for backend information
    DatabaseOptionsClass = DatabaseOptions
    LookupOptionsClass   = LookupOptions
    
    def __init__( self, database ):
        self._database      = database
        self._threadEnabled = False
    
    def __del__( self ):
        """
        Closes the connection when the connection instance is deleted.
        """
        self.close()
    
    @abstractmethod()
    def close( self ):
        """
        Closes the connection to the datbaase for this connection.
        
        :return     <bool> closed
        """
        return True
    
    @abstractmethod()
    def commit( self ):
        """
        Commits the changes to the current database connection.
        
        :return     <bool> success
        """
        return False
    
    @abstractmethod()
    def count( self, table_or_join, lookup, options ):
        """
        Returns the number of records that exist for this connection for
        a given lookup and options.
        
        :sa         distinct, select
        
        :param      table_or_join | <orb.Table> || <orb.Join>
                    lookup        | <orb.LookupOptions>
                    options       | <orb.DatabaseOptions>
        
        :return     <int>
        """
        return 0
    
    @abstractmethod()
    def createTable( self, schema, options ):
        """
        Creates a new table in the database based cff the inputed
        table information.
        
        :param      schema   | <orb.TableSchema>
                    options  | <orb.DatabaseOptions>
        
        :return     <bool> success
        """
        return False
    
    def database( self ):
        """
        Returns the database instance that this connection is
        connected to.
        
        :return     <Database>
        """
        return self._database
    
    def defaultPrimaryColumn( self ):
        """
        Defines a default column to be used as the primary column for this \
        database connection.  By default, an auto-incrementing integer field \
        called '_id' will be defined.
        
        :return     <orb.Column>
        """
        from orb import Column, ColumnType
        from orb import settings
        return Column( ColumnType.Integer,
                       settings.PRIMARY_FIELD,
                       primary          = True,
                       autoIncrement    = True,
                       fieldName        = settings.PRIMARY_FIELD,
                       getterName       = settings.PRIMARY_GETTER,
                       setterName       = settings.PRIMARY_SETTER,
                       displayName      = settings.PRIMARY_DISPLAY,
                       indexName        = settings.PRIMARY_INDEX,
                       indexed          = True,
                       unique           = True )
    
    @abstractmethod()
    def distinct( self, table_or_join, lookup, options ):
        """
        Returns the distinct set of records that exist for a given lookup
        for the inputed table or join instance.
        
        :sa         count, select
        
        :param      table_or_join | <orb.Table> || <orb.Join>
                    lookup        | <orb.LookupOptions>
                    options       | <orb.DatabaseOptions>
        
        :return     {<str> columnName: <list> value, ..}
        """
        return 0
        
    @abstractmethod()
    def execute( self, command, data = None, throw = False, flags = 0 ):
        """
        Executes the inputed command into the current 
        connection cursor.
        
        :param      command  | <str>
                    data     | <dict> || None
                    throw    | <bool> | determine if errors should be thrown
                    flags    | <orb.DatabaseFlags>
        
        :return     <variant> returns a native set of information
        """
        return None
    
    @abstractmethod()
    def insert( self, record, options ):
        """
        Inserts the database record into the database with the
        given values.
        
        :param      record      | <orb.Table>
                    options     | <orb.DatabaseOptions>
        
        :return     <bool>
        """
        return False
    
    @abstractmethod()
    def isConnected( self ):
        """
        Returns whether or not this conection is currently
        active.
        
        :return     <bool> connected
        """
        return False
    
    def isThreadEnabled( self ):
        """
        Returns whether or not this connection can be threaded.
        
        :return     <bool>
        """
        return self._threadEnabled
    
    @abstractmethod()
    def open( self ):
        """
        Opens a new database connection to the datbase defined
        by the inputed database.
        
        :return     <bool> success
        """
        return False
    
    def remove( self, schema, records, options ):
        """
        Removes the inputed records from the database.
        
        :param      schema      | <orb.TableSchema>
                    records     | [<orb.Table> record, ..] || <orb.RecordSet>
                    options     | <orb.DatabaseOptions>
        
        :return     <int> number of rows removed
        """
         # group the records by their schemas
        schema_keys = {}
        removing    = []
        for record in records:
            if ( orb.Table.recordcheck(record) ):
                key_schema = record.schema()
                key = record.primaryKey()
            else:
                key_schema = schema
                key = record
            
            if ( not key ):
                continue
            
            removing.append(record)
            schema_keys.setdefault(key_schema, [])
            schema_keys[key_schema].append(key)
        
        if ( not (removing and schema_keys) ):
            return 0
        
        count = 0
        transaction = orb.Transaction()
        transaction.begin()
        for schema, keys in schema_keys.items():
            count += self.removeRecords(schema, keys, options)
        transaction.end()
        
        # update the results
        if ( count == len(records) ):
            for record in removing:
                if ( orb.Table.recordcheck(record) ):
                    record._removedFromDatabase()
        
        return count
    
    @abstractmethod()
    def removeRecords( self, schema, primaryKeys, options ):
        """
        Removes the given records from the inputed schema.  This method is 
        called from the <Connection.remove> method that handles the pre
        processing of grouping records together by schema and only works
        on the primary key.
        
        :param      schema      | <orb.TableSchema>
                    primaryKeys | [<variant> pkey, ..]
                    options     | <orb.DatabaseOptions>
        
        :return     <int> | number of rows removed
        """
        return 0
    
    @abstractmethod()
    def rollback( self ):
        """
        Rollsback the latest code run on the database.
        """
        return False
    
    @abstractmethod()
    def select(self, table_or_join, lookup, options):
        """
        Selects the records from the database for the inputed table or join
        instance based on the given lookup and options.
                    
        :param      table_or_join   | <subclass of orb.Table>
                    lookup          | <orb.LookupOptions>
                    options         | <orb.DatabaseOptions>
        
        :return     [<variant> result, ..]
        """
        return []
    
    def selectFirst(self, table_or_join, lookup, options):
        """
        Returns the first result based on the inputed query options \
        from the database.database.
        
        
        :param      table    | <subclass of Table>
                    lookup   | <orb.LookupOptions>
                    options  | <orb.DatabaseOptions>
        
        :return     <Table> || None
        """
        # limit the lookup information to 1
        lookup.limit = 1
        
        # load the results
        results = self.select( table, query_options, options )
        
        if ( results ):
            return results[0]
        return None
    
    def setThreadEnabled( self, state ):
        """
        Sets whether or not this database backend supports threading.
        
        :param      state | <bool>
        """
        self._threadEnabled = state
    
    def syncRecord( self, record, options ):
        """
        Syncs the record to the current database, checking to \
        see if the record exists, and if so - updates the records \
        field values, otherise, creates the new record.  The possible sync \
        return types are 'created', 'updated', and 'errored'.
        
        :param      record      | <orb.Table>
                    options     | <orb.DatabaseOptions>
        
        :return     (<str> type, <dict> changeet) || None
        """
        changes = record.changeset()
        if ( not changes ):
            return ('', [])
        
        # create the new record in the database
        if ( not record.isRecord() ):
            results = self.insert(record, options)
            if ( 'db_error' in results ):
                return ('errored', results )
            return ('created', results)
        else:
            results = self.update(record, options)
            if ( 'db_error' in results ):
                return ('errored', results)
            return ('updated', results)
    
    def syncTable( self, schema, options):
        """
        Syncs the table to the current database, checking to see
        if the table exists, and if so - updates any new columns,
        otherwise, creates the new table.
        
        :param      schema     | <orb.TableSchema>
                    options    | <orb.DatabaseOptions>
        
        :return     ( <str> type, <bool> changed ) || None
        """
        
        if ( self.tableExists(schema, options) ):
            results = self.updateTable(schema, options)
            return ('created', )
        else:
            results = self.createTable(schema, options)
            return ('updated', results)
    
    @abstractmethod()
    def tableExists(self, schema, options):
        """
        Checks to see if the inputed table class exists as a
        database table.
        
        :param      schema  | <orb.TableSchema>
                    options | <orb.DatabaseOptions>
        
        :return     <bool>
        """
        return False
    
    @abstractmethod()
    def update(self, record, options):
        """
        Updates the database record into the database with the
        given values.
        
        :param      record  | <orb.Table>
                    options | <orb.DatabaseOptions>
        
        :return     <bool>
        """
        return False
    
    @abstractmethod
    def updateTable(self, table, options):
        """
        Determines the difference between the inputed table
        and the table in the database, creating new columns
        for the columns that exist in the table and do not
        exist in the database.
        
        :note       This method will NOT remove any columns, if a column
                    is removed from the table, it will simply no longer 
                    be considered part of the table when working with it.
                    If the column was required by the db, then it will need 
                    to be manually removed by a database manager.  We do not
                    wish to allow removing of columns to be a simple API
                    call that can accidentally be run without someone knowing
                    what they are doing and why.
        
        :param      table    | <orb.TableSchema>
                    options  | <orb.DatabaseOptions>
        
        :return     <bool> success
        """
        return False
    
    @staticmethod
    def init():
        """
        Initializes the backend modules for the connection plugin
        system.  Method is called automatically
        """
        if ( Connection.backends ):
            return
        
        # imports the standard plugins
        projex.importmodules(backends)
        
        # include any additional backends defined by the environment
        modules = os.environ.get('ORB_BACKEND_PLUGINS', '').split(';')
        for module in modules:
            if module:
                try:
                    __import__(module)
                except ImportError:
                    logger.exception('Could not import backend: %s' % module)
    
    @staticmethod
    def create( database ):
        """
        Returns a new datbase connection for the inputed database
        from the registered backends and the database type
        
        :return     <Connection> || None
        """
        # initialize the backend plugins
        Connection.init()
        
        # create the backend plugin
        cls = Connection.backends.get(database.databaseType())
        
        if ( not cls ):
            dbtype = database.databaseType()
            err = errors.BackendNotFoundError(dbtype)
            logger.critical(err)
            return None
        
        return cls(database)
    
    @staticmethod
    def register( databaseType, backend ):
        """
        registers the inputed backend class for the given
        database type
                    
        :param      databaseType        <str>
        :param      backend             <subclass of Connection>
        """
        Connection.backends[str(databaseType)] = backend

if os.environ.get('ORB_AUTO_INIT', 'False') == 'True':
    Connection.init()