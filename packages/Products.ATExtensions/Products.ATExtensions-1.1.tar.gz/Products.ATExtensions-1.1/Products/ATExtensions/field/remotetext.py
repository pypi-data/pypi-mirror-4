import os, urllib
from DateTime.DateTime import DateTime
from Products.Archetypes.public import TextField, DisplayList
from Products.Archetypes.Registry import registerField
from Products.Archetypes.Registry import registerPropertyType
from Products.Archetypes.annotations import AT_ANN_STORAGE as KEY
from Products.Archetypes.annotations import getAnnotation

from Products.ATExtensions.widget.remotetext import RemoteTextWidget

def _pipe(command, input=''):
    # XXX TODO  what kind of pipe do we want?
    fi, fo, fe = os.popen3(command, 't')
    fi.write(input)
    fi.close()
    output = fo.read()
    fo.close()
    error = fe.read()
    fe.close()
    return output, error
    

class RemoteTextField(TextField):
    """Field to represent text coming from a remote source like
    another web site (url) or a subversion repository"""

    _properties = TextField._properties.copy()
    _properties.update({
        'type' : 'remote_text',
        'source_types' : ('svn', 'web'),
        'timeout' : 1, # should be one day
        'customized' : False,
        'widget' : RemoteTextWidget,
        })

    def getSourceTypeVocabulary(self):
        """All supported repository types """
        d = DisplayList()
        for t in self.source_types:
            d.add(t,t)
        return d

    # source handling
    def getSourcePath(self, instance):
        """the source path from the instance annotations or empty string"""
        ann = getAnnotation(instance)
        subkey = "%s-source-path" % self.getName()
        return ann.getSubkey(KEY, subkey, default='')

    def setSourcePath(self, instance, value):
        """Stores source path in the instance annotations"""
        ann = getAnnotation(instance)
        subkey = "%s-source-path" % self.getName()
        return ann.setSubkey(KEY, value, subkey)

    def getSourceType(self, instance):
        """the source path from the instance annotations or empty string"""
        ann = getAnnotation(instance)
        subkey = "%s-source-type" % self.getName()
        return ann.getSubkey(KEY, subkey, default='')

    def setSourceType(self, instance, value):
        """Stores source path in the instance annotations"""
        ann = getAnnotation(instance)
        subkey = "%s-source-type" % self.getName()
        return ann.setSubkey(KEY, value, subkey)

    def getTimeout(self, instance):
        """the timeout from the instance annotations or empty string"""
        ann = getAnnotation(instance)
        subkey = "%s-timeout" % self.getName()
        return ann.getSubkey(KEY, subkey, default=self.timeout)

    def setTimeout(self, instance, value):
        """Stores the timeout in the instance annotations"""
        ann = getAnnotation(instance)
        subkey = "%s-timeout" % self.getName()
        return ann.setSubkey(KEY, value, subkey)

    def getLastUpdate(self, instance):
        """time of the last update or None"""
        ann = getAnnotation(instance)
        subkey = "%s-last-update" % self.getName()
        return ann.getSubkey(KEY, subkey, default=None)

    def setLastUpdate(self, instance, value):
        """Stores the time of the last update in the instance annotations"""
        ann = getAnnotation(instance)
        subkey = "%s-last-update" % self.getName()
        return ann.setSubkey(KEY, value, subkey)

    def is_customized(self, instance):
        """Flag whether this field has been customized"""
        ann = getAnnotation(instance)
        subkey = "%s-customized" % self.getName()
        return ann.getSubkey(KEY, subkey, default=self.customized)

    def customize(self, instance):
        """Set the customize flag to True"""
        ann = getAnnotation(instance)
        subkey = "%s-customized" % self.getName()
        ann.setSubkey(KEY, True, subkey)
        return None
        
    def uncustomize(self, instance):
        """Set the customize flag to False"""
        ann = getAnnotation(instance)
        subkey = "%s-customized" % self.getName()
        ann.setSubkey(KEY, False, subkey)
        return None

    def get(self, instance, **kw):
        if self._isexpired(instance):
            self.set(instance)
        return TextField.get(self, instance, **kw)

    def _isexpired(self, instance):
        if self.is_customized(instance):
            return False
        last_update = self.getLastUpdate(instance)
        if last_update is None:
            return False  # not yet loaded -> not expired
        timeout = self.getTimeout(instance)
        now = DateTime()
        if (now - timeout) > last_update:
            return True
        return False

    def set(self, instance, value=None, **kw):
        source_text = None
        if value is None or not self.is_customized(instance):
            source_text = self.getSourceText(instance, **kw)
        if source_text:
            value = source_text
            now = DateTime()
            self.setLastUpdate(instance, now)
        TextField.set(self, instance, value, **kw)

    def getSourceText(self, instance, **kw):
        """main method to fetch the value from the remote site"""
        stype = self.getSourceType(instance)
        value = ''
        if stype == 'web':
            value = self.getTextFromUrl(instance)
        if stype == 'svn':
            value = self.getTextFromSvn(instance)
        return value or ''

    def getTextFromUrl(self, instance):
        source_path = self.getSourcePath(instance)
        try:
            # better use Tiran's 'urlupload'?
            value = urllib.urlopen(source_path).read()
        except:  # XXX FIXME what to catch here?
            value = ''

        return value

    def getTextFromSvn(self, instance):
        source_path = self.getSourcePath(instance)
        error = None
        command = "svn export %s" % source_path
        try:
            value, error = _pipe(command)
        except:  # XXX FIXME what to catch here? - or is pipe
            # robust enough never to blow up??
            value = ''

        if error:
            return ''
        return value

registerField(RemoteTextField,
              title="Remote Text Field",
              description="Populate a field from a remote source")

registerPropertyType('source_types', 'lines', RemoteTextField)
registerPropertyType('timeout', 'DateTime', RemoteTextField)
registerPropertyType('customized', 'boolean', RemoteTextField)

