##########################################################################
#                                                                        #
#           copyright (c) 2005 ITB, Humboldt-University Berlin           #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

from formattablename import FormattableName

class FormattableNames:
    def __init__(self,names=[]):
        self.names = ()
        for name in names:
            self.append(name)

    def __call__(self, *args, **kwargs):
        return self.strfmt(*args, **kwargs)

    def __getitem__(self,key):
        return self.names[key]

    def __len__(self):
        return len(self.names)

    def append(self,name):
        self.names += (FormattableName(name),)

    def __add__(self, other):
        if isinstance(other, FormattableNames):
            return FormattableNames(self.names + other.names)
        sum = FormattableNames(self.names)
        sum.append(other)
        return sum

    def __str__(self):
        return self()

    def __repr__(self):
        return str(self.names)

    def strfmt(self, *args, **kw):
        length = len(self)
        empty_marker = kw.get('empty_marker', "No names specified")
        sep = kw.get('sep', ', ')
        lastsep = kw.get('lastsep', ', and ')

        if length == 0:
            return empty_marker
        if length == 1:
            return self.names[0](**kw)
        if length == 2:
            if ',' in lastsep:
                lastsep = lastsep.replace(',','')
            return lastsep.join([a(**kw) for a in self.names])

        return sep.join([a(**kw) for a in self.names[:-1]]) \
               + lastsep + self.names[-1](**kw)


