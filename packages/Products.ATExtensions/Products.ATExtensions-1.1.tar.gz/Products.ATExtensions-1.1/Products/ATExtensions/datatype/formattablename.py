##########################################################################
#                                                                        #
#           copyright (c) 2005 ITB, Humboldt-University Berlin           #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

from string import punctuation
from Products.CMFCore.utils import getToolByName
filtered_punctuation = [c for c in punctuation \
                        if c not in "()[]{}<>"]

default_format="%T %F %M %P %L %S"

default_formatter = {'T':'title',
                     'F':'firstname',
                     'M':'middlename',
                     'P':'prefix',
                     'L':'lastname',
                     'S':'suffix',
                     'H':'homepage',
                     'E':'email',
                     }

default_abbreviations = {}


def abbreviate(value, abbr=None, join_abbr=''):
    """
    return an abbreviation for 'value'

    1. from the abbreviations mapping
    2. or the first letter (or letters if value is multivalued)
    3. return '' if value is empty
    """
    if not value:
        return ''
    abbreviations = abbr or default_abbreviations
    special =  abbreviations.get(value, None)
    if special is not None:
        return special
    values = [v[0] for v in value.split()]
    return join_abbr.join(values)


class FormattableName:

    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, mapping={}):
        """sets defaults and updates from kw"""
        self._keys = ()
        self.update(mapping)

    def __call__(self, *args, **kwargs):
        value = self.stringformat(*args, **kwargs)
        if kwargs.get('withURL', False):
            homepage = self.getHomePage(*args, **kwargs)
            if homepage:
                value = '<a href="%s">%s</a>' % (homepage, value)
        return value

    def getHomePage(self, context=None, methodname='', *args, **kwargs):
        if self.get('homepage'):
            return self.get('homepage')
        membertool = getToolByName(context, 'portal_membership', None)

        # look up homepage from user
        if self.get('username', False):
            try:
                return membertool.getHomeUrl(self.get('username', ''), 1)
            except ValueError:
                pass
        try:
            return getattr(context, methodname)(self)
        except AttributeError:
            return None

    def __str__(self):
        return self.stringformat()

    def __repr__(self):
        return str(dict(self.items()))

    def __add__(self, other):
        from formattablenames import FormattableNames
        if isinstance(other, FormattableName):
            return FormattableNames([self, other])
        if isinstance(other, FormattableNames):
            return FormattableNames([self]) + other

    def stringformat(self,
                     format=default_format,
                     formatter=default_formatter,
                     abbr=None,
                     join_abbr='',
                     abbrev=None,        # backwards compat
                     lastnamefirst=None, # backwards compat
                     **kw
                     ):
        """Takes a format string to control the rendering
        of the name (inspired by DateTime).

        Default format is '%T %F %M %P %L %S' where the
        keys mapped to by the default formatter are:

           %T -> title: for a leading title (e.g. academic)
           %F -> firstname: for the first first (or given) name
           %M -> middlename: for the middle name(s)
           %P -> prefix: for a last name prefix (e.g. a title of nobility)
           %L -> lastname: for the last name
           %S -> suffix: for a suffix (e.g. a trailing 'PhD' or 'SA')

        Use lowercase keys to get the abbreviated value
        (default: first letter; use the 'abbr' mapping
        to define exceptions; for multi-worded values the first letter
        of each word, joined by the value of 'join_abbr', is returned)

        Pass in a mapping to 'formatter' for custom format key mapping.

        Usage of 'abbrev' and 'lastnamefirst' is deprecated and for
        backwards compatibility only.

        See the test suite for example usages.
        """
        if lastnamefirst:
            format = "L, %F, %P"
        if abbrev: format = format.replace("%F", "%f")

        for key in formatter.keys():
            match = "%"+key
            value = self[formatter[key]]
            format = format.replace(match, value)
            if match.lower() in format:
                format = format.replace(match.lower(),
                                        abbreviate(value, abbr, join_abbr))

        return self._normalize(format)

    def _normalize(self, format):
        """Remove leading, stray, and trailing punctuation
        and collapse whitespece"""
        format = self._remove_punctuation(format.strip())
        for match in ['  ', '()', '[]', '{}', '<>']:
            while match in format:
                format = format.replace(match,' ')
        return format.strip()

    def _remove_punctuation(self, format):
        for c in filtered_punctuation:
            match = ' ' + c + ' '
            format = format.replace(match, ' ')
            while format.startswith(c):
                format = format[1:]
            while format.endswith(c):
                format = format[:-1]
        return format


    # behave like a dict

    def __getitem__(self, key, default=''):
        return getattr(self, key, default)

    def __setitem__(self, key, value):
        setattr(self, key, value)
        if key not in self._keys:
            self._keys += (key,)

    def get(self, key, default=''):
        return getattr(self, key, default) or default

    def update(self, kw=None):
        if not kw:
            return None
        for k,v in kw.items():
            self[k] = v

    def keys(self):
        return self._keys

    def items(self):
        return [(k, self[k]) for k in self._keys]

    # our one hard-coded exception

    def __setattr__(self, name, value):
        if value and name == 'firstnames':
            self['firstname'] = value.split()[0]
            self['middlename'] = ' '.join(value.split()[1:]).strip()
        else:
            self.__dict__[name] = value

    def __getattr__(self, name):
        if name == 'firstnames':
            value = ' '.join([self['firstname'], self['middlename']])
            return value.strip()
        else:
            raise AttributeError


