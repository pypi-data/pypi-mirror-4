from gettext import gettext as _
from anthrax.field.ordered import OrderedField

from anthrax import widget as w

class IntegerField(OrderedField):
    """Field that represents integer numbers"""
    regexp = r' *-?[\d ]+'
    regexp_message = _('Valid integer required')
    widgets = [w.Spinner, w.TextInput]

    def to_python(self, value, bf):
        return int(value)

    def from_python(self, value, bf):
        return str(value)
