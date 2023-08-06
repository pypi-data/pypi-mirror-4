subject = context.REQUEST.get('subject',None)
address = context.REQUEST.get('email_from_address', None)
body    = context.REQUEST.get('body',None)
fullname= context.REQUEST.get('full_name',None)

regtool=context.portal_registration

if not body:
    state.setError('body', 'You have to enter a message text!',
                    new_status='failure')
if not subject:
    state.setError('subject', 'A subject is required!',
                    new_status='failure')
if not address:
    state.setError('email_from_address', 'You have to enter an emailaddress!',
                    new_status='failure')
if address:
    if not regtool.isValidEmail(address):
       state.setError('email_from_address','The emailaddress you entered is not valid!',
                       new_status='failure')

if state.getErrors():
    state.set(portal_status_message='Please correct the errors.')
return state

