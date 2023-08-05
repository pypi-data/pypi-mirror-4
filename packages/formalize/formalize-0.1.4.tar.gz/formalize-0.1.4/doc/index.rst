.. Formalize documentation master file, created by
   sphinx-quickstart on Wed Mar 17 16:06:40 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. testsetup:: *

        from formalize import *
        from pprint import pprint

Formalize documentation contents
================================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. toctree::
        :maxdepth: 3

        core
        types
        checks


.. include:: ../README.txt

 

Validators
-----------

Validators transformation and check data, resulting in either a validated
value, or a ``ValidationError`` containing one or more error messages.

A simple Validator object looks like this:

.. doctest::
        :options: -IGNORE_EXCEPTION_DETAIL

	>>> v = FormValidator()(
	... 	firstname=Unicode(),
	... 	surname=Unicode(required="Please enter your surname"),
	... 	age=Int(required=False)(greaterthan(18, "You must be at least 18 to proceed"))
	... )

This can be applied to any data held in a dictionary-like object:

.. doctest::
        :options: -IGNORE_EXCEPTION_DETAIL

        >>> input_data = {
        ...    'firstname': u'Fred',
        ...    'surname': u'Jones',
        ...    'age': u'21',
        ... }
        >>> result = v.process(input_data)
        >>> pprint(result)
        {'age': 21, 'firstname': u'Fred', 'surname': u'Jones'}

Notice that the age has been turned from a string into a python ``int``. You
can use validation functions to transform data from a string input into
whatever python object your application needs.

If errors are encountered a ``ValidationError`` is raised containing
contains details of the validation failures:

.. doctest::
        :options: -IGNORE_EXCEPTION_DETAIL

	>>> try:
	... 	v.process({'firstname': u'John', 'age': u'1'})
	... except ValidationError, e:
	... 	print e.errors
	...
	[('age', 'You must be at least 18 to proceed'), ('surname', 'Please enter your surname')]

You can also specify the name of the source field as the first argument to the
validator if it differs from the name you wish to use in the validator:

.. doctest::
        :options: -IGNORE_EXCEPTION_DETAIL

	>>> v = FormValidator()(
        ...   firstname = Unicode('First name'),
        ... )
        >>> v.process({'First name': 'George'})
        {'firstname': u'George'}

.. doctest::
        :hide:
        :options: -IGNORE_EXCEPTION_DETAIL,+ELLIPSIS

        >>> v.process({})
        Traceback (most recent call last):
          ...
        ValidationError: ValidationError([('firstname', u'Value empty or invalid')])



Validators can also be built up via dictionary-like assignment. This allows field
names to be used that cannot be represented as python identifiers:

.. doctest::
        :options: -IGNORE_EXCEPTION_DETAIL

	>>> v = FormValidator()
	>>> v['Number of apples'] = Int()
	>>> v['Number of oranges'] = Int()(
	... 	greaterthan(2, u"You must have at least two oranges")
	... )

.. doctest::
        :hide:
        :options: -IGNORE_EXCEPTION_DETAIL,+ELLIPSIS


        >>> v.process({'Number of apples': '4', 'Number of oranges': 1})
        Traceback (most recent call last):
          ...
        ValidationError: ValidationError([('Number of oranges', u'You must have at least two oranges')])

Empty values
-------------

Empty values can cause headaches if not handled correctly. Formalize assumes
all values are required unless you set ``required=False`` when creating a field
validator:

.. doctest::
        :options: -IGNORE_EXCEPTION_DETAIL

	>>> v = FormValidator()(
        ...     bananas=Int(),
        ...     pears=Int(required=False)
        ... )
	>>> v.process({}) 
	Traceback (most recent call last):
	 ...
	ValidationError: ValidationError([('bananas', u'Value empty or invalid')])

Optional and required fields
----------------------------

By default, all fields are treated as required. If you want a value to be
optional, you must say so:

.. doctest::
        :options: -IGNORE_EXCEPTION_DETAIL

	>>> v = FormValidator()(
        ...     bananas=Int(required=False)
        ... )
	>>> v.process({})
	{}

Note that optional fields, when left empty, are not put through the same
validation checks. So, a validator like this:

.. doctest::
        :options: -IGNORE_EXCEPTION_DETAIL

	>>> v = FormValidator()(
	... 	how_many = Int(required=False).add(greaterthan(4))
	... )

will pass validation if either ``how_many`` is left unspecified, or if it /is/
specified and an integer greater than 4:

.. doctest::
        :options: -IGNORE_EXCEPTION_DETAIL

	>>> v.process({})
	{}

	>>> v.process({'how_many': '8'})
	{'how_many': 8}

	>>> v.process({'how_many':'twenty-two'})
	Traceback (most recent call last):
	 ...
	ValidationError: ValidationError([('how_many', u'Value empty or invalid')])

	>>> v.process({'how_many':'3'})
	Traceback (most recent call last):
	 ...
	ValidationError: ValidationError([('how_many', u'Value empty or invalid')])


The ``required`` argument to a field validator can either be a boolean as shown above, or a 
non-empty string, in which case ``required=True`` will be assumed, and the
string you provide used as the error message if a value is not provided.

Some examples:

.. doctest::
        :options: -IGNORE_EXCEPTION_DETAIL

        >>> # Value not required
        >>> v = FormValidator()(name=Unicode(required=False))

        >>> # Value required, using the default error message
        >>> v = FormValidator()(name=Unicode(required=True))

        >>> # Value required, using a custom error message
        >>> v = FormValidator()(name=Unicode(required=u'Please tell us your name'))

Error messages
--------------

The error messages you choose for your application form an important part of
its user interface. Formalize provides some minimal default messages, which
you will almost certainly want to customize for real-world use.

Validators take a ``message`` argument in the constructor. Conventionally you
would use a string but there is no restriction on this: you can use any python
object you like.

Fields can fail to validate in two principle ways: if a required value is not
provided, or if the value provided is not valid. By default these two failure
cases are represented by the same error message, but it is easy to specify
different messages for the different cases:

.. doctest::

        >>> v = FormValidator()(
        ...     i = Int(
        ...             message=u"Expected an integer value",
        ...             required=u"You didn't provide a value"
        ...     )
        ... )
        >>>
        >>> # Case 1: required value not present
        >>> v.process({})
        Traceback (most recent call last):
         ...
        ValidationError: ValidationError([('i', u"You didn't provide a value")])
        >>>
        >>> # Value of wrong type
        >>> v.process({'i': 'one'})
        Traceback (most recent call last):
         ...
        ValidationError: ValidationError([('i', u'Expected an integer value')])

Or if you want the two cases to have the same message:

.. doctest::

        >>> v = FormValidator()(
        ...     i = Int(message=u"Expected an integer value", required=True)
        ... )

Multiple checks on a field will use the parent validator's message unless you
explicitly provide a message. For example:

.. doctest::

        >>> from formalize.checks import greaterthan, lessthan
        >>> i = Int(message=u'Please enter an integer between 1-10')(greaterthan(0), lessthan(11))
        >>> i.process(11)
        Traceback (most recent call last):
         ...
        ValidationError: ValidationError([(None, u'Please enter an integer between 1-10')])

Sub-validators can also have their own messages:

.. doctest::

        >>> from formalize.checks import greaterthan, lessthan
        >>> i = Int(message=u'Please enter an integer')(greaterthan(0, u'Too small!'), lessthan(11, u'Too big!'))
        >>> i.process(0)
        Traceback (most recent call last):
         ...
        ValidationError: ValidationError([(None, u'Too small!')])
        >>> i.process(11)
        Traceback (most recent call last):
         ...
        ValidationError: ValidationError([(None, u'Too big!')])

CompoundValidators – ie ``FormValidator``, ``DictValidator`` and
``ListValidator`` don't themselves have associated messages.


Default values
--------------

If a value is not provided for a field the ``default`` value can be used to
specify a default. The default value will be returned if no value for the field
is given and will not be tested against any further validation checks – default
values are implicitly valid.

Some examples:

.. doctest::
        :options: -IGNORE_EXCEPTION_DETAIL

        >>> v = FormValidator()(name=Unicode(default=u'Anonymous'))
        >>> v.process({})
        {'name': u'Anonymous'}

Note that setting ``default`` overrides any setting of ``required``. 

Custom types
------------

You may subclass ``formalize.types.CustomType`` to write custom validation types.
At a minimum you will need to supply a ``from_source`` method to convert the
data from the source input. The following example demonstrates most of the
functionality available:

.. testcode::

        from formalize.types import CustomType

        class Coordinates(CustomType):
                """
                Validate user input of coordinates in the form 'x,y,z...'
                """

                default_message = u"Enter coordinates separated by commas"

                def __init__(self, dimensions=2, *args, **kwargs):
                        super(Coordinates, self).__init__(*args, **kwargs)
                        self._dimensions = dimensions

                def from_source(self, source):
                        values = source.split(',')
                        if len(values) != self._dimensions:
                                raise ValidationError(None, self.message)
                        try:
                                return tuple(float(s.strip()) for s in values)
                        except ValueError:
                                raise ValidationError(None, self.message)

Here we see:

* A ``default_message`` that is used to specify the error message for this
  type if the caller does not create one. This will be used both for a
  missing/undefined value or an invalid input eg:

.. doctest::
        :options: -IGNORE_EXCEPTION_DETAIL
        
        >>> Coordinates().process(Undefined)
        Traceback (most recent call last):
        ...
        ValidationError: ValidationError([(None, u'Enter coordinates separated by commas')])

        >>> Coordinates().process('doobeedoobeedo')
        Traceback (most recent call last):
        ...
        ValidationError: ValidationError([(None, u'Enter coordinates separated by commas')])

* A custom argument to ``__init__``, allowing callers to specify the
  number of dimensions expected in the coordinates, as well as the
  standard arguments:

.. doctest::
        :options: -IGNORE_EXCEPTION_DETAIL
        
        >>> Coordinates(dimensions=3, default=(2,4,7)).process(Undefined)
        (2, 4, 7)

        >>> Coordinates(dimensions=3, default=(2,4,7)).process('0.5, 9, 2')
        (0.5, 9.0, 2.0)

        >>> Coordinates(dimensions=3, default=(2,4,7)).process('0.5, 9')
        Traceback (most recent call last):
        ...
        ValidationError: ValidationError([(None, u'Enter coordinates separated by commas')])

* And finally an implementation of ``from_source``, which will perform
  the conversion and any standard validation for this type. Note that
  ``from_source`` can exit in one of the following ways:

        1. Return the converted value, in this example this should always be a tuple of floats

        2. Return ``Undefined``. In this case, processing would proceed
                as if the user had not entered any data at all, and the
                settings of required/default values would be applied.

        3. Raise an instance of ``ValidationError`` if the value is
                invalid.
        

Calculated fields
-----------------

Sometimes you may want a value to be calculated from other fields. For this,
there is the ``Calculated`` field type. For example:

.. doctest::
        :options: -IGNORE_EXCEPTION_DETAIL

        >>> def calculate_total(coins, notes):
        ...     return notes * 100 + coins
        ...
        >>> v = FormValidator()(
        ...      value_of_coins = Int(message="Please provide the total value of coins in centimes"),
        ...      value_of_banknotes = Int(message="Please provide the total value of banknotes"),
        ...      total = Calculated(calculate_total, 'value_of_coins', 'value_of_banknotes')
        ... )
        >>> pprint(v.process({'value_of_coins': 40, 'value_of_banknotes': 3}))
        {'total': 340, 'value_of_banknotes': 3, 'value_of_coins': 40}



Conditional checks
------------------

Suppose you have a field that needs a different check depending on the value a
user's selected. 

The ``When`` validator can be used to acheive simple conditional checks.
``When`` takes the following form::

        When(<field>=<condition>)(<validators>)

``condition`` can be either a simple literal value, compared for equality:

.. doctest::

        >>> v = FormValidator()(
        ...     When(country='Belgium')(postcode = matches(r'\d{4}')),
        ...     country = Unicode(),
        ...     postcode = Unicode(),
        ... )

one of formalize's check functions:

.. doctest::

        >>> v = FormValidator()(
        ...     When(a=greaterthan(10))(b = Int()),
        ...     a = Int(),
        ... )


or a custom function:

.. doctest:: 

        >>> v = FormValidator()(
        ...     When(username=lambda s: s.startswith('admin'))(verification_code = Unicode()),
        ...     username = Unicode()
        ... )

The ``Using`` class allows ``When`` objects to check multiple fields. Be
careful with ``Using`` – you *must* use a check function that raises a
``ValidationError`` on failure, rather than a boolean function.

.. doctest:: 

        >>> v = FormValidator()(
        ...     When(
        ...             a=Using('a', 'b')(lambda a, b: assert_true(a + b > 20, None))
        ...     )(c = Int()),
        ...     a = Int(),
        ...     b = Int(),
        ... )

        >>> v.process({'a': 20, 'b': 1})
        Traceback (most recent call last):
         ...
        ValidationError: ValidationError([('c', u'Value empty or invalid')])
        >>> pprint(v.process({'a': 19, 'b': 1}))
        {'a': 19, 'b': 1}

Tests may also be supplied as positional arguments as tuples of ``(<fieldname>,  <condition>)``:

.. doctest::
  
        >>> v = FormValidator()(
        ...     When(
        ...         ('answer3', lambda v: v < 3),
        ...         ('answer4', Unicode()(is_in('wombat', 'boomerang'))),
        ...     )
        ... )

When multiple conditions are specified all conditions must pass for the
validators to be run.

To combine several checks, use the ``Case`` class. This combines multiple
mutually exclusive ``When`` objects and optionally an ``Otherwise``:

.. doctest::

        >>> v = FormValidator()(
        ...     Case(
        ...             When(country=equals('Belgium'))(postcode = matches(r'\d{4}')),
        ...             When(country=equals('UK'))(postcode = matches(r'\w+\d\s*\d\w\w')),
        ...             When(country=equals('US'))(
        ...                     postcode = matches(r'\d{5}'),
        ...                     state = Unicode(required='Please enter your 2 character state code')(matches(r'^\w\w$'))
        ...             ),
        ...             Otherwise()(postcode=minlen(4)),
        ...     ),
        ...     country = Unicode(),
        ...     postcode = Unicode(),
        ... )

        >>> pprint(v.process({'country': u'Belgium', 'postcode': u'1000'}))
        {'country': u'Belgium', 'postcode': u'1000'}
        >>> pprint(v.process({'country': 'US', 'postcode': '90210'}))
        Traceback (most recent call last):
         ...
        ValidationError: ValidationError([('state', u"Please enter your 2 character state code")])



Compound data structures
----------------------------

Sometimes forms might contain compound fields, like this::

        <fieldset>
                <legend>Person 1</legend>
                Name: <input name="people#0.name"/><br/>
                Email: <input name="people#0.email"/><br/>
        </fieldset>
        <fieldset>
                <legend>Person 2</legend>
                Name: <input name="people#1.name"/><br/>
                Email: <input name="people#1.email"/><br/>
        </fieldset>
        <fieldset>
                <legend>Person 3</legend>
                Name: <input name="people#2.name"/><br/>
                Email: <input name="people#2.email"/><br/>
        </fieldset>


We'd like to be able to turn this into a data structure like this::

        people = [
                {'email': '...', 'name': '...'},
                {'email': '...', 'name': '...'},
                {'email': '...', 'name': '...'},
        ]

Formalize will automatically do this:

.. doctest::


        >>> v = FormValidator()(
        ...     people = ListValidator(
        ...             DictValidator()(
        ...                     name = Unicode(),
        ...                     email = Unicode(),
        ...             )
        ...     )
        ... )
        >>> data = v.process({
        ...     'people#0.name': 'fred',
        ...     'people#0.email': 'fred@example.org',
        ...     'people#1.name': 'jim',
        ...     'people#1.email': 'jim@example.org',
        ...     'people#2.name': 'sheila',
        ...     'people#2.email': 'sheila@example.org',
        ... })
        >>> pprint(data['people'])
        [{'email': u'fred@example.org', 'name': u'fred'},
         {'email': u'jim@example.org', 'name': u'jim'},
         {'email': u'sheila@example.org', 'name': u'sheila'}]

By default, ``#`` is used to denote a list, and ``.`` a dictionary. You can
pass the ``list_separator`` and ``dict_separator`` arguments to change the
characters used for this.


Checking multiple fields together
----------------------------------

Sometimes you want to enforce checks over multiple fields.

Wrap your validator in ``Using(<field>, <field>)`` and it will be called with
the named fields' values as positional arguments:

.. doctest::

	>>> from formalize import Using
	>>> from formalize.checks import assert_true
	>>> def check_password(p1, p2, message=u"Passwords do not match"):
	... 	assert_true(p1 == p2, message)
	... 	return p1
	...
	>>> v = FormValidator()(
	... 	p1=Unicode(),
	... 	p2=Unicode()(Using('p1', 'p2')(check_password))
	... )
	>>> v.process({'p1': 'shoe', 'p2': 'gnu'})
	Traceback (most recent call last):
	 ...
	ValidationError: ValidationError([('p2', u'Passwords do not match')])

One common pattern is to check that one field in a group has been set. For
example a form requesting contact details where users may supply one or more of
phone, email or postal address.

Because subvalidation checks are skipped when non-required fields are left empty we can't attach a ``Using`` check to a normal field validation definition. For example the following will NOT validate as you might expect:

.. doctest::

	>>> def check_one_set(*args):
	... 	assert_true(any(args), 'Please supply contact details')
	... 	return args[0]
	...
        >>> v = FormValidator()(
        ...     phone=Unicode(default=None)(Using('phone', 'email', 'address')(check_one_set)),
	... 	email=Unicode(default=None),
	... 	address=Unicode(default=None),
        ... )
        
Why doesn't the ``check_one_set`` validator throw an error when phone is not
specified? Because the phone validator returns the default value of ``None``,
short-circuiting any further checks.

We can get around that by adding a separate check that is not bound to a
particular field:

.. doctest::

	>>> v = FormValidator()(
        ...     Using('phone', 'email', 'address')(check_one_set),
	... 	phone=Unicode(default=None),
	... 	email=Unicode(default=None),
	... 	address=Unicode(default=None),
	... )
	>>> v.process({})
	Traceback (most recent call last):
	 ...
	ValidationError: ValidationError([(None, u'Please supply contact details')])

Note however that the error now isn't associated with any fieldname. If you
want the ``ValidationError`` to be bound to a particular field name you will
need to add the check with an additional call to the FormValidator object:

.. doctest::

	>>> v = FormValidator()(
	... 	phone=Unicode(default=None),
	... 	email=Unicode(default=None),
	... 	address=Unicode(default=None),
	... )(
        ...     phone = PassThrough()(Using('phone', 'email', 'address')(check_one_set)),
        ... )
	>>> v.process({})
	Traceback (most recent call last):
	 ...
	ValidationError: ValidationError([('phone', u'Please supply contact details')])

