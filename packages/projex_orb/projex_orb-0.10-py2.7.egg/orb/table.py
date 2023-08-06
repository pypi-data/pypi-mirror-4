#!/usr/bin/python

""" 
Defines the main Table class that will be used when developing
database classes.
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

json = None # loaded later

import datetime
import logging
import re

import projex.text

from projex             import security
from projex.decorators  import abstractmethod

import orb

from orb.caching     import RecordCache, DataCache
from orb.tablebase   import TableBase
from orb.common      import RemovedAction, SearchMode
from orb._orb        import Orb
from orb             import errors, Query as Q
from orb.valuemapper import ValueMapper

logger = logging.getLogger(__name__)

TEMPLATE_PATTERN = re.compile('\[([^\]:]+[^\]]*)\]')

#------------------------------------------------------------------------------

class Table(object):
    """ 
    Defines the base class type that all database records should inherit from.
    """
    # define the table meta class
    __metaclass__       = TableBase
    
    # meta database information
    __db__              = ''         # name of DB in Environment for this model
    __db_group__        = 'Default'  # name of database group
    __db_name__         = ''         # name of database schema (defaults to 
                                     # class name)
    __db_tablename__    = ''         # name of table in database (defaults to 
                                     # [group]_[schemaname])
    __db_schema__       = None       # <TableSchema> for direct creation
    
    # define class level properties
    _recordCacheStack = None         # stack of cached information
    _baseTableQuery   = None
    
    @classmethod
    def __syncdatabase__( cls ):
        """
        This method will be called after all creation and updating syncing
        is called for a database sync.  It will allow a developer to specify
        default information for their class type.
        """
        pass
    
    def __str__( self ):
        """
        Defines the custom string format for this table.
        """
        schema = self.schema()
        format = ''
        orb_   = Orb.instance()
        
        while ( not format and schema ):
            format = schema.stringFormat()
            schema = orb_.schema(schema.inherits())
        
        if ( not format ):
            return super(Table, self).__str__()
        
        try:
            output = format % self.recordValues()
        
        except KeyError:
            output = super(Table, self).__str__()
        
        return output
    
    def __eq__( self, other ):
        """
        Checks to see if the two records are equal to each other
        by comparing their primary key information.
        
        :param      other       <variant>
        
        :return     <bool>
        """
        return id(self) == id(other) or hash(self) == hash(other)
    
    def __ne__( self, other ):
        """
        Returns whether or not this object is not equal to the other object.
        
        :param      other | <variant>
        
        :return     <bool>
        """
        return not self.__eq__(other)
    
    def __hash__( self ):
        """
        Creates a hash key for this instance based on its primary key info.
        
        :return     <int>
        """
        # use the base id information
        if ( not self.isRecord() ):
            return super(Table, self).__hash__()
        
        # return a combination of its table and its primary key hashes
        return hash((self.__class__, self.primaryKey()))
    
    def __init__( self, *args, **kwds ):
        """
        Initializes a database record for the table class.  A
        table model can be initialized in a few ways.  Passing
        no arguments will create a fresh record that does not
        exist in the database.  Providing keyword arguments will
        map to this table's schema column name information, 
        setting default values for the record.  Suppling an 
        argument will be the records unique primary key, and 
        trigger a lookup from the database for the record directly.
        
        :param      *args       <tuple> primary key
        :param      **kwds      <dict>  column default values
        """
        # define table properties in a way that shouldn't be accidentally
        # overwritten
        self.__record_defaults      = {}
        self.__record_values        = {}
        self.__record_database      = None
        self.__record_datacache     = None
        self.__record_dbloaded      = False
        self.__record_namespace     = None
        
        # specify a particular database this model should run in
        if ( 'db' in kwds ):
            self.__record_database      = kwds.pop('db')
        
        if ( 'recordNamespace' in kwds ):
            self.__record_namespace     = kwds.pop('recordNamespace')
        
        # initialize the defaults
        if ( not args ):
            self.initRecord()
            self.resetRecord()
        
        # initialize from the database
        else:
            # extract the primary key for initializing from a record
            if ( len(args) == 1 and Table.recordcheck(args[0]) ):
                record  = args[0]
                args    = record.primaryKey()
                values  = record.recordValues().copy()
                values.update(kwds)
                kwds    = values
            
            elif ( len(args) == 1 ):
                args = args[0]
            
            data = self.selectFirst(where = Q(type(self)) == args,
                                    limit = 1,
                                    namespace = self.__record_namespace,
                                    inflated = False)
            if ( data ):
                self._updateFromDatabase(data)
            
        self.setRecordValues(**kwds)
    
    # protected methods
    def _updateFromDatabase( self, values ):
        """
        Called from the connection class when it needs to
        manipulate information on this record instance.
        
        :param      values      { <str> key: <variant>, .. }
        """
        schema       = self.schema()
        tableName    = schema.tableName()
        dvalues      = {}
        
        for key, value in values.items():
            if ( key == 'PRIMARY_KEY' ):
                primary = self.schema().primaryColumns()
                if ( not type(value) in (list, tuple) ):
                    value = (value,)
                if ( len(primary) != len(value) ):
                    errors.InvalidPrimaryKeyError(primary, value)
                    continue
                
                for i, col in enumerate(primary):
                    dvalues[col.name()] = value[i]
                continue
                
            try:
                tname, colname = key.split('.')
            except ValueError:
                colname = key
                tname = tableName
            
            # value being set for another table from a join
            if ( tname != tableName ):
                continue
            
            column = schema.column(colname)
            if ( not column ):
                continue
            
            dvalues[column.name()] = value
            
        # pylint: disable-msg=W0142
        self.__record_values.update(dvalues)
        self.__record_defaults.update(dvalues)
        self.__record_dbloaded = True
        
    def _removedFromDatabase( self ):
        """
        Called after a record has been removed from the
        database, so the record instance can clean up
        any additional information.
        """
        self.__record_defaults     = {}
        self.__record_dbloaded     = False
    
    # public methods
    def changeset( self ):
        """
        Returns a dictionary of changees that have been made 
        to the data from this record.
        
        :return     { <fieldName>: ( <variant> old, <variant> new), .. }
        """
        changes = {}
        
        for column in self.schema().columns():
            columnName      = column.name()
            newValue        = self.__record_values.get(columnName)
            oldValue        = self.__record_defaults.get(columnName)
            
            # compare two datetimes
            if ( isinstance(newValue, datetime.datetime) and 
                 isinstance(oldValue, datetime.datetime) ):
                
                try:
                    equal = newValue == oldValue
                except TypeError:
                    equal = str(newValue) == str(oldValue)
            
            # compare all other types
            else:
                equal = newValue == oldValue
            
            if ( not equal ):
                changes[columnName] = (oldValue, newValue)
            
        return changes
    
    def commit( self, **kwds ):
        """
        Commits the current change set information to the database,
        or inserts this object as a new record into the database.
        This method will only update the database if the record
        has any local changes to it, otherwise, no commit will
        take place.  If the dryRun flag is set, then the SQL
        will be logged but not executed.
        
        :note       From version 0.6.0 on, this method now accepts a mutable
                    keyword dictionary of values.  You can supply any member 
                    value for either the <orb.LookupOptions> or
                    <orb.DatabaseOptions>, 'options' for 
                    an instance of the <orb.DatabaseOptions>
        
        :return     (<str> commit type, <dict> changeset) || None
        """
        options = kwds.get('options', orb.DatabaseOptions(**kwds))
        out     = self.database().connection().syncRecord(self, options)
        
        if ( out and not 'error' in out ):
            self.__record_defaults = self.__record_values.copy()
            
            # clear the cache on changes
            cache = self.recordCache()
            if ( cache ):
                cache.clear()
        
        return out
    
    def database( self ):
        """
        Returns the database instance for this record.  If no \
        specific datbase is defined, then the database will be looked up \
        based on the name, environment, and current settings from the current \
        Orb manager.
        
        :return     <Database> || None
        """
        if ( self.__record_database ):
            return self.__record_database
        
        return self.getDatabase()
    
    def dataCache( self ):
        """
        Returns the cache instance record for this record.
        
        :return     <DataCache>
        """
        if ( not self.__record_datacache ):
            self.__record_datacache = DataCache()
        return self.__record_datacache
    
    def duplicate( self ):
        """
        Creates a new record based on this instance, initializing
        it with the data from this record.
        
        :return     <Table>
        """
        return self.__class__(**self.recordValues())
    
    def initRecord( self ):
        """
        Initializes the default values for this record.
        """
        for column in self.schema().columns():
            key = column.name()
            self.__record_defaults[key] = column.default(resolve = True)
    
    def isModified( self ):
        """
        Returns whether or not any data has been modified for
        this object.
        
        :return     <bool>
        """
        return len(self.changeset()) > 0
    
    def isRecord( self ):
        """
        Returns whether or not this database table record exists
        in the database.
        
        :return     <bool>
        """
        return self.__record_dbloaded
    
    def primaryKey( self ):
        """
        Returns the values for the primary key for this record.
        It is important to note, that this will return the column
        values as they are in the database, not as they are on the
        class instance.
        
        :return     <variant> | will return a tuple or column value
        
        :usage      |>>> # this is just an example, not a provided class
                    |>>> from somemodule import Person
                    |>>> p = Person('Eric','Hulser')
                    |>>> p.isRecord()
                    |True
                    |>>> [ col.name() for col in p.schema().primaryColumns() ]
                    |['firstName','lastName']
                    |>>> p.primaryKey()
                    |('Eric','Hulser')
                    |>>> p.setLastName('Smith')
                    |>>> # accessing the column reflects the data on the object
                    |>>> p.firstName(), p.lastName()
                    |('Eric','Smith')
                    |>>> # accessing the pkey reflects the data in the db
                    |>>> p.primaryKey()
                    |('Eric','Hulser')
                    |>>> # committing to the db will update the database,
                    |>>> # and on success, update the object record
                    |>>> p.commit()
                    |{'updated',{'lastName': ('Hulser','Smith')})
                    |>>> # now that the changes are in the DB, the pkey is
                    |>>> # updated to reflect the record
                    |>>> p.primaryKey()
                    |('Eric','Smith')
        """
        cols     = self.schema().primaryColumns()
        defaults = self.__record_defaults
        output   = [defaults.get(col.name()) for col in cols]
        
        if ( len(output) == 1 ):
            return output[0]
        return tuple(output)
    
    def reloadColumns( self, columns = None ):
        """
        Reloads tne information from the database for the
        given columns.  If no columns are specified, then
        all the columns will be reloaded.
        
        :sa         loadColumns
        
        :param      columns     [ <str> name, ] || None
        """
        if ( not columns ):
            self.__record_defaults.clear()
        else:
            for col in columns:
                if ( col in self.__record_defaults ):
                    self.__record_defaults.pop(col)
        
        self.loadColumns(columns)
    
    def remove( self, **kwds ):
        """
        Removes this record from the database.  If the dryRun \
        flag is specified then the command will be logged and \
        not executed.
        
        :note       From version 0.6.0 on, this method now accepts a mutable
                    keyword dictionary of values.  You can supply any member 
                    value for either the <orb.LookupOptions> or
                    <orb.DatabaseOptions>, as well as the keyword 'lookup' to 
                    an instance of <orb.LookupOptions> and 'options' for 
                    an instance of the <orb.DatabaseOptions>
        
        :return     <int>
        """
        # checks to see if this is a record
        if ( not self.isRecord() ):
            return 0
        
        # lookup all relations recursively
        cascade_remove  = []
        options         = kwds.get('options', orb.DatabaseOptions(**kwds))
        pkey            = self.primaryKey()
        relations       = Orb.instance().findRelations(self.schema())
        
        for table, columns in relations:
            for column in columns:
                action = column.referenceRemovedAction()
                
                # determine the reference information
                if ( action == RemovedAction.Block ):
                    result = table.selectFirst(where = Q(column.name()) == pkey)
                    if ( result ):
                        msg = 'Cannot remove %s, remove %s records first.'
                        msg %= (self, table.__name__)
                        raise errors.CannotRemoveError(msg)
                
                # add cascaded removal
                elif ( action == RemovedAction.Cascade ):
                    records = table.select(where = Q(column.name()) == pkey)
                    cascade_remove.append(records)
        
        # handle permanent deletion
        count = 0
        for cascaded in cascade_remove:
            count += cascaded.remove(options = options)
            
        schema = self.schema()
        count += self.database().connection().remove(schema, [self], options)
        
        # clear the cache for this record if records were removed
        if ( count ):
            cache = self.recordCache()
            if ( cache ):
                cache.clear()
    
        return count
    
    def resetRecord( self ):
        """
        Resets the values for this record to the database
        defaults.
        """
        self.__record_values = self.__record_defaults.copy()
    
    @abstractmethod
    def retire( self ):
        """
        Generic method to "retire" a record.  Each record will handle retirement
        differently, so the system only provides the removal framework for it, 
        but does not support a generic retirement system.  To use this, subclass
        the Table class and implement the retirement method.
        
        :return     <int> | numer of records retired
        """
        return 0
    
    def setDatabase( self, database ):
        """
        Sets the specific database instance that this
        record will be using when executing transactions.
        
        :param      database        <Database> || None
        """
        self.__record_database = database
    
    def setRecordDefault( self, columnName, value ):
        """
        Sets the default value for the column name at the given value.
        
        :param      columnName | <str>
                    value      | <variant>
        
        :return     <bool> | success
        """
        if ( not columnName in self.__record_defaults ):
            return False
            
        self.__record_defaults[columnName] = value
        return True
    
    def setRecordValue( self, columnName, value ):
        """
        Sets the value for this record at the inputed column
        name.  If the columnName provided doesn't exist within
        the schema, then the ColumnNotFoundWarning error will be 
        raised.
        
        :param      columnName      <str>
        :param      value           <variant>
        
        :return     <bool> success
        """
        # convert the inputed value information
        value = ValueMapper.mappedValue(value)
        
        # validate the column
        column = self.schema().column(columnName)
        if ( not column ):
            logger.error( errors.ColumnNotFoundWarning(column) )
            return False
        
        # make sure we're not changning information
        curr_value = self.__record_values[column.name()]
        if ( curr_value == value or 
            (column.isEncrypted() and curr_value == security.encrypt(value)) ):
            return False
        
        # make sure the inputed value matches the validation
        validator = column.validator()
        if ( validator and not validator.match(value) ):
            logger.error( errors.ValidationError(column, value) )
            return False
        
        # encrypt the value if necessary
        if ( column.isEncrypted() ):
            value = security.encrypt(value)
        
        self.__record_values[column.name()] = value
        return True
    
    def setRecordValues( self, **data ):
        """
        Sets the values for this record from the inputed column
        value pairing
        
        :param      **data      key/value pair for column names
        
        :return     <int> number set
        """
        schema = self.schema()
        count = 0
        for colname, value in data.items():
            col = schema.column(colname)
            if ( not col ):
                continue
            
            if ( self.setRecordValue( col.name(), value ) ):
                count += 1
        return count
    
    def setRecordNamespace( self, namespace ):
        """
        Sets the namespace that will be used by this record in the database.
        If no namespace is defined, then it will inherit from its table settings.
        
        :param      namespace | <str> || None
        """
        self.__record_namespace = namespace
    
    def recordNamespace( self ):
        """
        Returns the records specific namespace.  This can be used to override
        particular settings for a record.
        
        :return     <str>
        """
        if ( not self.__record_namespace ):
            return self.schema().namespace()
        return self.__record_namespace
    
    def recordValue( self, columnName, default = None, autoInflate = True ):
        """
        Returns the value for the column for this record.
        
        :param      columnName  | <str>
                    default     | <variant>
                    autoInflate | <bool>
        
        :return     <variant>
        """
        from orb import Orb
        
        output = self.__record_values.get(columnName, default)
        
        # return none output's and non-auto inflated values immediately
        if ( output is None or not autoInflate ):
            return output
        
        # otherwise, determine if this is a foreign key that needs to be 
        # inflated
        column = self.schema().column(columnName)
        if ( not column.isReference() or isinstance(output, Table) ):
            return output
        
        cls = Orb.instance().model(column.reference())
        if ( not cls ):
            err = errors.TableNotFoundError(column.reference())
            logger.error( err )
            return None
        
        # inflate the class
        if ( type(output) == list ):
            inst = cls(*output)
        else:
            inst = cls(output)
            
        self.__record_values[columnName] = inst
        
        if (output == self.__record_defaults.get(columnName)):
            self.__record_defaults[columnName] = inst
        
        return inst
    
    def recordValues(self, useFieldNames=False, autoInflate=False, mapper=None):
        """
        Returns a dictionary grouping the columns and their
        current values.  If useFieldNames is set to true, then the keys
        for the returned dictionary will be the field name rather than the
        API name for the column.  If the autoInflate value is set to True,
        then you will receive any foreign keys as inflated classes (if you
        have any values that are already inflated in your class, then you
        will still get back the class and not the primary key value).  Setting
        the mapper option will map the value by calling the mapper method.
        
        :param      useFieldNames | <bool>
                    autoInflate | <bool>
                    mapper | <callable> || None
        
        :return     { <str> key: <variant>, .. }
        """
        output = {}
        schema = self.schema()
        for column_name, value in self.__record_values.items():
            if useFieldNames:
                column = schema.column(column_name)
                column_name = column.fieldName()
            
            if autoInflate:
                value = self.recordValue(column_name, autoInflate=True)
            
            if mapper:
                value = mapper(value)
            
            output[column_name] = value
        
        return output
    
    def validateRecord( self ):
        """
        Validates the current records values against its columns.
        
        :return     (<bool> valid, <str> message)
        """
        return self.validateValues(self.recordValues())
    
    def validateValues( self, values ):
        """
        Validates the values for the various columns of this record against
        the inputed list of values.
        
        :param      values | {<str> columnName: <variant> value, ..}
        
        :return     (<bool> valid, <str> message)
        """
        success = True
        msg = []
        
        schema = self.schema()
        
        # validate the columns
        for columnName, value in values.items():
            column = schema.column(columnName)
            if ( not column ):
                success = False
                msg.append('%s is not a valid column.' % columnName)
            
            else:
                valid, col_msg = column.validate(value)
                if ( not valid ):
                    success = False
                    msg.append(col_msg)
            
        return (success, '\n\n'.join(msg))
        
    @classmethod
    def buildSearchQuery(cls, 
                         terms, 
                         mode=SearchMode.All, 
                         additionalColumns=None):
        """
        Generates a search query for the given set of terms based on the given
        terms and join mode.  This method can be overloaded to define custom
        searching values, and is used by the <orb.RecordSet> class to filter
        records.
        
        :usage      |>>> from my_api import MyTable
                    |>>> MyTable.select().search('keywords')
        
        :sa         orb.RecordSet.search
        
        :param      terms   | [<str>, ..]
                    mode    | <orb.SearchMode>
        
        :return     <orb.Query>
        """
        from orb import Query
        
        query  = Query()
        schema = cls.schema()
        if ( not schema ):
            return query
        
        search_cols = schema.searchableColumns()
        
        if additionalColumns is not None:
            search_cols += additionalColumns
        
        for search_term in terms:
            term_query = Query()
            for search_col in search_cols:
                model = search_col.schema().model()
                q = Query(model, search_col.name()).contains(search_term)
                term_query |= q
            
            if ( mode == SearchMode.All ):
                query &= term_query
            else:
                query |= term_query
        
        return query
    
    @classmethod
    def baseTableQuery( cls ):
        """
        Returns the default query value for the inputed class.  The default
        table query can be used to globally control queries run through a 
        Table's API to always contain a default.  Common cases are when
        filtering out inactive results or user based results.
        
        :return     <orb.Query> || None
        """
        return cls._baseTableQuery
    
    @classmethod
    def dictify(cls,
                records,
                useFieldNames=False,
                autoInflate=False,
                mapper=None):
        """
        Converts the inputed records of this table to dictionary values.
        
        :sa         Table.recordValues
        
        :param      records         | <orb.RecordSet> || <list>
                    useFieldNames   | <bool>
                    autoInflate     | <bool>
                    mapper          | <callable> || None
        
        :return     [{<key>: <value>, ..}, ]
        """
        dicter = lambda x: x.recordValues(useFieldNames=useFieldNames,
                                          autoInflate=autoInflate,
                                          mapper=mapper)
        
        return map(dicter, records)
    
    @classmethod
    def getDatabase( cls ):
        """
        Returns the database instance for this class.
        
        :return     <Database> || None
        """
        if ( cls.__db__ ):
            from orb import Orb
            return Orb.instance().database(cls.__db__)
        else:
            return cls.schema().database()
    
    @classmethod
    def inflateRecord( cls, values ):
        """
        Returns a new record instance for the given class with the values
        defined from the database.
        
        :param      cls     | <subclass of orb.Table>
                    values  | <dict> values
        
        :return     <orb.Table>
        """
        if ( type(values) == dict ):
            out = cls()
            out._updateFromDatabase(values)
            return out
        elif ( Table.recordcheck(values) and type(values) != cls ):
            return cls(values)
        return None
    
    @classmethod
    def jsonify(cls, 
                records, 
                useFieldNames=False, 
                autoInflate=False, 
                mapper=None):
        """
        Converts the inputed records of this table to json format.
        
        :sa         Table.dictify
        
        :param      records         | <orb.RecordSet> || <list>
                    useFieldNames   | <bool>
                    autoInflate     | <bool>
                    mapper          | <callable> || None
        
        :return     <str> json data
        """
        global json
        if not json:
            # import the json libraries
            try:
                import json
            except ImportError:
                try:
                    import simplejson as json
                except ImportError:
                    raise
        
        # convert the data to a string if nothing else to jsonify successfully
        if mapper is None:
            mapper = str
        
        return json.dumps(cls.dictify(records, 
                                      useFieldNames=useFieldNames,
                                      autoInflate=autoInflate,
                                      mapper=mapper))
    
    @classmethod
    def popRecordCache( cls ):
        """
        Pops the last cache instance from the table.
        
        :return     <orb.RecordCache> || None
        """
        if ( cls._recordCacheStack ):
            return cls._recordCacheStack.pop()
        return None
    
    @classmethod
    def pushRecordCache( cls, cache ):
        """
        Pushes a caching class onto the stack for this table.
        
        :param      cache | <orb.RecordCache>
        """
        if ( cls._recordCacheStack is None ):
            cls._recordCacheStack = []
        cls._recordCacheStack.append(cache)
    
    @classmethod
    def recordCache( cls ):
        """
        Returns the record cache for the inputed class.  If the given class 
        schema does not define caching, then a None valu3e is returned, otherwise
        a RecordCache instance is returned.
        
        :return     <orb.RecordCache> || None
        """
        # returns the current record cache for this instance
        if ( cls._recordCacheStack ):
            return cls._recordCacheStack[-1]
        
        # checks to see if the schema defines a cache
        schema = cls.schema()
        if ( not schema.isCacheEnabled() ):
            return None
        
        # define the cache for the first time
        cache = RecordCache(cls)
        cache.setExpires(cls, schema.cacheExpireIn())
        cls.pushRecordCache(cache)
        
        return cache
    
    @classmethod
    def resolveQueryValue( cls, value ):
        """
        Allows for class-level definitions for creating custom query options.
        
        :param      value | <variant>
        
        :return     <variant>
        """
        return value
    
    @classmethod
    def schema(cls):
        """  Returns the class object's schema information. """
        return cls.__db_schema__
    
    @classmethod
    def selectFirst( cls, *args, **kwds ):
        """
        Selects records for the class based on the inputed \
        options.  If no db is specified, then the current \
        global database will be used.  If the inflated flag is specified, then \
        the results will be inflated to class instances.  If the flag is left \
        as None, then results will be auto-inflated if no columns were supplied.
        If columns were supplied, then the results will not be inflated by \
        default.
        
        :sa     select
        
        :return     <cls> || None
        """
        return cls.select().first(*args, **kwds)
        
    @classmethod
    def select( cls, *args, **kwds ):
        """
        Selects records for the class based on the inputed \
        options.  If no db is specified, then the current \
        global database will be used.  If the inflated flag is specified, then \
        the results will be inflated to class instances.  
        
        If the flag is left as None, then results will be auto-inflated if no 
        columns were supplied.  If columns were supplied, then the results will 
        not be inflated by default.
        
        If the groupBy flag is specified, then the groupBy columns will be added
        to the beginning of the ordered search (to ensure proper paging).  See
        the Table.groupRecords methods for more details.
        
        :note       From version 0.6.0 on, this method now accepts a mutable
                    keyword dictionary of values.  You can supply any member 
                    value for either the <orb.LookupOptions> or
                    <orb.DatabaseOptions>, as well as the keyword 'lookup' to 
                    an instance of <orb.LookupOptions> and 'options' for 
                    an instance of the <orb.DatabaseOptions>
        
        :return     [ <cls>, .. ] || { <variant> grp: <variant> result, .. }
        """
        from orb import RecordSet, LookupOptions, DatabaseOptions
        
        # support legacy code
        arg_headers = ['columns', 'where', 'order', 'limit']
        for i in range(len(args)):
            if ( i == 0 and isinstance(args[i], LookupOptions) ):
                kwds['lookup'] = args[i]
            elif ( i == 1 and isinstance(args[i], DatabaseOptions) ):
                kwds['options'] = args[i]
            else:
                kwds[arg_headers[i]] = args[i]
        
        lookup  = kwds.get('lookup', LookupOptions(**kwds))
        options = kwds.get('options', DatabaseOptions(**kwds))
        
        # setup the default query options
        default_q = cls.baseTableQuery()
        if ( default_q ):
            if ( lookup.where ):
                lookup.where &= default_q
            else:
                lookup.where = default_q
        
        # define the record set and return it
        rset = RecordSet(cls)
        rset.setLookupOptions(lookup)
        rset.setDatabaseOptions(options)
        
        return rset
    
    @classmethod
    def setBaseTableQuery( cls, query ):
        """
        Sets the default table query value.  This method can be used to control
        all queries for a given table by setting global where inclusions.
        
        :param      query | <orb.Query> || None
        """
        cls._baseTableQuery = query
    
    @staticmethod
    def __groupingKey( record, 
                       schema, 
                       grouping, 
                       ref_cache, 
                       autoInflate = False ):
        """
        Looks up the grouping key for the inputed record.  If the cache
        value is specified, then it will lookup any reference information within
        the cache and return it.
        
        :param      record | <orb.Table>
                    grouping | <str>
                    cache    | <dict> || None
                    autoInflate | <bool>
        
        :return     <str>
        """
        columnName = grouping
        
        # lookup template patterns
        if ( '[' in columnName ):
            # lookup column patterns
            columnNames = TEMPLATE_PATTERN.findall(columnName)
            syntax      = columnName
        else:
            columnNames = [columnName]
            syntax      = None
    
        column_data = {}
        for columnName in columnNames:
            columnName  = columnName.split(':')[0]
            column      = schema.column(columnName)
            
            if ( not column ):
                logger.warning('%s is not a valid column of %s', 
                               columnName,
                               schema.name())
                continue
            
            # lookup references
            if ( column.isReference() ):
                ref_key = record.recordValue(columnName, autoInflate = False)
                ref_cache_key = (column.reference(), ref_key)
                
                # cache this record so that we only access 1 of them
                if (not ref_cache_key in ref_cache):
                    col_value = record.recordValue(columnName, 
                                                   autoInflate = autoInflate)
                    ref_cache[ref_cache_key] = col_value
                else:
                    col_value = ref_cache[ref_cache_key]
            else:
                col_value = record.recordValue(columnName)
            
            column_data[columnName] = col_value
        
        if ( syntax ):
            return projex.text.render(syntax, column_data)
        else:
            return column_data[columnName]
    
    @staticmethod
    def groupRecords( records, groupings, autoInflate = False ):
        """
        Creates a grouping of the records based on the inputed columns.  You \
        can supply as many column values as you'd like creating nested \
        groups.
        
        :param      records     | <Table>
                    groupings     | [<str>, ..]
                    autoInflate | <bool>
        
        :return     <dict>
        """
        if ( autoInflate == None ):
            autoInflate = True
            
        output      = {}
        ref_cache   = {}  # stores the grouping options for auto-inflated vars
        
        for record in records:
            data    = output
            schema  = record.schema()
            
            # make sure we have the proper level
            for i in range(len(groupings) - 1):
                grouping_key = Table.__groupingKey(record, 
                                                   schema, 
                                                   groupings[i], 
                                                   ref_cache, 
                                                   autoInflate)
                
                data.setdefault(grouping_key, {})
                data = data[grouping_key]
            
            grouping_key = Table.__groupingKey(record, 
                                               schema, 
                                               groupings[-1], 
                                               ref_cache, 
                                               autoInflate)
            
            data.setdefault(grouping_key, [])
            data[grouping_key].append(record)
        
        return output
    
    @staticmethod
    def recordcheck( obj, cls = None ):
        """
        Checks to see if the inputed obj ia s Table record instance.
        
        :param      obj     | <variant>
                    cls     | <subclass of Table> || None
        
        :return     <bool>
        """
        if ( not cls ):
            cls = Table
            
        return isinstance( obj, cls )
    
    @staticmethod
    def typecheck( obj, cls = None ):
        """
        Checks to see if the inputed obj is a subclass of a table.
        
        :param      obj     |  <variant>
                    cls     |  <subclass of Table> || None
        
        :return     <bool>
        """
        if ( not cls ):
            cls = Table
            
        return isinstance( obj, type ) and issubclass( obj, cls )