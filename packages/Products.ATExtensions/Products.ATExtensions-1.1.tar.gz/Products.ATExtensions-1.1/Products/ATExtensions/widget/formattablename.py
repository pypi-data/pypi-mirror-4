from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget
from record import RecordWidget

class FormattableNameWidget(RecordWidget):
    _properties = RecordWidget._properties.copy()
    _properties.update({
        'macro_view' : "formattablename_view",
        'format' : '%T %F %M %P %L %S',
        'formatter' : {},
        'abbr' : {},
        'join_abbr' : '',
        'withURL' : False,
        })
    _format_properties = ['format', 'formatter', 'abbr',
                          'join_abbr', 'withURL']
    
    security = ClassSecurityInfo()

    security.declarePublic('getKwArgs')
    def getKwArgs(self):
        """mapping of all non-empty formatting properties"""
        result = {}
        for property in self._format_properties:
            value = getattr(self, property, None)
            if value:
                result[property] = value
        return result

InitializeClass(FormattableNameWidget)

registerWidget(FormattableNameWidget,
               title='FormattableName',
               description="Renders a formattable name.",
               used_for=('Products.ATExtensions.fields.FormattableNameField',)
               )
