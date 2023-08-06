# -*- coding: UTF-8 -*-

##################################################
#                                                #
#    Copyright (C), 2004, Thomas Förster         #
#    <t.foerster@biologie.hu-berlin.de>          #
#                                                #
#    Humboldt University of Berlin               #
#                                                #
##################################################

from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import CalendarWidget
from Products.Archetypes.Registry import registerWidget

class DateTimeWidget(CalendarWidget):
    _properties = CalendarWidget._properties.copy()
    _properties.update({
        'macro' : "datetime_widget",
        })

    security = ClassSecurityInfo()

InitializeClass(DateTimeWidget)

registerWidget(DateTimeWidget,
               title='DateTime',
               description="An improved DateTime Widget.",
               used_for=('Products.ATExtensions.fields.DateTimeField',)
               )
