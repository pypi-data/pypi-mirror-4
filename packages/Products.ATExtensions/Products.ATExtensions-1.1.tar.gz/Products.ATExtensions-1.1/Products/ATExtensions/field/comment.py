from Acquisition import aq_get
from zope.i18n import translate
from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.Field import StringField
from Products.Archetypes.Registry import registerField
from Products.Archetypes.Registry import registerPropertyType

from Products.ATExtensions.widget import CommentWidget

class CommentField(StringField):
    """specific field for URLs""" 
    _properties = StringField._properties.copy()
    _properties.update({
        'type' : 'comment',
        'comment' : ' ',
        'comment_type' : 'text/structured',
        'comment_msgid' : '',
        'comment_method' : None,
        'widget' : CommentWidget,
        })
    security = ClassSecurityInfo()

    def get(self, instance, **kwargs):
        domain = self.widget.i18n_domain
        request = aq_get(instance, 'REQUEST', None)
        if self.comment_method is not None:
            self.comment = getattr(instance, self.comment_method)()
        if request is not None:
            if self.comment_msgid:
                comment = translate(domain=domain, msgid=self.comment_msgid, default=self.comment, context=request)
            else:
                comment = translate(domain=domain, msgid=self.comment, default=self.comment, context=request)    
        else:
            comment = self.comment
        transforms = getToolByName(instance, 'portal_transforms', None)
        if transforms is None:
            return comment
        return transforms.convertTo('text/html',
                                    comment,
                                    context=instance,
                                    mimetype=self.comment_type).getData()

    def set(self, instance, value, **kwargs):
        pass

InitializeClass(CommentField)

registerField(CommentField,
              title="Comment",
              description="Used for inserting comments into the views",
              )
registerPropertyType('comment', 'string', CommentField)
registerPropertyType('comment_type', 'string', CommentField)
