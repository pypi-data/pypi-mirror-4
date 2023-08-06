#!/usr/bin/python

""" Defines the backend connection class for Postgres databases. """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintanence information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

# define version information (major,minor,maintanence)
__depends__        = ['pyscopg2']
__version_info__   = (0, 0, 0)
__version__        = '%i.%i.%i' % __version_info__

#------------------------------------------------------------------------------

import logging

import projex.errors

from orb                 import errors, Orb
from orb.connection      import Connection
from orb.transaction     import Transaction
from orb.table           import Table
from orb.join            import Join
from orb.query           import Query as Q
from orb.valuemapper     import ValueMapper

logger = logging.getLogger(__name__)

try:
    import psycopg2 as pg
    from psycopg2.extras import DictCursor
    
except ImportError:
    text = 'For Postgres backend, download the psycopg2 module'
    deperr  = projex.errors.DependencyNotFoundError(text)
    logger.debug( deperr )
    pg = None

#------------------------------------------------------------------------------

from orb.backends.sqlbase import SqlBase

class Postgres(SqlBase):
    """ 
    Creates a PostgreSQL backend connection type for handling database
    connections to Postgres databases.
    """
    def __init__( self, database ):
        super(Postgres, self).__init__(database)
        
        # define custom properties
        self._postgresdb = None
        
        # set standard properties
        self.setThreadEnabled(True)
    
    def close( self ):
        """
        Closes the connection to the datbaase for this connection.
        
        :return     <bool> closed
        """
        if ( not self.isConnected() ):
            return False
        
        self._postgresdb.close()
        self._postgresdb = None
        
        return True
    
    def count( self, table_or_join, lookup, options ):
        """
        Returns the count of records that will be loaded for the inputed 
        information.
        
        :param      table_or_join | <subclass of orb.Table> || None
                    lookup        | <orb.LookupOptions>
                    options       | <orb.DatabaseOptions>
        
        :return     <int>
        """
        sql, data = self.selectCommand(table_or_join, lookup, options)
        sql = 'SELECT COUNT(*) AS "count" FROM (%s) as records' % sql
        return sum(self.execute(sql, data, mapper = lambda x: dict(x)['count']))
    
    def commit( self ):
        """
        Commits the changes to the current database connection.
        
        :return     <bool> success
        """
        if ( not self.isConnected() ):
            return False
        
        if ( Transaction.current() ):
            Transaction.current().setDirty(self)
        else:
            self._postgresdb.commit()
        return True
    
    def createTableCommand( self, schema, options ):
        """
        Defines the table SQL creation commands.
        
        :param      schema  | <orb.TableSchema>
                    options | <orb.DatabaseOptions>
        
        :return     <str>
        """
        # make sure we have the namespace
        namespace = options.namespace
        if ( not namespace ):
            namespace = schema.namespace()
        
        tableName   = schema.tableName()
        inherits    = []
        cols        = []
        constraints = []
        data        = {}
        
        # convert the column information to command
        for column in schema.columns(recurse = False):
            col, col_data = self.columnCommand(column)
            if ( not col ):
                continue
            
            # add the column
            cols.append(col)
            data.update(col_data)
        
        # create inherited table information
        for schemaName in schema.inherits().split(','):
            inherits_schema = Orb.instance().schema(schemaName)
            if ( not inherits_schema ):
                continue
                
            inherits_table = inherits_schema.tableName()
            if ( not (inherits_table and inherits_table != tableName) ):
                continue
            
            inherits.append(inherits_table)
        
        # create primary key constraints
        pkeys = schema.primaryColumns()
        if ( pkeys and not schema.inherits() ):
            pkey_names = [ '"%s"' % col.fieldName() for col in pkeys ]
            options = (tableName, ','.join(pkey_names))
            constraint = 'CONSTRAINT "%s_pkey" PRIMARY KEY (%s)' % options
            constraints.append( constraint )
        
        # create the SQL query
        if ( namespace ):
            sql = 'CREATE TABLE "%s"."%s" (\n' % (namespace, tableName)
        else:
            sql = 'CREATE TABLE "%s" (\n' % tableName
        
        if ( cols ):
            sql += ',\n'.join(cols)
            sql += ',\n'
        
        if ( constraints ):
            sql += ',\n'.join(constraints)
            
        sql = sql.strip().rstrip(',')
        sql += '\n)'
        
        if ( inherits ):
            sql += '\nINHERITS ("%s")' % ','.join(inherits)
        
        username = self.database().username()
        sql += ' WITH ( OIDS=FALSE );\n'
        
        if ( namespace ):
            sql += 'ALTER TABLE "%s"."%s" OWNER to "%s"' % (namespace,
                                                                tableName,
                                                                username)
        else:
            sql += 'ALTER TABLE "%s" OWNER TO "%s";' % (tableName, username)
        
        return sql, data
    
    def isConnected( self ):
        """
        Returns whether or not this conection is currently
        active.
        
        :return     <bool> connected
        """
        return self._postgresdb != None
    
    def execute( self, 
                 command, 
                 data       = None, 
                 throw      = False,
                 autoCommit = True,
                 autoClose  = True,
                 returning  = True,
                 mapper     = dict ):
        """
        Executes the inputed command into the current \
        connection cursor.
        
        :param      command    | <str>
                    data       | <dict> || None
                    throw      | <bool> | determine whether to raise error
                    autoCommit | <bool> | commit database changes immediately
                    autoClose  | <bool> | closes connections immediately
        
        :return     [{<str> key: <variant>, ..}, ..]
        """
        if ( data is None ):
            data = {}
            
        # open the connection if it is not alrady open
        if ( not self.open() ):
            return {}
        
        # when in debug mode, simply log the command to the logger
        elif ( self.database().commandsBlocked() ):
            logger.info(command % data)
            return {}
        
        for key, value in data.items():
            data[key] = ValueMapper.mappedValue(value)
        
        # create a new cursor for this transaction
        cursor = self._postgresdb.cursor(cursor_factory=DictCursor)
        
        sql = (command % data)
        dbg = '[orb.backends.postgres] %s' % sql
        logger.debug( dbg )
        
        try:
            cursor.execute(command, data)
            
        except pg.Error:
            err = errors.DatabaseQueryError(command, data)
            
            if ( Transaction.current() ):
                Transaction.current().rollback(err)
            
            self.rollback()
            
            logger.exception(err)
            if ( throw ):
                raise err
            return {}
        
        except pg.ProgrammingError:
            self._postgresdb.rollback()
            err = errors.DatabaseQueryError(command, data)
            logger.exception(err)
            if ( throw ):
                raise
            return {}
        
        if ( returning ):
            results = map(mapper, cursor.fetchall())
        else:
            results = []
        
        if ( autoCommit ):
            self.commit()
        if ( autoClose ):
            cursor.close()
        
        return results
    
    def open( self ):
        """
        Opens a new database connection to the datbase defined
        by the inputed database.
        
        :return     <bool> success
        """
        # make sure we have a postgres module
        if ( not pg ):
            return False
        
        # check to see if we already have a connection going
        if ( self._postgresdb ):
            return True
        
        elif ( not self._database ):
            logger.error( errors.DatabaseNotFoundError() )
            return False
        
        dbname  = self._database.databaseName()
        user    = self._database.username()
        pword   = self._database.password()
        host    = self._database.host()
        if ( not host ):
            host = 'localhost'
        
        port    = self._database.port()
        if ( not port ):
            port = 5432
        
        # create the python connection
        try:
            self._postgresdb    = pg.connect(   database = dbname, 
                                                user     = user, 
                                                password = pword, 
                                                host     = host, 
                                                port     = port )
        except pg.OperationalError:
            logger.exception('Error connecting to database.')
            self._postgresdb = None
            return False
            
        return True
    
    def rollback( self ):
        """
        Rollsback changes made to this database.
        """
        self._postgresdb.rollback()
        return True
    
    def returningCommand( self ):
        """
        Returns the SQL command for returning information from an insert or
        update.
        
        :return     <str>
        """
        return ' RETURNING *'
    
    def schemaColumnsCommand( self, schema, namespace = None ):
        """
        Returns the list of columns that exist in the database for the given
        schema.
        
        :param      schema | <orb.TableSchema>
        
        :return     [<str>, ..]
        """
        if ( not namespace ):
            namespace = 'public'
        
        # collect existing column names
        data = { 'schema': namespace, 'table': schema.tableName() }
        sql = 'SELECT column_name FROM information_schema.columns\
               WHERE table_name=%(table)s AND table_schema=%(schema)s'
        
        return sql, data
    
    def selectCommand( self, table_or_join, lookup, options, distinct = False ):
        """
        Generates the SQL for the select statement for the lookup and options.
        
        :param      table_or_join | <subclass of orb.Table> || <orb.Join>
                    lookup        | <orb.LookupOptions>
                    options       | <orb.DatabaseOptions>
                    data          | <dict> | in/out dictionary of values
        
        :return     (<str> sql, <dict> data)
        """
        # grab the database field information
        db_fields  = self.fields(table_or_join, 
                                 lookup.columns, options.namespace)
        
        db_schemas = db_fields.keys()
        
        if ( lookup.where ):
            db_schemas += [table.schema() for table in lookup.where.tables()]
        
        db_tables = self.tableNames(db_schemas, options.namespace)
        
        # make sure we have information to select
        if ( not (db_fields and db_tables) ):
            return []
        
        all_fields      = []
        distinct_fields = []
        for schema, fields in db_fields.items():
            for key, value in fields.items():
                all_fields.append(value)
                
                column = schema.column(key[0])
                if ( column.primary() or \
                    (lookup.columns and not key[0] in lookup.columns) ):
                    continue
                
                distinct_fields.append(key[1])
        
        if ( distinct ):
            distinct_fields = ','.join(distinct_fields)
            sql = ['SELECT DISTINCT ON (%s) %s FROM %s' % (distinct_fields,
                                                           ','.join(all_fields),
                                                           ','.join(db_tables))]
        else:
            sql = ['SELECT %s FROM %s' % (','.join(all_fields), 
                                          ','.join(db_tables))]
        
        # add a where clause
        data = {}
        if ( lookup.where ):
            where_sql = self.queryCommand(table_or_join,
                                          lookup.where,
                                          data, 
                                          options.namespace)
            if ( where_sql ):
                sql.append('WHERE ' + where_sql)
        
        # add ordering options
        if ( lookup.order ):
            order_sql = []
            
            if ( Table.typecheck(table_or_join) ):
                tables = [table_or_join]
            else:
                tables = table_or_join.tables()
            
            for table in tables:
                schema    = table.schema()
                tableName = schema.tableName()
                
                for col_name, typ in lookup.order:
                    col = schema.column(col_name)
                    if ( not col ):
                        continue
                    
                    namespace = options.namespace
                    if ( namespace ):
                        namespace = schema.namespace()
                    
                    column_sql = '"%s"."%s" %s' % (tableName, 
                                                  col.fieldName(),
                                                  typ.upper())
                    if ( namespace ):
                        column_sql += '"%s".' % namespace
                    
                    order_sql.append(column_sql)
                
            sql.append('ORDER BY ' + ','.join(order_sql))
        
        # add the limit lookup
        if ( lookup.limit is not None ):
            sql.append('LIMIT %i' % lookup.limit)
        
        if ( lookup.start is not None ):
            sql.append('OFFSET %i' % lookup.start)
        
        return '\n'.join(sql), data
    
    def tableExistsCommand( self, schema, namespace = None ):
        """
        Returns the SQL command to run to check if the table exists in the
        database.
        
        :param      schema    | <orb.TableSchema>
                    namespace | <str> || None
        
        :return     (<str> sql, <dict> data)
        """
        if ( not namespace ):
            namespace = 'public'
        
        # check to see if the table exists
        data  = {'schema': namespace, 'table': schema.tableName()}
        sql   = """SELECT table_name FROM information_schema.tables\
                   WHERE table_schema=%(schema)s AND table_name=%(table)s"""
        
        return sql, data
    
# register the postgres backend
if ( pg ):
    Connection.register( 'Postgres', Postgres )