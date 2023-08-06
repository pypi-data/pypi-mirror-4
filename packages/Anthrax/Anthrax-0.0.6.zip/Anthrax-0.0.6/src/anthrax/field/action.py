"""These fields represent actions that can be fired on the form. In www
frontends they are probably buttons."""
from gettext import gettext as _

from anthrax.field.base import Field
from anthrax.widget.action import Button#, Command

class Action(Field):
    """Generic action."""

class RejectAction(Action):
    """Frontends shouldn't require the form to be valid if this action is
    performed."""

class AcceptAction(Action):
    """Frontend can if it is possible ensure that the form is valid before
    performing the action."""

class HttpActionMixin():
    """Call a url via HTTP."""
    # url = ''
    # method = 'POST'
    widgets = [Button]
    def from_python(self, val, bf):
        return None
    def to_python(self, val, bf):
        return ''

class HttpSubmit(HttpActionMixin, AcceptAction):
    """Submit form via HTTP."""
    label = _('OK')

class HttpCancel(AcceptAction, HttpActionMixin):
    """Cancel a HTTP form."""
    label = _('Cancel')
