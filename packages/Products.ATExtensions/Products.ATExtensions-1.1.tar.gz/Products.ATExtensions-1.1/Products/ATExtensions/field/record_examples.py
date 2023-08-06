from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerField

from Products.ATExtensions.Extensions.utils import getDisplayList
from Products.ATExtensions.widget import LabeledUrlWidget

from record import RecordField

class AddressField(RecordField):
    """ dedicated address field"""
    _properties = RecordField._properties.copy()
    _properties.update({
        'type' : 'address',
        'subfields' : ('street1','street2','zip','city', 'country'),
        'required_subfields': ('city', 'country'),
        'subfield_labels':{'zip':'ZIP code'},
        'subfield_vocabularies' :{'country':'CountryNames'},
        'outerJoin':'<br />',
        })
    security = ClassSecurityInfo()
    
    security.declarePublic("CountryNames")
    def CountryNames(self, instance=None):
        if not instance:
            instance = self
        return getDisplayList(instance, 'country_names')

InitializeClass(AddressField)

class LocationField(RecordField):
    """ dedicated location (city, country) field"""
    _properties = RecordField._properties.copy()
    _properties.update({
        'type' : 'location',
        'subfields' : ('city', 'country'),
        'subfield_types' : {'country' : 'selection'},
        'subfield_vocabularies' :{'country':'CountryNames'},
        })
    security = ClassSecurityInfo()
    
    security.declarePublic("CountryNames")
    def CountryNames(self, instance=None):
        if not instance:
            instance = self
        return getDisplayList(instance, 'country_names')

InitializeClass(LocationField)

class ContactField(RecordField):
    """name, phone, fax, email, address field"""
    _properties = RecordField._properties.copy()
    _properties.update({
        'type' : 'contact',
        'subfields' : ('name','phone','fax','email', 'address'),
        'innerJoin' : '<br>',
        'subfield_types' : {'address': 'lines'},
        'subfield_maxlength' : {'email' : 256},
        'outerJoin':'<br />',
        })    
    security = ClassSecurityInfo()

InitializeClass(ContactField)

class SimpleNameField(RecordField):
    """just first and last name"""
    _properties = RecordField._properties.copy()
    _properties.update({
        'type' : 'simple_name',
        'subfields' : ('first_name','last_name'),
        'subfield_labels':{'first_name':'First or given name(s)',
                           'last_name':'Last or family name(s)',
                           },
        'outerJoin':' ',
        })    
    security = ClassSecurityInfo()

InitializeClass(SimpleNameField)    

class NetAddressField(RecordField):
    """ dedicated net address field"""
    _properties = RecordField._properties.copy()
    _properties.update({
        'type' : 'net_address',
        'subfields' : ('email','homepage'),
        'subfield_validators':{'homepage':'isURL'},
        'outerJoin':'<br />',
        })
    security = ClassSecurityInfo()

InitializeClass(NetAddressField)

class LabeledUrlField(RecordField):
    """field for holding a link to be displayed using a label"""
    _properties = RecordField._properties.copy()
    _properties.update({
        'type' : 'labeled_url',
        'subfields' : ('label','url'),
        'subfield_validators':{'url':'isURL'},
        'outerJoin':': ',
        'widget' : LabeledUrlWidget,
        })
    security = ClassSecurityInfo()

InitializeClass(LabeledUrlField)


registerField(SimpleNameField,
              title="SimpleName",
              description="Used for storing a structured (first, last) name",
              )

registerField(LocationField,
              title="Location",
              description="Used for storing a location (city, country)",
              )

registerField(AddressField,
              title="Address",
              description="Used for storing an address (street1, street2, zip, city, country)",
              )

registerField(ContactField,
              title="Contact",
              description="Used for storing contact information (name, phone, fax, email, address)",
              )

registerField(NetAddressField,
              title="NetAddress",
              description="Used for storing email and homepage",
              )

registerField(LabeledUrlField,
              title="labeledUrl",
              description="Used for storing a label and a URL",
              )
