class ValidationError(BaseException):
    def __init__(self, message, suggestions=None):
        self.message = message
        self.suggestions = suggestions

class FormValidationError(ValidationError):
    def __init__(self, fields, message):
        self.fields = fields
        super(FormValidationError, self).__init__(message, None)
