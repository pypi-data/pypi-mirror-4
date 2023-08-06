from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerField
from Products.Archetypes.Field import ObjectField
from Products.ATExtensions.datatype.formattablenames \
     import FormattableNames
from Products.ATExtensions.widget import FormattableNamesWidget
from records import RecordsField

class FormattableNamesField(RecordsField):
    """ field for managing 'FormattableNames' (custom type)"""
    _properties = RecordsField._properties.copy()
    _properties.update({
        'type' : 'formattable_names',
        'default' : FormattableNames(),
        'subfields' : ('title','firstname','middlename','lastname',),
        'subfield_sizes' : {'title':10,
                            'firstname': 15,
                            'middlename':15,
                            'lastname':30},
        'widget' : FormattableNamesWidget,
        })
    security = ClassSecurityInfo()
    
    security.declarePrivate('get')
    def get(self, instance, **kwargs):
        value = RecordsField.get(self, instance, **kwargs)
        return FormattableNames(value)

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        value = self._decode_strings(value, instance, **kwargs)
        value = FormattableNames(value)
        ObjectField.set(self, instance, value, **kwargs)

InitializeClass(FormattableNamesField)

registerField(FormattableNamesField,
              title="Formattable Names",
              description="Used for storing formattable names",
              )
