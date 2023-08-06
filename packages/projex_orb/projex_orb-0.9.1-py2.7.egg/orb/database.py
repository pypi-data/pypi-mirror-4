#!/usr/bin/python

""" Defines the base database class. """

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
from xml.etree  import ElementTree

from projex.decorators import retrymethod

import orb
from orb            import errors
from orb.decorators import transactedmethod

logger = logging.getLogger(__name__)

class Database(object):
    """ Contains all the database connectivity information. """
    _current = None
    _databases = {}
    
    def __init__(   self, 
                    typ          = None, 
                    name         = '', 
                    user         = '', 
                    password     = '', 
                    host         = '', 
                    port         = None,
                    databaseName = None,
                    applicationToken = '' ):
        
        if ( not typ ):
            typ = 'Sqlite'
        
        self._databaseType      = typ
        self._default           = False
        self._name              = name
        self._databaseName      = databaseName
        self._host              = host
        self._port              = port
        self._username          = user
        self._password          = password
        self._connection        = None
        self._commandsBlocked   = False
        self._applicationToken  = applicationToken
        self._namespace         = None
    
    def applicationToken( self ):
        """
        Returns the application token that is linked to the current API.  This
        value is used for backends that require communication with a remote
        server.
        
        :return     <str>
        """
        return self._applicationToken
    
    def blockCommands( self, state ):
        """
        Sets whether or not the database should be blocking
        the calls from hitting the database.  When this is
        on, the backends will simply log the command that is 
        created to the current logger vs. actually executing it.
        
        :sa         commandsBlocked
        
        :param      state   <bool>
        """
        self._commandsBlocked = state
    
    def commandsBlocked( self ):
        """
        Returns whether or not the commands are being blocked
        from hitting the database.  When this is on, the backends
        will simploy log the command that is created to the
        current logger vs. actually executing it.
        
        :sa         commandsBlocked
        
        :return     <bool> success
        """
        return self._commandsBlocked
    
    def connect( self ):
        """
        Returns the current database connection for this
        instance.
        
        :return     <bool>
        """
        if ( self._connection ):
            return True
        
        # create a new connection based on the type
        from orb import Connection
        connection = Connection.create(self)
        if ( not connection ):
            msg = 'There was an error creating a backend class for database.'
            raise errors.BackendNotFoundError(self._databaseType)
        
        self._connection = connection
        return True
    
    def connection( self, autoConnect=True):
        """
        Returns the connection instance for this database.
        
        :param      autoConnect     <bool>
        
        :return     <Connection> || None
        """
        # automatically connect when necessary
        if ( autoConnect ):
            self.connect()
            
        return self._connection
    
    def databaseName( self ):
        """
        Returns the database name that will be used at the lower level for \
        this database.  If not explicitly set, then the name will be used.
        
        :return     <str>
        """
        if ( not self._databaseName ):
            return self.name()
        
        return self._databaseName
    
    def databaseType( self ):
        """
        Returns the database type for this instance.
        
        :return     <str>
        """
        return self._databaseType
    
    def disconnect( self ):
        """
        Disconnects the current database connection from the
        network.
                    
        :return     <bool>
        """
        if ( not self._connection ):
            return False
            
        self._connection.close()
        return True
    
    def host( self ):
        """
        Returns the host location assigned to this
        database object.
        
        :returns    <str>
        """
        if ( not self._host ):
            return 'localhost'
        return self._host
    
    def isDefault( self ):
        """
        Returns if this is the default database when loading the system.
        
        :return     <bool>
        """
        return self._default
    
    def isThreadEnabled( self ):
        """
        Returns whether or not threading is enabled for this database.
        
        :return     <bool>
        """
        con = self.connection()
        if ( con ):
            return con.isThreadEnabled()
        return False
    
    def name( self ):
        """
        Returns the database name for this database instance.
        
        :return     <str>
        """
        return self._name
    
    def namespace( self ):
        """
        Returns the default namespace for this database.  If no namespace
        is defined, then the global Orb default namespace is returned.
        
        :return     <str>
        """
        if ( self._namespace is not None ):
            return self._namespace
        
        from orb import Orb
        return Orb.instance().namespace()
    
    def password( self ):
        """
        Returns the password used for this database instance.
        
        :return     <str>
        """
        return self._password
    
    def port( self ):
        """
        Returns the port number to connect to the host on.
        
        :return     <int>
        """
        return self._port
    
    def schemas( self ):
        """
        Looks up all the table schemas in the Orb manager that are mapped to \
        this database.
        
        :return     [<TableSchema>, ..]
        """
        from orb import Orb
        return Orb.instance().databaseSchemas(self)
    
    def setApplicationToken(self, token):
        """
        Sets the application token for this database to the inputed token.
        
        :param      token | <str>
        """
        self._applicationToken = token
    
    def setCurrent( self ):
        """
        Makes this database the current default database
        connection for working with models.
        
        :param      database        <Database>
        """
        Database._current = self
    
    def setDatabaseName( self, databaseName ):
        """
        Sets the database name that will be used at the lower level to manage \
        connections to various backends.
        
        :param      databaseName | <str>
        """
        self._databaseName = databaseName
    
    def setDatabaseType( self, databaseType ):
        """
        Sets the database type that will be used for this instance.
        
        :param      databaseType | <str>
        """
        self._databaseType = str(databaseType)
    
    def setDefault( self, state ):
        """
        Sets whether or not this database is the default database.
        
        :param      state | <bool>
        """
        self._default = state
    
    def setName( self, name ):
        """
        Sets the database name for this instance to the given name.
        
        :param      datatbaseName   <str>
        """
        self._name = str(name)
    
    def setNamespace( self, namespace ):
        """
        Sets the default namespace for this database to the inputed name.
        
        :param      namespace | <str> || None
        """
        self._namespace = namespace
    
    def setHost( self, host ):
        """
        Sets the host path location assigned to this
        database object.
        
        :param      host      <str>
        """
        self._host = str(host)
    
    def setPassword( self, password ):
        """ 
        Sets the password for the connection for this database.
        
        :param      password    <str>
        """
        self._password  = str(password)
    
    def setPort( self, port ):
        """
        Sets the port number to connect to.  The default value
        will be 5432.
        
        :param      port    <int>
        """
        self._port = port
    
    def setUsername( self, username ):
        """
        Sets the username used for this database's connection.
        
        :param      username        <str>
        """
        self._username = str(username)
    
    @transactedmethod()
    def sync( self, **kwds ):
        """
        Syncs the datbase by calling its schema sync method.  If
        no specific schema has been set for this database, then
        the global database schema will be used.  If the dryRun
        flag is specified, then all the resulting commands will
        just be logged to the current logger and not actually 
        executed on the database.
        
        :note       From version 0.6.0 on, this method now accepts a mutable
                    keyword dictionary of values.  You can supply any member 
                    value for either the <orb.LookupOptions> or
                    <orb.DatabaseOptions>, 'options' for 
                    an instance of the <orb.DatabaseOptions>
        
        :return     <bool> success
        """
        # collect the information for this database
        con     = self.connection()
        schemas = self.schemas()
        schemas.sort(Database.compareSchemas)
        
        options = kwds.get('options', orb.DatabaseOptions(**kwds))
        
        # first pass will add columns and default columns, but may miss
        # certain foreign key references since one table may not exist before
        # another yet
        for schema in schemas:
            con.syncTable(schema, options)
    
        # second pass will ensure that all columns, including foreign keys
        # will be generated
        for schema in schemas:
            con.updateTable(schema, options)
        
        # third pass will generate all the proper value information
        for schema in schemas:
            model = schema.model()
            model.__syncdatabase__()
        
    def toXml( self, xparent ):
        """
        Saves this datbase instance to xml under the inputed parent.
        
        :param      xparent | <xml.etree.ElementTree.Element>
        
        :return     <xml.etree.ElementTree.Element>
        """
        xdatabase = ElementTree.SubElement(xparent, 'database')
        xdatabase.set('name', self._name)
        xdatabase.set('default', str(self._default))
        
        if ( self.databaseType() ):
            xdatabase.set('type', self.databaseType())
        
        if ( self._host ):
            ElementTree.SubElement(xdatabase, 'host').text = str(self._host)
        if ( self._port ):
            ElementTree.SubElement(xdatabase, 'port').text = str(self._port)
        if ( self._username ):
            ElementTree.SubElement(xdatabase, 'username').text = self._username
        if ( self._password ):
            ElementTree.SubElement(xdatabase, 'password').text = self._password
        if ( self._databaseName ):
            ElementTree.SubElement(xdatabase, 
                                   'dbname').text = self._databaseName
        if ( self._applicationToken ):
            ElementTree.SubElement(xdatabase, 
                                   'token').text = self._applicationToken
        return xdatabase
    
    def username( self ):
        """
        Returns the username used for the connection of this
        instance.
        
        :return     <str>
        """
        return self._username
    
    @staticmethod
    def compareSchemas( schemaA, schemaB ):
        """
        Compares the two schemas based on their groups.
        
        :param      schemaA | <TableSchema>
                    schemaB | <TableSchema>
        """
        grpA = schemaA.group()
        grpB = schemaB.group()
        
        if ( grpA and grpB ):
            return cmp(grpA.order(), grpB.order())
        
        return cmp(schemaA, schemaB)
    
    @staticmethod
    def current():
        """
        Returns the current database instance.
        
        :return     <Database> || None
        """
        return Database._current
    
    @staticmethod
    def find( name ):
        """
        Looks up a database with the inputed name.
        
        :param      name | <str>
        
        :return     <Database> || None
        """
        return Database._databases.get(str(name))
    
    @staticmethod
    def fromXml( xdatabase ):
        """
        Returns a new database instance from the inputed xml data.
        
        :param      xdatabase | <xml.etree.Element>
        
        :return     <Database>
        """
        db = Database()
        
        db.setDatabaseType( xdatabase.get('type', 'Sqlite') )
        db.setName(         xdatabase.get('name', '') )
        db.setDefault(      xdatabase.get('default') == 'True')
        
        xhost   = xdatabase.find('host')
        xport   = xdatabase.find('port')
        xuser   = xdatabase.find('username')
        xpword  = xdatabase.find('password')
        xdbname = xdatabase.find('dbname')
        xtoken  = xdatabase.find('token')
        
        if ( xhost != None ):
            db.setHost(xhost.text)
        if ( xport != None ):
            db.setPort(xport.text)
        if ( xuser != None ):
            db.setUsername(xuser.text)
        if ( xpword != None ):
            db.setPassword(xpword.text)
        if ( xdbname != None ):
            db.setDatabaseName(xdbname.text)
        if ( xtoken != None ):
            db.setApplicationToken(xtoken.text)
        
        return db
    
    @staticmethod
    def register( db ):
        """
        Registers the inputed database to the system.
        
        :param      db | <Database>
        """
        Database._databases[db.name()] = db