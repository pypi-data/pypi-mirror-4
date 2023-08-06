class Widget():
    """Widgets symbolize a visual representation of data and data input
facilities. Unlike views, widgets are frontend-agnostic, they may however be
or not be supported by a given frontend"""

    def __init__(self, view):
        self.view = view
    
    def render(self, **kwargs):
        return self.view(field = self.field, widget = self, **kwargs)
