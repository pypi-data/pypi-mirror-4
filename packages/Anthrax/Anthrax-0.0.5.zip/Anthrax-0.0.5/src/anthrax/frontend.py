import abc
from anthrax.util import load_entry_point

class Frontend(metaclass=abc.ABCMeta):
    """Frontend class"""

    def __init__(self, widget_dict, form_view):
        self.form_view = form_view
        self.widgets = {} 
        for k, v in widget_dict.items():
            try:
                self.widgets[
                    load_entry_point('anthrax.widget', k, 'widget')
                ] = v
            except ValueError:
                pass

    def negotiate_widget(self, field):
        for widget in field.widgets:
            if widget in self.widgets:
                return widget(view = self.widgets[widget])
        raise NotImplementedError(
            """Frontend {0} couldn't find a widget to use with field {1}.
Tried: {2}""".format(
                self, field, ', '.join(field.widgets)
            )
        )
