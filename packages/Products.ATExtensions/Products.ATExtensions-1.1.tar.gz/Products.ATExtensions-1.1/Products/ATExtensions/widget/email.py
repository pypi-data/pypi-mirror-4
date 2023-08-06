from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import StringWidget
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Registry import registerPropertyType

class EmailWidget(StringWidget):
    _properties = StringWidget._properties.copy()
    _properties.update({
        'macro_view' : "email_widget",
        'at_mask' : '(at)',
        })
    security = ClassSecurityInfo()

InitializeClass(EmailWidget)

registerWidget(EmailWidget,
               title='Email',
               description="Renders an email address (masked for anonymous).",
               used_for=('Products.ATExtensions.fields.EmailField',)
               )
registerPropertyType('at_mask', 'string', EmailWidget)
