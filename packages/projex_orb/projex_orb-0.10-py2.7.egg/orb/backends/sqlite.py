#!/usr/bin/python

""" Defines the backend connection class for SQLite databases. """

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
__depends__        = ['sqlite3']
__version_info__   = (0, 0, 0)
__version__        = '%i.%i.%i' % __version_info__

#------------------------------------------------------------------------------

import datetime
import logging
import os.path
import re

import projex.text
import projex.errors

from orb                 import errors, Orb
from orb.common          import ColumnType
from orb.connection      import Connection
from orb.transaction     import Transaction
from orb.table           import Table
from orb.join            import Join
from orb.query           import Query as Q
from orb.valuemapper     import ValueMapper

logger = logging.getLogger(__name__)

try:
    import sqlite3 as sqlite
    
except ImportError:
    text = 'For SQLite backend, ensure your python version supports sqlite3'
    deperr  = projex.errors.DependencyNotFoundError(text)
    logger.debug( deperr )
    sqlite = None

#------------------------------------------------------------------------------

from orb.backends.sqlbase import SqlBase

FORMAT_EXPR = re.compile('(%\(([^\)]+)\)s)')

def dict_factory(cursor, row):
    """
    Converts the cursor information from a SQLite query to a dictionary.
    
    :param      cursor | <sqlite3.Cursor>
                row    | <sqlite3.Row>
    
    :return     {<str> column: <variant> value, ..}
    """
    out = {}
    for i, col in enumerate(cursor.description):
        out[col[0]] = row[i]
    return out

#------------------------------------------------------------------------------

class SQLite(SqlBase):
    """ 
    Creates a SQLite backend connection type for handling database
    connections to SQLite databases.
    """
    TypeMap = {
        ColumnType.Bool:        'INTEGER',
        
        ColumnType.Decimal:     'REAL',
        ColumnType.Double:      'REAL',
        ColumnType.Integer:     'INTEGER',
        
        ColumnType.ForeignKey:  'INTEGER',
        
        ColumnType.Datetime:    'TEXT',
        ColumnType.Date:        'TEXT',
        ColumnType.Time:        'TEXT',
        ColumnType.Interval:    'TEXT',
        
        ColumnType.String:      'TEXT',
        ColumnType.Color:       'TEXT',
        ColumnType.Email:       'TEXT',
        ColumnType.Password:    'TEXT',
        ColumnType.Url:         'TEXT',
        ColumnType.Filepath:    'TEXT',
        ColumnType.Directory:   'TEXT',
        ColumnType.Text:        'TEXT',
        ColumnType.Xml:         'TEXT',
        ColumnType.Html:        'TEXT',
    }
    
    def __init__( self, database ):
        super(SQLite, self).__init__(database)
        
        self._sqlitedb = None
    
    def addMissingColumns( self, schema, columns, options ):
        """
        Adds the missing columns to the given schema.
        
        :param      schema  | <orb.TableSchema>
                    columns | [<str>, ..]
        """
        trans = Transaction()
        trans.begin()
        for column in columns:
            super(SQLite, self).addMissingColumns(schema, [column], options)
        trans.end()
    
    def close( self ):
        """
        Closes the connection to the datbaase for this connection.
        
        :return     <bool> closed
        """
        if ( not self.isConnected() ):
            return False
        
        self._sqlitedb.close()
        self._sqlitedb = None
        
        return True
    
    def cleanValue( self, value ):
        """
        Cleans the value for the insertion to the database.
        
        :param      value | <variant>
        """
        if ( type(value) == bool ):
            return int(value)
        elif ( type(value) in (int, float) ):
            return value
        elif ( Table.recordcheck(value) ):
            result = super(SQLite, self).cleanValue(value)
            if ( type(result) == tuple ):
                return result[0]
            return result
        elif ( value is None ):
            return 0
        else:
            return str(value)
    
    def containsCommand( self, caseSensitive ):
        """
        Returns the contains command query for this sql database.
        
        :param      caseSensitive | <bool>
        
        :return     <str>
        """
        return 'LIKE'
    
    def columnCommand( self, column ):
        """
        Converts the inputed column object to a SQL creation command.
        
        :param      column  | <orb.Column>
        
        :return     (<str> command, <dict> data)
        """
        data = {}
        
        # create a new foreign key reference
        if ( column.isReference() ):
            refname     = column.reference()
        
            # make sure there is a valid reference
            if ( not refname ):
                err = errors.ForeignKeyMissingReferenceError(column)
                logger.error ( err )
                return '', {}
            
            # make sure we have a valid table in the schema
            reference   = Orb.instance().schema(refname)
            if ( not reference ):
                err = errors.TableNotFoundError(refname)
                logger.error( err )
                return '', {}
            
            db_type = self.referenceCommand(column)
        else:
            db_type = self.typeCommand(column)
        
        # validates that we have a valid database type
        if ( not db_type ):
            err = errors.InvalidColumnTypeError(column.columnType())
            logger.error( err )
            return '', {}
        
        # for auto incrementing integers, use the serial data type
        if ( column.columnType() == ColumnType.Integer and \
             column.autoIncrement() ):
            db_type = self.serialCommand()
        
        command = '"%s" %s' % (column.fieldName(), db_type)
        if ( column.required() ):
            command += ' NOT NULL'
        
        return command, data
    
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
            self._sqlitedb.commit()
    
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
    
    def createTableCommand( self, schema, options ):
        """
        Defines the table SQL creation commands.
        
        :param      schema  | <orb.TableSchema>
                    options | <orb.DatabaseOptions>
        
        :return     <str>
        """
        tableName   = schema.tableName()
        cols        = []
        constraints = []
        data        = {}
        
        # convert the column information to command
        for column in schema.columns():
            col, col_data = self.columnCommand(column)
            if ( not col ):
                continue
            
            # add the column
            cols.append(col)
            data.update(col_data)
        
        # create the SQL query
        sql = 'CREATE TABLE "%s" (\n' % tableName
        
        if ( cols ):
            sql += ',\n'.join(cols)
            sql += ',\n'
        
        sql = sql.strip().rstrip(',')
        sql += '\n)'
        
        return sql, data
    
    def existingColumns( self, schema, namespace = None ):
        """
        Looks up the existing columns from the database based on the
        inputed schema and namespace information.
        
        :param      schema      | <orb.TableSchema>
                    namespace   | <str> || None
        
        :return     [<str>, ..]
        """
        sql = 'PRAGMA table_info(%s)' % schema.tableName()
        return self.execute(sql, {}, mapper = lambda x: x['name'])
    
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
        
        # create a new cursor for this transaction
        cursor = self._sqlitedb.cursor()
        
        sql = (command % data)
        dbg = '[orb.backends.sqlite] %s' % sql
        logger.debug( dbg )
        
        # map the dictionary options to the parameter based required by sqlite
        args = []
        for grp, key in FORMAT_EXPR.findall(command):
            value = ValueMapper.mappedValue(data[key])
            
            if ( type(value) in (list, tuple) ):
                def _gen_subvalue(val):
                    out  = []
                    repl = []
                    
                    for sub_value in val:
                        if ( type(sub_value) in (list, tuple) ):
                            cmd, vals = _gen_subvalue(sub_value)
                            repl.append(cmd)
                            out += vals
                        else:
                            repl.append('?')
                            out.append(sub_value)
                    
                    return '(' + ','.join(repl) + ')', out
                
                repl, values = _gen_subvalue(value)
                command = command.replace(grp, repl)
                args += values
            else:
                command = command.replace(grp, '?')
                args.append(value)
        
        args = tuple(args)
        
        try:
            cursor.execute(command, args)
            
        except Exception:
            # log an error
            err = errors.DatabaseQueryError(command, args)
            
            # rollback the full transaction
            if ( Transaction.current() ):
                Transaction.current().rollback(err)
            
            self.rollback()
            logger.exception(err)
            if ( throw ):
                raise err
            
            return {}
        
        if ( returning ):
            results = map(mapper, cursor.fetchall())
            if ( not results and cursor.lastrowid ):
                results = [{'PRIMARY_KEY': cursor.lastrowid}]
        else:
            results = []
        
        if ( autoCommit ):
            self.commit()
        
        if ( autoClose ):
            cursor.close()
        
        return results
    
    def isConnected( self ):
        """
        Returns whether or not this conection is currently
        active.
        
        :return     <bool> connected
        """
        return self._sqlitedb != None
    
    def open( self ):
        """
        Opens a new database connection to the datbase defined
        by the inputed database.
        
        :return     <bool> success
        """
        # make sure we have a sqlite module
        if ( not sqlite ):
            return False
        
        # check to see if we already have a connection going
        if ( self._sqlitedb ):
            return True
        
        elif ( not self._database ):
            logger.error( errors.DatabaseNotFoundError() )
            return False
        
        # create the name of the database
        dbname  = os.path.normpath(str(self._database.databaseName()))
        
        # create the python connection
        try:
            self._sqlitedb = sqlite.connect(dbname)
            self._sqlitedb.row_factory = dict_factory
        
        except sqlite.Error:
            logger.exception('Error connecting to database.')
            self._sqlitedb = None
            return False
            
        return True
    
    def restoreValue( self, column, value ):
        """
        Restores the value from the database for the given column.
        
        :param      column | <orb.Column>
                    value  | <variant>
        """
        coltype = column.columnType()
        
        if ( coltype == ColumnType.Date ):
            return datetime.datetime.strptime(str(value), '%Y-%m-%d').date()
        elif ( coltype == ColumnType.Time ):
            return datetime.datetime.strptime(str(value), '%H:%M:%S').time()
        elif ( coltype == ColumnType.Datetime ):
            return datetime.datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S')
        elif ( coltype == ColumnType.Bool ):
            return bool(value)
        
        return super(SQLite, self).restoreValue(column, value)
    
    def rollback( self ):
        """
        Rolls back changes to this database.
        """
        self._sqlitedb.rollback()
        return True
    
    def serialCommand( self ):
        """
        Returns the serial command for this SQL database.
        
        :return     <str>
        """
        return 'INTEGER PRIMARY KEY ASC'
    
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
                
                distinct_fields.append(value)
        
        if ( distinct ):
            sql = ['SELECT DISTINCT %s FROM %s' % (','.join(distinct_fields),
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
        # check to see if the table exists
        data = {'table': schema.tableName()}
        sql = "SELECT tbl_name FROM sqlite_master WHERE type='table' AND "\
              "tbl_name=%(table)s"
        
        return sql, data
    
# register the sqlite backend
if ( sqlite ):
    Connection.register('SQLite', SQLite)