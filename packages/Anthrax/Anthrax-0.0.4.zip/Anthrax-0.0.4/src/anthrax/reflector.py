import abc

# Field positions for reflection overrides:
TOP = 'TOP'
BOTTOM = 'BOTTOM'
AFTER = 'AFTER'
BEFORE = 'BEFORE'

class Reflector(metaclass=abc.ABCMeta):
    """Base class for all reflectors"""

    def __init__(self, source):
        self.source = source

    @abc.abstractmethod
    def get_fields(self, form):
        """Override this method to return ordered dict of fields."""
