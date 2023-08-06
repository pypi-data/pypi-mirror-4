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
from Products.Archetypes.public import DateTimeField as BaseField
from Products.Archetypes.Registry import registerField, \
     registerPropertyType

from Products.ATExtensions.widget.datetime import DateTimeWidget

class DateTimeField(BaseField):
    """
    An improved DateTime Field. It allows to specify
    whether only dates or only times are interesting.
    """

    _properties = BaseField._properties.copy()
    _properties.update({
        'type' : 'datetime_ng',
        'widget' : DateTimeWidget,
        'with_time' : 1, # set to False if you want date only objects
        'with_date' : 1, # set to False if you want time only objects
        })
    security = ClassSecurityInfo()

InitializeClass(DateTimeField)

registerField(DateTimeField,
              title="DateTime Field",
              description="An improved DateTimeField, which also allows time or date only specifications.",
              )

registerPropertyType('with_time', 'boolean', DateTimeField)
registerPropertyType('with_date', 'boolean', DateTimeField)
