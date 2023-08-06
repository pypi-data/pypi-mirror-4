import abc
import re
import types
import random
from string import ascii_lowercase
from gettext import gettext as _
from types import MethodType

from anthrax.exc import ValidationError

class MD(dict):
    """Mode dependent property."""
    pass


class BoundField():
    _regexp_compiled = None

    def __init__(self, field, parent):
        self._field = field
        self.parent = parent

    def __getattr__(self, key):
        value = getattr(self._field, key)
        if isinstance(value, MD):
            value = value.get(self.form.mode)
        return value

    def render(self, **kwargs):
        return self.widget.render(**kwargs)

    @property
    def form(self):
        from anthrax.container.form import Form
        node = self
        while not isinstance(node, Form):
            node = node.parent
        return node

    def __str__(self):
        return '<BoundField: {0}>'.format(self._field)

    @property
    def value(self):
        return self.parent.get(self.name, None)

    @property
    def raw_value(self):
        return self.parent.__raw__.get(self.name, '')

    @property
    def regexp_compiled(self):
        if self._regexp_compiled is None and self.regexp is not None:
            self._regexp_compiled = re.compile(self.regexp)
        return self._regexp_compiled

    def _raw2python(self, rvalue):
        return type(self._field)._raw2python(self, rvalue, self)

    def _python2raw(self, pvalue):
        return type(self._field)._python2raw(self, pvalue, self)

class FieldMeta(abc.ABCMeta):
    def __instancecheck__(cls, instance):
        if isinstance(instance, BoundField):
            instance = instance._field
        return super(FieldMeta, cls).__instancecheck__(instance)

class Field(object, metaclass=FieldMeta):
    """Abstract Field class. Fields encapsulate validation and
encoding/decoding logic. Non-abstract children of Field class should
override at least to_python() and from_python() methods. Constructor arguments:
        
label:
    The label to display before the field

regexp:
    The regular expression that raw values should match. Don't pass a compiled
    regexp here. The string will be compiled at creation.

regexp_message:
    An error message to display when the value doesn't match the regexp.
    It can contain a {regexp} placeholder.

min_len:
    Minimum length of raw value

min_len_message:
    An error message to display when the value is shorter than min_len. 
    Can contain a {min_len} placeholder.

max_len:
    Maximum length of raw value

max_len_message:
    An error message to display when the value is longer than max_len. 
    Can contain a {max_len} placeholder.

mode:
    If None this field will be displayed in all modes. Other value - this
    field will be restricted to a mode.

widgets:
    Widgets that can represent this field. Preferred ones should be put in
    front.
    """

    regexp = None
    regexp_message = _('Value should match regexp {regexp}')
    min_len = None
    min_len_message = _("Value can't be shorter than {min_len}")
    max_len = None
    max_len_message = _("Value can't be longer than {max_len}")
    mode = None
    label = ''
    is_upload = False

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        if 'id' not in kwargs:
            self.id = ''.join(
                (random.choice(ascii_lowercase) for i in range(16))
            )

    # def __get__(self, inst, cls):
    #     return BoundField(inst)

        
    widgets = abc.abstractproperty()
    
    @abc.abstractmethod
    def to_python(self, value, bf):
        """Transform the raw, string value into a python object possibly
        raising ValidationError. This method is meant to be overridden by
        child classes"""
        return value

    @abc.abstractmethod
    def from_python(self, value, bf):
        """Transform a python object into renderable string. This method is
        meant to be overridden by child classes."""
        return str(value)

    def validate_raw(self, value, bf):
        """Validate raw value. Don't return anything. Possibly raise
        ValidationError."""
        pass


    def validate_python(self, value, bf):
        """Validate python object. Don't return anything. Possibly raise
        ValidationError."""
        pass


    def _declarative_raw_validation(self, value, bf):
        """This method is called as a part of validation process on the raw
        value. You should override it if you add more declarative validation
        parameters (like regexp or min_len)."""
        len_ = len(value)
        if bf.regexp is not None:
            if not bf.regexp_compiled.match(value):
                raise ValidationError(
                    message = self.regexp_message.format(regexp=self.regexp)
                )
        if self.min_len is not None and len_ < self.min_len:
            raise ValidationError(
                message=self.min_len_message.format(min_len=self.min_len)
            )
        if self.max_len is not None and len_ > self.max_len:
            raise ValidationError(
                message=self.max_len_message.format(max_len=self.max_len)
            )

    def _declarative_python_validation(self, value, bf):
        """This method is called as a part of validation process on the python
        object. You should override it if you add more declarative validation
        parameters."""
        pass 

    def _raw2python(self, rvalue, bf=None):
        """This method shouldn't normally be overridden. It is called by Form
        object to process the raw value."""
        self._declarative_raw_validation(rvalue, bf)
        self.validate_raw(rvalue, bf)
        pvalue = self.to_python(rvalue, bf)
        self._declarative_python_validation(pvalue, bf)
        self.validate_python(pvalue, bf)
        return pvalue

    def _python2raw(self, pvalue, bf=None):
        """This method shouldn't normally be overridden. It is called by Form
        object to process the python object."""
        try:
            self.validate_python(pvalue, bf)
        except ValidationError as err:
            raise ValueError(
                'This value is invalid. Validator said: {0}'.format(
                    err.message
                )
            )
        return self.from_python(pvalue, bf)

    def bind(self, container):
        """Returns a BoundField for this field."""
        return BoundField(self, container)

Field.register(BoundField)
