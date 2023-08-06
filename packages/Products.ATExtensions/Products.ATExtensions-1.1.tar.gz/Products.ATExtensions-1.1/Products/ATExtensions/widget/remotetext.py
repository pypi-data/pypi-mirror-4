from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import RichWidget
from Products.Archetypes.Registry import registerWidget

class RemoteTextWidget(RichWidget):
    _properties = RichWidget._properties.copy()
    _properties.update({
        'macro' : 'remotetext_widget',
        })

    # what to handle now where?
    # customization; triggering upload
    # all in process_form?
    # or do we customize via an extra button with custom action?
    # wouldn't an empty value be sufficient for the non-customized case?
    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        """
        Basic impl for form processing in a widget plus setting
        additional values used by our associated field
        """
        value = form.get(field.getName(), empty_marker)
        if value is empty_marker:
            return empty_marker
        if emptyReturnsMarker and value == '':
            return empty_marker

        ## now check to see if we need to take care of some
        ## extra values
        stname = "%s_source_type" % field.getName()
        spname = "%s_source_path" % field.getName()
        stype = form.get(stname, None)
        spath = form.get(spname, None)
        if stype:
            field.setSourceType(instance, stype)
        if spath:
            field.setSourcePath(instance, spath)
        return value, {}    

InitializeClass(RemoteTextWidget)

registerWidget(RemoteTextWidget,
               title="Remote Text Widget",
               description="Populate a field from a remote source",
               used_for="Products.ATExtensions.field.remotetext.RemoteTextField",
               )
