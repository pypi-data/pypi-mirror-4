#!/usr/bin/python

"""
Defines the global query building syntzx for generating db
agnostic queries quickly and easily.
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

import datetime
import os
import re
import projex.text
import logging

from orb.common import ColumnType, SearchMode

from projex.enum import enum

logger = logging.getLogger(__name__)

FIELD_SYNTAX = os.environ.get('ORB_FIELD_SYNTAX', '(?P<%s>[\w_\.]+)')
VALUE_SYNTAX = os.environ.get('ORB_VALUE_SYNTAX', 
                              '(?P<%s>([\w\-_\.,]+|"[^"]+")|\[[^\]]+\])')

class QueryPattern(object):
    def __init__( self, syntax ):
        self._syntax = syntax
        
        field       = FIELD_SYNTAX % 'field'
        value       = VALUE_SYNTAX % 'value'
        val_min     = VALUE_SYNTAX % 'min'
        val_max     = VALUE_SYNTAX % 'max'
        
        opts = {'value': value, 
                'min': val_min, 
                'max': val_max,
                'field': field}
        
        expr = syntax % opts
        
        self._pattern = re.compile(expr)
    
    def pattern( self ):
        """
        Returns the regular expression pattern for this pattern.
        
        :return     <re.SRE_Pattern>
        """
        return self._pattern
    
    def syntax( self ):
        """
        Returns the string syntax to be used for this pattern.
        
        :return     <str>
        """
        return self._syntax

#------------------------------------------------------------------------------

class Query:
    """ 
    Defines the central class for the abstract query markup language.
    
    For more information, refer to the [[$ROOT/querying|querying documentation]]
    
    """
    
    Op = enum(
        # equality operators
        'Is',
        'IsNot',
        
        # comparison operators
        'LessThan',
        'LessThanOrEqual',
        'Before',
        'GreaterThan',
        'GreaterThanOrEqual',
        'After',
        'Between',
        
        # string operators
        'Contains',
        'DoesNotContain',
        'Startswith',
        'Endswith',
        'Matches',
        'DoesNotMatch',
        
        # list operators
        'IsIn',
        'IsNotIn'
    )
    
    SyntaxPatterns = [
        (Op.IsNotIn,            QueryPattern('%(field)s is not in %(value)s')),
        (Op.IsIn,               QueryPattern('%(field)s is in %(value)s')),
        (Op.IsNot,              QueryPattern('%(field)s is not %(value)s')),
        (Op.Is,                 QueryPattern('%(field)s is %(value)s')),
        (Op.LessThanOrEqual,    QueryPattern('%(field)s <= %(value)s')),
        (Op.LessThan,           QueryPattern('%(field)s < %(value)s')),
        (Op.Before,             QueryPattern('%(field)s before %(value)s')),
        (Op.GreaterThanOrEqual, QueryPattern('%(field)s >= %(value)s')),
        (Op.GreaterThan,        QueryPattern('%(field)s > %(value)s')),
        (Op.After,              QueryPattern('%(field)s after %(value)s')),
        (Op.Between,            QueryPattern('%(field)s between %(value)s')),
        (Op.Contains,           QueryPattern('%(field)s contains %(value)s')),
        (Op.DoesNotContain,     QueryPattern('%(field)s doesnt contain %(value)s')),
        (Op.Startswith,         QueryPattern('%(field)s startwith %(value)s')),
        (Op.Endswith,           QueryPattern('%(field)s endswith %(value)s')),
        (Op.Matches,            QueryPattern('%(field)s matches %(value)s')),
        (Op.DoesNotMatch,       QueryPattern('%(field)s doesnt match %(value)s')),
    ]
    
    ColumnOps = {
        # default option
        None: (
            Op.Is,
            Op.IsNot,
            Op.Contains,
            Op.DoesNotContain,
            Op.Startswith,
            Op.Endswith,
            Op.Matches,
            Op.DoesNotMatch,
            Op.IsNotIn,
            Op.IsIn
        ),
        # column specific options
        ColumnType.Bool: (
            Op.Is,
            Op.IsNot
        ),
        ColumnType.ForeignKey: (
            Op.Is,
            Op.IsNot,
            Op.IsIn,
            Op.IsNotIn
        ),
        ColumnType.Date: (
            Op.Is,
            Op.IsNot,
            Op.Before,
            Op.After,
            Op.Between,
            Op.IsIn,
            Op.IsNotIn
        ),
        ColumnType.Datetime: (
            Op.Is,
            Op.IsNot,
            Op.Before,
            Op.After,
            Op.Between,
            Op.IsIn,
            Op.IsNotIn
        ),
        ColumnType.Time: (
            Op.Is,
            Op.IsNot,
            Op.Before,
            Op.After,
            Op.Between,
            Op.IsIn,
            Op.IsNotIn
        )
    }
    
    # additional option values to control query flow
    UNDEFINED   = '__QUERY__UNDEFINED__'
    NOT_EMPTY   = '__QUERY__NOT_EMPTY__'
    EMPTY       = '__QUERY__EMPTY__'
    ALL         = '__QUERY__ALL__'

    def __str__( self ):
        return self.toString()
    
    def __nonzero__( self ):
        return not self.isNull()
    
    def __contains__( self, value ):
        """
        Returns whether or not the query defines the inputed column name.
        
        :param      value | <variant>
        
        :return     <bool>
        
        :usage      |>>> from orb import Query as Q
                    |>>> q = Q('testing') == True
                    |>>> 'testing' in q
                    |True
                    |>>> 'name' in q
                    |False
        """
        return value == self._columnName
        
    def __init__( self, *args, **options ):
        """
        Initializes the Query instance.  The only required variable
        is the column name, the rest can be manipulated after
        creation.  This class takes a variable set of information
        to initialize.  You can initialize a blank query object
        by supplying no arguments, which is useful when generating
        queries in a loop, or you can supply only a string column
        value for lookup (the table will auto-populate from the
        selection, or you can supply a model and column name (
        used in the join operation).
        
        :param      *args           <tuple>
                    
                    #. None
                    #. <str> columnName
                    #. <subclass of Table>
                    #. (<subclass of Table> table,<str> columnName)
                    
        :param      **options       <dict> options for the query.
        
                    *. op               <Query.Op>
                    *. value            <variant>
                    *. caseSensitive    <bool>
        
        """
        from orb.table import Table
        
        # initialized with (table,column,)
        if ( len(args) == 2 ):
            self._table      = args[0]
            self._columnName = args[1]
        
        # initialized with (table,)
        elif ( len(args) == 1 and Table.typecheck(args[0]) ):
            # when only a table is supplied, auto-use the primary key
            self._table      = args[0]
            
            pcols = args[0].schema().primaryColumns()
            if ( pcols ):
                self._columnName = pcols[0].fieldName()
            else:
                self._columnName = None
        
        # initialized with (column,)
        elif ( len(args) == 1 ):
            # create a Table.column option
            if ( '.' in args[0] ):
                arg_split = args[0].split('.')
                if ( len(arg_split) == 2 ):
                    tableName = arg_split[0]
                    columnName = arg_split[1]
                    table = Orb.instance().model(tableName)
                else:
                    table = None
                    columnName = args[0]
            
            # use the standard column
            else:
                table = None
                columnName = args[0]
                
            self._table      = table
            self._columnName = columnName
        
        # initialized with nothing
        else:
            self._table      = None
            self._columnName = None
        
        self._op            = options.get('op',    Query.Op.Is)
        self._value         = options.get('value', Query.UNDEFINED)
        self._caseSensitive = options.get('caseSensitive', False)
        self._negate        = options.get('negate', False)
    
    # operator methods
    def __and__( self, other ):
        """
        Creates a new compound query using the 
        QueryCompound.Op.And type.
        
        :param      other   <Query> || <QueryCompound>
        
        :return     <QueryCompound>
        
        :sa         and_
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = (Q('test') != 1) & (Q('name') == 'Eric')
                    |>>> print query
                    |(test is not 1 and name is Eric)
        """
        return self.and_(other)
    
    def __cmp__( self, other ):
        """
        Use the compare method to be able to see if two query items are
        the same vs. ==, since == is used to set the query's is value.
        
        :param      other       <variant>
        
        :return     <int> 1 | 0 | -1
        """
        if ( not isinstance(other, Query) ):
            return -1
        
        # returns 0 if these are the same item
        if ( id(self) == id(other) ):
            return 0
        return 1
    
    def __eq__( self, other ):
        """
        Allows joining of values to the query by the == operator.
        If another Query instance is passed in, then it will do 
        a standard comparison.
        
        :param      other       <variant>
        
        :return     <Query>
        
        :sa         is
        
        :usage      |>>> from orb import *
                    |>>> query = Query('test') == 1 
                    |>>> print query
                    |test is 1
        """
        return self.is_(other)
    
    def __gt__( self, other ):
        """
        Allows the joining of values to the query by the > 
        operator. If another Query instance is passed in, then it 
        will do a standard comparison.
        
        :param      other       <variant>
        
        :return     <Query>
        
        :sa         lessThan
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test') > 1
                    |>>> print query
                    |test greater_than 1
        """
        return self.greaterThan(other)
    
    def __ge__( self, other ):
        """
        Allows the joining of values to the query by the >= 
        operator.  If another Query instance is passed in, then it 
        will do a standard comparison.
        
        :param      other       <variant>
        
        :return     <Query>
        
        :sa         greaterThanOrEqual
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test') >= 1
                    |>>> print query
                    |test <= 1
        """
        return self.greaterThanOrEqual(other)
    
    def __lt__( self, other ):
        """
        Allows the joining of values to the query by the < 
        operator.  If another Query instance is passed in, then it 
        will do a standard comparison.
        
        :param      other       <variant>
        
        :return     <Query>
        
        :sa         lessThan
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test') < 1
                    |>>> print query
                    |test less_than 1
        """
        return self.lessThan(other)
    
    def __le__( self, other ):
        """
        Allows the joining of values to the query by the <= 
        operator.  If another Query instance is passed in, then it 
        will do a standard comparison.
        
        :param      other       <variant>
        
        :return     <Query>
        
        :sa         lessThanOrEqual
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test') <= 1
                    |>>> print query
                    |test <= 1
        """
        return self.lessThanOrEqual(other)
    
    def __ne__( self, other ):
        """
        Allows joining of values to the query by the != operator.
        If another Query instance is passed in, then it will do a
        standard comparison.
        
        :param      other       <variant>
        
        :return     <Query>
        
        :sa         isNot
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test') != 1
                    |>>> print query
                    |test is not 1
        """
        return self.isNot(other)
    
    def __neg__( self ):
        """
        Negates the values within this query by using the - operator.
        
        :return     self
        
        :sa         negated
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test') == 1
                    |>>> print -query
                    |NOT test is 1
        """
        return self.negated()
    
    def __or__( self, other ):
        """
        Creates a new compound query using the
        QueryCompound.Op.Or type.
        
        :param      other   <Query> || <QueryCompound>
        
        :return     <QueryCompound>
        
        :sa         or_
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = (Q('test') != 1) | (Q('name') == 'Eric')
                    |>>> print query
                    |(test is not 1 or name is Eric)
        """
        return self.or_(other)
    
    # public methods
    def after( self, value ):
        """
        Sets the operator type to Query.Op.After and sets the value to 
        the amount that this query should be lower than.  This is functionaly
        the same as doing the lessThan operation, but is useufl for visual 
        queries for things like dates.
        
        :param      value   | <variant>
        
        :return     <Query>
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('dateStart').after(date.today())
                    |>>> print query
                    |dateStart after 2011-10-10
        """
        newq = Query(self.table(), self.columnName())
        newq.setOperatorType( Query.Op.After )
        newq.setValue(value)
        
        return newq
    
    def and_( self, other ):
        """
        Creates a new compound query using the 
        QueryCompound.Op.And type.
        
        :param      other   <Query> || <QueryCompound>
        
        :return     <QueryCompound>
        
        :sa         __and__
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = (Q('test') != 1).and_((Q('name') == 'Eric')
                    |>>> print query
                    |(test is not 1 and name is Eric)
        """
        if ( other is None or other.isNull() ):
            return self
            
        elif ( self.isNull() ):
            return other
        
        return QueryCompound(self, other, op = QueryCompound.Op.And)
    
    def before( self, value ):
        """
        Sets the operator type to Query.Op.Before and sets the value to 
        the amount that this query should be lower than.  This is functionaly
        the same as doing the lessThan operation, but is useufl for visual 
        queries for things like dates.
        
        :param      value   | <variant>
        
        :return     <Query>
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('dateStart').before(date.today())
                    |>>> print query
                    |dateStart before 2011-10-10
        """
        newq = Query(self.table(), self.columnName())
        newq.setOperatorType( Query.Op.Before )
        newq.setValue(value)
        
        return newq
    
    def between( self, valueA, valueB ):
        """
        Sets the operator type to Query.Op.Between and sets the
        value to a tuple of the two inputed values.
        
        :param      valueA      <variant>
        :param      valueB      <variant>
        
        :return     <Query>
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test').between(1,2)
                    |>>> print query
                    |test between [1,2]
        """
        newq = Query(self.table(), self.columnName())
        newq.setOperatorType( Query.Op.Between )
        newq.setValue( [valueA, valueB] )
        
        return newq
    
    def caseSensitive( self ):
        """
        Returns whether or not this query item will be case
        sensitive.  This will be used with string lookup items.
        
        :return     <bool>
        """
        return self._caseSensitive
    
    def column( self ):
        """
        Returns the column instance for this query.
        
        :return     <orb.Column>
        """
        if ( self._table ):
            return self._table.schema().column(self._columnName)
        return None
    
    def columnName( self ):
        """
        Reutrns the column name that this query instance is
        looking up.
        
        :return     <str>
        """
        return self._columnName
    
    def contains( self, value, caseSensitive = False ):
        """
        Sets the operator type to Query.Op.Contains and sets the    
        value to the inputd value.  Use an asterix for wildcard
        characters.
        
        :param      value           <variant>
        :param      caseSensitive   <bool>
        
        :return     self    (useful for chaining)
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('comments').contains('test')
                    |>>> print query
                    |comments contains test
        """
        newq = Query(self.table(), self.columnName())
        newq.setOperatorType( Query.Op.Contains )
        newq.setValue( value )
        newq.setCaseSensitive( caseSensitive )
        
        return newq
    
    def copy( self ):
        """
        Returns a duplicate of this instance.
        
        :return     <Query>
        """
        out = Query()
        vars(out).update(vars(self))
        return out
    
    def doesNotContain( self, value ):
        """
        Sets the operator type to Query.Op.DoesNotContain and sets the
        value to the inputed value.
        
        :param      value       <variant>
        
        :return     self    (useful for chaining)
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('comments').doesNotContain('test')
                    |>>> print query
                    |comments does_not_contain test
        """
        newq = Query(self.table(), self.columnName())
        newq.setOperatorType( Query.Op.DoesNotContain )
        newq.setValue( value )
        
        return newq
    
    def doesNotMatch( self, value ):
        """
        Sets the operator type to Query.Op.DoesNotMatch and sets the \
        value to the inputed value.
        
        :param      value       <variant>
        
        :return     self    (useful for chaining)
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('comments').doesNotMatch('test')
                    |>>> print query
                    |comments does_not_contain test
        """
        newq = Query(self.table(), self.columnName())
        newq.setOperatorType( Query.Op.DoesNotMatch )
        newq.setValue( value )
        
        return newq
    
    def isNot( self, value ):
        """
        Sets the operator type to Query.Op.IsNot and sets the
        value to the inputed value.
        
        :param      value       <variant>
        
        :return     <Query>
        
        :sa         __ne__
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test').isNot(1)
                    |>>> print query
                    |test is not 1
        """
        newq = Query(self.table(), self.columnName())
        newq.setOperatorType( Query.Op.IsNot )
        newq.setValue( value )
        
        return newq
    
    def endswith( self, value ):
        """
        Sets the operator type to Query.Op.Endswith and sets \
        the value to the inputed value.  This method will only work on text \
        based fields.
        
        :param      value       <str>
        
        :return     <Query>
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test').endswith('blah')
                    |>>> print query
                    |test startswith blah
        """
        newq = Query(self.table(), self.columnName())
        newq.setOperatorType( Query.Op.Endswith )
        newq.setValue( value )
        
        return newq
    
    def is_( self, value ):
        """
        Sets the operator type to Query.Op.Is and sets the
        value to the inputed value.
        
        :param      value       <variant>
        
        :return     <Query>
        
        :sa         __eq__
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test').is_(1)
                    |>>> print query
                    |test is 1
        """
        newq = Query(self.table(), self.columnName())
        newq.setOperatorType( Query.Op.Is )
        newq.setValue( value )
        
        return newq
    
    def greaterThan( self, value ):
        """
        Sets the operator type to Query.Op.GreaterThan and sets the
        value to the inputed value.
        
        :param      value       <variant>
        
        :return     <Query>
        
        :sa         __gt__
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test').greaterThan(1)
                    |>>> print query
                    |test greater_than 1
        """
        newq = Query(self.table(), self.columnName())
        newq.setOperatorType( Query.Op.GreaterThan )
        newq.setValue( value )
        
        return newq
    
    def greaterThanOrEqual( self, value ):
        """
        Sets the operator type to Query.Op.GreaterThanOrEqual and 
        sets the value to the inputed value.
        
        :param      value       <variant>
        
        :return     <Query>
        
        :sa         __ge__
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test').greaterThanOrEqual(1)
                    |>>> print query
                    |test greater_than_or_equal 1
        """
        newq = Query(self.table(), self.columnName())
        newq.setOperatorType( Query.Op.GreaterThanOrEqual )
        newq.setValue( value )
        
        return newq
    
    def isNegated( self ):
        """
        Returns whether or not this query is negated.
        
        :return <bool>
        """
        return self._negate
    
    def isNull( self ):
        """
        Return whether or not this query contains any information.
        
        :return     <bool>
        """
        if ( self._columnName or self._value != Query.UNDEFINED ):
            return False
        return True
    
    def isUndefined( self ):
        """
        Return whether or not this query contains undefined value data.
        
        :return <bool>
        """
        return self._value == Query.UNDEFINED
    
    def in_( self, value ):
        """
        Sets the operator type to Query.Op.IsIn and sets the value
        to the inputed value.
        
        :param      value       <variant>
        
        :return     <Query>
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test').isIn([1,2])
                    |>>> print query
                    |test is_in [1,2]
        """
        newq = Query(self.table(), self.columnName())
        newq.setOperatorType( Query.Op.IsIn )
        newq.setValue( value )
        
        return newq
    
    def notIn( self, value ):
        """
        Sets the operator type to Query.Op.IsNotIn and sets the value
        to the inputed value.
        
        :param      value       <variant>
        
        :return     <Query>
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test').not_in([1,2])
                    |>>> print query
                    |test is_not_in [1,2]
        """
        newq = Query(self.table(), self.columnName())
        newq.setOperatorType( Query.Op.IsNotIn )
        newq.setValue( value )
        
        return newq
    
    def lessThan( self, value ):
        """
        Sets the operator type to Query.Op.LessThan and sets the
        value to the inputed value.
        
        :param      value       <variant>
        
        :return     <Query>
        
        :sa         lessThan
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test').lessThan(1)
                    |>>> print query
                    |test less_than 1
        """
        newq = Query(self.table(), self.columnName())
        newq.setOperatorType( Query.Op.LessThan )
        newq.setValue( value )
        
        return newq
    
    def lessThanOrEqual( self, value ):
        """
        Sets the operator type to Query.Op.LessThanOrEqual and sets 
        the value to the inputed value.
        
        :param      value       <variant>
        
        :return     <Query>
        
        :sa         lessThanOrEqual
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test').lessThanOrEqual(1)
                    |>>> print query
                    |test less_than_or_equal 1
        """
        newq = Query(self.table(), self.columnName())
        newq.setOperatorType( Query.Op.LessThanOrEqual )
        newq.setValue( value )
        
        return newq
    
    def matches( self, value ):
        """
        Sets the operator type to Query.Op.Matches and sets \
        the value to the inputed regex expression.  This method will only work \
        on text based fields.
        
        :param      value       <str>
        
        :return     <Query>
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test').matches('^\d+-\w+$')
                    |>>> print query
                    |test matches ^\d+-\w+$
        """
        newq = Query(self.table(), self.columnName())
        newq.setOperatorType( Query.Op.Matches )
        newq.setValue( value )
        
        return newq
    
    def negated( self ):
        """
        Negates the current state for this query.
        
        :return     <self>
        """
        query = Query(self.table(), self.columnName())
        query.setOperatorType(self.operatorType())
        query.setValue(self.value())
        query._negate = not self._negate
        return query
    
    def operatorType( self ):
        """
        Returns the operator type assigned to this query
        instance.
        
        :return     <Query.Op>
        """
        return self._op
    
    def or_( self, other ):
        """
        Creates a new compound query using the 
        QueryCompound.Op.Or type.
        
        :param      other   <Query> || <QueryCompound>
        
        :return     <QueryCompound>
        
        :sa         or_
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = (Q('test') != 1).or_(Q('name') == 'Eric')
                    |>>> print query
                    |(test does_not_equal 1 or name is Eric)
        """
        if ( other is None or other.isNull() ):
            return self
            
        elif ( self.isNull() ):
            return other
        
        return QueryCompound(self, other, op = QueryCompound.Op.Or)
    
    def setCaseSensitive( self, state ):
        """
        Sets whether or not this query will be case sensitive.
        
        :param      state   <bool>
        """
        self._caseSensitive = state
    
    def setColumnName( self, columnName ):
        """
        Sets the column name used for this query instance.
        
        :param      columnName      <str>
        """
        self._columnName = columnName
    
    def setOperatorType( self, op ):
        """
        Sets the operator type used for this query instance.
        
        :param      op          <Query.Op>
        """
        self._op = op
    
    def setTable( self, table ):
        """
        Sets the table instance that is being referenced for this query.
        
        :param      table | <subclass of orb.Table>
        """
        self._table = table
    
    def setValue( self, value ):
        """
        Sets the value that will be used for this query instance.
        
        :param      value       <variant>
        """
        self._value = value
    
    def setValueString( self, valuestring ):
        """
        Sets the value for this query from the inputed string representation \
        of the value.  For this method to work, the table and column name for 
        this query needs to be set.  Otherwise, the string value will be used.
        
        :param      valuestring | <str>
        """
        column = self.column()
        if ( column ):
            self.setValue(column.valueFromString(valuestring))
        else:
            self.setValue(valuestring)
    
    def startswith( self, value ):
        """
        Sets the operator type to Query.Op.Startswith and sets \
        the value to the inputed value.  This method will only work on text \
        based fields.
        
        :param      value       <str>
        
        :return     <Query>
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test').startswith('blah')
                    |>>> print query
                    |test startswith blah
        """
        newq = Query(self.table(), self.columnName())
        newq.setOperatorType( Query.Op.Startswith )
        newq.setValue( value )
        
        return newq
    
    def table( self ):
        """
        Return the table instance that this query is referencing.
        
        :return     <subclass of Table> || None
        """
        return self._table
    
    def tables( self ):
        """
        Returns the tables that this query is referencing.
        
        :return     [ <subclass of Table>, .. ]
        """
        output = []
        if ( self._table ):
            output.append(self._table)
        
        if ( isinstance( self._value, Query ) ):
            output += self._value.tables()
        
        return list(set(output))
    
    def toString( self ):
        """
        Returns this query instance as a semi readable language
        query.
        
        :warning    This method will NOT return a valid SQL statement.  The
                    backend classes will determine how to convert the Query
                    instance to whatever lookup code they need it to be.
        
        :return     <str>
        """
        if ( not self.__nonzero__() ):
            return ''
            
        pattern = dict(Query.SyntaxPatterns)[self.operatorType()]
        column  = self.columnName()
        val     = self.value()
        
        if ( self.table() ):
            column = '%s.%s' % (self.table().__name__, column)
        
        # comparing against another column in the DB
        if ( isinstance(val, Query) ):
            if ( val.isNull() ):
                val = None
            
            if ( val.table() ):
                val = '%s.%s' % (val.table().__name__, val.columnName())
            
            else:
                val = val.columnName()
        
        if ( val == Query.UNDEFINED ):
            return column
        
        opts = {'field': column, 'value': val}
        output = pattern.syntax() % opts
        return output
    
    def validate( self, record ):
        """
        Validates this query's value against the inputed record.  This will 
        return True if the record satisies the query condition.
        
        :param      record | <
        
        :return     <bool>
        """
        from orb import Table
        
        if ( isinstance(record, Table) ):
            rvalue = record.recordValue(self._columnName, autoInflate=False)
        else:
            rvalue = record.get(self._columnName)
        
        mvalue = self._value
        
        if Table.recordcheck(mvalue):
            mvalue = mvalue.primaryKey()
        if Table.recordcheck(rvalue):
            rvalue = rvalue.primaryKey()
        
        # basic operations
        if ( self._op == Query.Op.Is ):
            return rvalue == mvalue
        
        elif ( self._op == Query.Op.IsNot ):
            return rvalue != mvalue
        
        # comparison operations
        elif ( self._op == Query.Op.Between ):
            if ( len(mvalue) == 2 ):
                return mvalue[0] < rvalue < mvalue[1]
            return False
        
        elif ( self._op == Query.Op.LessThan ):
            return rvalue < mvalue
        
        elif ( self._op == Query.Op.LessThanOrEqual ):
            return rvalue <= mvalue
        
        elif ( self._op == Query.Op.GreaterThan ):
            return rvalue > mvalue
        
        elif ( self._op == Query.Op.GreaterThanOrEqual ):
            return rvalue >= mvalue
        
        # string operations
        elif ( self._op == Query.Op.Contains ):
            return unicode(rvalue) in unicode(mvalue)
        
        elif ( self._op == Query.Op.DoesNotContain ):
            return not unicode(rvalue) in unicode(mvalue)
        
        elif ( self._op == Query.Op.Startswith ):
            return unicode(rvalue).startswith(unicode(mvalue))
        
        elif ( self._op == Query.Op.Endswith ):
            return unicode(rvalue).endswith(unicode(mvalue))
        
        elif ( self._op == Query.Op.Matches ):
            return re.match(unicode(mvalue), str(rvalue)) != None
        
        elif ( self._op == Query.Op.DoesNotMatch ):
            return re.match(unicode(mvalue), str(rvalue)) == None
        
        # list operations
        elif ( self._op == Query.Op.IsIn ):
            return rvalue in mvalue
        
        elif ( self._op == Query.Op.IsNotIn ):
            return rvalue not in mvalue
        
        return False
    
    def value( self ):
        """
        Returns the value for this query instance
        
        :return     <variant>
        """
        return self._value
    
    def valueString( self ):
        """
        Converts the data for this query to a string value and returns it.  For
        this method to properly work, you need to have the columnName and table
        set for this query.
        
        :return     <str>
        """
        column = self.column()
        if ( column ):
            return column.valueToString(self.value())
        
        return str(self.value())
    
    @staticmethod
    def fromSearch( searchstr, mode = SearchMode.All ):
        """
        Creates a query instance from a particular search string.  Search 
        strings are a custom way of defining short hand notation search syntax.
        
        :param      searchstr | <str>
                    mode      | <orb.SearchMode>
        
        :return     ([<str> keyword, ..], <Query> query)
        
        :syntax     no deliminator (testing test test) | search keywords
                    column:value                       | column contains value
                    column:*value                      | column endswith value
                    column:value*                      | column startswith value
                    column:"value"                     | column == value
                    column:<value                      | column < value
                    column:<=value                     | column <= value
                    column:a<b                         | column between a and b
                    column:>value                      | column > value
                    column:>=value                     | column >= value
                    column:!value                      | column negate value
        """
        searchstr = str(searchstr)
        search_re = re.compile('(\w+):([\w,]+|"[^"]+")')
        results   = search_re.search(searchstr)
        query     = Query()
        
        def eval_value(value):
            result = re.match('^' + projex.regex.DATETIME + '$', value)
            
            # convert a datetime value
            if ( result ):
                data = result.groupdict()
                if ( len(data['year']) ):
                    data['year'] = '20' + data['year']
                
                if ( not data['second'] ):
                    data['second'] = '0'
                
                if ( data['ap'].startswith('p') ):
                    data['hour'] = 12 + int(data['hour'])
                
                return datetime.datetime(int(data['year']),
                                         int(data['month']),
                                         int(data['day']),
                                         int(data['hour']),
                                         int(data['min']),
                                         int(data['second']))
            
            # convert a date value
            result = re.match('^' + projex.regex.DATE + '$', value)
            if ( result ):
                data = result.groupdict()
                if ( len(data['year']) ):
                    data['year'] = '20' + data['year']
                
                return datetime.date(int(data['year']),
                                     int(data['month']),
                                     int(data['day']))
            
            # convert a time value
            result = re.match('^' + projex.regex.TIME + '$', value)
            if ( result ):
                data = result.groupdict()
                if ( not data['second'] ):
                    data['second'] = '0'
                
                if ( data['ap'].startswith('p') ):
                    data['hour'] = 12 + int(data['hour'])
                
                return datetime.time(int(data['hour']),
                                     int(data['min']),
                                     int(data['second']))
            
            try:
                return eval(value)
            except:
                return value
            
        while ( results ):
            column, values = results.groups()
            values = values.strip()
            
            # see if this is an exact value
            if ( values.startswith('"') and values.endswith('"') ):
                query &= Q(column) == values.strip('"')
            
            # process multiple values
            all_values = values.split(',')
            sub_q = Query()
            
            for value in all_values:
                value = value.strip()
                
                # process a contains search (same as no asterixes)
                if ( value.startswith('*') and value.endswith('*') ):
                    value = value.strip('*')
                
                if ( not value ):
                    continue
                
                negate = False
                if ( value.startswith('!') ):
                    negate = True
                
                value  = eval_value(value)
                if ( not isinstance(value, basestring) ):
                    sub_q |= Query(column) == value
                
                elif ( value.startswith('*') ):
                    sub_q |= Query(column).startswith(value.strip('*'))
                
                elif ( value.endswith('*') ):
                    sub_q |= Query(column).endswith(value.strip('*'))
                
                elif ( value.startswith('<=') ):
                    sub_q |= Query(column) <= value
                
                elif ( value.startswith('<') ):
                    sub_q |= Query(column) < value
                
                elif ( value.startswith('>=') ):
                    sub_q |= Query(column) >= value
                
                elif ( value.startswith('>') ):
                    sub_q |= Query(column) > value
                
                elif ( '<' in value ):
                    try:
                        a, b = value.splits('<')
                        success = True
                    except ValueError:
                        success = False
                    
                    if ( success ):
                        a = eval_value(a)
                        b = eval_value(b)
                        
                        sub_q |= Query(column).between(a, b)
                        
                    else:
                        sub_q |= Query(column).contains(value)
                else:
                    sub_q |= Query(column).contains(value)
            
            if ( mode == SearchMode.All ):
                query &= sub_q
            else:
                query |= sub_q
            
            # update the search values
            searchstr = searchstr[:results.start()] + searchstr[results.end():]
            results   = search_re.search(searchstr)
        
        return (searchstr.split(), query)
    
    @staticmethod
    def fromString( querystr ):
        """
        Recreates a query instance from the inputed string value.
        
        :param      querystr | <str>
        
        :return     <Query> || <QueryCompound> || None
        """
        querystr = str(querystr)
        
        queries  = {}
        for op, pattern in Query.SyntaxPatterns:
            pattern = pattern.pattern()
            match   = pattern.search(querystr)
            
            while ( match ):
                # extract query information
                key  = 'QUERY_%i' % (len(queries) + 1)
                grp  = match.group()
                data = match.groupdict()
                
                # built the new query instance
                value = data['value']
                if ( op in (Query.Op.IsIn, Query.Op.IsNotIn) ):
                    value = map(lambda x: x.strip(), 
                                data['value'].strip('[]').split(','))
                
                query = Query(data['field'], op = op, value = value)
                queries[key] = query
                
                # replace the querystr with a pointer to this query for 
                # future use
                querystr = querystr.replace(grp, key)
                match    = pattern.search(querystr)
        
        # if only 1 query existed, then no need to create a compound
        if (len(queries) == 1 ):
            return queries.values()[0]
        
        # otherwise, we need to build a compound
        return QueryCompound.build(querystr, queries)
    
    @staticmethod
    def typecheck( obj ):
        """
        Returns whether or not the inputed object is a type of a query.
        
        :param      obj     <variant>
        
        :return     <bool>
        """
        return isinstance( obj, Query )

#------------------------------------------------------------------------------

class QueryCompound:
    """ Defines combinations of queries via either the AND or OR mechanism. """
    Op = enum(
        'And',
        'Or'
    )
    
    def __contains__( self, value ):
        """
        Returns whether or not the query compound contains a query for the
        inputed column name.
        
        :param      value | <variant>
        
        :return     <bool>
        
        :usage      |>>> from orb import Query as Q
                    |>>> q = Q('testing') == True
                    |>>> 'testing' in q
                    |True
                    |>>> 'name' in q
                    |False
        """
        for query in self._queries:
            if ( value in query ):
                return True
        return False
    
    def __nonzero__( self ):
        return not self.isNull()
    
    def __str__( self ):
        """
        Returns the string representation for this query instance
        
        :sa         toString
        """
        return self.toString()
        
    def __init__( self, *queries, **options ):
        self._queries   = queries
        self._op        = options.get('op', QueryCompound.Op.And)
        self._negate    = options.get('negate', False)
    
    def __and__( self, other ):
        """
        Creates a new compound query using the 
        QueryCompound.Op.And type.
        
        :param      other   <Query> || <QueryCompound>
        
        :return     <QueryCompound>
        
        :sa         and_
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = (Q('test') != 1) & (Q('name') == 'Eric')
                    |>>> print query
                    |(test does_not_equal 1 and name is Eric)
        """
        return self.and_(other)
    
    def __neg__( self ):
        """
        Negates the current state of the query.
        
        :sa     negate
        
        :return     self
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = (Q('test') == 1) & (Q('name') == 'Eric')
                    |>>> print -query
                    |NOT (test is  1 and name is Eric)
        """
        return self.negated()
    
    def __or__( self, other ):
        """
        Creates a new compound query using the 
        QueryCompound.Op.Or type.
        
        :param      other   <Query> || <QueryCompound>
        
        :return     <QueryCompound>
        
        :sa         or_
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = (Q('test') != 1) | (Q('name') == 'Eric')
                    |>>> print query
                    |(test isNot 1 or name is Eric)
        """
        return self.or_(other)
        
    def and_( self, other ):
        """
        Creates a new compound query using the 
        QueryCompound.Op.And type.
        
        :param      other   <Query> || <QueryCompound>
        
        :return     <QueryCompound>
        
        :sa         __and__
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = (Q('test') != 1).and_((Q('name') == 'Eric')
                    |>>> print query
                    |(test isNot 1 and name is Eric)
        """
        if ( other is None or other.isNull() ):
            return self
        
        elif ( self.isNull() ):
            return other
        
        # grow this objects list if the operator types are the same
        if ( self.operatorType() == QueryCompound.Op.And and
             not self.isNegated() ):
            queries = list(self._queries)
            queries.append(other)
            opts = { 'op': QueryCompound.Op.And }
            
            # pylint: disable-msg=W0142
            return QueryCompound( *queries, **opts )
            
        # create a new compound
        return QueryCompound(self, other, op = QueryCompound.Op.And)
    
    def copy( self ):
        """
        Returns a copy of this query compound.
        
        :return     <QueryCompound>
        """
        out = QueryCompound()
        out._queries = [q.copy() for q in self._queries]
        out._op      = self._op
        out._negate  = self._negate
        return out
    
    def isNegated( self ):
        """
        Returns whether or not this query is negated.
        
        :return <bool>
        """
        return self._negate
    
    def isNull( self ):
        """
        Returns whether or not this join is empty or not.
        
        :return     <bool>
        """
        am_null = True
        for query in self._queries:
            if ( not query.isNull() ):
                am_null = False
                break
        
        return am_null
    
    def negated( self ):
        """
        Negates this instance and returns it.
        
        :return     self
        """
        qcompound = QueryCompound(*self._queries)
        qcompound._op     = self._op
        qcompound._negate = not self._negate
        return qcompound
    
    def operatorType( self ):
        """
        Returns the operator type for this compound.
        
        :return     <QueryCompound.Op>
        """
        return self._op
    
    def or_( self, other ):
        """
        Creates a new compound query using the 
        QueryCompound.Op.Or type.
        
        :param      other   <Query> || <QueryCompound>
        
        :return     <QueryCompound>
        
        :sa         or_
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = (Q('test') != 1).or_(Q('name') == 'Eric')
                    |>>> print query
                    |(test isNot 1 or name is Eric)
        """
        if ( other is None or other.isNull() ):
            return self
            
        elif ( self.isNull() ):
            return other
        
        # grow this objects list if the operator types are the same
        if ( self.operatorType() == QueryCompound.Op.Or and
             not self.isNegated() ):
            queries = list(self._queries)
            queries.append(other)
            opts = { 'op': QueryCompound.Op.Or }
            
            # pylint: disable-msg=W0142
            return QueryCompound(*queries, **opts)
        
        return QueryCompound(self, other, op = QueryCompound.Op.Or)
    
    def queries( self ):
        """
        Returns the list of queries that are associated with
        this compound.
        
        :return     <list> [ <Query> || <QueryCompound>, .. ]
        """
        return self._queries
    
    def setOperatorType( self, op ):
        """
        Sets the operator type that this compound that will be
        used when joining together its queries.
        
        :param      op      <QueryCompound.Op>
        """
        self._op = op
    
    def tables( self ):
        """
        Returns the tables that this query is referencing.
        
        :return     [ <subclass of Table>, .. ]
        """
        output = []
        for query in self._queries:
            output += query.tables()
        
        return list(set(output))
    
    def toString( self ):
        """
        Returns this query instance as a semi readable language
        query.
        
        :warning    This method will NOT return a valid SQL statement.  The
                    backend classes will determine how to convert the Query
                    instance to whatever lookup code they need it to be.
        
        :return     <str>
        """
        optypestr = QueryCompound.Op[self.operatorType()]
        op_type = ' %s ' % projex.text.underscore(optypestr)
        query = '(%s)' % op_type.join([q.toString() for q in self.queries()])
        if ( self.isNegated() ):
            query = 'NOT ' + query
        return query
    
    def validate( self, record ):
        """
        Validates the inputed record against this query compound.
        
        :param      record | <orb.Table>
        """
        op      = self._op
        queries = self.queries()
        
        if ( not queries ):
            return False
        
        for query in queries:
            valid = query.validate(record)
            
            if ( op == QueryCompound.Op.And and not valid ):
                return False
            elif ( op == QueryCompound.Op.Or and valid ):
                return True
        
        return op == QueryCompound.Op.And
    
    @staticmethod
    def build( compound, queries ):
        """
        Builds a compound based on the inputed compound string.  This should 
        look like: ((QUERY_1 and QUERY_2) or (QUERY_3 and QUERY_4)).  The 
        inputed query dictionary should correspond with the keys in the string.
        
        This method will be called as part of the Query.fromString method and 
        probably never really needs to be called otherwise.
        
        :param      compound | <str>
                    queries  | [<Query>, ..]
        
        :return     <Query> || <QueryCompound>
        """
        found      = False
        open       = 0
        indexStack = []
        compounds  = {}
        new_text   = str(compound)
        
        for index, char in enumerate(str(compound)):
            # open a new compound
            if ( char == '(' ):
                indexStack.append(index)
                
            # close a compound
            elif ( char == ')' and indexStack ):
                openIndex = indexStack.pop()
                match     = compound[openIndex+1:index]
                
                if ( not match ):
                    continue
                
                # create the new compound
                new_compound = QueryCompound.build(match, queries)
                
                key = 'QCOMPOUND_%i' % (len(compounds) + 1)
                compounds[key] = new_compound
                
                new_text = new_text.replace('(' + match + ')', key)
        
        new_text = new_text.strip('()')
        query    = Query()
        last_op  = 'and'
        for section in new_text.split():
            section = section.strip('()')
            
            # merge a compound
            if ( section in compounds ):
                section_q = compounds[section]
            
            elif ( section in queries ):
                section_q = queries[section]
            
            elif ( section in ('and', 'or') ):
                last_op = section
                continue
            
            else:
                logger.warning('Missing query section: %s', section)
                continue
            
            if ( query is None ):
                query = section_q
            elif ( last_op == 'and' ):
                query &= section_q
            else:
                query |= section_q
        
        return query
        
    @staticmethod
    def fromString( querystr ):
        """
        Returns a new compound from the inputed query string.  This simply calls
        the Query.fromString method, as the two work the same.
        
        :param      querystr | <str>
        
        :return     <Query> || <QueryCompound> || None
        """
        return Query.fromString(querystr)
    
    @staticmethod
    def typecheck( obj ):
        """
        Returns whether or not the inputed object is a QueryCompound object.
        
        :param      obj     <variant>
        
        :return     ,bool>
        """
        return isinstance( obj, QueryCompound )