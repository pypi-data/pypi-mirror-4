##########################################################################
#                                                                        #
#           copyright (c) 2004 ITB, Humboldt-University Berlin           #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

""" utilities for the ATExtensions product """

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import DisplayList

def getValues(self, prop_name):
    ptool = getToolByName(self, 'portal_properties', None)
    if ptool and hasattr(ptool, 'extensions_properties'):
        return ptool.extensions_properties.getProperty(prop_name, None)
    else:
        return None

def makeDisplayList(values=None,add_select=True):
    if values and type(values) not in [type([]), type(())]:
        values = (values,)
    if not values: values = []
    if add_select:
        results = [['', 'Select'],]
    else:
        results = []
    for x in values:
        results.append([x,x])
    values_tuple = tuple(results)
    return DisplayList(values_tuple)

def getDisplayList(self, prop_name=None,add_select=True):
    return makeDisplayList(getValues(self, prop_name),add_select)
