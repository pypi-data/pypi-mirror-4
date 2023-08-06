from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Field import StringField
from Products.Archetypes.Registry import registerField

from Products.ATExtensions.widget import EmailWidget

class EmailField(StringField):
    """specific field for emails""" 
    _properties = StringField._properties.copy()
    _properties.update({
        'type' : 'email',
        'validators' : ('isEmail'),
        'widget' : EmailWidget,
        })
    security = ClassSecurityInfo()

InitializeClass(EmailField)

registerField(EmailField,
              title="Email",
              description="Used for storing a validated email.",
              )
