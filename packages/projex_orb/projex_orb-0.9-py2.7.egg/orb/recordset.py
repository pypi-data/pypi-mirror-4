""" 
Creates a class for manipulating groups of records at once. 
This is useful when you need to remove a lot of records at one time, and is the
return result from the select mechanism that supports paging.
"""

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2012, Projex Software'
__license__         = 'LGPL'

# maintenance information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

#------------------------------------------------------------------------------

import logging

import orb

from orb        import errors
from orb        import settings
from orb._orb   import Orb
from orb.query  import Query as Q
from orb.table  import Table
from orb.common import RemovedAction, SearchMode

from projex.decorators import deprecatedmethod

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------

class RecordSet(object):
    """
    Defines a class that can be used to manipulate table records in bulk.  For
    more documentation on the RecordSet, check out the 
    [[$ROOT/recordsets|record set documentation]].
    """
    def __init__( self, *args ):
        self._table             = None
        
        # default options
        self._grouped           = False
        self._ordered           = False
        self._inflated          = None
        
        # sorting options
        self._sort_cmp_callable = None
        self._sort_key_callable = None
        self._sort_reversed     = False
        
        # record cache
        self._all               = None
        self._length            = None
        
        # select information
        self._start             = None
        self._limit             = None
        self._database          = None
        self._query             = None
        self._columns           = None
        self._groupBy           = None
        self._order             = None
        self._namespace         = None
        
        # join another record set as RecordSet(recordSet)
        if ( args ):
            data = args[0]
            
            if ( RecordSet.typecheck(data) ):
                self.duplicate(data)
                
            # join a list of records as RecordSet([record, record, record])
            elif ( type(data) in (list, tuple) ):
                self._all = data[:]
                if ( data ):
                    self._table = type(data[0])
            
            # assign a table as the record set RecordSet(Table)
            elif ( Table.typecheck(data) ):
                self._table = data
                
                if ( len(args) > 1 and type(args[1]) in (list, tuple) ):
                    self._all = args[1][:]
    
    def __len__( self ):
        """
        The length of this item will be its total count.
        
        :return     <int>
        """
        # return the length of the all records cache
        if ( self._all is not None ):
            return len(self._all)
        
        # return 0 for null record sets
        elif ( self.isNull() ):
            return 0
        
        # collect the length from the database
        elif ( self._length == None ):
            self._length = self.count()
            
        return self._length
    
    def __iter__( self ):
        """
        Return the fully resolved list of data.
        
        :return     <list>
        """
        return iter(self.all())
    
    def __add__( self, other ):
        """
        Adds two record set instances together and returns them.
        
        :param      other | <RecordSet> || <list>
        """
        return RecordSet(self).join(other)
    
    def __getitem__( self, index ):
        """
        Returns the item at the inputed index for this record set.
        
        :return     <Table>
        """
        return list(self)[index]
    
    def __nonzero__( self ):
        """
        Returns whether or not this record set is a non-zero entry.
        
        :return     <bool>
        """
        return not self.isEmpty()
    
    def all( self, **options ):
        """
        Looks up all the records based on the current query information.
        Additional options can include any options available for the 
        <orb.LookupOptions> or <orb.DatabaseOptions> classes that will be passed
        to this recordset backend.
        
        :return     [<orb.Table>, ..]
        """
        cls = self.table()
        db  = self.database()
        
        if ( self.isNull() ):
            return []
        
        # return the cached lookups
        if ( self._all is not None ):
            if ( options.get('inflated', True) ):
                output = map(lambda x: self.inflateRecord(cls, x), self._all)
            else:
                output = self._all[:]
        
        else:
            # create the lookup information
            cache   = cls.recordCache()
            lookup  = self.lookupOptions(**options)
            options = self.databaseOptions(**options)
            
            # try to make a connection
            connection = db.connection()
            if ( not connection ):
                return []
            
            # cache the result for this query
            if ( cache is not None ):
                results = cache.select(cls, lookup, options)
            else:
                results = connection.select(cls, lookup, options)
            
            self._all = results
            
            # return specific columns
            if ( lookup.columns ):
                if ( len(lookup.columns) == 1 ):
                    output = map(lambda x: x[lookup.columns[0]], results)
                else:
                    output = [[r[col] for col in lookup.columns] \
                                for r in results]
            
            # return inflated records
            elif ( options.inflateRecords ):
                output =  map(lambda x: self.inflateRecord(cls, x), self._all)
            
            # return the raw results
            else:
                output = self._all[:]
        
        # return sorted results from an in-place sort
        if ( self._sort_cmp_callable is not None or \
             self._sort_key_callable is not None ):
            return sorted(output, 
                          cmp = self._sort_cmp_callable,
                          key = self._sort_key_callable,
                          reverse = self._sort_reversed)
        return output
    
    def clear( self ):
        """
        Clears all the cached information such as the all() records,
        records, and total numbers.
        """
        self._all    = None
        self._length = None
    
    def count( self, **options ):
        """
        Collects the count of records for this record set.  Additional options
        can include any options available for the <orb.LookupOptions> or 
        <orb.DatabaseOptions> classes that will be passed to this records
        backend.
        
        :return     <int>
        """
        cls     = self.table()
        db      = self.database()
        
        if ( self.isNull() ):
            return 0
        
        lookup  = self.lookupOptions(**options)
        options = self.databaseOptions(**options)
        
        # retrieve the count information
        cache      = cls.recordCache()
        if ( cache is not None ):
            return cache.count(cls, lookup, options)
        else:
            return db.connection().count(cls, lookup, options)
    
    def columns( self ):
        """
        Returns the columns that this record set should be querying for.
        
        :return     [<str>, ..] || None
        """
        return self._columns
    
    def database( self ):
        """
        Returns the database instance that this recordset will use.
        
        :return     <Database>
        """
        if ( self._database ):
            return self._database
        
        if ( self.table() ):
            db = self.table().getDatabase()
        else:
            from orb import Orb
            db = Orb.instance().database()
            
        if ( not db ):
            logger.error( errors.DatabaseNotFoundError() )
        
        return db
    
    def databaseOptions( self, **options ):
        """
        Returns the database options for this record set.  See the
        <orb.DatabaseOptions> documentation about the optional arguments.
        
        :return     <orb.DatabaseOptions>
        """
        options.setdefault('inflateRecords', self.isInflated())
        options.setdefault('namespace',      self.namespace())
        
        return orb.DatabaseOptions(**options)
    
    def duplicate( self, other ):
        """
        Duplicates the data from the other record set instance.
        
        :param      other | <RecordSet>
        """
        self._table             = other._table
        
        self._database          = other._database
        self._query             = other._query
        self._columns           = other._columns
        self._groupBy           = other._groupBy
        self._order             = other._order
        self._namespace         = other._namespace
    
    def distinct( self, columns, **options ):
        """
        Returns a distinct series of column values for the current record set
        based on the inputed column list.
        
        The additional options are any keyword arguments supported by the
        <orb.LookupOptions> or <orb.DatabaseOptions> classes.  
        
        If there is one column supplied, then the result will be a list, 
        otherwise, the result will be a dictionary.
        
        :param      column   | <str> || [<str>, ..]
                    **options
        
        :return     [<variant>, ..] || {<str> column: [<variant>, ..]}
        """
        # ensure we have a list of values
        if ( not type(columns) in (list, tuple) ):
            columns = [str(columns)]
        
        cls = self.table()
        db  = self.database()
        
        # ensure we have a database and table class
        if ( self.isNull() ):
            if ( len(columns) > 1 ):
                return {}
            return []
        
        # return information from the database
        cache  = cls.recordCache()
        schema = cls.schema()
        
        con     = db.connection()
        lookup  = self.lookupOptions(**options)
        options = self.databaseOptions(**options)
        
        lookup.columns = columns
        
        if cache is not None:
            output = cache.distinct(cls, lookup, options)
        else:
            output = con.distinct(cls, lookup, options)
        
        if options.inflateRecords:
            for key in output.keys():
                column = schema.column(key)
                if ( column and column.isReference() ):
                    ref_model = column.referenceModel()
                    if ( not ref_model ):
                        msg = '%s is not a valid model.' % column.reference()
                        logger.error(msg)
                        continue
                    
                    ids = output[key]
                    records = []
                    if None in ids:
                        ids.remove(None)
                        records.append(None)
                    
                    if ids:
                        q = Q(ref_model).in_(ids)
                        records += list(ref_model.select(where=q))
                    
                    output[key] = records
        
        if ( len(columns) == 1 ):
            return output.get(columns[0], [])
        return output
        
    def first( self, **options ):
        """
        Returns the first record that matches the current query.
        
        :return     <orb.Table> || None
        """
        cls = self.table()
        db  = self.database()
        
        if ( self.isNull() ):
            return None
        
        options['limit'] = 1
        
        lookup       = self.lookupOptions(**options)
        options      = self.databaseOptions(**options)
        
        # retrieve the data from the cache
        cache = cls.recordCache()
        if ( cache is not None ):
            records = cache.select(cls, lookup, options)
        else:
            records = db.connection().select(cls, lookup, options)
        
        if ( records ):
            if ( options.inflateRecords ):
                return self.inflateRecord(cls, records[0])
            return records[0]
        return None
        
    def groupBy( self ):
        """
        Returns the grouping information for this record set.
        
        :return     [<str>, ..] || None
        """
        return self._groupBy
    
    def grouped( self, grouping = None, **options ):
        """
        Returns the records in a particular grouping.  If the groupBy option
        is left as None, then the base grouping for this instance will be used.
        
        :param      groupBy | [<str>, ..] || None
        
        :return     { <str> grouping: <orb.RecordSet>, .. }
        """
        if ( grouping is None ):
            grouping = self.groupBy()
        
        if ( not type(grouping) in (list, tuple) ):
            grouping = [str(grouping)]
        
        table  = self.table()
        output = {}
        
        if ( grouping ):
            column = grouping[0]
            remain = grouping[1:]
            
            values = self.distinct(column, **options)
            
            for value in values:
                lookup      = self.lookupOptions(**options)
                db_options  = self.databaseOptions(**options)
                sub_query   = orb.Query(column) == value
                
                if ( lookup.where is None ):
                    lookup.where = sub_query
                else:
                    lookup.where &= sub_query
                
                sub_set     = RecordSet(table)
                sub_set.setLookupOptions(lookup)
                sub_set.setDatabaseOptions(db_options)
                
                if ( remain ):
                    output[value] = sub_set.grouped(remain, **options)
                else:
                    output[value] = sub_set
        
        return output
    
    def inflateRecord( self, cls, record ):
        """
        Inflates the record for the given class, applying a namespace override
        if this record set is using a particular namespace.
        
        :param      cls     | <subclass of orb.Table>
                    record  | <dict>
        
        :return     <orb.Table>
        """
        inst = cls.inflateRecord(record)
        if ( self._namespace is not None ):
            inst.setRecordNamespace(self._namespace)
        return inst
    
    def index( self, record ):
        """
        Returns the index of the inputed record within the all list.
        
        :param      record | <orb.Table>
        
        :return     <int>
        """
        if ( not record ):
            return -1
        elif ( self._all is not None ):
            return self._all.index(record)
        else:
            return self.primaryKeys().index(record.primaryKey())
    
    def isEmpty( self ):
        """
        Returns whether or not this record set contains any records.
        
        :return     <bool>
        """
        if ( self._all is not None ):
            return len(self._all) == 0
        
        return self.count(limit = 1) == 0
    
    def isGrouped( self ):
        """
        Returns whether or not this record set is intended to be grouped.  This
        method is used to share the intended default usage.  This does not force
        a record set to be grouped or not.
        
        :return     <bool>
        """
        return self._grouped
    
    def isInflated( self ):
        """
        Returns whether or not this record set will be inflated.
        
        :return     <bool>
        """
        if ( self._inflated == None ):
            return self._columns is None
        return self._inflated
    
    def isLoaded( self ):
        """
        Returns whether or not this record set already is loaded or not.
        
        :return     <bool>
        """
        return self._all is not None
    
    def isOrdered( self ):
        """
        Returns whether or not this record set is intended to be ordered.  This
        method is used to share the intended default usage.  This does not force
        a record set to be grouped or not.
        
        :return     <bool>
        """
        return self._ordered
    
    def isNull( self ):
        """
        Returns whether or not this record set can contain valid data.
        
        :return     <bool>
        """
        cls = self.table()
        db  = self.database()
        
        return not (cls and db and db.connection())
    
    def isThreadEnabled( self ):
        """
        Returns whether or not this record set is threadable based on its
        database backend.
        
        :return     <bool>
        """
        db = self.database()
        if ( db ):
            return db.isThreadEnabled()
        return False
    
    def join( self, records ):
        """
        Joins together a list of records or another record set to this instance.
        
        :param      records | <RecordSet> || <list> || None
        
        :return     <bool>
        """
        if ( isinstance(records, RecordSet) ):
            self._all = self.all() + records.all()
            return True
        
        elif ( type(records) in (list, tuple) ):
            self._all = self.all() + records
            return True
        
        else:
            return False
    
    def limit( self ):
        """
        Returns the limit for this record set.
        
        :return     <int>
        """
        return self._limit
    
    def lookupOptions( self, **options ):
        """
        Returns the lookup options for this record set.
        
        :return     <orb.LookupOptions>
        """
        # initialize the options with this record sets values
        options.setdefault('columns',  self.columns())
        options.setdefault('where',    self.query())
        options.setdefault('order',    self.order())
        options.setdefault('start',    self.start())
        options.setdefault('limit',    self.limit())
        options.setdefault('inflated', self.isInflated())
        
        return orb.LookupOptions(**options)
    
    def namespace( self ):
        """
        Returns the namespace for this query.
        
        :return     <str> || None
        """
        return self._namespace
    
    def order( self ):
        """
        Returns the ordering information for this record set.
        
        :return     [(<str> field, <str> asc|desc), ..] || None
        """
        return self._order
    
    def pageCount( self, pageSize ):
        """
        Returns the number of pages that this record set contains.  If no page
        size is specified, then the page size for this instance is used.
        
        :sa         setPageSize
        
        :param      pageSize | <int> || None
        
        :return     <int>
        """
        # if there is no page size, then there is only 1 page of data
        pageSize = max(0, pageSize)
        if ( not pageSize ):
            return 1
        
        # determine the number of pages in this record set
        pageFraction = len(self) / float(pageSize)
        pageCount    = int(pageFraction)
        
        # determine if there is a remainder of records
        remain = pageFraction % 1
        if ( remain ):
            pageCount += 1
        
        return pageCount
    
    def page( self, pageno, pageSize ):
        """
        Returns the records for the current page, or the specified page number.
        If a page size is not specified, then this record sets page size will
        be used.
        
        :param      pageno   | <int>
                    pageSize | <int>
        
        :return     <orb.RecordSet>
        """
        pageSize = max(0, pageSize)
        
        # for only 1 page of information, return all information
        if ( not pageSize ):
            return RecordSet(self)
        
        # lookup the records for the given page
        start   = pageSize * (pageno - 1)
        limit   = pageSize
        
        # returns a new record set with this start and limit information
        output = RecordSet(self)
        output.setStart(start)
        output.setLimit(limit)
        
        return output
    
    def pages( self ):
        """
        Returns a range for all the pages in this record set.
        
        :return     [<int>, ..]
        """
        return range(1, self.pageCount() + 1)
    
    def primaryKeys( self, **options ):
        """
        Returns a list of keys for the records defined for this recordset.
        
        :return     [<variant>, ..]
        """
        if ( self._all is not None ):
            return [record.primaryKey() for record in self._all]
        
        elif ( self.table() ):
            cols = self.table().schema().primaryColumns()
            cols = map(lambda x: x.fieldName(), cols)
            return self.values(cols, **options)
        
        return self.values(settings.PRIMARY_FIELD, **options)
    
    def query( self ):
        """
        Returns the query for this record set.
        
        :return     <Query> || <QueryCompound> || None
        """
        return self._query
    
    def refine( self, query ):
        """
        Creates a subset of this record set with a joined query based on the 
        inputed search text.  The search will be applied to all columns that are
        marked as searchable.
        
        :sa         Column.setSearchable
        
        :param      search_text | <str>
        
        :return     <RecordSet>
        """
        if ( self._query ):
            query &= self._query
        
        rset = RecordSet(self)
        rset.setQuery(query)
        return rset
    
    def remove( self, **options ):
        """
        Removes the records from this set based on the inputed removal mode.
        
        :note       As of version 0.6.0 on, this method accepts variable 
                    keyword arguments.  This is to support legacy code,
                    the preferred method to call is to pass in options =
                    <orb.DatabaseOptions>, however, you can supply any
                    members as keyword arguments and it will generate an
                    options instance for you.
        
        :return     <int>
        """
        if ( self.isNull() ):
            return 0
        
        if ( self.isEmpty() ):
            return 0
        
        # lookup all relations recursively
        cascade_remove  = []
        db_options      = self.databaseOptions(**options)
        schema          = self.table().schema()
        relations       = Orb.instance().findRelations(schema)
        records         = self.primaryKeys()
        
        for table, columns in relations:
            for column in columns:
                action = column.referenceRemovedAction()
                q      = Q(column.name()).in_(records)
                
                # determine the reference information
                if ( action == RemovedAction.Block ):
                    if ( not table.select(where = q).isEmpty() ):
                        msg = 'Could not remove records, there are still '\
                              'references to the %s model.'
                        raise errors.CannotRemoveError(msg % table.__name__)
                
                # add cascaded removal
                elif ( action == RemovedAction.Cascade ):
                    cascade_remove.append(table.select(where = q))
        
        count = 0
        
        # handle permanent deletion
        for cascaded in cascade_remove:
            count += cascaded.remove(**options)
        
        # remove this record sets records
        count += self.database().connection().remove(schema, records, db_options)
        
        # clear any cached information on removal
        if ( count and self.table() and self.table().recordCache() ):
            self.table().recordCache().clear()
        
        return count
        
    def search( self, search_terms, mode = SearchMode.All, limit=None ):
        """
        Creates a subset of this record set with a joined query based on the 
        inputed search text.  The search will be applied to all columns that are
        marked as searchable.
        
        :sa         Column.setSearchable
        
        :param      search_terms | [<str>, ..] || <str>
        
        :return     <RecordSet>
        """
        if ( not self.table() ):
            return RecordSet()
        
        if ( not search_terms ):
            return RecordSet(self)
        
        from orb import Query
        if ( not type(search_terms) in (list, tuple) ):
            terms, column_query = Query.fromSearch(str(search_terms), mode)
        else:
            terms = list(search_terms)
            column_query = None
        
        terms_query  = self.table().buildSearchQuery(terms)
        
        search_query  = Query()
        
        if ( mode == SearchMode.All ):
            search_query &= terms_query
            search_query &= column_query
        else:
            search_query |= terms_query
            search_query |= column_query
        
        output = self.refine(search_query)
        if limit is not None:
            output.setLimit(limit)
        return output
        
    def setColumns( self, columns ):
        """
        Sets the columns that this record set should be querying the database
        for.
        
        :param      columns | [<str>, ..] || None
        """
        self._columns = columns
    
    def setDatabase( self, database ):
        """
        Sets the database instance for this record set.  If it is left blank,
        then the default orb database for the table class will be used.
        
        :param      database | <Database> || None
        """
        self._database = database
    
    def setGrouped( self, state ):
        """
        Sets whether or not this record set is intended to be grouped.  This
        method is used to share the intended default usage.  This does not force
        a record set to be grouped or not.
        
        :return     state | <bool>
        """
        self._grouped = state
    
    def setGroupBy( self, groupBy ):
        """
        Sets the group by information that this record set will use.
        
        :param      groupBy | [<str>, ..] || None
        """
        self._groupBy = groupBy
    
    def setDatabaseOptions( self, options ):
        """
        Sets the database options for selectin to the inputed options.
        
        :param      options | <orb.DatabaseOptions>
        """
        self._namespace = options.namespace
    
    def setInflated( self, state ):
        """
        Sets whether or not by default the results from this record set should
        be inflated.
        
        :param      state | <bool> || None
        """
        self._inflated = state
    
    def setLimit( self, limit ):
        """
        Sets the limit for this record set.
        
        :param      limit | <int>
        """
        self._limit = limit
    
    def setLookupOptions( self, lookup ):
        """
        Sets the lookup options for this instance to the inputed lookup data.
        
        :param      lookup | <orb.LookupOptions>
        """
        self._query             = lookup.where
        self._columns           = lookup.columns
        self._order             = lookup.order
        self._ordered           = lookup.order != None
        self._limit             = lookup.limit
        self._start             = lookup.start
    
    def setNamespace( self, namespace ):
        """
        Sets the namespace information for this recordset to the given namespace
        
        :param      namespace | <str>
        """
        self._namespace = namespace
    
    def setOrder( self, order ):
        """
        Sets the field order that this record set will use.
        
        :param      order | [(<str> field, <str> asc|desc), ..] || None
        """
        self._order = order
        self.setOrdered(order is not None)
    
    def setOrdered( self, state ):
        """
        Sets whether or not this record set is intended to be grouped.  This
        method is used to share the intended default usage.  This does not force
        a record set to be ordered or not.
        
        :param      state | <bool>
        """
        self._ordered = state
    
    def setQuery( self, query ):
        """
        Sets the query that this record set will use.  This will also clear the
        cache information since it will alter what is being stored.
        
        :param      query | <Query> || <QueryCompound> || None
        """
        self._query = query
        self.clear()
    
    def setStart( self, index ):
        """
        Sets the start index for this query.
        
        :param      index | <int>
        """
        self._start = index
    
    def sumOf( self, columnName ):
        """
        Returns the sum of the values from the column name.
        
        :return     <int>
        """
        return sum(self.values(columnName))
    
    def sort( self, cmp = None, key = None, reverse = False ):
        """
        Sorts the resulted all records by the inputed arguments.
        
        :param      *args | arguments
        """
        self._sort_cmp_callable = cmp
        self._sort_key_callable = key
        self._sort_reversed     = reverse
    
    def start( self ):
        """
        Returns the start index for this query.
        
        :return     <int>
        """
        return self._start
    
    def table( self ):
        """
        Returns the table class that this record set is associated with.
        
        :return     <subclass of orb.Table>
        """
        return self._table
    
    @deprecatedmethod('orb.RecordSet', 'You should use len() or count() now.')
    def total( self ):
        """
        Returns the total number of records that are in this set.
        
        :return     <int>
        """
        return self.count()
    
    def values( self, columns, **options ):
        """
        Returns either a list of values for all the records if the inputed arg
        is a column name, or a dictionary of columnName values for multiple
        records for all the records in this set.
        
        :param      columns | <str> || [<str>, ..]
        
        :return     [<variant>, ..] || { <str> column: [<variant>, ..], ..}
        """
        # update the list
        if ( isinstance(columns, basestring) ):
            columns = [str(columns)]
        
        if ( self.isNull() ):
            return []
        
        options['columns'] = columns
        
        cls     = self.table()
        db      = self.database()
        lookup  = self.lookupOptions(**options)
        options = self.databaseOptions(**options)
        
        cache = cls.recordCache()
        if ( cache ):
            records = cache.select(cls, lookup, options)
        else:
            records = db.connection().select(cls, lookup, options)
        
        # parse the values from the cache
        output = {}
        for record in records:
            for column in columns:
                output.setdefault(column, [])
                
                col = cls.schema().column(column)
                if ( col ):
                    expand = col.isReference() and options.inflateRecords
                    value  = record[column]
                else:
                    expand = False
                    value  = record.get(column)
                
                if ( expand and value is not None ):
                    ref_model = col.referenceModel()
                    
                    if ( not ref_model ):
                        output[column].append(None)
                    else:
                        output[column].append(ref_model(value))
                else:
                    output[column].append(value)
        
        if ( len(output) == 1 ):
            return output[columns[0]]
        elif ( output ):
            return zip(*[output[column] for column in columns])
        else:
            return []
    
    @staticmethod
    def typecheck( value ):
        """
        Checks to see if the inputed type is of a Recordset
        
        :param      value | <variant>
        
        :return     <bool>
        """
        return isinstance(value, RecordSet)