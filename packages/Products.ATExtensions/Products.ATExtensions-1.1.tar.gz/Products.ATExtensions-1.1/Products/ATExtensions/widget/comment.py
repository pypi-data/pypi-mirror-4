from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import StringWidget
from Products.Archetypes.Registry import registerWidget

class CommentWidget(StringWidget):
    _properties = StringWidget._properties.copy()
    _properties.update({
        'macro' : "comment_widget",
        'i18n_domain': "plone",
        'visible' : {'edit' : 'visible',
                     'view' : 'invisible',
                     }
        })
    security = ClassSecurityInfo()
    
InitializeClass(CommentWidget)

registerWidget(CommentWidget,
               title='Comment',
               description="Renders a comment in 'base_edit'.",
               used_for=('Products.ATExtensions.fields.CommentField',)
               )
