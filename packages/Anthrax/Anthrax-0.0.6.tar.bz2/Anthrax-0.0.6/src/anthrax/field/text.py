""""""
import unicodedata
import re
import abc

from anthrax.field.base import Field
from anthrax import widget as w
from gettext import gettext as _
from anthrax.exc import ValidationError

class TextField(Field):
    """Simple field that represents a string. Inherits
    regexp, min_len, and max_len arguents available."""

    widgets = [w.TextInput, w.LongTextInput]

    def to_python(self, value, bf):
        return super(TextField, self).to_python(value, bf)

    def from_python(self, value, bf):
        return super(TextField, self).from_python(value, bf)

class EmailField(TextField):
    """Like TextField, but checks input to be correct email."""

    regexp = r'[a-z0-9]+@([a-z0-9]+\.)*[a-z0-9]+'
    regexp_message = _('Valid E-mail address required')

class MirrorField(TextField):
    """A text-field which content somehow depends on another field.
    WARNING: Current implementation limits its use to a single container.
    """

    mirrored = None

    @abc.abstractproperty
    def force_mirror(self):
        """Whether the mirroring is mandatory or just a suggestion."""

    @abc.abstractmethod
    def mirror_filter(self, mirrored):
        """The method that will be called to perform the transformation."""

    def to_python(self, value, bf):
        value = super(MirrorField, self).to_python(value, bf)
        if value:
            if self.force_mirror:
                raise ValidationError('This file should be left blank!')
            else:
                return value
        else:
            value = self.mirror_filter(bf.bound_mirrored)
        return value

    def bind(self, container):
        if self.mirrored is None:
            raise TypeError('No field set to mirror!')
        if isinstance(self.mirrored, str):
            self.mirrored = container.__fields__[self.mirrored]
        bf = super(MirrorField, self).bind(container)
        bf.bound_mirrored = self.mirrored.bind(container)
        return bf

class SlugField(MirrorField):
    """A field that contains only lowercase letters, numbers and minus signs.
    The value can be entered manually or can reflect other field. The frontend
    can also provide dynamic suggestion for the value.TextField"""

    force_mirror = False

    def mirror_filter(self, mirrored):
        value = mirrored.value
        value = value.replace('ł', 'l')
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
        value = value.decode('ascii')
        return re.sub('\W+', '-', value.lower())
