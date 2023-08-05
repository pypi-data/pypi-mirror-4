Formalize: form processing and validation
=========================================

Formalize is designed to process and validate web form data cleanly and easily.

A FormValidator object looks like this::

	>>> v = FormValidator(
	... 	firstname=Unicode(),
	... 	surname=Unicode(required="Please enter your surname"),
	... 	age=Int(greaterthan(18, "You must be at least 18 to proceed"), required=False),
	... )

And can be applied to any data held in a dictionary-like object::

        >>> input_data = {
        ...    'firstname': u'Fred',
        ...    'surname': u'Jones',
        ...    'age': u'21',
        ... }
        >>> v.process(input_data)
        {'age': 21, 'firstname': u'Fred', 'surname': u'Jones'}

When validation fails, a ``ValidationError`` is raised. This contains error
messages for all the failing validation tests::

        >>> input_data = {
        ...    'firstname': u'Fred',
        ...    'age': u'16',
        ... }
        >>> v.process(input_data)
        Traceback (most recent call last):
          ...
	ValidationError: ValidationError([('surname', 'Please enter your
	surname'), ('age', 'You must be at least 18 to proceed')])

Documentation and download
---------------------------

* `Documentation for the latest version <http://www.ollycope.com/software/formalize>`_.

* Download the python egg from the `Python Package Index <http://pypi.python.org/pypi/formalize/>`_

* View the source code on `patch-tag.com <http://patch-tag.com/r/oliver/formalize>`_

Licensing
----------

Formalize is available under the terms of the `new BSD licence <http://www.opensource.org/licenses/bsd-license.php>`_.


