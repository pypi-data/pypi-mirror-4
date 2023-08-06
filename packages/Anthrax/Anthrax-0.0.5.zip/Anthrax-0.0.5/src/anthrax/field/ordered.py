from gettext import gettext as _

from anthrax.field.base import Field
from anthrax.exc import ValidationError

class OrderedField(Field):
    """Base field for any well ordered data. The python representation should
support < and > operators. This field adds two declarative validators: min
and max. Arguments::

min:
    Minimal value.

min_message:
    Error message for values lower than min. Can contain {min} placeholder.

max:
    Maximal value.

max_message:
    Error message for values higher than max. Can contain {max} placeholder.
    """

    min = None
    max = None
    min_message = _("Value can't be lower than {min}.")
    max_message = _("Value can't be higher than {max}.")

    def _declarative_python_validation(self, value, bf):
        if self.min is not None and value < self.min:
            raise ValidationError(self.min_message.format(
                min=self._python2raw(self.min)
            ), suggestions=[self.min])
        if self.max is not None and value > self.max:
            raise ValidationError(self.max_message.format(
                max=self._python2raw(self.max)
            ), suggestions=[self.max])
        super(OrderedField, self)._declarative_python_validation(value, bf)
