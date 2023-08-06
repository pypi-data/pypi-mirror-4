from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import StringWidget
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Registry import registerPropertyType

class UrlWidget(StringWidget):
    _properties = StringWidget._properties.copy()
    _properties.update({
        'macro' : "url_widget",
        'default_protocol' : 'http',
        })
    security = ClassSecurityInfo()
    
    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        """
        add the default protocol if there is none
        """
        value = form.get(field.getName(), empty_marker)
        if value is empty_marker:
            return empty_marker
        if emptyReturnsMarker and value == '':
            return empty_marker
        if value and '://' not in value:
            value = self.default_protocol + '://' + value
        return value, {}

InitializeClass(UrlWidget)

registerWidget(UrlWidget,
               title='Url',
               description="Renders a URL in an anchor tag.",
               used_for=('Products.ATExtensions.fields.UrlField',)
               )
registerPropertyType('default_protocol', 'string', UrlWidget)
