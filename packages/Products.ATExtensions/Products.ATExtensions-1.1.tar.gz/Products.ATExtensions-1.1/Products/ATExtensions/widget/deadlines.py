from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget

## rr: this has gotten nowhere so far

class DeadlinesWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro' : "deadlines_widget",
        })
    security = ClassSecurityInfo()

InitializeClass(DeadlinesWidget)

registerWidget(DeadlinesWidget,
               title='Deadlines',
               description="Manage a list of deadlines.",
               ## rr: ?? used_for=('Products.ATExtensions.fields.UrlField',)
               )
