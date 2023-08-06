#!/usr/bin/python

""" Looks up resources in the orb system. """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2012, Projex Software'
__license__         = 'LGPL'

# maintenance information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

import os.path

CURR_PATH = os.path.dirname(__file__)

def find( relpath ):
    """
    Returns a relative path from this file.
    
    :return     <str>
    """
    return os.path.join(CURR_PATH, relpath)