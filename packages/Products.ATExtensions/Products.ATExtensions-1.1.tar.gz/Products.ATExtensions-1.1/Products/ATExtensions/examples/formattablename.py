##########################################################################
#                                                                        #
#           copyright (c) 2005 ITB, Humboldt-University Berlin           #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

""" demonstrates the use of the formattable name(s) field"""

from Products.Archetypes.public import *
from Products.ATExtensions.ateapi import *
from Products.ATExtensions.config import PROJECTNAME


schema = BaseSchema + Schema((
    FormattableNameField('name1'),
    FormattableNameField('name2',
                         subfields = ('title',
                                      'firstnames',
                                      'lastname',
                                      'homepage'),
                         widget = FormattableNameWidget(
    format="%f%l: %F %m. %L (%T)",
    join_abbr=".",
    withURL = True,
    ),
                         ),
    FormattableNamesField('friends',
                          widget = FormattableNamesWidget(format="%L %f%m"),
                          )
    ))

class FormattableNameDemo(BaseContent):
    """
    Demo from ATExtensions
    Illustrates useage of the formattable name(s) field
    """
    content_icon = "user.gif"
    schema = schema
    global_allow = 0

    _at_rename_after_creation = True

registerType(FormattableNameDemo, PROJECTNAME)
