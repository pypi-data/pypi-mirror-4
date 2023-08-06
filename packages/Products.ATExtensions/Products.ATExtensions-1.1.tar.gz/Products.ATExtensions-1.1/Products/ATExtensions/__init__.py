##########################################################################
#                                                                        #
#           copyright (c) 2004 ITB, Humboldt-University Berlin           #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

"""package installer"""

from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
from Products.Archetypes.public import process_types, listTypes
from config import *

# the custom validator
from Products.validation import validation
from validator.isPartialUrl import PartialUrlValidator
validation.register(PartialUrlValidator('isPartialUrl'))

# the demo content types
from examples import demo, formattablename

# backwards compatibility
import sys
import ateapi
sys.modules['Products.ATExtensions.at_extensions'] = ateapi

registerDirectory(SKINS_DIR, GLOBALS)

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)
    utils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)

