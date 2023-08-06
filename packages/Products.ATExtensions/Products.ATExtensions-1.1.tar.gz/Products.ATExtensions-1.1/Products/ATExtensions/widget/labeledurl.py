from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import StringWidget
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Registry import registerPropertyType

class LabeledUrlWidget(StringWidget):
    _properties = StringWidget._properties.copy()
    _properties.update({
        'macro_view' : "labeled_url_widget",
        'macro_edit' : "record_widget",
        'default_protocol' : 'http',
        })
    security = ClassSecurityInfo()
    
    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        """
        add the default protocol to the url field if there is none
        """
        value = form.get(field.getName(), empty_marker)
        if value is empty_marker:
            return empty_marker
        if emptyReturnsMarker and value in ('', {}):
            return empty_marker
        url = value.get('url', None)
        if url and '://' not in url:
            url = self.default_protocol + '://' + url
            value.url = url
        return value, {}

InitializeClass(LabeledUrlWidget)

registerWidget(LabeledUrlWidget,
               title='LabeledUrl',
               description="Renders a URL in an anchor tag "
               "using label as display text.",
               used_for=('Products.ATExtensions.fields.LabeledUrlField',)
               )
registerPropertyType('default_protocol', 'string', LabeledUrlWidget)
