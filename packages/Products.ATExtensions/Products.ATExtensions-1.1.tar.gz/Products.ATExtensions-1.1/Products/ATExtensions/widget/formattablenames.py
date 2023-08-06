from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget
from records import RecordsWidget
from formattablename import FormattableNameWidget

class FormattableNamesWidget(RecordsWidget, FormattableNameWidget):
    _properties = RecordsWidget._properties.copy()
    _properties.update({
        'macro_view' : "formattablename_view",
        'format' : '%T %F %M %P %L %S',
        'formatter' : {},
        'abbr' : {},
        'join_abbr' : '',
        'withURL' : False,
        'sep' : '',
        'lastsep' : '',
        'empty_marker' : '',
        })
    _format_properties = ['format', 'formatter', 'abbr', 'join_abbr',
                          'withURL', 'sep', 'lastsep', 'empty_marker']
    security = ClassSecurityInfo()


InitializeClass(FormattableNamesWidget)

registerWidget(FormattableNamesWidget,
               title='FormattableNames',
               description="Renders formattable names.",
               used_for=('Products.ATExtensions.fields.FormattableNamesField',)
               )
