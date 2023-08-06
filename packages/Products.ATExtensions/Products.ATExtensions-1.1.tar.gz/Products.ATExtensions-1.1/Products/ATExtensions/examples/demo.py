##########################################################################
#                                                                        #
#           copyright (c) 2004, 2005 ITB, Humboldt-University Berlin     #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

""" demonstrates the use of ATExtensions """

from Products.Archetypes.public import *
from Products.ATExtensions.ateapi import *
from Products.ATExtensions.config import PROJECTNAME


schema = BaseSchema + Schema((
    SimpleNameField('principal_investigator',
                    widget=RecordWidget(label='Principal Investigator',
                                        description='The person leading the group',
                                        ),
                    ),
    LabeledUrlField('home_institute',
                    required=0,
                    widget=LabeledUrlWidget(label='Institution',
                                            description='Name and Url of the institution hosting the group'),
                ),
    PhoneNumbersField('phone',
                      schemata="contact",
                      ),
    NetAddressField('e_address',
                    schemata="contact",
                    widget= RecordWidget(label='E-Contact',
                                         description='Electronic contact addresses'),
                    ),
    SmartEmailField('safe_email',
                    schemata="contact",
                    ),
    AddressField('street_address',
                 schemata="contact",
                 required=1,
                 widget=RecordWidget(label='Address',
                                     description='Street (or postal) contact address'),
                 ),
    # separate schemata page for members and partner groups;
    # the useage of minimalSize and maximalSize is for demonstration only
    MultipleNamesField('group_members',
                       schemata='members',
                       minimalSize = 1,  # effectively 2 because 'More' is enabled
                       maximalSize = 4,
                       widget=RecordsWidget(label="Group Members",
                                            description="Members of this group; press 'more' to enable additional entries (restricted to 4 at most)."),
                       ),
    # and a relation field for partner groups
    ReferenceField('partners',
                   schemata='members',
                   relationship="partner_groups",
                   multiValued=1,
                   allowed_types=("WorkingGroup",),
                   widget=ReferenceWidget(description="Groups with which this group has a collaborations",
                                          addable=1,
                                          destination="/",
                                          ),
                   ),
    # and here a record field configured in the schema declaration
    RecordsField('seminars',
                 schemata='seminars',
                 subfields = ('speaker', 'room', 'date'),
                 subfield_types = {'date':'datetime'},
                 subfield_sizes = {'speaker' : 15, 'room': 6},
                 innerJoin = ', ',
                 outerJoin = '<br />',
                 widget = RecordsWidget(
    helper_js=('jscalendar/calendar_stripped.js',
               'jscalendar/calendar-en.js'),
    helper_css=('jscalendar/calendar-system.css',),
            )

                ),
    TextField('short_description',
              widget=TextAreaWidget(label='Description',
                                    description="A short (plain text) description of the research group's focus.",
                                    ),
              accessor='getShortDescription',
              edit_accessor='getShortDescription',
              mutator='setShortDescription',
              ),
    StringField('test_combo',
                schemata='testing',
                vocabulary='DemoVocab',
                widget=ComboWidget(description="You need to select 'other' if you want to specify the value yourself below."),
                ),
    UrlField('url',
             schemata='testing',
             ),
    RemoteTextField('remote',
                    schemata='remote',
                    default_output_type='text/html',
                    allowable_content_types = ('text/plain',
                                               'text/html',
                                               'text/structured',
                                               ),
                    ),
    ))

class WorkingGroup(BaseContent):
    """
    Demo from ATExtensions
    stores information about a research group
    """
    content_icon = "group.gif"
    schema = schema
    _at_rename_after_creation = True

    # enable field sharing between 'short_description' and 'description'

    def getShortDescription(self, **kw):
        """ get the 'description' and put it in the 'short_description'
        """
        return self.Description()

    def setShortDescription(self, val, **kw):
        """ synchronize 'short_description' and 'description'
        """
        self.setDescription(val)

    # for the catalog metadata

    def Name(self):
        """
        the name of the group
        """
        return self.Title() + ', ' + self.getHome_institute()

    def LastName(self):
        """PI's last name; needed by the catalog for sorting"""
        return self.getPrincipal_investigator().get('last_name','')


    def PI(self):
        """
        the name of the principal investigator
        """
        pi_name = self.getPrincipal_investigator().get('first_name','') \
                  + ' ' + \
                  self.getPrincipal_investigator().get('last_name','')
        return pi_name.strip()

    def City(self):
        """ subfield of street address """
        return self.getStreet_address().get('city','')

    def Country(self):
        """ subfield of street address """
        return self.getStreet_address().get('country','')

    # the demo vocab

    def DemoVocab(self):
        """just to have some display list"""
        return getDisplayList(self, 'phone_number_types')


def modify_fti(fti):
    fti['allow_discussion'] = 1
    fti['global_allow'] = 0
    # hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in ('references',):
            a['visible'] = 0
    return fti

registerType(WorkingGroup, PROJECTNAME)
