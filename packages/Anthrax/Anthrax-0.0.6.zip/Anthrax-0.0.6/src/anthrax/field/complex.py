"""Definitions of fields that combine multiple values."""
from anthrax.field.base import Field, BoundField
from anthrax.widget import LongTextInput

class ListField(Field):
    """A field that is represented by a formatted list on the raw side and by
    a list on the python side.
    Options:
    * separators - list of strings that can be used to separate items. Defaults
      to ``['\\n\\r', '\\n', '\\r']``
    * default_separator - a separator that will be used when converting to raw
      defaults to ``'\\n'``
    * strip_items - whether to strip the whitespaces of items (default
      ``True``)
    * drop_blanks - whether to omit the blank (empty after stripping) items
    (default ``True``)
    * subfield - a field used to process all the items in the list (
      **required**)
    """

    separators = ['\n\r', '\n', '\r']
    default_separator = '\n'
    strip_items = True
    drop_blanks = True
    subfield = None

    widgets = [LongTextInput]

    def bind(self, container):
        bf = super(ListField, self).bind(container)
        bf.subfield = self.subfield.bind(container)
        return bf

    def to_python(self, value, bf):
        value = [value]
        for separator in self.separators:
            value = sum([item.split(separator) for item in value], [])
        if self.strip_items:
            value = [subvalue.strip() for subvalue in value]
        if self.drop_blanks:
            value = [subvalue for subvalue in value if subvalue]
        return [bf.subfield._raw2python(subvalue) for subvalue in value]
    
    def from_python(self, value, bf):
        value = [self.subfield._python2raw(subvalue) for subvalue in value]
        return self.default_separator.join(value)
