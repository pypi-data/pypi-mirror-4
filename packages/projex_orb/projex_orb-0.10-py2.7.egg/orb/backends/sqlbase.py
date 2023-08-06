#!/usr/bin/python

""" Defines the backend connection class for basic SQL based databases. """

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
__depends__        = []
__version_info__   = (0, 0, 0)
__version__        = '%i.%i.%i' % __version_info__

#------------------------------------------------------------------------------

import logging

import projex.errors
from projex.decorators import abstractmethod

from orb                 import errors, Orb
from orb.common          import ColumnType, SelectionMode
from orb.connection      import Connection
from orb.transaction     import Transaction
from orb.table           import Table
from orb.join            import Join
from orb.recordset       import RecordSet
from orb.query           import Query as Q, QueryCompound

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------

class SqlBase(Connection):
    """ 
    Creates a SQL based backend connection type for handling database
    connections to different SQL based databases.  This class can be subclassed
    to define different SQL connections.
    """
    
    # map the default operator types to a SQL operator
    OpMap = {
        Q.Op.Is:                   '=',
        Q.Op.IsNot:                '!=',
        Q.Op.LessThan:             '<',
        Q.Op.LessThanOrEqual:      '<=',
        Q.Op.GreaterThan:          '>',
        Q.Op.GreaterThanOrEqual:   '>=',
        Q.Op.Matches:              '~',
        Q.Op.DoesNotMatch:         '!~'
    }
    
    TypeMap = {
        ColumnType.Bool:        'BOOLEAN',
        
        ColumnType.Decimal:     'DECIMAL',
        ColumnType.Double:      'DOUBLE PRECISION',
        ColumnType.Integer:     'INTEGER',
        
        ColumnType.ForeignKey:  'INTEGER',
        
        ColumnType.Datetime:    'TIMESTAMP',
        ColumnType.Date:        'DATE',
        ColumnType.Time:        'TIME',
        ColumnType.Interval:    'TIMEDELTA',
        
        ColumnType.String:      'CHARACTER VARYING(%(maxlen)s)',
        ColumnType.Color:       'CHARACTER VARYING(25)',
        ColumnType.Email:       'CHARACTER VARYING(%(maxlen)s)',
        ColumnType.Password:    'CHARACTER VARYING(%(maxlen)s)',
        ColumnType.Url:         'CHARACTER VARYING(500)',
        ColumnType.Filepath:    'CHARACTER VARYING(500)',
        ColumnType.Directory:   'CHARACTER VARYING(500)',
        ColumnType.Text:        'TEXT',
        ColumnType.Xml:         'TEXT',
        ColumnType.Html:        'TEXT',
    }
    
    def addMissingColumns( self, schema, columns, options ):
        """
        Adds the missing columns to the given schema.
        
        :param      schema  | <orb.TableSchema>
                    columns | [<str>, ..]
        """
        # create the update sql code
        sql = 'ALTER TABLE "%s" ' % schema.tableName()
        actions = []
        data = {}
        for col_name in columns:
            column = schema.column(col_name)
            action, column_data = self.columnCommand(column)
            data.update(column_data)
            actions.append('ADD COLUMN ' + action)
        
        sql += ','.join(actions) + ';'
        
        if ( options.dryRun ):
            logger.info(sql % data)
        else:
            self.execute(sql, data, returning = False)
            
            opts = (schema.name(), ','.join(columns))
            info = 'Updated %s table: added %s' % opts
            logger.info( info )
    
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
        
        default = column.default()
        if ( default is not None ):
            command += ' DEFAULT %%(%s)s' % column.name()
            data[column.name()] = default
        
        return command, data
    
    def containsCommand( self, caseSensitive ):
        """
        Returns the contains command query for this sql database.
        
        :param      caseSensitive | <bool>
        
        :return     <str>
        """
        if ( not caseSensitive ):
            return 'ILIKE'
        else:
            return 'LIKE'
        
    def cleanValue( self, value ):
        """
        Converts the value to the database version for the given database.
        
        :param      column | <orb.Column>
                    value  | <variant>
        
        :return     <variant>
        """
        # convert the record to its primary key
        if ( Table.recordcheck(value) ):
            pkey = value.primaryKey()
            
            # require the key to exist for a record
            if ( not pkey ):
                err = errors.PrimaryKeyNotFoundError(value.schema().name(), 
                                                     value)
                logger.error( err )
                return None
            
            # ensure the primary key is a tuple of information
            if ( not type(pkey) in (list, tuple) ):
                pkey = (pkey,)
            
            return pkey
        
        # convert list/tuple information to clean values
        if ( type(value) in (list, tuple) ):
            return [self.cleanValue(sub_value) for sub_value in value]
        
        # just return the value
        return value
    
    def createTable( self, schema, options ):
        """
        Creates a new table in the database based cff the inputed
        schema information.  If the dryRun flag is specified, then
        the SQL will only be logged to the current logger, and not
        actually executed in the database.
        
        :param      schema    | <orb.TableSchema>
                    options   | <orb.DatabaseOptions>
        
        :return     <bool> success
        """
        if ( schema.isAbstract() ):
            name = schema.name()
            logger.debug('%s is an abstract table, not creating' % name)
            return False
        
        command, data = self.createTableCommand(schema, options)
        
        if ( not options.dryRun ):
            self.execute(command, data, returning = False)
        else:
            logger.info('SQL: %s' % command)
        
        logger.info('Created %s table.' % schema.tableName())
        
        return True
    
    @abstractmethod('SQLBase')
    def createTableCommand( self, schema, options ):
        """
        Defines the SQL command for creating a table.
        
        :param      schema  | <orb.TableSchema>
                    options | <orb.DatabaseOptions>
        
        :return     <str>
        """
        return ''
    
    def distinct( self, table_or_join, lookup, options ):
        """
        Returns a distinct set of results for the given information.
        
        :param      table_or_join | <subclass of orb.Table> || <orb.Join>
                    lookup        | <orb.LookupOptions>
                    options       | <orb.DatabaseOptions>
        
        :return     {<str> columnName: <list> value, ..}
        """
        command, data   = self.selectCommand(table_or_join, 
                                             lookup, 
                                             options,
                                             distinct = True)
        
        db_fields       = self.fields(table_or_join, 
                                      lookup.columns, 
                                      options.namespace)
        
        # ignore results we know will be empty
        if ( '__RECORDS_ARE_BLANK__' in command ):
            db_results = []
        else:
            db_results = self.execute(command, data)
        
        output     = dict([(column, set()) for column in lookup.columns])
        for schema in db_fields:
            for db_result in db_results:
                for columnName, lookup in db_fields[schema]:
                    output[columnName].add(db_result.get(lookup))
        
        for key, value in output.items():
            output[key] = list(value)
        
        return output
    
    def existingColumns( self, schema, namespace = None ):
        """
        Looks up the existing columns from the database based on the
        inputed schema and namespace information.
        
        :param      schema      | <orb.TableSchema>
                    namespace   | <str> || None
        
        :return     [<str>, ..]
        """
        sql, data = self.schemaColumnsCommand(schema, namespace)
        return self.execute(sql, data, mapper = lambda x: str(x[0]))
    
    @abstractmethod('SQLBase')
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
        return []
    
    def fields( self, table_or_join, columns = None, namespace = None ):
        """
        Creates a field string list to lookup based on the 
        inputed schema and columns.  If the explicit flag is set, then the
        columns will be explict containing the table and column name.
        
        :param      table_or_join  | <subclass of orb.Table> || <orb.Join>
                    columns        | [<str>, ..] || None
                    namespace      | <str> || None
        
        :return     {<orb.TableSchema>: {(<str> columnName, <str> lookup):\
                                          <str> db_field, ..], ..}
        """
        if ( Table.typecheck(table_or_join) ):
            tables = [table_or_join]
        else:
            tables = table_or_join.tables()
        
        output = {}
        for table in tables:
            schema     = table.schema()
            tableName  = schema.tableName()
            tnamespace = namespace
            
            if ( not tnamespace ):
                tnamespace = schema.namespace()
            
            if ( not columns ):
                columns = schema.columnNames()
            
            fieldNames = {}
            for column in columns:
                col = schema.column(column)
                if ( not col ):
                    continue
                
                field  = col.fieldName()
                format = '"%(table)s"."%(field)s" AS "%(table)s_%(field)s"'
                if ( tnamespace ):
                    format = '"%(namespace)s".' + format
                
                opts = {'namespace': tnamespace, 
                        'field': field, 
                        'table': tableName}
                
                lookup = '%(table)s_%(field)s' % opts
                fieldNames[(col.name(), lookup)] = format % opts
            
            output[schema] = fieldNames
        
        return output
    
    def insert( self, record, options ):
        """
        Inserts the table instance into the database.  If the
        dryRun flag is specified, then the command will be 
        logged but not executed.
        
        :param      record   | <orb.Table>
                    options  | <orb.DatabaseOptions>
        
        :return     <dict> changes
        """
        schema      = record.schema()
        tableName   = schema.tableName()
        fields      = []
        slots       = []
        values      = {}
        changes     = {}
        dryRun      = options.dryRun
        
        if ( options.namespace is None ):
            namespace = record.recordNamespace()
        else:
            namespace = options.namespace
        
        # insert the columns 
        for column in schema.columns():
            columnName  = column.name()
            value       = record.recordValue(columnName)
            
            # ignore auto incrementing columns
            if ( column.autoIncrement() ):
                continue
            
            # make sure all the required columns have been set
            elif ( column.required() and value == None ):
                err = errors.ColumnRequiredError(columnName)
                logger.error( err )
                return {'db_error': err}
            
            # no need fo undefined items to be set
            elif ( value == None ):
                continue
            
            changes[columnName] = (None, value)
            
            # update the info into the insertion
            fieldName = column.fieldName()
            fields.append('"%s"' % fieldName)
            slots.append('%%(%s)s' % fieldName)
            
            values[fieldName] = self.cleanValue(value)
        
        if ( not changes ):
            return {}
        
        pkeys = []
        pColumns = schema.primaryColumns()
        for col in pColumns:
            pkeys.append('"%s"' % col.fieldName())
        
        fieldtxt = ','.join(fields)
        slottxt  = ','.join(slots)
        
        if ( namespace ):
            opt      = (namespace, tableName, fieldtxt, slottxt)
            command  = 'INSERT INTO "%s"."%s" (%s) VALUES (%s)'
            command  %= opt
        else:
            opt      = (tableName, fieldtxt, slottxt)
            command  = 'INSERT INTO "%s" (%s) VALUES (%s)' % opt
        
        command += self.returningCommand()
        
        if ( options.dryRun ):
            logger.info( command % values )
        
        else:
            try:
                results = self.execute(command, values, throw = True)
            except Exception, err:
                return {'db_error': err}
            
            # update the record from the database
            if ( results ):
                record._updateFromDatabase(results[0])
            
        return changes
    
    def queryCommand( self, table_or_join, query, data, namespace = None ):
        """
        Converts the inputed query object to a SQL query command.
        
        :param      table_or_join  | <subclass of orb.Table> || <orb.Join>
                    query       | <orb.Query>
                    data        | <dict> | in/out python values for the queries
        
        :return     <str> command
        """
        if ( data is None ):
            data = {}
        
        # convert QueryCompounds to SQL
        if ( QueryCompound.typecheck(query) ):
            # extract the rest of the query information
            sql = []
            for q in query.queries():
                query_sql = self.queryCommand(table_or_join, q, data, namespace)
                if ( not query_sql ):
                    continue
                
                sql.append(query_sql)
            
            if ( not sql ):
                return ''   
            
            optype = ' %s ' % QueryCompound.Op[query.operatorType()].upper()
            return '(%s)' % optype.join(sql)
        
        # initialize the field options
        sql_field_header = ''
        
        table = query.table()
        if ( not table and Table.typecheck(table_or_join) ):
            table = table_or_join
        
        # ensure that we have a table (joins must specify in the query)
        if ( not table ):
            err = errors.InvalidQueryError(query)
            logger.error(err)
            return ''
        
        # extract query valye information
        schema  = table.schema()
        value   = query.value()
        op      = query.operatorType()
        field   = query.columnName()
        index   = 1
        
        # pull the field name from the query information
        column  = schema.column(field)
        if ( column ):
            field = column.fieldName()
        
        # make sure we have a valid field
        if ( not field ):
            if ( not query.table() ):
                logger.error(errors.ColumnNotFoundWarning(field))
                return ''
            
            table           = query.table()
            schema          = table.schema()
            primary_columns = schema.primaryColumns()
            
            if ( len(primary_columns) == 1 ):
                field  = primary_columns[0].fieldName()
                column = primary_columns
            
            elif ( op in (Q.Op.IsIn, Q.Op.IsNotIn) ):
                sub_q = Q()
                for value in value:
                    value_q = Q()
                    
                    if ( len(value) != len(primary_columns) ):
                        logger.error(errors.ColumnNotFoundWarning(field))
                        return ''
                    
                    for i, column in enumerate(primary_columns):
                        value_q &= Q(column) == value[i]
                    sub_q |= value_q
                
                return self.queryCommand(table, sub_q, data, namespace)
            
            elif ( len(primary_columns) != len(value) ):
                value_q = Q()
                for i, column in enumerate(primary_columns):
                    value_q &= Q(column) == value[i]
                
                return self.queryCommand(table, value_q, data, namespace)
                
            else:
                logger.error(errors.ColumnNotFoundWarning(field))
                return ''
        
        # grab the sql for the lookup
        tnamespace  = namespace
        if ( not tnamespace ):
            tnamespace = table.schema().namespace()
        
        if ( tnamespace ):
            db_field = '"%s"."%s"."%s"' % (tnamespace, 
                                           schema.tableName(),
                                           field)
        else:
            db_field = '"%s"."%s"' % (schema.tableName(), field)
        
        # make sure we have a unique data field
        bfield = field
        while (field in data):
            field = bfield + str(index)
            index += 1
        
        # convert a query to SQL
        if ( Q.typecheck(value) ):
            if ( value.table() ):
                v_schema = value.table().schema()
                v_namespace = namespace
                
                if ( v_namespace is None ):
                    v_namespace = v_schema.namespace()
                
                v_table_name = v_schema.tableName()
                v_column     = v_schema.column(value.columnName())
                
                if ( v_column ):
                    v_columnName = v_column.fieldName()
                else:
                    v_columnName = value.columnName()
                
                if ( v_namespace ):
                    db_val = '"%s"."%s"."%s"' % (v_namespace,
                                                 v_table_name,
                                                 v_columnName)
                else:
                    db_val = '"%s"."%s"' % (v_table_name,
                                            v_columnName)
            else:
                v_column = schema.column(value.columnName())
                if ( v_column ):
                    v_columnName = v_column.fieldName()
                else:
                    v_columnName = value.columnName()
                    
                db_val = '"%s"' % v_columnName
        
        # convert a table to sql
        elif ( Table.typecheck(value) ):
            keycol = value.schema().primaryColumns()
            if ( not keycol ):
                return ''
            
            v_table_name = value.schema().tableName()
            column_name  = keycol[0].fieldName()
            v_namespace  = namespace
            
            if ( v_namespace is None ):
                v_namespace = value.namespace()
            
            if ( v_namespace ):
                db_val = '"%s"."%s"."%s"' % (v_namespace,
                                            v_table_name,
                                            column_name)
            else:
                db_val = '"%s"."%s"' % (v_table_name, column_name)
        
        # convert the field to a value
        else:
            db_val = '%%(%s)s' % field
        
        # convert the value from being a record instance to its primary key
        if ( not Q.typecheck(value) and value == Q.ALL ):
            # ignore look ups for all value types - this is a convenient
            # way to accept an optional keyword for a query
            return ''
        
        # look up NOT NULL objects
        elif ( not Q.typecheck(value) and (
               value == Q.NOT_EMPTY or 
               value == None and op == Q.Op.IsNot) ):
            # return where the value is not null
            return '%s IS NOT NULL' % db_field
        
        # look up NULL objects
        elif ( not Q.typecheck(value) and (
               value == Q.EMPTY or
               value == None and op == Q.Op.Is) ):
            # return where the value is null
            return '%s IS NULL' % db_field
        
        elif ( Table.recordcheck(value) ):
            nvalue = value.primaryKey()
            
            if ( not nvalue ):
                err = errors.PrimaryKeyNotDefinedError(value)
                logger.error(err)
                return ''
                
            if ( not type(nvalue) in (list, tuple) ):
                nvalue = (nvalue,)
            
            if ( len(nvalue) == 1 ):
                value = nvalue[0]
            else:
                value = nvalue
        
        elif ( RecordSet.typecheck(value) ):
            value = value.primaryKeys()
        
        elif ( isinstance(value, list) ):
            nvalue = []
            for val in value:
                if ( Table.recordcheck(val) ):
                    pkey = val.primaryKey()
                    
                    if ( not pkey ):
                        err = errors.PrimaryKeyNotDefinedError(val)
                        logger.error(err)
                        return ''
                    
                    if ( not type(pkey) in (list, tuple) ):
                        pkey = (pkey,)
                    
                    nvalue.append(pkey)
                else:
                    nvalue.append(val)
                    
            value = nvalue
        
        else:
            value = self.cleanValue(value)
        
        # look up between options
        if ( op == Q.Op.Between ):
            data[field]         = value[0]
            data[field+'_b']    = value[1]
            
            db_val_b = '%%(%s_b)s' % field
            
            return '(%s <= %s AND %s <= %s)' % (db_val, 
                                                db_field, 
                                                db_field, 
                                                db_val_b)
            
        # look up contains
        elif ( op == Q.Op.Contains ):
            data[field] = '%' + str(value).replace('*','%') + '%'
            
            if ( ' ' in data[field] ):
                data[field] = "'%s'" % data[field]
            
            cmd = self.containsCommand(query.caseSensitive())
            
            return '%s %s %s' % (db_field, cmd, db_val)
            
        # look up does not contain
        elif ( op == Q.Op.DoesNotContain ):
            data[field] = '%' + str(value).replace('*','%') + '%'
            
            if ( ' ' in data[field] ):
                data[field] = "'%s'" % data[field]
            
            cmd = self.containsCommand(query.caseSensitive())
            return '%s NOT %s %s' % (db_field, cmd, db_val)
            
        # look up in options
        elif ( op == Q.Op.IsIn ):
            if ( not value ):
                return '__RECORDS_ARE_BLANK__'
            
            data[field] = tuple(value)
            return '%s IN %s' % (db_field, db_val)
        
        # look up not in options
        elif ( op == Q.Op.IsNotIn ):
            data[field] = tuple(value)
            return '%s NOT IN %s' % (db_field, db_val)
        
        else:
            # look up simple items
            db_op = SqlBase.OpMap.get(op)
            data[field] = value
            if ( not op ):
                err = errors.DatabaseError('Missing operator type: %s' % op)
                logger.error(err)
                return ''
            
            return '%s%s%s' % (db_field, db_op, db_val)
    
    def referenceCommand( self, column ):
        """
        Returns the SQL command that will generate the column information.
        
        :param      column | <orb.Column>
        
        :return     <str>
        """
        # look up the column type based on the reference schema
        ref_model   = column.referenceModel()
        if ( not ref_model ):
            return ''
        
        ref_schema  = ref_model.schema()
        ref_columns = ref_schema.primaryColumns()
        
        if ( len(ref_columns) == 1 ):
            return self.typeCommand(ref_columns[0])
        
        elif ( len(ref_columns) == 0 ):
            msg = '%s has no primary column.' % reference.name()
            err = errors.DatabaseError(msg)
            logger.error(err)
            return ''
        
        else:
            msg = '%s has too many primary columns.' % reference.name()
            err = errors.DatabaseError()
            logger.error(err)
            return ''
    
    def removeRecords( self, schema, records, options ):
        """
        Removes the inputed record from the database.
        
        :param      schema      | <orb.TableSchema>
                    record      | [<variant> primaryKey, ..]
                    options     | <orb.DatabaseOptions>
        
        :return     <int> number of rows removed
        """
        tableName = schema.tableName()
        columns   = schema.primaryColumns()
        data      = {}
        recordsql = []
        
        if ( options.namespace is None ):
            tnamespace = schema.namespace()
        else:
            tnamespace = options.namespace
        
        for pkey in records:
            if ( not type(pkey) in (list, tuple) ):
                pkey = (pkey,)
            
            colsql = []
            for i, col in enumerate(columns):
                fieldName   = col.fieldName()
                entry       = '%s_%si' % (fieldName, len(data))
                data[entry] = pkey[i]
                
                colsql.append('"%s"=%%(%s)s' % (fieldName, entry))
            
            recordsql.append('(%s)' % ','.join(colsql))
        
        pkeyquery = ' OR '.join(recordsql)
        count = len(recordsql)
        
        if ( not tnamespace ):
            sql = 'DELETE FROM "%s" WHERE %s;\n' % (tableName, pkeyquery)
        else:
            sql = 'DELETE FROM "%s"."%s" WHERE %s;\n' % (tnamespace,
                                                         tableName,
                                                         pkeyquery)
        
        if ( options.dryRun ):
            logger.info( sql % data )
        else:
            self.execute(sql, data, returning = False)
        
        return count
    
    def restoreValue( self, column, value ):
        """
        Restores the value from the database for the given column.
        
        :param      column | <orb.Column>
                    value  | <variant>
        """
        coltype = column.columnType()
        
        if ( coltype in (ColumnType.String, 
                         ColumnType.Email, 
                         ColumnType.Password,
                         ColumnType.Filepath,
                         ColumnType.Url)):
            return str(value)
        return value
    
    def returningCommand( self ):
        """
        Returns the SQL command for returning information from an insert or
        update.
        
        :return     <str>
        """
        return ''
    
    @abstractmethod('SQLBase')
    def schemaColumnsCommand( self, schema, namespace = None ):
        """
        Returns the list of columns that exist in the database for the given
        schema.
        
        :param      schema | <orb.TableSchema>
        
        :return     [<str>, ..]
        """
        return '', {}
    
    def select( self, table_or_join, lookup, options ):
        """
        Selects from the database for the inputed items where the
        results match the given dataset information.
        
        :param      table_or_join   | <subclass of orb.Table> || <orb.Join>
                    lookup          | <orb.LookupOptions>
                    options         | <orb.DatabaseOptions>
        
        :return     [({<str> columnName: <variant> value, .., ..), ..]
        """
        command, data   = self.selectCommand(table_or_join, lookup, options)
        db_fields       = self.fields(table_or_join, 
                                      lookup.columns, 
                                      options.namespace)
        
        # ignore records we know will be empty
        if ( '__RECORDS_ARE_BLANK__' in command ):
            db_results = []
        else:
            db_results = self.execute(command, data)
        
        output     = []
        for db_result in db_results:
            records = []
            for schema in db_fields:
                record = {}
                for columnName, lookup in db_fields[schema]:
                    col = schema.column(columnName)
                    val = db_result.get(lookup)
                    
                    record[columnName] = self.restoreValue(col, val)
                
                records.append(record)
            
            output.append(tuple(records))
        
        if ( Table.typecheck(table_or_join) ):
            return map(lambda x: x[0], output)
        return output
    
    @abstractmethod('SQLBase')
    def selectCommand( table_or_join, lookup, options, distinct = False ):
        """
        Generates the SQL for the select statement for the lookup and options.
        
        :param      table_or_join | <subclass of orb.Table> || <orb.Join>
                    lookup        | <orb.LookupOptions>
                    options       | <orb.DatabaseOptions>
                    data          | <dict> | in/out dictionary of values
                    distinct      | <bool>
        
        :return     (<str> sql, <dict> data)
        """
        return '', {}
        
    def serialCommand( self ):
        """
        Returns the serial command for this SQL database.
        
        :return     <str>
        """
        return 'SERIAL'
    
    def tableExists( self, schema, options ):
        """
        Checks to see if the inputed table class exists in the
        database or not.
        
        :param      schema  | <orb.Table>
                    options | <orb.DatabaseOptions>
        
        :return     <bool> exists
        """
        namespace = options.namespace
        if ( not namespace ):
            namespace = schema.namespace()
        
        sql, data = self.tableExistsCommand(schema, namespace)
        if ( not sql ):
            return False
        
        results   = self.execute(sql, data)
        
        if ( results ):
            return True
        return False
    
    @abstractmethod('SQLBase')
    def tableExistsCommand( self, schmea, namepace = None ):
        """
        Returns the SQL command to run to check if the table exists in the
        database.
        
        :param      schema    | <orb.TableSchema>
                    namespace | <str> || None
        
        :return     (<str> sql, <dict> data)
        """
        return ''
    
    def tableNames( self, schemas, namespace = None ):
        """
        Returns the database table name information for the given schemas.
        
        :param      schemas   | [<orb.TableSchema>, ..]
                    namespace | <str> || None
        
        :return     [<str>, ..]
        """
        output = []
        for schema in set(schemas):
            tnamespace = namespace
            if ( not tnamespace ):
                tnamespace = schema.namespace()
            
            table_name = schema.tableName()
            if ( tnamespace ):
                output.append('"%s"."%s"' % (tnamespace, table_name))
            else:
                output.append('"%s"' % table_name)
        return output
    
    def typeCommand( self, column ):
        """
        Returns the type command for the given column type.
        
        :param      columnType | <orb.ColumnType>
        
        :return     <str>
        """
        opts = {'maxlen': column.maxlength()}
        
        return self.TypeMap.get(column.columnType(), '') % opts
    
    def update( self, record, options ):
        """
        Updates the modified data in the database for the 
        inputed record.  If the dryRun flag is specified then
        the command will be logged but not executed.
        
        :param      record     | <orb.Table>
                    options    | <orb.DatabaseOptions>
        
        :return     <dict> changes
        """
        changes = record.changeset()
        
        # make sure we have some changes to commit
        if ( not len(changes) ):
            return {}
        
        # grab the primary key information
        pkey = record.primaryKey()
        if ( not pkey ):
            err = errors.PrimaryKeyNotDefinedError(record)
            logger.error( err )
            return { 'db_error': err }
        
        if ( not type(pkey) in (list, tuple) ):
            pkey = (pkey,)
        
        # extract the lookup data
        schema      = record.schema()
        tableName   = schema.tableName()
        namespace   = options.namespace
        values      = {}
        fields      = []
        
        if ( not namespace ):
            namespace = record.recordNamespace()
        
        # generate the update SQL commands
        for colname, changevals in changes.items():
            column   = schema.column(colname)
            newValue = changevals[1]
            
            if ( not column ):
                logger.error( errors.ColumnNotFoundWarning(colname) )
                continue
            
            elif ( column.required() and newValue == None ):
                logger.error( errors.ColumnRequiredError(colname) )
                continue
            
            fieldName   = column.fieldName()
            values[fieldName] = self.cleanValue(newValue)
            fields.append('"%s"=%%(%s)s' % (fieldName, fieldName))
        
        pkeyColumns = schema.primaryColumns()
        pkeyValues  = record.primaryKey()
        if ( not type(pkeyValues) in (list, tuple) ):
            if ( pkeyValues ):
                pkeyValues = (pkeyValues,)
            else:
                pkeyValues = ()
        
        pvalues     = []
        pkeys       = []
        
        for i, col in enumerate(pkeyColumns):
            fieldName = col.fieldName()
            pvalues.append( '"%s"=%%(%s_pkey)s' % (fieldName, fieldName) )
            pkeys.append( '"%s"' % fieldName )
            values[fieldName+'_pkey'] = pkeyValues[i]
        
        if ( namespace ):
            command = 'UPDATE "%s"."%s" SET ' % (namespace, tableName)
        else:
            command = 'UPDATE "%s" SET ' % tableName
        
        command += ','.join(fields)
        command += ' WHERE ' + ' AND '.join(pvalues)
        command += self.returningCommand()
        
        # pylint: disable-msg=W0212
        if ( options.dryRun ):
            logger.info( command % values )
        else:
            try:
                results = self.execute(command, values, throw = True)
            except Exception, err:
                return {'db_error': err}
            
            if ( results ):
                record._updateFromDatabase(results[0])
        
        return changes.copy()
    
    def updateTable( self, schema, options ):
        """
        Determines the difference between the inputed schema
        and the table in the database, creating new columns
        for the columns that exist in the schema and do not
        exist in the database.  If the dryRun flag is specified,
        then the SQL won't actually be executed, just logged.

        :note       This method will NOT remove any columns, if a column
                    is removed from the schema, it will simply no longer 
                    be considered part of the table when working with it.
                    If the column was required by the db, then it will need to 
                    be manually removed by a database manager.  We do not
                    wish to allow removing of columns to be a simple API
                    call that can accidentally be run without someone knowing
                    what they are doing and why.
        
        :param      schema     | <orb.TableSchema>
                    options    | <orb.DatabaseOptions>
        
        :return     <bool> success
        """
        namespace = options.namespace
        if ( not namespace ):
            namespace = schema.namespace()
        
        # look for existing columns
        
        # determine the new columns
        existing    = self.existingColumns(schema, namespace)
        columns     = schema.columns(recurse = False)
        columnNames = [col.fieldName() for col in  columns]
        missing     = list(set(columnNames).difference(existing))
        
        # if no columns are missing, return True to indicate the table is
        # up to date
        if ( not missing ):
            return True
        
        self.addMissingColumns(schema, missing, options)
        
        return True