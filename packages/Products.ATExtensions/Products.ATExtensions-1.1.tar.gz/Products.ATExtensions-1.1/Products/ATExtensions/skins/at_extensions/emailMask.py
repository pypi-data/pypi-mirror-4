## Script (Python) "emailMask"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters= emailaddress
##title=
##
# This is the script which is used to mask the emailaddresses
# in smartemailwidgets.
#

return emailaddress.replace('@',' at ')