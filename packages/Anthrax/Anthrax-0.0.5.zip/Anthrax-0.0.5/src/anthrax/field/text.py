""""""
from anthrax.field.base import Field
from anthrax import widget as w
from gettext import gettext as _

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
