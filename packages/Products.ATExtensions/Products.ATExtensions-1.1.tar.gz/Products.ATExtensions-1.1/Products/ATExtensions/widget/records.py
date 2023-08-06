from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import StringWidget
from Products.Archetypes.Registry import registerWidget

from Products.ATExtensions.widget import RecordWidget

class RecordsWidget(RecordWidget):
    _properties = RecordWidget._properties.copy()
    _properties.update({
        'macro' : "records_widget",
        })
    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        """
        Basic impl for form processing in a widget plus clearing
        of the value if the 'delete all entries' flag is set
        """
        ## check to see if the delete all entries flag was selected
        delete = form.get('%s_delete' % field.getName(), empty_marker)
        if delete is not empty_marker: return {}, {}
        
        value = form.get(field.getName(), empty_marker)
        if value is empty_marker:
            return empty_marker
        if emptyReturnsMarker and value == '':
            return empty_marker

        ## now check to see if we need to delete an individual item
        for idx in range(len(value)-1,-1,-1):
            flag_name = '%s_delete_%s' % (field.getName(),idx)
            delete = form.get(flag_name, None)
            if delete:
                del value[idx]
                del form[flag_name]
        return value, {}    

InitializeClass(RecordsWidget)

registerWidget(RecordsWidget,
               title='Records',
               description="Renders a list of records.",
               used_for=('Products.ATExtensions.fields.RecordsField',)
               )
