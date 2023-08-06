##########################################################################
#                                                                        #
#           copyright (c) 2004 ITB, Humboldt-University Berlin           #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

"""plone installer script"""

from StringIO import StringIO

from Products.CMFCore.utils import getToolByName
from Products.CMFFormController.FormAction import FormActionKey
from Products.CMFFormController.FormValidator import FormValidatorKey

from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils \
     import installTypes, install_subskin

from Products.ATExtensions.config import *


def setupProperties(self, out):
    ptool = getToolByName(self, 'portal_properties')
    psheet = getattr(ptool, 'extensions_properties', None)

    if not psheet:
        ptool.addPropertySheet('extensions_properties',
                               'Properties of the ATExtension product')

        ps = getattr(ptool, 'extensions_properties')
        ps._properties = ps._properties + (
            {'id':'phone_number_types', 'type':'lines', 'mode':'wd'},
            {'id':'country_names', 'type':'lines', 'mode':'wd'},
            )
        ps._updateProperty('phone_number_types', PHONE_NUMBER_TYPES)
        ps._updateProperty('country_names', COUNTRY_NAMES)
        out.write("Added %s's properties." % PROJECTNAME)
    else:
        out.write("Found %s's properties." % PROJECTNAME)

def configureFormController(self, out):
    pfc = getToolByName(self, 'portal_form_controller')
    pfc.addFormValidators('base_edit',
                          '',   # context_type
                          'more',
                          '')   # validators
    pfc.addFormAction('base_edit',
                      'success',
                      '',    # context_type
                      'more',
                      'traverse_to',
                      'string:more_edit')
    out.write("Added validator and action for the 'more' button to the form controller.")



def install(self):
    out = StringIO()
    if INSTALL_DEMO_TYPES:
        installTypes(self, out, listTypes(PROJECTNAME), PROJECTNAME)
    install_subskin(self, out, GLOBALS)
    setupProperties(self, out)
    configureFormController(self, out)
    out.write("Successfully installed %s." % PROJECTNAME)
    return out.getvalue()

# for the uninstall we need to take care of the form controller
# explicitly

def reconfigureFormController(self, out):
    pfc = getToolByName(self, 'portal_form_controller')

    #BAAH no Python API for deleting actions or validators in FormController
    #lets get our hands dirty
    container = pfc.actions
    try:
        container.delete(FormActionKey('base_edit', 'success', '',
                                       'more', pfc))
    except KeyError: pass

    container = pfc.validators
    try:
        container.delete(FormValidatorKey('base_edit', '',
                                          'more', pfc))
    except KeyError: pass

    out.write("Removed validator and action for the 'more' button from the form controller.")

def uninstall(self):
    out = StringIO()
    reconfigureFormController(self, out)
    # all the rest we leave to the quick installer
    out.write("Uninstalled %s." % PROJECTNAME)
    return out.getvalue()
