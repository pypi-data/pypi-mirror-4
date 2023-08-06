#!/usr/bin/python

""" 
Defines caching methods to use when working with tables.
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

import datetime
import orb

from projex.decorators import wraps

#------------------------------------------------------------------------------

class OrderCompare(object):
    def __init__( self, order ):
        self._order = order
    
    def __call__( self, a, b ):
        for col, direction in self._order:
            a_val = a.get(col)
            b_val = b.get(col)
            
            # ignore same results
            result = cmp(a_val, b_val)
            if ( result == 0 ):
                continue
            
            if ( direction == 'desc' ):
                return -result
            return result
        return 0

#-------------------------------------------------------------------------------

class DataCache(object):
    """
    This class is used to store custom properties on individual records via
    the <orb.Table.dataCache> method.
    """
    def __init__( self ):
        self._cache = {}
    
    def clear( self ):
        """
        Clears all the cache data from this record.
        """
        self._cache.clear()
    
    def isCached( self, key ):
        """
        Returns whether or not this cache instance has the given key cached.
        
        :param      key | <str>
        
        :return     <bool>
        """
        return str(key) in self._cache
    
    def setValue( self, key, value ):
        """
        Sets the value for the key in the cache to the given value.
        
        :param      key   | <str>
                    value | <variant>
        """
        self._cache[str(key)] = value
    
    def value( self, key, default = None ):
        """
        Returns the value from the inputed cache key.  If no value is found,
        the default value is returned.
        
        :param      key     | <str>
                    default | <variant>
        """
        return self._cache.get(str(key), default)

#------------------------------------------------------------------------------

class RecordCache(object):
    """
    Defines a key cache class for the table to use when caching records from the
    system.  Caching is defined on the TableSchema class, see 
    TableSchema.setCachingEnabled for more info.
    
    :usage      |from orb import RecordCache
                |
                |with RecordCache(User, AccountType):
                |   for transaction in Transactions.select():
                |       print transaction.transferredBy()  # lookups up from
                |                                          # the user cache
                
                |from orb import Table
                |
                |class User(Table):
                |   __db_cached__ = True
                |
                |User.select() # looks up from the RecordCache for the table
    """
    def __init__( self, *tables ):
        self._tables  = list(tables) # [<orb.Table>, ..]
        self._cache   = {} # {<orb.Table>: {<variant> pkey: <variant> val}}
        self._updated = {} # {<orb.Table>: <datetime>}
        self._expires = {} # {<orb.Table>: <int> minutes}
        
        # set the default caching value to 5 minutes
        for table in tables:
            self._expires[table] = 5
    
    def __enter__( self ):
        self.begin()
    
    def __exit__( self ):
        self.end()
    
    def begin( self ):
        """
        Begins the caching process for this instance.
        """
        for table in self._tables:
            table.pushRecordCache(self)
    
    def clear( self, table = None ):
        """
        Clears the current cache information.
        """
        if ( table ):
            for d in (self._cache, self._updated, self._expires):
                try:
                    d.pop(table)
                except IndexError:
                    pass
        else:
            self._cache.clear()
            self._updated.clear()
            self._expires.clear()
    
    def count( self, table, lookup, options ):
        """
        Returns the number of entries based on the given options.
        
        :param      table   | <subclass of orb.Table>
                    lookup  | <orb.LookupOptions>
                    options | <orb.DatabaseOptions>
        
        :return     <int>
        """
        options.inflateRecords = False
        return len(self.select(table, lookup, options))
    
    def distinct( self, table, lookup, options ):
        """
        Returns a distinct set o fentries based on the given lookup options.
        
        :param      table   | <subclass of orb.Table>
                    lookup  | <orb.LookupOptions>
                    options | <orb.DatabaseOptions>
        
        :return     {<str> columnName: <list> value, ..}
        """
        output = dict([(column, set()) for column in lookup.columns])
        for record in self.select(table, lookup, options):
            for column in lookup.columns:
                output[column].add(record.get(column))
        
        for key, value in output.items():
            output[key] = list(value)
        
        return output
    
    def end( self ):
        """
        Ends the caching process for this instance.
        """
        for table in self._tables:
            table.popRecordCache()
    
    def isValid( self, table, query = None ):
        """
        Returns whether or not this cache is currently valid.
        
        :return     <bool>
        """
        # check to see if we have looked up results for this query
        query_key         = str(query)
        query_used        = self._updated.get(table, {}).get(query_key)
        all_records_found = self._cache.get(table, {}).get('all_records_found')
        if ( not (query_used or all_records_found) ):
            return False
        
        # if the values never expire, then one of our options succeeded
        expires = self._expires.get(table, 0)
        if ( not expires ):
            return True
        
        if ( query_used ):
            updated = self._updated.get(table, {}).get(query_key)
        else:
            updated = self._updated.get(table, {}).get('all_records_found')
        
        # determine if the cache is out of date by comparing the current
        # time against the last updated time
        time_delta = datetime.datetime.now() - updated
        if ( (time_delta.seconds / 60) > expires ):
            try:
                self._cache.pop(table)
            except KeyError:
                pass
            
            return False
        
        return True
    
    def record( self, table, primaryKey ):
        """
        Returns a record for the given primary key.
        
        :return     {<str> columnName: <variant> value, ..} record
        """
        table_cache = self._cache.get(table, {})
        keys_cache  = table_cache.get('primaryKeys', {})
        
        record = keys_cache.get(primaryKey)
        
        # select an individual record
        if ( record is None ):
            results = self.records(table, Q(table) == primaryKey)
            if ( not results ):
                record = {}
            else:
                record = results[0]
            
            keys_cache[primaryKey] = record
        
        return keys_cache
    
    def records( self, table, query = None ):
        """
        Returns a list of records that are cached.
        
        :param      table | <orb.Table>
                    query | <orb.Query> || None
        
        :return     [<Table>, ..]
        """
        query_key = str(query)
        
        # lookup against the current records
        if ( self.isValid(table, query) ):
            records = self._cache.get(table, {}).get(query_key)
            if ( records is None ):
                records = self._cache.get(table, {}).get('primaryKeys', {})
            
            return records.values()
        
        # grab the records from the database
        db      = table.getDatabase()
        if ( not (db and db.connection()) ):
            return []
        
        # lookup all the records to cache
        lookup       = orb.LookupOptions()
        lookup.where = query
        options      = orb.DatabaseOptions(inflated = False)
        
        records = db.connection().select(table, lookup,options)
        
        # store the records by their primary key
        cols = table.schema().primaryColumns()
        
        record_cache = {}
        for record in records:
            pkey    = []
            for col in cols:
                pkey.append(record.get(col.name(), None))
            
            if ( len(pkey) == 1 ):
                pkey = pkey[0]
            
            record_cache[pkey] = record
        
        self._cache.setdefault(table, {})
        
        self._cache[table].setdefault('primaryKeys', {})
        self._cache[table].setdefault(query_key, {})
        
        self._cache[table]['primaryKeys'].update(record_cache)
        self._cache[table][query_key].update(record_cache)
        
        self._updated.setdefault(table, {})
        self._updated[table][query_key] = datetime.datetime.now()
        
        # record that we have all the records
        if ( not query ):
            self._cache[table]['all_records_found'] = True
        
        return record_cache.values()
    
    def setExpires( self, table, minutes ):
        """
        Sets the length of time in minutes to hold onto this cache before 
        re-querying the database.
        
        :param      minutes | <int> || <float>
        """
        self._expires[table] = minutes
    
    def selectFirst( self, table, lookup, options ):
        """
        Returns a list of records from the cache that matches the inputed
        parameters.
        
        :param      table   | <orb.Table>
                    lookup  | <orb.LookupOptions>
                    options | <orb.DatabaseOptions>
        
        :return     <dict> record || None
        """
        lookup.limit = 1
        results = self.select(lookup, options)
        if ( results ):
            return results[0]
        return None
    
    def select( self, table, lookup, options ):
        """
        Returns a list of records from the cache that matches the inputed
        parameters.
        
        :param      table   | <orb.Table>
                    lookup  | <orb.LookupOptions>
                    options | <orb.DatabaseOptions>
        
        :return     [<dict> record, ..]
        """
        records = self.records(table, lookup.where)
        
        # sort the data
        if ( lookup.order ):
            records.sort(OrderCompare(lookup.order))
        
        output = []
        
        # filter the data
        if ( lookup.where ):
            if ( lookup.start is None ):
                lookup.start = 0
            
            for i in range(lookup.start, len(records)):
                record = records[i]
                if ( lookup.where and not lookup.where.validate(record) ):
                    continue
                
                output.append(record)
                if ( lookup.limit and len(output) == lookup.limit ):
                    break
        
        # limit the data
        elif ( lookup.start is not None and lookup.limit is not None ):
            output = records[lookup.start:(lookup.start + lookup.limit)]
        
        # start the data
        elif ( lookup.start is not None ):
            output = records[lookup.start:]
        
        # limit the data
        elif ( lookup.limit is not None ):
            output = records[:lookup.limit]
        
        # return the data
        else:
            output =  records
        
        return output
    
    def tables( self ):
        """
        Returns the tables linked with this cache set.
        
        :return     [<orb.Table>, ..]
        """
        return self._tables