#!/usr/bin/python

""" 
ORB stands for Object Relation Builder and is a powerful yet simple to use \
database class generator.
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

# define version information (major,minor,maintanence)
__depends__ = ['projex']
__major__   = 0
__minor__   = 10

try:
    from __revision__ import __revision__
except:
    __revision__ = 0

__version_info__   = (__major__, __minor__, __revision__)
__version__        = '%s.%s' % (__major__, __minor__)

#------------------------------------------------------------------------------

import logging

from orb.common              import *            # pylint: disable-msg=W0401
from orb.settings            import *

from orb._orb                import Orb
from orb._orbgroup           import OrbGroup
from orb.connection          import Connection, DatabaseOptions, LookupOptions
from orb.database            import Database
from orb.tableschema         import TableSchema
from orb.column              import Column
from orb.query               import Query, QueryCompound, QueryPattern
from orb.join                import Join
from orb.index               import Index
from orb.table               import Table
from orb.tableenum           import TableEnum
from orb.environment         import Environment
from orb.recordset           import RecordSet
from orb.valuemapper         import ValueMapper
from orb.caching             import RecordCache
from orb.transaction         import Transaction

logger = logging.getLogger(__name__)