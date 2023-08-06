#!/usr/bin/python

""" Defines the meta information for a column within a table schema. """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = ['Eric Hulser']
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintanence information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

#------------------------------------------------------------------------------

import datetime
import decimal
import re
from time import strptime

from xml.etree import ElementTree

import projex.text
import projex.regex

from orb.common import ColumnType, RemovedAction
from orb import errors

class Column(object):
    """ Used to define database schema columns when defining Table classes. """
    
    # define default naming system
    TEMPLATE_PRIMARY_KEY = 'id'
    TEMPLATE_GETTER      = '[name::camelHump::lower_first]'
    TEMPLATE_SETTER      = 'set[name::camelHump::upper_first::lstrip(Is)]'
    TEMPLATE_FIELD       = '[name::underscore::lower]'
    TEMPLATE_DISPLAY     = '[name::upper_first::words]'
    TEMPLATE_INDEX       = 'by[name::camelHump::upper_first]'
    TEMPLATE_REVERSED    = '[name::reversed::camelHump::lower_first]'
    TEMPLATE_REFERENCE   = '[name::underscore::lower]_id'
    TEMPLATE_COMPLEX_REF = '[table::underscore::lower]_' \
                           '[name::underscore::lower]_id'
    
    TEMPLATE_MAP = {
        'getterName':   TEMPLATE_GETTER,
        'setterName':   TEMPLATE_SETTER,
        'fieldName':    TEMPLATE_FIELD,
        'displayName':  TEMPLATE_DISPLAY,
        'indexName':    TEMPLATE_INDEX,
        'primaryKey':   TEMPLATE_PRIMARY_KEY,
    }
    
    VALIDATOR_TYPES = {
        ColumnType.Email:       projex.regex.EMAIL,
        ColumnType.Password:    projex.regex.PASSWORD,
    }
    
    VALIDATOR_HELP = {
        ColumnType.Email:       projex.regex.EMAIL_HELP,
        ColumnType.Password:    projex.regex.PASSWORD_HELP
    }
    
    def __init__( self, typ, name, **options ):
        self._name   = name
        self._type   = typ
        self._schema = options.get('schema')
        
        # set default values
        ref = options.get('reference', '')
        for key in Column.TEMPLATE_MAP.keys():
            if ( not key in options ):
                options[key] = Column.defaultDatabaseName(key, name, ref)
        
        # accessor properties
        self._getterName    = options.get('getterName')
        self._fieldName     = options.get('fieldName')
        self._setterName    = options.get('setterName')
        self._displayName   = options.get('displayName')
        self._indexName     = options.get('indexName')
        self._reversedName  = options.get('reversedName', '')
        self._searchable    = options.get('searchable', False)
        
        # define validator expression
        if ( not 'validator' in options ):
            self._validatorText  = Column.VALIDATOR_TYPES.get( typ, '' )
        else:
            self._validatorText = options['validator']
        
        if ( not 'validatorHelp' in options ):
            self._validatorHelp  = Column.VALIDATOR_HELP.get( typ, '')
        else:
            self._validatorHelp = options.get('validatorHelp', '')
        
        # column description properties
        self._reference     = options.get('reference',      '')
        self._reversed      = options.get('reversed',       False)
        self._default       = options.get('default',        None)
        self._primary       = options.get('primary',        False)
        self._autoIncrement = options.get('autoIncrement',  False)
        self._required      = options.get('required',       self._primary)
        self._unique        = options.get('unique',         False)
        self._indexed       = options.get('indexed',        False)
        self._maxlength     = options.get('maxlength',      256)
        self._encrypted     = options.get('encrypted',      False)
        self._validator     = None
        self._customData    = {}
        self._referenceRemovedAction = options.get('referenceRemovedAction',
                                                   RemovedAction.DoNothing)
        
        # encrypt passwords by default
        if ( not 'encrypted' in options and typ == ColumnType.Password ):
            self._encrypted = True
    
    def autoIncrement( self ):
        """
        Returns whether or not this column should 
        autoIncrement in the database.
        
        :return     <bool>
        """
        return self._autoIncrement
    
    def columnType( self ):
        """
        Returns the type of data that this column represents.
        
        :return     <orb.common.ColumnType>
        """
        return self._type
    
    def columnTypeText( self ):
        """
        Returns the column type text for this column.
        
        :return     <str>
        """
        return ColumnType[self.columnType()]
    
    def customData( self, key, default = None ):
        """
        Returns custom information that was assigned to this column for the \
        inputed key.  If no value was assigned to the given key, the inputed \
        default value will be returned.
        
        :param      key     | <str>
                    default | <variant>
            
        :return     <variant>
        """
        return self._customData.get(key, default)
    
    def default( self, resolve = False ):
        """
        Returns the default value for this column to return
        when generating new instances.
        
        :return     <variant>
        """
        default = self._default
        ctype   = self.columnType()
        
        if ( not resolve or default is not None ):
            return default
        
        elif ( ctype == ColumnType.Date ):
            return datetime.date.today()
            
        elif ( ctype == ColumnType.Time ):
            return datetime.datetime.now().time()
            
        elif ( ctype & (ColumnType.Datetime | ColumnType.UTC_Datetime) ):
            return datetime.datetime.now()
        
        elif ( ctype == ColumnType.Interval ):
            return datetime.timedelta()
        
        elif ( ctype & (ColumnType.Integer | ColumnType.Enum) ):
            return 0
        
        elif ( ctype == ColumnType.Double ):
            return 0.0
        
        elif ( ctype == ColumnType.Decimal ):
            return decimal.Decimal()
        
        elif ( ctype == ColumnType.Bool ):
            return False
        
        elif ( ctype != ColumnType.ForeignKey ):
            return ''
        
        else:
            return default
    
    def displayName( self, autoGenerate = True ):
        """
        Returns the display name for this column - if no name is \
        explicitly set, then the words for the column name will be \
        used.
        
        :param      autoGenerate | <bool>
        
        :return     <str>
        """
        if ( not autoGenerate or self._displayName ):
            return self._displayName
        
        return projex.text.capitalizeWords( self.name() )
    
    def fieldName( self ):
        """
        Returns the field name that this column will have inside
        the database.  The Column.TEMPLATE_FIELD variable will be
        used for this property by default.
                    
        :return     <str>
        """
        return self._fieldName
    
    def getterName( self ):
        """
        Returns the name for the getter method that will be 
        generated for this column.  The Column.TEMPLATE_GETTER 
        variable will be used for this property by default.
        
        :return     <str>
        """
        return self._getterName
    
    def indexed( self ):
        """
        Returns whether or not this column is indexed for quick
        lookup.
        
        :return     <bool>
        """
        return self._indexed
    
    def indexName( self ):
        """
        Returns the name to be used when generating an index
        for this column.
        
        :return     <str>
        """
        return self._indexName
    
    def isEncrypted( self ):
        """
        Returns whether or not the data in this column should be encrypted.
        
        :return     <bool>
        """
        return self._encrypted
    
    def isReference( self ):
        """
        Returns whether or not this column is a reference to another table.
        
        :return     <bool>
        """
        if ( self._reference ):
            return True
        return False
    
    def isReversed( self ):
        """
        Returns whether or not this column generates a reverse lookup method \
        for its reference model.
        
        :return     <bool>
        """
        return self._reversed   
    
    def isSearchable( self ):
        """
        Returns whether or not this column is a searchable column.  If it is,
        when the user utilizes the search function for a record set, this column
        will be used as a matchable entry.
        
        :return     <bool>
        """
        return self._searchable
    
    def maxlength( self ):
        """
        Returns the max length for this column.  This property
        is used for the varchar data type.
        
        :return     <int>
        """
        return self._maxlength
    
    def name( self ):
        """
        Returns the accessor name that will be used when 
        referencing this column around the app.
        
        :return     <str>
        """
        return self._name
    
    def primary( self ):
        """
        Returns if this column is one of the primary keys for the
        schema.
        
        :return     <bool>
        """
        return self._primary
    
    def reference( self ):
        """
        Returns the model that this column is related to when
        it is a foreign key.
                    
        :return     <str>
        """
        return self._reference
    
    def referenceRemovedAction( self ):
        """
        Determines how records for this column will act when the reference it
        points to is removed.
        
        :return     <ReferencedAction>
        """
        return self._referenceRemovedAction
    
    def referenceModel( self ):
        """
        Returns the model that this column references.
        
        :return     <Table> || None
        """
        if ( self.isReference() ):
            from orb import Orb
            return Orb.instance().model(self.reference())
        return None
    
    def required( self ):
        """
        Returns whether or not this column is required when
        creating records in the database.
        
        :return     <bool>
        """
        return self._required
    
    def reversedName( self ):
        """
        Returns the name that will be used when generating a reverse accessor \
        for its reference table.
        
        :return     <str>
        """
        return self._reversedName
    
    def setterName( self ):
        """
        Returns the setter name that will be used to generate the
        setter method on the table as it is generated.  The
        Column.TEMPLATE_SETTER property will be used by default.
        
        :return     <str>
        """
        return self._setterName
    
    def setAutoIncrement( self, state ):
        """
        Sets whether or not this column should auto increment.
        
        :param      state | <bool>
        """
        self._autoIncrement = state
    
    def setColumnType( self, columnType ):
        """
        Sets the column type that this column represents in the database.
        
        :param      columnType | <ColumnType>
        """
        self._type = columnType
    
    def setCustomData( self, key, value ):
        """
        Sets the custom data at the inputed key to the given value.
        
        :param      key     | <str>
                    value   | <variant>
        """
        self._customData[str(key)] = value
    
    def setDefault( self, default ):
        """
        Sets the default value for this column to the inputed value.
        
        :param      default | <str>
        """
        # convert the string default based on the column type
        if ( isinstance(default, basestring) and
             not self.columnType() in (ColumnType.String,
                                       ColumnType.Text,
                                       ColumnType.Email,
                                       ColumnType.Password,
                                       ColumnType.Url)):
            
            if ( self.columnType() == ColumnType.Bool ):
                default = default == 'True'
                
            elif ( self.columnType() in (ColumnType.Integer,
                                         ColumnType.Double)):
                try:
                    default = eval(default)
                except SyntaxError:
                    default = None
            else:
                default = None
        
        self._default = default
    
    def setDisplayName( self, displayName ):
        """
        Sets the display name for this column.
        
        :param      displayName | <str>
        """
        if ( displayName is not None ):
            self._displayName = displayName
    
    def setEncrypted( self, state ):
        """
        Sets whether or not this column is encrypted in the database.
        
        :param      state   | <bool>
        """
        self._encrypted = state
    
    def setFieldName( self, fieldName ):
        """
        Sets the field name for this column.
        
        :param      fieldName | <str>
        """
        if ( fieldName is not None ):
            self._fieldName = fieldName
    
    def setName( self, name ):
        """
        Sets the name of this column to the inputed name.
        
        :param      name    | <str>
        """
        self._name = name
    
    def setGetterName( self, getterName ):
        """
        Sets the getter name for this column.
        
        :param      getterName | <str>
        """
        if ( getterName is not None ):
            self._getterName = getterName
    
    def setIndexed( self, state ):
        """
        Sets whether or not this column will create a lookup index.
        
        :param      state   | <bool>
        """
        self._indexed = state
    
    def setIndexName( self, indexName ):
        """
        Sets the index name for this column.
        
        :param      indexName | <str>
        """
        if ( indexName is not None ):
            self._indexName = indexName
    
    def setMaxlength( self, length ):
        """
        Sets the maximum length for this column.  Used when defining string \
        column types.
        
        :param      length | <int>
        """
        self._maxlength = length
    
    def setPrimary( self, primary ):
        """
        Sets whether or not this column is one of the primary columns \
        for a table.
        
        :param      primary     | <bool>
        """
        self._primary = primary
    
    def setReference( self, reference ):
        """
        Sets the name of the table schema instance that this column refers \
        to from its schema.
        
        :param      reference       | <str>
        """
        self._reference = reference
    
    def setReferenceRemovedAction( self, referencedAction ):
        """
        Sets how records for this column will act when the reference it
        points to is removed.
        
        :param     referencedAction | <ReferencedAction>
        """
        self._referenceRemovedAction = referencedAction
    
    def setRequired( self, required ):
        """
        Sets whether or not this column is required in the databse.
        
        :param      required | <bool>
        """
        self._required = required
    
    def setReversed( self, state ):
        """
        Sets whether or not this column generates a reverse accessor for \
        lookups to its reference table.
        
        :param      state | <bool>
        """
        self._reversed = state
    
    def setReversedName( self, reversedName ):
        """
        Sets the reversing name for the method that will be generated for the \
        lookup to its reference table.
        
        :param      reversedName | <str>
        """
        if ( reversedName is not None ):
            self._reversedName = reversedName
    
    def setSearchable( self, state ):
        """
        Sets whether or not this column is used during record set searches.
        
        :param      state | <bool>
        """
        self._searchable = state
    
    def setSetterName( self, setterName ):
        """
        Sets the setter name for this column.
        
        :param      setterName | <str>
        """
        if ( setterName is not None ):
            self._setterName = setterName
    
    def setUnique( self, unique ):
        """
        Sets whether or not this column is unique in the database.
        
        :param      unique | <bool>
        """
        self._unique = unique
    
    def setValidatorText( self, validatorText ):
        """
        Sets the validation pattern for this column.
        
        :param      validatorText | <str>
        """
        self._validatorText = validatorText
        self._validator = None
    
    def setValidatorHelp( self, validatorHelp ):
        """
        Sets the validation help for this column.
        
        :param      validatorHelp | <str>
        """
        self._validatorHelp = validatorHelp
    
    def schema( self ):
        """
        Returns the table that this column is linked to in the database.
        
        :return     <TableSchema>
        """
        return self._schema
    
    def toXml( self, xparent ):
        """
        Saves the data about this column out to xml as a child node for the
        inputed parent.
        
        :param      xparent    | <xml.etree.ElementTree.Element>
        
        :return     <xml.etree.ElementTree.Element>
        """
        xcolumn = ElementTree.SubElement( xparent, 'column' )
        
        # save the properties
        xcolumn.set('type',             ColumnType[self.columnType()])
        xcolumn.set('name',             self.name())
        xcolumn.set('getter',           self.getterName())
        xcolumn.set('setter',           self.setterName())
        xcolumn.set('field',            self.fieldName())
        xcolumn.set('index',            self.indexName())
        xcolumn.set('indexed',          str(self.indexed()))
        xcolumn.set('default',          str(self.default()))
        xcolumn.set('primary',          str(self.primary()))
        xcolumn.set('autoIncrement',    str(self.autoIncrement()))
        xcolumn.set('unique',           str(self.unique()))
        xcolumn.set('required',         str(self.required()))
        xcolumn.set('encrypted',        str(self.isEncrypted()))
        xcolumn.set('searchable',       str(self.isSearchable()))
        
        if ( self.reference() ):
            xrelation = ElementTree.SubElement( xcolumn, 'relation' )
            xrelation.set('table',          self.reference())
            xrelation.set('reversed',       str(self.isReversed()))
            xrelation.set('reversedName',   self.reversedName())
            xrelation.set('removedAction',  str(self.referenceRemovedAction()))
            
        return xcolumn
        
    def unique( self ):
        """
        Returns whether or not this column should be unique in the
        database.
                    
        :return     <bool>
        """
        return self._unique
    
    def validate( self, value ):
        """
        Validates the inputed value against this columns rules.
        
        :param      value | <variant>
        
        :return     (<bool> success, <str> message)
        """
        # don't validate against the primary field
        if ( self.primary() ):
            return (True, '')
        
        # validate against expression information
        validator = self.validator()
        if ( validator and not validator.match(value) ):
            return (False, 
                    str(errors.ValidationError(self, value)))
        
        # validate against requirement parameters
        if ( self.required() and value in ('', None) ):
            return (False,
                    '%s is a required value.' % self.displayName())
        
        return (True, '')
    
    def validator( self ):
        """
        Returns the regular expression pattern validator for this column.
        
        :return     <SRE_Pattern> || None
        """
        if ( not self._validator and self._validatorText ):
            self._validator = re.compile(self._validatorText)
        return self._validator
    
    def validatorText( self ):
        """
        Returns the validation text that is used to generate the validator \
        for this column.
        
        :return     <str>
        """
        return self._validatorText
    
    def validatorHelp( self ):
        """
        Returns the help string associated with this columns validation \
        checker.
        
        :return     <str>
        """
        return self._validatorHelp
    
    def valueFromString( self, value, extra = None ):
        """
        Converts the inputed string text to a value that matches the type from
        this column type.
        
        :param      value | <str>
                    extra | <variant>
        """
        if ( self.columnType() == ColumnType.Date ):
            if ( extra == None ):
                extra = '%Y-%m-%d'
            
            time_struct = strptime(value, extra)
            return datetime.date(time_struct.tm_year,
                                 time_struct.tm_month,
                                 time_struct.tm_day)
        
        elif ( self.columnType() == ColumnType.Time ):
            if ( extra == None ):
                extra = '%h:%m:%s'
            
            time_struct = strptime(value, extra)
            return datetime.time(time_struct.tm_hour,
                                 time_struct.tm_min,
                                 time_struct.tm_sec)
        
        elif ( self.columnType() == ColumnType.Datetime ):
            if ( extra == None ):
                extra = '%Y-%m-%d %h:%m:s'
            
            time_struct = strptime(value, extra)
            return datetime.datetime(time_struct.tm_year,
                                     time_struct.tm_month,
                                     time_struct.tm_day,
                                     time_struct.tm_hour,
                                     time_struct.tm_minute,
                                     time_struct.tm_sec)
        
        elif ( self.columnType() == ColumnType.Bool ):
            return str(value).lower() == 'true'
        
        elif ( self.columnType() in (ColumnType.Integer, 
                                     ColumnType.Double,
                                     ColumnType.Decimal) ):
            try:
                value = eval(value)
            except ValueError:
                value = 0
            
            return value
        
        return str(value)
    
    def valueToString( self, value, extra = None ):
        """
        Converts the inputed string text to a value that matches the type from
        this column type.
        
        :param      value | <str>
                    extra | <variant>
        """
        if ( self.columnType() == ColumnType.Date ):
            if ( extra == None ):
                extra = '%Y-%m-%d'
            
            return value.strftime(extra)
            
        elif ( self.columnType() == ColumnType.Time ):
            if ( extra == None ):
                extra = '%h:%m:%s'
            
            return value.strftime(extra)
            
        elif ( self.columnType() == ColumnType.Datetime ):
            if ( extra == None ):
                extra = '%Y-%m-%d %h:%m:s'
            
            return value.strftime(extra)
        
        return str(value)
    
    @staticmethod
    def defaultDatabaseName( typ, name, reference = '' ):
        """
        Returns the default schema name based on the current column templates.
        
        :param      typ         |  <str>
                    name        |  <str>
                    reference   | <str> | table the column refers to
        
        :return     <str>
        """
        # make sure we have an actual name to process
        name = str(name).strip()
        if ( not name ):
            return ''
        
        # generate a reference field type
        if ( typ == 'fieldName' and reference ):
            if ( name.lower() == reference.lower() ):
                templ = Column.TEMPLATE_REFERENCE
            else:
                templ = Column.TEMPLATE_COMPLEX_REF
        
        # generate the default templates
        else:
            templ = Column.TEMPLATE_MAP.get(typ)
            
        if ( templ == None ):
            return ''
        
        return projex.text.render( templ, 
                                      {'name':  name, 
                                       'table': reference})
    
    @staticmethod
    def defaultPrimaryColumn( name ):
        """
        Creates a default primary column based on the inputed table schema.
        
        :return     <Column>
        """
        
        # generate the auto column
        fieldName   = Column.defaultDatabaseName( 'primaryKey', name)
        column      = Column( ColumnType.Integer, 'id' )
        column.setPrimary(True)
        column.setFieldName(fieldName)
        column.setAutoIncrement(True)
        column.setRequired(True)
        column.setUnique(True)
        
        return column
        
    @staticmethod
    def fromXml( xcolumn ):
        """
        Generates a new column from the inputed xml column data.
        
        :param      xcolumn | <xml.etree.Element>
        
        :return     <Column> || None
        """
        typ  = ColumnType.get( xcolumn.get('type') )
        name = xcolumn.get('name')
        if ( typ is None or not name ):
            return None
        
        # create the column
        column = Column(typ, name)
        
        column.setGetterName(       xcolumn.get('getter') )
        column.setSetterName(       xcolumn.get('setter') )
        column.setFieldName(        xcolumn.get('field') )
        column.setIndexName(        xcolumn.get('index') )
        column.setIndexed(          xcolumn.get('indexed') == 'True' )
        column.setDefault(          xcolumn.get('default', None) )
        column.setPrimary(          xcolumn.get('primary') == 'True' )
        column.setAutoIncrement(    xcolumn.get('autoIncrement') == 'True' )
        column.setUnique(           xcolumn.get('unique') == 'True' )
        column.setRequired(         xcolumn.get('required') == 'True' )
        column.setEncrypted(        xcolumn.get('encrypted') == 'True' )
        column.setSearchable(       xcolumn.get('searchable') == 'True' )
        
        # create relation information
        xrelation = xcolumn.find('relation')
        if ( xrelation is not None ):
            column.setReference(    xrelation.get('table', '') )
            column.setReversed(     xrelation.get('reversed') == 'True' )
            column.setReversedName( xrelation.get('reversedName') )
            
            action = int(xrelation.get('removedAction', 1))
            column.setReferenceRemovedAction( action )
        
        return column
        