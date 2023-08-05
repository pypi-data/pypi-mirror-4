import re
from formalize.core import ValidationError

__all__ = [
    'assert_true', 'assert_false', 'test', 'maxlen', 'minlen',
    'greaterthan', 'lessthan', 'matches', 'looks_like_email',
    'maxwords', 'minwords', 'equals', 'notempty', 'is_in'
]

def assert_true(predicate, message):
    u"""
    Raise a ``ValidationError`` if ``predicate`` is not ``True``
    """
    if not predicate:
        raise ValidationError(None, message)

def assert_false(predicate, message):
    u"""
    Raise a ``ValidationError`` if ``predicate`` is not ``False``
    """
    if predicate:
        raise ValidationError(None, message)

def test(func, message):
    """
    Allow an arbitrary test via a function (or lambda) returning a boolean value.

    Example::

        >>> from formalize import FormValidator, Unicode, Using
        >>> banned = ['password', 'letmein', '123456']
        >>> v = FormValidator()(
        ...     password=Unicode()(
        ...         test(lambda value: value not in banned, u"Password is too simple")
        ...     )
        ... )
        >>> v.process({'password': 'hello'})
        {'password': u'hello'}
        >>> v.process({'password': 'password'}) # doctest: +ELLIPSIS
        Traceback (most recent call last):
         ...
        ValidationError: ValidationError([('password', u'Password is too simple')])

    This can also be combined with ``Using``::

        >>> from formalize import FormValidator, Unicode, Using
        >>> v = FormValidator()(
        ...     oldpassword=Unicode(),
        ...     newpassword=Unicode()(
        ...         Using('newpassword', 'oldpassword')(test(lambda new, old: old != new, u"New password cannot be the same as your old password"))
        ...     )
        ... )
        >>> v.process({'oldpassword': 'sliced', 'newpassword': 'bread'}) == {'oldpassword': 'sliced', 'newpassword': 'bread'}
        True
        >>> v.process({'oldpassword': 'sliced', 'newpassword': 'sliced'})
        Traceback (most recent call last):
         ...
        ValidationError: ValidationError([('newpassword', u'New password cannot be the same as your old password')])


    """

    def check(*args, **kwargs):
        assert_true(func(*args, **kwargs), message)
        return args[0]
    return check

# Prevent the nose test runner from picking this up as part of the test suite
test.__test__ = False

def minlen(l, message=None):
    """
    Synopsis::

        >>> from formalize import FormValidator, Unicode
        >>> v = FormValidator()(
        ...     password=Unicode()(minlen(6, message=u"Password is too short"))
        ... )
        >>> v.process({'password': 'hello'}) # doctest: +ELLIPSIS
        Traceback (most recent call last):
         ...
        ValidationError: ValidationError([('password', u'Password is too short')])
    """

    def check(value):
        assert_true(len(value) >= l, message)
        return value
    return check

def maxlen(l, message=None):
    """
    Synopsis::

        >>> from formalize import FormValidator, Unicode
        >>> v = FormValidator()(
        ...     username=Unicode()(maxlen(20, message=u'Username is too long'))
        ... )
        >>> v.process({'username': 'abcdefghijklmnopqrstu'}) # doctest: +ELLIPSIS
        Traceback (most recent call last):
         ...
        ValidationError: ValidationError([('username', u'Username is too long')])
    """

    def check(value):
        assert_true(len(value) <= l, message)
        return value
    return check

def greaterthan(l, message=None):
    """
    Synopsis::

        >>> from formalize import FormValidator, Int
        >>> v = FormValidator()(
        ...     age=Int()(greaterthan(18, message=u'You must be at least 18 years old'))
        ... )
        >>> v.process({'age': '8'}) # doctest: +ELLIPSIS
        Traceback (most recent call last):
         ...
        ValidationError: ValidationError([('age', u'You must be at least 18 years old')])
    """

    def check(value):
        assert_true(value > l, message)
        return value
    return check

def lessthan(l, message=None):
    """
    Synopsis::

        >>> from formalize import FormValidator, Int
        >>> v = FormValidator()(
        ...     day=Int()(lessthan(7, message=u'Value must be less than 7'))
        ... )
        >>> v.process({'day': '8'}) # doctest: +ELLIPSIS
        Traceback (most recent call last):
         ...
        ValidationError: ValidationError([('day', u'Value must be less than 7')])
    """

    def check(value):
        assert_true(value < l, message)
        return value
    return check

def notempty(message=None):
    """
    Check that a string value is not empty or whitespace

    Synopsis::

        >>> from formalize import FormValidator, Unicode
        >>> v = FormValidator()(
        ...     name=Unicode()(notempty(message=u'Value is required'))
        ... )
        >>> v.process({'name': ''}) # doctest: +ELLIPSIS
        Traceback (most recent call last):
         ...
        ValidationError: ValidationError([('name', u'Value is required')])

    """
    return matches(re.compile(r'\S'), message)

def matches(p, message=None):
    """
    Synopsis::

        >>> from formalize import FormValidator, Unicode
        >>> v = FormValidator()(
        ...     code=Unicode()(matches(r'^[a-z0-9]+$', u'Please only lower case letters and digits'))
        ... )
        >>> v.process({'code': 'A1'}) # doctest: +ELLIPSIS
        Traceback (most recent call last):
         ...
        ValidationError: ValidationError([('code', u'Please only lower case letters and digits')])
    """

    if isinstance(p, basestring):
        p = re.compile(p)

    def check(value):
        assert_true(p.search(value) is not None, message)
        return value

    return check

def equals(testvalue, message=None):
    """
    Synopsis::

        >>> from formalize import FormValidator, Bool
        >>> v = FormValidator()(
        ...     terms_accepted=Bool()(equals(True, u'Please accept the terms of service to continue'))
        ... )
        >>> v.process({'terms_accepted': ''}) # doctest: +ELLIPSIS
        Traceback (most recent call last):
         ...
        ValidationError: ValidationError([('terms_accepted', u'Please accept the terms of service to continue')])
    """
    def check(value):
        assert_true(value == testvalue, message)
        return value
    return check


def is_in(values, message=None):
    """
    Synopsis::

        >>> from formalize import FormValidator, Unicode
        >>> v = FormValidator()(
        ...     terms_accepted=Unicode()(is_in(['Y', 'N'], u'Please answer yes or no'))
        ... )
        >>> v.process({'terms_accepted': 'maybe'}) # doctest: +ELLIPSIS
        Traceback (most recent call last):
         ...
        ValidationError: ValidationError([('terms_accepted', u'Please answer yes or no')])
    """
    def check(value):
        assert_true(value in values, message)
        return value
    return check

def looks_like_email(message=None):
    """
    Check that the value is superficially like an email address, ie that it
    contains a local part and domain, separated with an ``@``.

    Beyond this it is rather difficult to verify an email address (and
    technically valid RFC2822 email addresses may still break your application
    code - the range of what counts as valid is notoriously wide).


    Synopsis::

        >>> from formalize import FormValidator, Unicode
        >>> v = FormValidator()(
        ...     email=Unicode()(looks_like_email(message=u'Please supply an email address'))
        ... )
        >>> v.process({'email': 'me at example dot com'}) # doctest: +ELLIPSIS
        Traceback (most recent call last):
         ...
        ValidationError: ValidationError([('email', u'Please supply an email address')])
    """
    def check(value):
        try:
            user, host = value.split('@')
        except ValueError:
            raise ValidationError(None, message)

        # Check we have at least something in the user and host parts
        assert_true(len(user) > 0 and len(host) > 0, message)
        assert_true('..' not in host, message)
        return value

    return check

def maxwords(count, message=None):
    """
    Check that the value has no more than ``count`` words

    Synopsis::

        >>> from formalize import FormValidator, Unicode
        >>> v = FormValidator()(
        ...     message=Unicode()(maxwords(2, message=u"Value is too long"))
        ... )
        >>> v.process({'message': u'hello world!'})
        {'message': u'hello world!'}

        >>> v.process({'message': u'to be or not to be'})
        Traceback (most recent call last):
         ...
        ValidationError: ValidationError([('message', u'Value is too long')])

    """
    def check(value):
        assert_true(len(re.split(r'\s+', value)) <= count, message)
        return value
    return check

def minwords(count, message=None):
    """
    Check that the value has at least ``count`` words

    Synopsis::

        >>> from formalize import FormValidator, Unicode
        >>> v = FormValidator()(
        ...     message=Unicode()(minwords(3, message=u"Value is too short"))
        ... )
        >>> v.process({'message': u'to be or not to be'})
        {'message': u'to be or not to be'}
        >>> v.process({'message': u'hello world'}) # doctest: +ELLIPSIS
        Traceback (most recent call last):
         ...
        ValidationError: ValidationError([('message', u'Value is too short')])
    """
    def check(value):
        assert_true(len(re.split(r'\s+', value)) >= count, message)
        return value
    return check


