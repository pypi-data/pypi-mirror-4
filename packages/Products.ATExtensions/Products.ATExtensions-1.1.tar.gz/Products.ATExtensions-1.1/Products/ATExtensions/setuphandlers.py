# an 'import_various' step to deal with form controller settings
# as there seems to be no support for doing this via GS at the moment
# (March 12, 2007)

def importVarious(context):
    """ Import various settings for ATExtensions

    This provisional handler will be removed again as soon as
    full handlers are implemented for this step.
    """
    site = context.getSite()
    pfc = site.portal_form_controller
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
    pfc.addFormValidators('atct_edit',
                          '',   # context_type
                          'more',
                          '')   # validators
    pfc.addFormAction('atct_edit',
                      'success',
                      '',    # context_type
                      'more',
                      'traverse_to',
                      'string:more_edit')
    return "Added validator and action for the 'more' button to " \
           "the form controller."
