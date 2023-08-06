"""Generic comparison validators."""
from gettext import gettext as _

from anthrax.exc import FormValidationError

def equals(self, *values):
    """Checks if all the fields have exactly the same value."""
    first_value = values[0]
    for value in values[1:]:
        if value != first_value:
            raise FormValidationError(
                fields=[], message=_('Fields should be equal.')
            )

def difference(self, value1, value2, min=None, max=None):
    """Checks the absolute diffenece between values."""
    diff = abs(value1 - value2)
    if min is not None and diff < min:
        raise FormValidationError(
            fields=[], message=_('Difference must exceed {0}'.format(min))
        )
    if max is not None and diff > max:
        raise FormValidationError(
            fields=[], message=_('Difference cannot exceed {0}'.format(max))
        )


