#!/usr/bin/python

""" Defines an overall management class for all environments, databases, 
    and schemas. """

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

import glob
import logging
import os.path
import xml.parsers.expat

from xml.etree  import ElementTree

import projex.text
import projex.security

logger = logging.getLogger(__name__)

class Orb(object):
    _instance = None
    
    def __init__( self ):
        # currency
        self._environment   = None
        self._database      = None
        self._namespace     = ''
        self._filename      = ''
        self._merging       = False
        
        # registry
        self._environments  = {}
        self._groups        = {}
        self._databases     = {}
        self._schemas       = {}
        self._properties    = {}
    
    def clear( self ):
        """
        Clears out all the current data from this orb instance.
        """
        self._environment   = None
        self._database      = None
        
        # close any active connections
        for db in self._databases.values():
            con = db.connection()
            if ( con ):
                db.connection().close()
        
        # close any active environments
        for env in self._environments.values():
            env.clear()
        
        self._filename = ''
        self._groups.clear()
        self._environments.clear()
        self._databases.clear()
        self._schemas.clear()
        self._properties.clear()
    
    def clearCache( self ):
        """
        Force clears all the cached data from the various schemas.
        """
        for schema in self.schemas():
            model = schema.model()
            if ( not (model and schema.isCacheEnabled()) ):
                continue
            
            model.instanceCache().clear()
    
    def database( self, name = None, environment = None ):
        """
        Returns the database for this manager based on the inputed name. \
        If no name is supplied, then the currently active database is \
        returned.  If the environment variable is specified then the \
        database lookup will occur in the specific environment, otherwise \
        the active environment is used.
        
        :usage      |>>> from orb import Orb
                    |>>> Orb.instance().database() # returns active database
                    |>>> Orb.instance().database('User') # returns the User db
                    |>>> Orb.instance().database('User', 'Debug') # from Debug
        
        :param      name | <str> || None
                    environment | <str> || <orb.environment.Environment> || None
        
        :return     <orb.database.Database> || None
        """
        from orb import Environment
        
        if ( not name ):
            return self._database
        
        if ( not environment ):
            environment = self._environment
        elif ( not isinstance(environment, Environment) ):
            environment = self.environment(environment)
        
        if ( environment ):
            db = environment.database(name)
        else:
            db = None
        
        if ( not db ):
            db = self._databases.get(str(name))
        
        return db
    
    def databases( self, recursive = False ):
        """
        Returns the databases for this system.  If the recursive flag is \
        set, then all databases defined by all environments will also be \
        returned.
        
        :return     [<orb.database.Database>, ..]
        """
        output = self._databases.values()
        
        if ( recursive ):
            for env in self.environments():
                output += env.databases()
        
        return output
    
    def databaseSchemas( self, db ):
        """
        Returns a list of schemas that are mapped to the inputed database.
        
        :param      db | <orb.database.Database>
        """
        is_curr = db == self._database
        
        out = []
        for schema in self._schemas.values():
            if ( not schema.databaseName() and is_curr or
                 schema.databaseName() == db.name() ):
                out.append(schema)
                
        return out
    
    def environment( self, name = None ):
        """
        Returns the environment for this manager based on the inputed name. \
        If no name is supplied, then the currently active environment is \
        returned.
        
        :param      name | <str> || None
        
        :return     <orb.environment.Environment> || None
        """
        if ( name ):
            return self._environments.get(str(name))
        return self._environment
    
    def environments( self ):
        """
        Returns a list of all the environments that are used by this orb \
        instance.
        
        :return     [<orb.environment.Environment>, ..]
        """
        return self._environments.values()
    
    def findRelatedColumns( self, schema ):
        """
        Looks up all the related columns and tables for the inputed table \
        schema.
        
        :param      schema | <orb.tableschema.TableSchema>
        """
        names           = [schema.name()] + schema.inheritsRecursive()
        related_columns = []
        
        for table_schema in self._schemas.values():
            for column in table_schema.columns():
                if ( column in related_columns ):
                    continue
                    
                if ( column.reference() in names ):
                    related_columns.append(column)
        
        return related_columns
    
    def findRelations( self, schema ):
        """
        Looks up all the related columns and tables for the inputed table \
        schema.
        
        :param      schema | <orb.tableschema.TableSchema>
        """
        names       = [schema.name()] + schema.inheritsRecursive()
        relations   = []
        processed   = []
        
        for table_schema in self._schemas.values():
            rel_cols = []
            
            for column in table_schema.columns():
                if ( column in processed ):
                    continue
                    
                if ( column.reference() in names ):
                    rel_cols.append(column)
                    processed.append(column)
            
            if ( rel_cols ):
                relations.append( (table_schema.model(), rel_cols) )
        
        return relations
    
    def filename( self ):
        """
        Returns the filename linked with this orb manager.  This property will \
        be set by the load and save methods.
        
        :return     <str>
        """
        return self._filename
    
    def group( self, name, autoAdd = False ):
        """
        Returns a group based on the inputed name.
        
        :param      name | <str>
                    autoAdd | <bool>
        
        :return     <orb._orbgroup.OrbGroup> || None
        """
        grp = self._groups.get(str(name))
        if ( not grp and autoAdd ):
            from orb import OrbGroup
            
            grp = OrbGroup(str(name))
            grp.setOrder(len(self._groups))
            self._groups[grp.name()] = grp
            
        return grp
    
    def groups( self ):
        """
        Returns a list of all the registered groups for this orb instance.
        
        :return     [<orb._orbgroup.OrbGroup>, ..]
        """
        out = self._groups.values()
        out.sort(key = lambda x: x.order())
        return out
    
    def inheritedModels( self, model ):
        """
        Returns any models that inherit from the inputed moddel.
        
        :return     [<orb.tableschema.Table>, ..]
        """
        out = []
        for schema in self._schemas.values():
            smodel = schema.model()
            
            if ( model == smodel ):
                continue
            
            if ( smodel and issubclass(smodel, model) ):
                out.append(smodel)
        return out
    
    def load( self, filename = '' ):
        """
        Loads the settings for this orb manager from the inputed xml file.
        
        :param      filename | <str>
        
        :return     <bool> | success
        """
        if ( not filename ):
            filename = self.filename()
        
        if ( not (filename and os.path.exists(filename)) ):
            logger.error('Invalid ORB file: %s' % filename)
            return False
        
        self.clear()
        if ( not self.merge(filename) ):
            return False
            
        self._filename = str(filename)
        return True
    
    def merge( self, filename ):
        """
        Merges the inputed ORB file to the schema.
        
        :param      filename | <str>
        
        :return     <bool>
        """
        filename = str(filename)
        if os.path.isdir(filename):
            for orbfile in glob.glob(os.path.join(filename, '*.orb')):
                self.merge(orbfile)
            return False
        
        if not os.path.exists(filename):
            return False
        
        from orb import Environment, Database
        
        try:
            xorb = ElementTree.parse(filename).getroot()
        except (xml.parsers.expat.ExpatError, xml.etree.ElementTree.ParseError):
            xorb = None
        
        if xorb is None:
            f = open(filename, 'r')
            data = f.read()
            f.close()
            
            # try unencrypting the data
            unencrypted = projex.security.decrypt(data, useBase64=True)
            try:
                xorb = ElementTree.fromstring(unencrypted)
            except (xml.parsers.expat.ExpatError, 
                    xml.etree.ElementTree.ParseError):
                logger.exception('Failed to load ORB file: %s' % filename)
                return False
        
        # load properties
        xprops = xorb.find('properties')
        if ( xprops is not None ):
            for xprop in xprops:
                self.setProperty(xprop.get('key'), xprop.get('value'))
            
        # load environments
        xenvs = xorb.find('environments')
        if ( xenvs is not None ):
            for xenv in xenvs:
                env = Environment.fromXml(xenv)
                self.registerEnvironment(env, env.isDefault())
        
        # load databases
        xdbs = xorb.find('databases')
        if ( xdbs is not None ):
            for xdb in xdbs:
                db = Database.fromXml(xdb)
                self.registerDatabase(db, db.isDefault())
                
        # load schemas
        xgroups = xorb.find('groups')
        if ( xgroups is not None ):
            from orb import OrbGroup
            for xgroup in xgroups:
                grp = OrbGroup.fromXml(xgroup)
                if ( not grp ):
                    continue
                
                self.registerGroup(grp)
        
        return True
    
    def model( self, name, autoGenerate=False):
        """
        Looks up a model class from the inputed name.
        
        :param      name | <str>
                    autoGenerate | <bool>
        
        :return     <subclass of Table> || <orb.Table> || None
        """
        schema = self.schema(name)
        # define a model off an existing schema
        if ( schema ):
            return schema.model(autoGenerate = autoGenerate)
        
        # generate a blank table
        elif autoGenerate:
            logger.warning('Could not find a schema for %s' % name)
            from orb.table import Table
            return Table
        
        return None
    
    def namespace( self ):
        """
        Returns the current namespace that the system should be operating in.
        
        :return     <str>
        """
        return self._namespace
    
    def property( self, propname, default = '' ):
        """
        Returns the property value for this manager from the given name.  \
        If no property is set, then the default value will be returned.
        
        :return     <str>
        """
        return self._properties.get(propname, str(default))
    
    def registerDatabase( self, database, active = False ):
        """
        Registers a particular database with this environment.
        
        :param      database | <orb.database.Database>
                    active   | <bool>
        """
        self._databases[database.name()] = database
        if ( active or not self._database ):
            self._database = database
    
    def registerEnvironment( self, environment, active = False ):
        """
        Registers a particular environment with this environment.
        
        :param      database | <orb.environment.Environment>
                    active | <bool>
        """
        self._environments[environment.name()] = environment
        
        # set the active environment
        if ( active or not self._environment ):
            self.setEnvironment(environment)
    
    def registerGroup( self, group ):
        """
        Registers the inputed orb group to the system.
        
        :param      group | <orb._orbgroup.OrbGroup>
        """
        group.setOrder(len(self._groups))
        self._groups[str(group.name())] = group
        for schema in group.schemas():
            self._schemas[str(schema.name())] = schema
    
    def registerSchema( self, schema ):
        """
        Registers the inputed schema with the environment.
        
        :param      schema | <orb.tableschema.TableSchema>
        """
        grp = self.group(schema.groupName(), autoAdd = True)
        grp.addSchema(schema)
        
        self._schemas[schema.name()] = schema
    
    def save( self, encrypted = False ):
        """
        Saves the current orb structure out to a file.  The filename will be \
        based on the currently set name.
        
        :param      encrypted | <bool>
        
        :sa     saveAs
        
        :return     <bool>
        """
        return self.saveAs(self.filename(), encrypted = encrypted)
    
    def saveAs( self, filename, encrypted = False ):
        """
        Saves the current orb structure out to the inputed file.
        
        :param      filename | <str>
                    encrypted | <bool>
        
        :return     <bool> | success
        """
        if ( not filename ):
            return False
        
        xorb = ElementTree.Element('orb')
        
        import orb
        xorb.set('version', orb.__version__)
        
        # save out properties
        xprops = ElementTree.SubElement(xorb, 'properties')
        for key, value in self._properties.items():
            xprop = ElementTree.SubElement(xprops, 'property')
            xprop.set('key', key)
            xprop.set('value', value)
        
        # save out the environments
        xenvs = ElementTree.SubElement(xorb, 'environments')
        for env in self.environments():
            env.toXml(xenvs)
        
        # save out the global databases
        xdbs = ElementTree.SubElement(xorb, 'databases')
        for db in self.databases():
            db.toXml(xdbs)
        
        # save out the groups
        xgroups = ElementTree.SubElement(xorb, 'groups')
        for grp in self.groups():
            grp.toXml(xgroups)
        
        projex.text.xmlindent(xorb)
        data = ElementTree.tostring(xorb)
        
        if encrypted:
            data = projex.security.encrypt(data, useBase64=True)
        
        f = open(filename, 'w')
        f.write(data)
        f.close()
        
        return True
    
    def schema( self, name ):
        """
        Looks up the registered schemas for the inputed schema name.
        
        :return     <orb.tableschema.TableSchema> || None
        """
        return self._schemas.get(str(name))
    
    def schemas( self ):
        """
        Returns a list of all the schemas for this instance.
        
        :return     [<orb.tableschema.TableSchema>, ..]
        """
        return self._schemas.values()
    
    def setDatabase( self, database, environment = None ):
        """
        Sets the active database to the inputed database.
        
        :param      database | <str> || <orb.database.Database> || None
                    environment | <str> || <orb.environment.Environment> || None
        """
        from orb import Database
        
        if ( not isinstance(database, Database) ):
            database = self.database(database, environment)
            
        self._database = database
    
    def setEnvironment( self, environment ):
        """
        Sets the active environment to the inputed environment.
        
        :param      environment | <str> || <orb.environment.Environment> || None
        """
        from orb import Environment
        
        if ( not isinstance(environment, Environment) ):
            environment = self.environment(environment)
        
        self._environment = environment
        self.setDatabase(environment.defaultDatabase())
    
    def setModel( self, name, model ):
        """
        Sets the model class for the inputed schema to the given model.
        
        :param      name    | <str>
                    model   | <subclass of Table>
        
        :return     <bool> | success
        """
        schema = self._schemas.get(str(name))
        if ( schema ):
            schema.setModel(model)
            return True
        return False
    
    def setNamespace( self, namespace ):
        """
        Sets the namespace that will be used for this system.
        
        :param      namespace | <str>
        """
        self._namespace = namespace
    
    def setProperty( self, property, value ):
        """
        Sets the custom property to the inputed value.
        
        :param      property | <str>
                    value    | <str>
        """
        self._properties[str(property)] = str(value)
    
    def unregisterDatabase( self, database ):
        """
        Un-registers a particular database with this environment.
        
        :param      database | <orb.database.Database>
        """
        if ( database.name() in self._databases ):
            con = database.connection()
            if ( con ):
                con.close()
            self._databases.pop(database.name())
    
    def unregisterGroup( self, group ):
        """
        Un-registers the inputed orb group to the system.
        
        :param      group | <orb._orbgroup.OrbGroup>
        """
        if ( not group.name() in self._groups ):
            return
        
        self._groups.pop(group.name())
        for schema in group.schemas():
            if ( schema.name() in self._schemas ):
                self._schemas.pop(schema.name())
        
    def unregisterEnvironment( self, environment ):
        """
        Un-registers a particular environment with this environment.
        
        :param      database | <orb.environment.Environment>
        """
        if ( environment.name() in self._environments ):
            self._environments.pop(environment.name())
    
    def unregisterSchema( self, schema ):
        """
        Un-registers the inputed schema with the environment.
        
        :param      schema | <orb.tableschema.TableSchema>
        """
        if ( schema.name() in self._schemas ):
            grp = self.group(schema.groupName())
            grp.removeSchema(schema)
            
            self._schemas.pop(schema.name())
    
    def loadModels( self, scope, groupName = None, autoGenerate = True ):
        """
        Loads the models from the orb system into the inputed scope.
        
        :param      scope       | <dict>
                    groupName   | <str> || None
        """
        if ( scope is None ):
            return []
        
        added = []
        for schema in self._schemas.values():
            if ( groupName != None and schema.groupName() != groupName ):
                continue
            
            added.append(schema.name())
            model = schema.model(autoGenerate = autoGenerate)
            scope[model.__name__] = model
        
        return added
    
    @staticmethod
    def databaseTypes():
        """
        Returns a list of all the database types (Connection backends) that are
        available for the system.
        
        :return     [<str>, ..]
        """
        from orb import Connection
        Connection.init()
        return sorted(Connection.backends.keys())
    
    @staticmethod
    def instance():
        """
        Returns the instance of the Orb manager.
        
        :return     <orb._orb.Orb>
        """
        if ( not Orb._instance ):
            Orb._instance = Orb()
            
        return Orb._instance
    
    @staticmethod
    def quickinit( filename, scope = None ):
        """
        Loads the settings for the orb system from the inputed .orb filename. \
        If the inputed scope variable is passed in, then the scope will be \
        updated with the models from the system.
        
        :param      filename | <str>
                    scope | <bool>
        
        :return     <bool> | success
        """
        # clear the current information
        Orb.instance().clear()
        
        # load the new information
        if ( not Orb.instance().load(filename) ):
            return False
        
        # update the scope with the latest data
        Orb.instance().loadModels(scope)
        return True
