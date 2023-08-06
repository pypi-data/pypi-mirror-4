## Script (Python) "formatdemo"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# This is s special purpose script to illustrate
# the formatting capabilities of the formattable name(s)
#
# it can only be applied to 'Formattable Name Demo' objects
#
n1 = context.getName1()
n2 = context.getName2()
g = context.getFriends()
print n1
print n1("%f %L")
print n2
print n2("%f%l (%F %L)")
print n1+n2
print (n1+n2)(lastsep=' & ')
print g
print (n1+n2+g)(format="%L %f%m", lastsep=' & ')
return printed
