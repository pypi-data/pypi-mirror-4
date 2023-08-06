from App.class_init import InitializeClass
from Products.Archetypes.Registry import registerField
from Products.ATExtensions.Extensions.utils import getDisplayList
from Products.Archetypes.Field import StringField
from Products.ATExtensions.widget import SmartEmailWidget


class SmartEmailField(StringField):
    """ SmartEmailField with isEmail validator and the SmartEmailWidget """
    _properties = StringField._properties.copy()
    _properties.update({
        'type':'smartemail',
        'validators':('isEmail'),
        'widget':SmartEmailWidget,
        })

    def getRawValue(self,instance):
	    return self.get(instance)
    
InitializeClass(SmartEmailField)