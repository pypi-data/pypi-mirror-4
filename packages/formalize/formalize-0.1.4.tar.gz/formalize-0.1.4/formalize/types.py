import decimal
from datetime import datetime

from formalize.core import BaseValidator, Undefined, UsingKeyError, ValidationError, DictValidator

__all__ = [
    'CustomType', 'PassThrough', 'Int', 'Float', 'Unicode', 'Bool', 'Decimal',
    'Calculated', 'DateTime', 'Date'
]


class CustomType(BaseValidator):
    u"""
    Subclass this for conversion fields to custom python objects.

    At the least you must override the ``from_source`` method.
    """

class PassThrough(BaseValidator):
    """
    Original object passed through without modification
    """
    def from_source(self, source):
        return source

class Int(BaseValidator):

    def from_source(self, strvalue):
        try:
            return int(strvalue)
        except (TypeError, ValueError):
            raise ValidationError(None, self.message)

class Float(BaseValidator):

    def from_source(self, strvalue):
        try:
            return float(strvalue)
        except (TypeError, ValueError):
            raise ValidationError(None, self.message)

class Decimal(BaseValidator):
    """
    Convert to a ``decimal.Decimal`` value.

    Note that to avoid a name conflict with ``decimal.Decimal`` in the stdlib,
    you may prefer to import this using::

        from formalize import Decimal as ValidatorDecimal
    """

    def from_source(self, strvalue):
        try:
            return decimal.Decimal(strvalue)
        except (TypeError, decimal.InvalidOperation):
            raise ValidationError(self.message)

class Unicode(BaseValidator):

    def __init__(self, *args, **kwargs):
        """
        Arguments:

            strip
                if specified, strip leading and trailing whitespace from the string.
        """
        strip = kwargs.pop('strip', False)
        super(Unicode, self).__init__(*args, **kwargs)
        if strip:
            def strip_filter(v):
                if v is not None:
                    return v.strip()
                return v
            self.addprefilter(strip_filter)

    def from_source(self, strvalue):
        return unicode(strvalue)

class Bool(BaseValidator):

    """
    Bool is a bit special: Undefined values are be treated as ``False``, by
    default. This to play nicely with HTML checkbox inputs::

        >>> from formalize.core import FormValidator
        >>> v = FormValidator()(
        ...     a = Bool()
        ... )
        >>> v.process({})
        {'a': False}

    You can also tell Bool which values to consider false; anything else will
    be considered true, and non-presence will be handled as in other types::

        >>> from formalize.core import FormValidator
        >>> v = FormValidator()(
        ...     a = Bool(falsevalues=['n', 'N'])
        ... )
        >>> v.process({'a': 'yes'})
        {'a': True}

        >>> v.process({})
        Traceback (most recent call last):
         ...
        ValidationError: ValidationError([('a', u'Value empty or invalid')])

    """

    def __init__(self, source=None, falsevalues=None, *args, **kwargs):
        self.falsevalues = falsevalues
        if not falsevalues:
            kwargs.setdefault('default', False)
        super(Bool, self).__init__(source, *args, **kwargs)

    def from_source(self, value):
        if self.falsevalues and value in self.falsevalues:
            return False
        return bool(value)

class Calculated(BaseValidator):

    def __init__(self, func, *source_fields, **kwargs):

        super(Calculated, self).__init__(**kwargs)

        self.func = func
        self.source_fields = source_fields

    def process_main(self, value, context):
        c = context.closest(DictValidator)
        assert c is not None, "Calculated requires a DictValidator parent"

        try:
            args = tuple(c.workingdata[field] for field in self.source_fields)
        except KeyError, e:
            raise UsingKeyError(e.args[0])
        if Undefined in args:
            return Undefined
        value = self.func(*args)
        return super(Calculated, self).process_main(value, context)

class DateTime(BaseValidator):
    """
    Validate and return a python ``datetime.datetime`` object
    """

    default_message = "not a date in a recognized format"

    def __init__(
        self,
        source=None,
        default=Undefined,
        message=None,
        required=True,
        format='%d/%m/%y %H:%M:%S',
    ):
        super(DateTime, self).__init__(source, default, message, required)
        self.format = format

    def from_source(self, source):
        try:
            return datetime.strptime(source.strip(), self.format)
        except ValueError:
            raise ValidationError(None, self.message)

class Date(DateTime):
    """
    Validate and return a python ``datetime.date`` object
    """

    default_message = "not a date in a recognized format"

    def __init__(
        self,
        source=None,
        default=Undefined,
        message=None,
        required=True,
        format='%d/%m/%y',
    ):
        super(Date, self).__init__(source, default, message, required, format)

    def from_source(self, source):
        return super(Date, self).from_source(source).date()


