#!/usr/bin/python

""" Defines the common errors for the database module. """

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

class OrbError(StandardError):
    """ Defines the base error class for the orb package """
    pass

class OrbWarning(Warning):
    """ Defines the base warnning class for the orb package """
    pass

# B
#------------------------------------------------------------------------------

class BackendNotFoundError(OrbError):
    def __init__(self, backend):
        OrbError.__init__( self, 'Could not find %s backend' % backend )

# C
#------------------------------------------------------------------------------

class CannotRemoveError(OrbError):
    def __init__( self, msg ):
        OrbError.__init__( self, msg )

class ColumnNotFoundWarning(OrbWarning):
    def __init__( self, column ):
        OrbWarning.__init__( self, '%s is a missing column.' % column )

class ColumnReadOnlyError(OrbError):
    def __init__( self, column ):
        OrbError.__init__( self, '%s is a read-only column.' % column )

class ColumnRequiredError(OrbError):
    def __init__( self, column ):
        OrbError.__init__( self, '%s is a required column.' % column )

class ConnectionError(OrbError):
    def __init__( self, msg, db ):
        from orb import Connection
        
        msgs = [msg]
        msgs.append('')
        
        pwd = '*' * (len(db.password()) - 4) + db.password()[-4:]
        
        msgs.append('type: %s' % db.databaseType())
        msgs.append('database: %s' % db.databaseName())
        msgs.append('username: %s' % db.username())
        msgs.append('password: %s' % pwd)
        msgs.append('host: %s' % db.host())
        msgs.append('port: %i' % db.port())
        
        msgs.append('')
        
        Connection.init()
        typs = ','.join(Connection.backends.keys())
        
        msgs.append('valid types: %s' % typs)
        
        OrbError.__init__(self, '\n'.join(msgs))

class ConnectionLostError(OrbError):
    def __init__(self):
        OrbError.__init__(self, 'Connection was lost to the database.  '\
                                'Please retry again soon.')

# D
#------------------------------------------------------------------------------

class DatabaseError(OrbError):
    def __init__( self, err ):
        text = '%s\n\nUnknown database error occurred.' % err
        OrbError.__init__( self, text )

class DatabaseQueryError(OrbError):
    def __init__( self, sql, options ):
        msg = 'Query was:\n\n"%s"\n\nArgs: %s' % (sql, options)
        OrbError.__init__(self, msg)

class DatabaseNotFoundError(OrbError):
    def __init__( self ):
        OrbError.__init__( self, 'No database was found.' )

class DuplicateColumnWarning(OrbWarning):
    """ Thrown when there is a duplicate column found within a single \
        hierarchy of a Table. """
    
    def __init__( self, column ):
        err = '%s is already a column and cannot be duplicated.' % column
        OrbWarning.__init__(self, err)

# F
#------------------------------------------------------------------------------

class ForeignKeyMissingReferenceError(OrbError):
    def __init__( self, column ):
        text = '%s is a foreign key with no reference table.' % column.name()
        OrbError.__init__( self, text )

# I
#------------------------------------------------------------------------------

class InvalidDatabaseXmlError(OrbError):
    def __init__( self, xml ):
        OrbError.__init__( self, '%s is an invalid XML data set.' % xml )

class InvalidColumnTypeError(OrbError):
    def __init__( self, columnType ):
        text = '%s is an invalid Column type.' % columnType
        OrbError.__init__( self, text )

class InvalidQueryError(OrbError):
    def __init__( self, query ):
        text = 'Invalid lookup info: %s' % query
        OrbError.__init__( self, text )

class InvalidPrimaryKeyError(OrbError):
    def __init__( self, columns, pkey ):
        colnames = ','.join([col.name() for col in columns])
        text     = 'Invalid key: %s | %s' % (colnames, pkey)
        OrbError.__init__( self, text )

class InvalidSchemaDefinitionError(OrbError):
    def __init__( self, definition ):
        err = '%s is not a valid schema definition type.' % type(definition)
        err += ' A schema must be either a dictionary or a TableSchema.'
        OrbError.__init__( self, err )

# M
#------------------------------------------------------------------------------

class MissingTableSchemaWarning(OrbWarning):
    """ Thrown when a call to the tableSchema method of the \
        class cannot find the requested table schema. """
    def __init__( self, tableName ):
        err = '%s is not a valid table schema.' % tableName
        OrbWarning.__init__( self, err )

# P
#------------------------------------------------------------------------------

class PrimaryKeyNotDefinedError(OrbError):
    def __init__( self, record ):
        OrbError.__init__( self, 'No primary key defined for %s.' % record )

class PrimaryKeyNotFoundError(OrbError):
    def __init__( self, table, pkey ):
        msg = '%s has not primary key: %s.' % (table, pkey)
        OrbError.__init__( self, msg )

# T
#------------------------------------------------------------------------------

class TableNotFoundError(OrbError):
    def __init__( self, table ):
        OrbError.__init__( self, 'Could not find "%s" table.' % table )

# S
#------------------------------------------------------------------------------

class SchemaNotFoundError(OrbError):
    def __init__( self ):
        OrbError.__init__( self, 'No schema was found to sync.' )

# V
#------------------------------------------------------------------------------

class ValidationError(OrbError):
    """ 
    Raised when a column is being set with a value that does not pass
    validation.
    """
    def __init__( self, column, value ):
        err  = '"%s" does not meet %s validation requirements.\n%s'
        err %= (value, column.displayName(), column.validatorHelp())
        
        OrbError.__init__( self, err )