from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.Registry import registerWidget


class ComboWidget(SelectionWidget):
    _properties = SelectionWidget._properties.copy()
    _properties.update({
        'type' : 'combobox',
        'macro' : "combo_widget",
        'specify' : False,
        'specifystring' : 'or specify:',
        'br' : True,
        'other' : 'Other',
        'addother' : True,
        })
    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        """
        if no value or value equals 'other'
        replace it with the optionally entered one
        """
        value = form.get(field.getName(), empty_marker)
        if value is empty_marker:
            return empty_marker
        if not value or value.lower() in ('other', u'other'):
            # XXX is this generic enough?
            other_name = "%s_other" % field.getName()
            value = form.get(other_name, empty_marker)
        if emptyReturnsMarker and value == '':
            return empty_marker
        return value, {}

InitializeClass(ComboWidget)

registerWidget(ComboWidget,
               title='ComboBox',
               description="Select box together with a string field.",
               used_for=('Products.Archetypes.Field.StringField',)
               )
