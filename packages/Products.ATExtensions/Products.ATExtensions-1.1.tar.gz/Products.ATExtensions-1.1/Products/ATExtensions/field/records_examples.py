from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerField

from Products.ATExtensions.Extensions.utils import getDisplayList

from records import RecordsField


class MultipleNamesField(RecordsField):
    """a list of stuctured names (first, last)"""
    _properties = RecordsField._properties.copy()
    _properties.update({
        'type' : 'multiple_names',
        'subfields' : ('first_name','last_name'),
        'subfield_labels':{'first_name':'First or given name(s)',
                           'last_name':'Last or family name(s)',
                           },
        })
    security = ClassSecurityInfo()

InitializeClass(MultipleNamesField)

class PhoneNumbersField(RecordsField):
    """a list of phone numbers (number, type)"""
    _properties = RecordsField._properties.copy()
    _properties.update({
        'type' : 'phone_numbers',
        'subfields' : ('type','number'),
        'subfield_vocabularies':{'type':'PhoneNumberTypes',},
        'innerJoin':': ',
        'outerJoin':'<br />',
        })
    security = ClassSecurityInfo()

    security.declarePublic("PhoneNumberTypes")
    def PhoneNumberTypes(self, instance=None):
        """phone number types"""
        if not instance:
            instance = self
        return getDisplayList(instance, 'phone_number_types')

InitializeClass(PhoneNumbersField)

registerField(MultipleNamesField,
              title="MultipleNames",
              description="Used for storing a list of structured names (first_name, last_name)",
              )

registerField(PhoneNumbersField,
              title="PhoneNumbers",
              description="Used for storing a list of phone numbers (type, number)",
              )

