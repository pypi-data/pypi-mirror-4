from collections import namedtuple
from gettext import gettext as _

from anthrax.field.base import Field
from anthrax import widget as w
from anthrax.exc import ValidationError

_BaseChoice = namedtuple('_BaseChoice', ['system', 'display'])

class Choice(_BaseChoice):

    @classmethod
    def _make(cls, arg):
        if isinstance(arg, str):
            arg = (arg, arg)
        return super(Choice, cls)._make(arg)

class ChoiceField(Field):
    """An abstract field that features a list of options.
    choices - a list of pair (system, display). These tuples get named during
    initialization. You can also provide a list of strings if you want
    system to equal display.
    """

    choices = []
    widgets = [w.SingleSelect, w.TextInput]

    def __init__(self, *args, **kwargs):
        super(ChoiceField, self).__init__(*args, **kwargs)
        self._normalize_choices()

    def validate_raw(self, value, bf):
        if value not in self.get_system_choices():
            raise ValidationError(_('Invalid option'))
        super(ChoiceField, self).validate_raw(value, bf)

    def _normalize_choices(self):
        self.choices = [Choice._make(choice) for choice in self.choices]

    def to_python(self, value, bf):
        return super(ChoiceField, self).to_python(value, bf)

    def from_python(self, value, bf):
        return super(ChoiceField, self).from_python(value, bf)

    def get_system_choices(self):
        return (choice.system for choice in self.choices)

    def get_display_choices(self):
        return (choice.display for choice in self.choices)
