from_address = context.REQUEST.get('email_from_address')
from_name    = context.REQUEST.get('sender_fullname')
subject      = context.REQUEST.get('subject')
mailbody     = context.REQUEST.get('body')
uid          = context.REQUEST.get('uid')
fid          = context.REQUEST.get('fid')
enc	     = context.plone_utils.getSiteEncoding()
mhost        = context.MailHost
if from_name:
    from_address = '%s <%s>' % (from_name,from_address)



recipentObject  = context.uid_catalog(UID=uid)
recipentObject  = recipentObject[0]
recipentObject  = recipentObject.getObject()
recipentAddress = recipentObject.getField(fid).getRawValue(recipentObject)
objurl          = recipentObject.absolute_url()


msg="""
This email was send to you by using the mail form at %s.
--- 

%s
"""
Smsg=msg %(objurl,mailbody)


mhost.secureSend(message=Smsg,mto=recipentAddress,mfrom=from_address,subject=subject,charset=enc)

screenMsg = "Your email has been sent!"
state.setKwargs( {'portal_status_message':screenMsg})
link=recipentObject.absolute_url()+'?portal_status_message=%s' % screenMsg
context.REQUEST.RESPONSE.redirect(link)