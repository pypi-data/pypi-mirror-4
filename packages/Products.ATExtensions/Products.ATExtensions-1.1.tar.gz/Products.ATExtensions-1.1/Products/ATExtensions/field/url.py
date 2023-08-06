from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Field import ObjectField
from Products.Archetypes.Registry import registerField

from Products.ATExtensions.widget import UrlWidget

class UrlField(ObjectField):
    """specific field for URLs""" 
    _properties = ObjectField._properties.copy()
    _properties.update({
        'type' : 'url',
        'validators' : ('isPartialUrl'),
        'widget' : UrlWidget,
        })
    security = ClassSecurityInfo()

InitializeClass(UrlField)

registerField(UrlField,
              title="Url",
              description="Used for storing a validated url",
              )
