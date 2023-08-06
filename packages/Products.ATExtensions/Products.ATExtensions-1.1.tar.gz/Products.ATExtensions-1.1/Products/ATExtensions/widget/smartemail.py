from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Widget import StringWidget
from Products.Archetypes.Registry import registerWidget
from Products.CMFCore.utils import getToolByName
from types import StringType, UnicodeType, StringTypes
from Products.Archetypes.utils import mapply
from zLOG import LOG , WARNING
STRING_TYPES = [StringType, UnicodeType]


class SmartEmailWidget(StringWidget):
    """You should use the SmartEmailWidget only with a SmartEmailField!
    
    The SmartEmailWidget is a StringWidget with the 'mask' property.
    This property holds a string with the name of a method, which will
    be looked up and used to modify the rendering of an email address for
    anonymous view.

    The default value for 'mask' is emailMask. This method is found at 
    ATExtensions/skins/at_extensions/emailMask.py.
    Use this as an example or customize it or define your own method
    to be registered via the widget's 'mask' property.
    """
    _properties = StringWidget._properties.copy()
    _properties.update({'macro_view':"smartemail_widget",
                        'mask':'emailMask'})

    security = ClassSecurityInfo()
    security.declarePublic('EmailMask')
    def EmailMask(self,instance,value=None):
        """ This method calls the masking method as defined in the
	    'emailMask' property of the SmartEmailWidget. If the 
	    method can not be found or is not callable it falls back to
	    using '(et)' as mask for '@'."""
	   
        try :
           val=self.mask
           if type(val) in STRING_TYPES:
                method = getattr(instance, val, None)
                if callable(method):
                    value = method(value)
        except :
           LOG('ATExtensions:', WARNING,
               'There are problems with the emailMask poperty. The script '
               'you state has to be available e.g. in the portal_skins folder.'
               ' It should accept one parameter (the string with the raw '
               'emailaddress) and return a string (the masked emailaddress). '
               'You fall back to standard behavior now.')
           value=value.replace('@','(et)') 
        return value
           
    security.declarePublic('linkToMailForm')      
    def linkToMailForm(self,field,instance):
	"""Constructs a link to the email formular"""
        uid=instance.UID()
        field_id=field
        url=instance.absolute_url()
        link='%s/mailout_form?uid=%s&fid=%s' % (url,uid,field_id)
        return link

InitializeClass(SmartEmailWidget)

registerWidget(SmartEmailWidget,
               title='SmartEmail',
               description="Renders a SmartEmailField.",
               used_for=('Products.ATExtensions.fields.SmartEmailField',)
               )
