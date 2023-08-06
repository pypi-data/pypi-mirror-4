## Controller Python Script "customize_remotefield"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=
##
field_id = context.REQUEST.get('customize_field', None)

if field_id is not None:
    field = context.getField(field_id)
    field.customize(context)

# Always make sure to return the ControllerState object
return state
