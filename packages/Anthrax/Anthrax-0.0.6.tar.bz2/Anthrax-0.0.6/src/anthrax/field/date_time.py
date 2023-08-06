import datetime as dt

from anthrax.exc import ValidationError
from anthrax.field.ordered import OrderedField
from anthrax.widget.date_time import DatePicker
from anthrax.widget.simple import TextInput
from gettext import gettext as _

class DateField(OrderedField):
    date_format = '%d-%m-%Y'
    widgets = [DatePicker, TextInput]

    def to_python(self, value, bf):
        try:
            return dt.datetime.strptime(value, self.date_format).date()
        except ValueError:
            raise ValidationError(
                message = _('Misformed date.')
            )

    def from_python(self, value, bf):
        if value:
            return value.strftime(self.date_format)
        else:
            return value
