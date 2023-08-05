"""
Form processing/validation module.

See docs/index.rst for full documentation.
"""

__docformat__ = 'restructuredtext en'
__all__ = [
    'FormValidator', 'DictValidator', 'BaseValidator', 'ListValidator',
    'ValidationError', 'Undefined', 'Using', 'Group', 'Any', 'When', 'Case', 'Otherwise'
]

import copy
from itertools import chain

def partition(predicate, iterable):
    """
    Split ``iterable`` into two lists, the first all items for which
    ``predicate(item)`` evaluates ``True``, the second where it evaluates
    ``False``
    """
    result = {True: [], False: []}
    for item in iterable:
        result[predicate(item)].append(item)
    return result[True], result[False]


class Context(object):
    """
    Represents the data context as the validation progresses.

    The context passed to a validator should always represent the data context
    of the parent validator.

    The following code traces context values through the validation process::

        >>> from pprint import pprint
        >>> class ContextTracer(object):
        ...     def process_main(self, value, context):
        ...         print(self)
        ...         pprint(context.__dict__)
        ...         print('----')
        ...         return super(ContextTracer, self).process_main(value, context)
        ...

        >>> class trace_DictValidator(ContextTracer, DictValidator):
        ...     pass
        ...
        >>> class trace_Int(ContextTracer, DictValidator):
        ...     pass
        ...

        >>> v = trace_DictValidator()(
        ...     trace_Int('a'),
        ...     trace_Int('b'),
        ... )
        >>> result = v.process({'a':1, 'b': 1}) #doctest: +ELLIPSIS
        <formalize.core.trace_DictValidator object at ...>
        {'currentfield': None,
         'inputdata': {'a': 1, 'b': 1},
         'parent': None,
         'validator': <formalize.core.trace_DictValidator object at ...>,
         'workingdata': None}
        ----
        <formalize.core.trace_Int object at ...>
        {'currentfield': 'a',
         'inputdata': {'a': 1, 'b': 1},
         'parent': <formalize.core.Context object at ...>,
         'validator': <formalize.core.trace_DictValidator object at ...>,
         'workingdata': {}}
        ----
        <formalize.core.trace_Int object at ...>
        {'currentfield': 'b',
         'inputdata': {'a': 1, 'b': 1},
         'parent': <formalize.core.Context object at ...>,
         'validator': <formalize.core.trace_DictValidator object at ...>,
         'workingdata': {'a': {}}}
        ----

    """
    def __init__(self, validator, inputdata, parent=None):

        # The parent validator
        self.validator = validator

        # The parent context object
        self.parent = parent

        # The unprocessed data
        self.inputdata = inputdata

        # Current working data. Validators that operate on compound data types
        # (eg DictValidator, ListValidator) should use this to store
        # intermediate results in such a way that they are accessible by
        # subvalidators. 
        self.workingdata = None

        # Current fieldname being processed
        self.currentfield = None

    def push(self, validator, inputdata=None, currentfield=None, workingdata=None):
        """
        Create and return a new validation context with ``self`` as parent
        """
        if not validator.creates_context:
            return self

        inputdata = self.inputdata if inputdata is None else inputdata
        currentfield = self.currentfield if currentfield is None else currentfield
        context = Context(validator, inputdata, self)
        context.currentfield = currentfield
        context.workingdata = workingdata
        return context

    def closest(self, type_):
        """
        Return the closest validation context associated with the given
        validator type.
        """
        context = self
        while context.parent:
            if isinstance(context.validator, type_) and context.validator.creates_context:
                return context
            context = context.parent
        return None

class Undefined(object):
    """
    Undefined value
    """

    def __str__(self):
        return 'Undefined'

    def __repr__(self):
        return 'Undefined'

    def __nonzero__(self):
        return False

    def __deepcopy__(self, memo):
        """
        Prevent deepcopy calls from creating copies of this object as it must
        retain object identity.
        """
        return self


class ErrorList(list):
    """
    Represent a list of errors contained within a ValidationError.

    An error message can be any object, including a list, so it is necessary
    to have a unique subclass representing a list of errors that can be
    distinguished from a regular python list.
    """

Undefined = Undefined()

class BaseValidator(object):
    """
    Base validator class, from which other Validators are derived.

    To validate HTML form submissions you will want to use ``FormValidator``.
    To validate other data structures you will need to use ``DictValidator``,
    ``ListValidator``, and the other subtypes of ``BaseValidator`` that
    represent primitive types, or own subclasses of ``BaseValidator``.

    Validator objects take an input value [typically from a web form] and
    process it through multiple stages, resulting in either a processed, valid
    python object being returned, or a ``ValidationError`` being raised.

        1. ``process_prefilters`` applies any prefilters (see
           ``addprefilter``). These should do any necessary preprocessing of
           the raw input.

        2. ``process_main`` calls the ``from_source`` method to perform the
           type conversion.

        3. Additional subvalidation checks are performed (see ``add``). These
           operate on the python object, so can perform tasks such as checking
           values are within given numerical ranges etc.

    At any stage, a ``ValidationError`` may be raised. In this event no
    further processing of the value will be done.
    """

    # Reference to the parent validator, if any
    parent = None

    # Name of the source data field this validator is associated with, if
    # appropriate
    source = None

    # Some validators might need to operate over multiple values.
    # ``_using_keys`` holds the tuple of field names the validator expects as
    # additional arguments to ``process``. If _using_keys is set, ``process``
    # method *must* accept the positional arguments named in _using_keys.
    _using_keys = None

    # Error message for this instance, accessed via the ``message`` property
    _message = None

    # Error message for this instance when value is ``Undefined``, accessed via
    # the ``required_message`` property
    _required_message = None

    # Default error message used if instance has not been configured with a
    # specific message
    default_message = u"Value empty or invalid"

    # Set of filter functions to be run over raw data (before from_source is
    # called)
    prefilters = tuple()

    # Default value to be returned if the input value is Undefined
    _default = Undefined

    # Is raise an error if a value is required for this validator
    required = True

    # Validators that create a new data contexts should set this to ``True``.
    # Those that only act on the data available from their parents should
    # leave this at ``False``.
    creates_context = False

    def __init__(
        self,
        source=None,
        default=Undefined,
        message=None,
        required=True
    ):
        """
        source
            If the item is part of a DictValidator, this will be used as
            the source field for the data.

        default
            Default value to return if no value was specified

        message
            error message to raise if the given value is of the wrong type for the validator

        required
            if False, a value will not be required. Otherwise should be the
            error message associated to raise when the required value is
            not specified.
        """
        super(BaseValidator, self).__init__()
        self.source = source
        self._subvalidators = []
        self.message = message
        self._default = default if default is not Undefined else self._default
        if self._default is Undefined:
            self.required = bool(required)
            if required is True:
                self.required_message = self._message
            elif required is not False:
                self.required_message = required

    def process(self, value, context=None):
        """
        Main entry point for type conversion and validation.
        """
        if context is None:
            context = Context(self, value)

        try:
            value = self.process_prefilters(value, context)
            value = self.process_main(value, context)
            value = self.process_subvalidators(value, context)
        except ValidationError, e:
            raise ValidationError([
                (fieldname, msg if msg is not None else self.message)
                for fieldname, msg in e.errors
            ])

        if value is Undefined:
            if self._default is not Undefined:
                return self._default
            if self.required:
                raise ValidationError(None, self.required_message)

        return value

    def process_prefilters(self, value, context):
        """
        Handle the prefilter stage of processing
        """
        for func in self.prefilters:
            if value is Undefined:
                break
            value = func(value)
        return value

    def process_main(self, value, context):
        """
        Handle the main conversion and validation stage of processing
        """
        if value is Undefined:
            return Undefined
        return self.from_source(value)

    def process_subvalidators(self, value, context):
        """
        Handle the subvalidation stage of processing
        """
        if value is Undefined:
            return Undefined
        for validator in self._subvalidators:
            subcontext = context.push(self, value)
            value = validator.process(value, subcontext)
        return value

    def __call__(self, *args, **kwargs):
        """
        Add subvalidators specified via ``*args`` and ``**kwargs`` to this
        validator. Return the validator object so that call chaining is
        possible.
        """
        self.add(*args, **kwargs)
        return self

    def add(self, *validators):
        """
        Add subvalidators to this validator.
        """
        for v in validators:
            v = make_validator(v)
            v.register(self)
            self._subvalidators.append(v)
        return self

    def addprefilter(self, func):
        """
        Add a prefilter to this validator.
        """
        self.prefilters += (func,)
        return self

    def copy(self, **kwargs):
        """
        Return a copy of the validator. If keyword arguments are specified,
        they will be taken as fields to add to the copy::

            >>> from formalize import Unicode
            >>> v = DictValidator()(firstname=Unicode())
            >>> v2 = v.copy(surname=Unicode())
            >>>
            >>> v.process({'firstname': 'fred'})
            {'firstname': u'fred'}
            >>> v2.process({'firstname': 'fred'})
            Traceback (most recent call last):
                ...
            ValidationError: ValidationError([('surname', u'Value empty or invalid')])
        """
        new = copy.deepcopy(self)
        new.add(**kwargs)
        return new

    def from_source(self, ob):
        """
        Given source object ``ob`` (probably a string) return a python object
        of the destination type.
        """
        return ob

    def register(self, parent):
        """
        Register the validator as belonging to context ``parent``.
        """
        self.parent = parent

    def _get_message(self, use_default=True):
        """
        ``message`` property getter.

        Recursively calls parent validator's ``_get_message`` method.
        ``use_default`` flag is used to ensure that only the first call to
        ``self.message`` will return ``default_message`` if no instance-level
        message is found.
        """
        if self._message is not None:
            return self._message

        if self.parent is not None:
            result = self.parent._get_message(False)
            if result is not None:
                return result

        if use_default:
            return self.default_message

        return None

    def _set_message(self, value):
        """
        ``message`` property setter
        """
        self._message = value

    message = property(_get_message, _set_message)

    def _get_required_message(self, use_default=True):
        """
        ``required_message`` property getter

        Recursively calls parent validator's ``_get_message`` method.
        ``use_default`` flag is used to ensure that only the first call to
        ``self.required_message`` will return ``default_message`` if no
        instance-level message is found.
        """
        if self._required_message is not None:
            return self._required_message

        if self._message is not None:
            return self._message

        if self.parent is not None:
            result = self.parent._get_required_message(False)
            if result is not None:
                return result

        if use_default:
            return self.default_message

        return None

    def _set_required_message(self, value):
        """
        ``required_message`` property setter
        """
        self._required_message = value

    required_message = property(_get_required_message, _set_required_message)

class MappingValidator(BaseValidator):
    """
    Base validator for anything that handles dict-like mapping structures.
    """

    creates_context = False

    def add(self, *subvalidators, **kwargs):
        """
        Add the given positional/keyword arguments as field validators
        """
        for validator in subvalidators:
            self._subvalidators += [(validator.source, make_validator(validator))]

        for name, validator in kwargs.items():
            self.__setitem__(name, validator)
        return self

    def __setitem__(self, name, validator):
        """
        Validate the value associated with ``name`` in the input with the
        validator ``func``, which must return either the new value (can be
        unchanged), or raise a ``ValidationError``.
        """
        validator = make_validator(validator)
        self._subvalidators = [
            (k, v)
            for k, v in self._subvalidators
            if k != name
        ] + [(name, validator)]
        validator.register(self)

    def __getitem__(self, name):
        try:
            return dict(self._subvalidators)[name]
        except KeyError:
            return super(MappingValidator, self).__getitem__(name)

    def get_fieldname(self, subvalidator):
        """
        Return the fieldname associated with the given subvalidator object
        """
        try:
            return (k for k, v in self._subvalidators if v is subvalidator).next()
        except StopIteration:
            raise ValueError("%r is not a subvalidator of %r" % (subvalidator, self))

    def process_subvalidators(self, value, context):

        if value is Undefined:
            value = {}

        errors = []
        subcontext = context.push(self, value, workingdata={})

        # tuples are hashable and so can be compared for loop detection
        to_process = tuple(self._subvalidators[:])
        loop_catcher = set()

        while to_process:

            if to_process in loop_catcher:
                raise UsingKeyError(
                    to_process[-1][0],
                    "Circular dependency found in Using arguments"
                )
            loop_catcher.add(to_process)

            (name, validator), to_process = to_process[0], to_process[1:]
            source = name
            try:
                if validator.source is not None:
                    source = validator.source

                subcontext.currentfield = source
                if name in subcontext.workingdata:
                    v = subcontext.workingdata[name]
                else:
                    v = value.get(source, Undefined)
                subcontext.workingdata[name] = validator.process(v, subcontext)

            except ValidationError, e:
                subcontext.workingdata[name] = Undefined

                # Single error from a scalar source
                if len(e.errors) == 1 and e.errors[0][0] is None:
                    _, message = e.errors[0]
                    errors.append((name, message))

                # Errors from a compound source without fieldname (When validator)
                elif name is None:
                    errors.extend(e.errors)

                # Errors from a compound source with fieldname (any other
                # compound subvalidator)
                else:
                    errors.append((name, e.errors))

            except UsingKeyError, e:

                # We've not processed the requested field yet
                if e.args[0] in (name for name, validator in to_process):
                    to_process += ((name, validator),)

                else:
                    raise

        if errors:
            raise ValidationError([
                (field, self.message if message is None else message)
                for field, message in errors
            ])

        return dict((k, v) for k, v in subcontext.workingdata.items() if v is not Undefined)

class DictValidator(MappingValidator):
    """
    Validator for processing dictionary-like data structures
    """
    creates_context = True

    def __init__(self, source=None, default=Undefined, message=None, required=True):
        super(DictValidator, self).__init__(
            source, default=default, message=message, required=required
        )
        self._subvalidators = []


class FormValidator(DictValidator):
    """
    A specialism of Validator for processing HTTP forms. An ``Unpacker`` object
    will pre-process the data to arrange multi-valued lists into hierarchical
    data structures.
    """

    from formalize.unpack import default_unpacker
    unpacker = default_unpacker
    """
    The unpacker object to use. See ``formalize.unpack``
    """

    empty_values_undefined = False
    """
    HTML forms do not distinguish between no value entered and an empty string.
    If ``empty_values_undefined`` is ``True``, empty values are treated as
    undefined. Otherwise they are treated as empty strings.
    """

    def __init__(
        self,
        source=None,
        unpacker=unpacker,
        empty_values_undefined=empty_values_undefined
    ):
        super(FormValidator, self).__init__(source)
        self.unpacker = unpacker
        self.empty_values_undefined = empty_values_undefined

    def from_source(self, source):
        if self.empty_values_undefined:
            source = source.copy()
            for key in source:
                if source[key] == '':
                    source[key] = Undefined

        if not self.unpacker:
            return source

        return self.unpacker(source)

    def process(self, ob, context=None):
        """
        Return processed data from source ``ob``.

        If this is called as a subvalidator, ``context`` should contain
        the validation context.
        """
        try:
            return super(FormValidator, self).process(ob, context)
        except ValidationError, e:
            raise ValidationError(self.unpacker.repack_errors(e.errors))


class ListValidator(BaseValidator):
    """
    Applies a type conversion and validation to a list of values.

    Synopsis::

        >>> from formalize.core import FormValidator
        >>> from formalize.types import Int
        >>> v = FormValidator()(
        ...     a = ListValidator(Int())
        ... )
        >>> v.process({'a' : ['1', '2', '-39']})
        {'a': [1, 2, -39]}

    See ``formalize.core.list_transform`` for a way to transform
    multiple HTTP form-fields submissions into lists.
    """
    itemtype = None
    creates_context = True

    def __init__(self, itemtype, source=None):
        super(ListValidator, self).__init__(source)
        self.itemtype = itemtype

    def add(self, *subvalidators):
        self.itemtype.add(*subvalidators)
        return self

    def addprefilter(self, *prefilters):
        self.itemtype.addprefilter(*prefilters)
        return self

    def process(self, value, context=None):
        if value is Undefined:
            value = []
        if context is None:
            context = Context(self, value)
        value = super(ListValidator, self).process(value, context)
        result = []
        errors = []
        subcontext = context.push(self)
        for ix, item in enumerate(value):
            try:
                subcontext.currentfield = ix
                value = self.itemtype.process(item, subcontext)
                if value is Undefined:
                    value = None
                result.append(value)
            except ValidationError, e:
                if len(e.errors) == 1 and e.errors[0][0] is None:
                    errors.append((ix, e.errors[0][1]))
                else:
                    errors.append((ix, e.errors))
        if errors:
            raise ValidationError(errors)
        return result


class ValidationError(Exception):

    errors = None

    def __init__(self, *args):

        Exception.__init__(self, *args)
        if len(args) == 2:
            fieldname, message = args
            self.errors = ErrorList([(fieldname, message)])
        elif len(args) == 1:
            if isinstance(args[0], basestring):
                self.errors = ErrorList([(None, args[0])])
            else:
                self.errors = ErrorList(args[0])
        else:
            assert False, \
                "arguments not in format (fieldname, message) or [(fieldname, message), ...]"

    def __str__(self):
        return '%s(%r)' % (self.__class__.__name__, self.errors)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.errors)

def make_validator(ob):
    """
    Return a validator object created from ``ob``.

    If ``ob`` is already a subclass of ``BaseValidator`` then return it as is.
    otherwise return a ``ValidatorWrapper`` around the ``ob``.
    """
    if isinstance(ob, BaseValidator):
        return ob

    return ValidatorWrapper(ob)

class ValidatorWrapper(BaseValidator):
    """
    Wraps any callable inside a BaseValidator.

    >>> def my_validator(value, message=u'does nothing'):
    ...     return value
    >>> ValidatorWrapper(my_validator).process(True)
    True
    """

    def __init__(self, func, source=None):
        super(ValidatorWrapper, self).__init__(source)
        self.process_func = func

    def process_main(self, value, context):
        if value is Undefined:
            return value
        if isinstance(context.validator, Using):
            return self.process_func(*value)
        else:
            return self.process_func(value)

class Using(BaseValidator):
    """
    ``Using`` instances wrap other validators to cause them to be called
    with an arbitrary values pulled from the parent validator.

    Example::

        >>> from formalize import FormValidator, Unicode, Using
        >>> from formalize.checks import assert_true
        >>> def check_password(p1, p2, message=u"Passwords do not match"):
        ...     assert_true(p1 == p2, message)
        ...     return p1
        ...
        >>> v = FormValidator()(
        ...     p1=Unicode(),
        ...     p2=Unicode()(Using('p1', 'p2')(check_password))
        ... )
        >>> v.process({'p1': 'shoe', 'p2': 'gnu'})
        Traceback (most recent call last):
        ...
        ValidationError: ValidationError([('p2', u'Passwords do not match')])

    """

    creates_context = True

    def __init__(self, *source_fields):
        self.source_fields = source_fields
        super(Using, self).__init__()

    def process(self, value, context=None):
        if context is None:
            context = Context(self, value)
        c = context.closest(MappingValidator)
        assert c is not None, "Using requires a MappingValidator parent"

        try:
            value = tuple(
                value if name == context.currentfield else c.workingdata[name]
                for name in self.source_fields
            )
            if Undefined in value:
                return Undefined
        except KeyError, e:
            raise UsingKeyError(e.args[0])
        return super(Using, self).process(value, context)

class UsingKeyError(KeyError):
    """
    Raised by a subvalidator that has requires a specific key in
    context.workingdata that does not (yet) exist.

    Usually this is because that the named field has not been processed by the
    parent yet, and the key should be retried later.
    """

class Group(MappingValidator):
    """
    Group validators take a number of fields and group them together into a
    single value.

    The constructor takes the following parameters:

        * Source fields (as a tuple/list), eg ``(date_y, date_m, date_d)``

        * Individual keyword arguments to specify validators for the source
          fields, as per ``DictValidator``, eg ``date_y=Int(), date_m=Int(),
          date_d=Int()``

    The ``required`` and ``default`` parameters are ignored in this validator
    type, specify these on the source fields as desired.
    """

    creates_context = True

    def __init__(
        self,
        source_fields,
        message=None,
        default=Undefined,
        required=True,
        propagate_source_errors=False
    ):
        """
        message
            Error message to use

        propagate_source_errors
            If ``True``, propagate errors from source fields (default is
            is ``False``: replace individual errors found in source fields with a
            single error for the entire group).
        """
        super(Group, self).__init__(message=message, default=default, required=required)
        self.propagate_source_errors = propagate_source_errors
        self._subvalidators = []
        self._group_subvalidators = []
        for i in source_fields:
            self.__setitem__(i, BaseValidator())
        self.source_fields = source_fields

    def process_subvalidators(self, value, context):
        """
        Return processed input data from ``value`` or raise a
        ``ValidationError`` """

        if not isinstance(self.parent, MappingValidator):
            raise AssertionError("Group object must be a child of a MappingValidator")

        try:
            dict_result = super(Group, self).process_subvalidators(value, context)
        except ValidationError:
            if self.propagate_source_errors:
                raise
            else:
                raise ValidationError(None, self.message)

        value = tuple(dict_result[key] for key in self.source_fields)

        for validator in self._group_subvalidators:
            value = validator.process(value, context)

        return value

    def add(self, *args, **kwargs):
        """
        Add subvalidators, which act on the grouped value, and fieldvalidators
        which act on the source field values.

        All validator keyword arguments and positional arguments with a non-None ``source``
        attribute are treated as fieldvalidators. Positional arguments with
        ``source`` left as ``None`` are treated as subvalidators.
        """

        subvalidators, fieldvalidators = partition(
            lambda item: item.source is None,
            (make_validator(v) for v in args)
        )
        super(Group, self).add(*fieldvalidators, **kwargs)
        for v in subvalidators:
            v = make_validator(v)
            v.register(self)
            self._group_subvalidators.append(v)
        return self

    def register(self, parent):
        """
        Register the validator as belonging to content ``parent``, with
        fieldname ``fieldname``.
        """
        super(Group, self).register(parent)
        fieldname = parent.get_fieldname(self)

        def prefilter(data):
            data[fieldname] = dict(
                (item, data.get(item, Undefined)) for item in self.source_fields
            )
            return data
        parent.addprefilter(prefilter)

class Case(MappingValidator):
    """
    When objects work in the context of ``MappingValidator`` objects,
    conditionally applying validation rules.
    """

    def __init__(self, *cases):
        super(Case, self).__init__(required=False)
        for case in cases:
            assert isinstance(case, WhenBase), \
                    "Cases must be initialized with ``When`` or ``Otherwise`` instances only"

        self.cases = [case for case in cases if isinstance(case, When)]
        otherwises = [case for case in cases if isinstance(case, Otherwise)]

        assert len(otherwises) < 2, "Only one otherwise case permitted"
        if otherwises:
            self.otherwise = otherwises[0]
        else:
            self.otherwise = DictValidator()

    def process_subvalidators(self, value, context):

        def case_applies(tests):
            """
            Return True if all test functions/validators pass for the given
            case
            """
            for key, func in tests:
                if key not in context.workingdata:
                    raise UsingKeyError(key)
                if isinstance(func, BaseValidator):
                    try:
                        validator.process(context.workingdata[key], context.push(self))
                    except ValidationError:
                        return False

                elif not func(context.workingdata[key]):
                    return False
            return True

        context = context.closest(MappingValidator)

        for case in self.cases:
            if case.applies(context):
                return case.process_subvalidators(context.workingdata, context)

        return self.otherwise.process_subvalidators(context.workingdata, context)


        case_validator = DictValidator()
        self.cases.append((
            case_validator
        ))
        return case_validator

class WhenBase(MappingValidator):

    def __init__(self):
        super(WhenBase, self).__init__(required=False)

    def applies(self):
        raise NotImplentedError

    def process_subvalidators(self, value, context):
        context = context.closest(MappingValidator)

        if self.applies(context):
            context.workingdata.update(
                super(WhenBase, self).process_subvalidators(context.inputdata, context)
            )
        return Undefined


class When(WhenBase):
    """
    When instances can be used to apply validation rules conditionally and may
    also be passed to the ``Case`` constructor as part of a ``When(...) ...
    Otherwise(...)`` series.
    """
    def __init__(self, *tests, **kwtests):
        super(When, self).__init__()
        self.tests = [(key, func) for key, func in chain(tests, kwtests.items())]

    def applies(self, context):
        for key, test in self.tests:
            if key not in context.workingdata:
                raise UsingKeyError(key)
            try:
                if isinstance(test, BaseValidator):
                    test.process(context.workingdata[key], context.push(self))
                elif callable(test):
                    return test(context.workingdata[key])
                else:
                    return context.workingdata[key] == test
            except ValidationError:
                return False
        return True

class Otherwise(WhenBase):
    """
    Otherwise instances can be passed to the ``Case`` constructor as part of a
    ``When(...) ... Otherwise(...)`` series.
    """
    def applies(self, context):
        return True

class Any(BaseValidator):
    """
    Raise a ValidationError unless at least one of the subvalidators passes.

    Example::

        >>> from formalize.types import Int
        >>> from formalize.checks import lessthan, greaterthan
        >>> v = FormValidator()(
        ...     a=Int()(
        ...         Any(
        ...             lessthan(3),
        ...             greaterthan(7),
        ...             message=u"Must be less than 3 or greater than 7"
        ...         )
        ...     )
        ... )
        >>> v.process({'a': 2})
        {'a': 2}
        >>> v.process({'a': 8})
        {'a': 8}
        >>> v.process({'a': 5})
        Traceback (most recent call last):
            ...
        ValidationError: ValidationError([('a', u'Must be less than 3 or greater than 7')])
    """

    def __init__(self, *subvalidators, **kwargs):
        """
        Initialize ``Any`` with the given subvalidators. Keyword arguments are
        passed to the constructor of ``BaseValidator``
        """
        super(Any, self).__init__(**kwargs)
        assert len(subvalidators) >= 1
        self.add(*subvalidators)

    def register(self, parent):
        """
        Register the validator as belonging to content ``parent``, with
        fieldname ``fieldname``.
        """
        super(Any, self).register(parent)
        for validator in self._subvalidators:
            validator.register(self)

    def process(self, data, context):

        errors = []
        for item in self._subvalidators:
            try:
                return item.process(data, context.push(self, data))
            except ValidationError, e:
                errors.append(e)

        if self._message:
            raise ValidationError(None, self._message)
        else:
            raise errors[0]

class Not(BaseValidator):
    """
    Raise a ValidationError if the subvalidators all pass.

    Example::

        >>> from formalize.types import Int
        >>> from formalize.checks import lessthan, greaterthan
        >>> v = FormValidator()(
        ...     a=Int()(
        ...         Not(
        ...             greaterthan(7),
        ...             message=u"Must be less than 7"
        ...         )
        ...     )
        ... )
        >>> v.process({'a': 5})
        {'a': 5}
        >>> v.process({'a': 8})
        Traceback (most recent call last):
            ...
        ValidationError: ValidationError([('a', u'Must be less than 7')])
    """


    def __init__(self, subvalidator, **kwargs):
        super(Not, self).__init__(**kwargs)
        self._subvalidator = make_validator(subvalidator)
        self._subvalidator.register(self)

    def register(self, parent):
        """
        Register the validator as belonging to content ``parent``.
        """
        super(Not, self).register(parent)
        self._subvalidator.register(self)

    def process(self, data, context):
        try:
            self._subvalidator.process(data, context)
        except ValidationError, e:
            return data
        else:
            raise ValidationError(None, self.message)


