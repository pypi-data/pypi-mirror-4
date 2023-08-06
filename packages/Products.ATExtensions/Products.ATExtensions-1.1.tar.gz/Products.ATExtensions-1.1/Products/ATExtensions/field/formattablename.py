from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerField
from Products.Archetypes.Field import ObjectField
from Products.ATExtensions.datatype.formattablename \
     import FormattableName
from Products.ATExtensions.widget import FormattableNameWidget
from record import RecordField

class FormattableNameField(RecordField):
    """ field for managing a 'FormattableName' (custom type)"""
    _properties = RecordField._properties.copy()
    _properties.update({
        'type' : 'formattable_name',
        'default' : FormattableName(),
        'subfields' : ('title','firstname','middlename','lastname',),
        'widget' : FormattableNameWidget,
        })
    security = ClassSecurityInfo()
    
    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        value = self._decode_strings(value, instance, **kwargs)
        value = FormattableName(value)
        ObjectField.set(self, instance, value, **kwargs)

InitializeClass(FormattableNameField)

registerField(FormattableNameField,
              title="Formattable Name",
              description="Used for storing a formattable name",
              )
