from django.core.exceptions import ValidationError
from os.path import splitext


class FileTypeValidator(object):
    def __init__(self, file_extensions):
        if isinstance(file_extensions, basestring):
            file_extensions = [file_extensions]
        self.file_extensions = [file_extension.lower() for file_extension in file_extensions]

    def __call__(self, value):
        file_extension = splitext(value.name)[-1][1:].lower()
        if file_extension not in self.file_extensions:
            raise ValidationError(u'File type %s not allowed.' % file_extension, code='invalid')


class NumericRangeValidator(object):
    def __init__(self, min_value, max_value):
        assert(min_value <= max_value)
        self.min_value = min_value
        self.max_value = max_value

    def __call__(self, value):
        if value < self.min_value or value > self.max_value:
            raise ValidationError(u'Value is out of range [%s - %s].' % (self.min_value, self.max_value))
