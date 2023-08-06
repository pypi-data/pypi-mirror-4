import cgi
import mimetypes
import os

from gettext import gettext as _
from anthrax.field.base import Field
from anthrax.widget import FileUpload, TextInput
from anthrax.exc import ValidationError

BINARY_MIMETYPES = {'image'}

class AnthraxFileWrapper(object):
    """A common interface for differently stored files."""
    def __init__(self, arg, field):
        if isinstance(arg, cgi.FieldStorage):
            self.file = arg.file
            self.mimetype = arg.type
            self.field_storage = arg
            self.filename = arg.filename
        elif isinstance(arg, str):
            if field.directory is None:
                raise ValidationError("This field doesn't support filenames")
            if os.path.isabs(arg):
                raise ValidationError("Absolute paths aren't allowed")
            self.filename = arg
            full_path = os.path.join(field.directory, arg)
            self.mimetype, encoding = mimetypes.guess_type(arg)
            binary = self.mimetype.split('/')[0] in BINARY_MIMETYPES
            self.file = open(full_path, 'rb' if binary else 'r')
        else:
            raise TypeError("Can't instantiate wrapper with {}!".format(
                type(arg)))
            

class FileField(Field):
    """Field that represents a file (uploaded or server side).
    * accept_mime - A mimetype or an iterable of them that are available for
    this field. Asterisks can be used.
    * directory - A directory on the disk that is available for server-side
    files.
    """
    accept_mime = {'*/*'}
    widgets = [FileUpload, TextInput]
    directory = None
    is_upload = True

    def __init__(self, *args, **kwargs):
        super(FileField, self).__init__(*args, **kwargs)
        if isinstance(self.accept_mime, str):
            self.accept_mime = {self.accept_mime}
        if not isinstance(self.accept_mime, set):
            self.accept_mime = set(self.accept_mime)

    def to_python(self, value, bf):
        return AnthraxFileWrapper(value, self)

    def from_python(self, value, bf):
        return None

    def _declarative_raw_validation(self, value, bf):
        pass

    def _declarative_python_validation(self, value, bf):
        super(FileField, self)._declarative_python_validation(value, bf)
        maintype, subtype = value.mimetype.split('/')
        possible_mimetypes = {
            value.mimetype, maintype + '/*', '*/' + subtype, '*/*'
        }
        if not possible_mimetypes & self.accept_mime:
            raise ValidationError(_('Invalid mime'))
