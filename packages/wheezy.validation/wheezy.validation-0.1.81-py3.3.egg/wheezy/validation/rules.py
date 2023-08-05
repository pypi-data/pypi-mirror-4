
""" ``rules`` module.
"""

import re

from datetime import date
from datetime import datetime
from datetime import time

from wheezy.validation.comp import ref_getter
from wheezy.validation.comp import regex_pattern


_ = lambda s: s
required_but_missing = [date.min, datetime.min, time.min]


class RequiredRule(object):
    """ Any value evaluated to boolean ``True`` pass this rule.
    """
    __slots__ = ('message_template')

    def __init__(self, message_template=None):
        self.message_template = message_template or _(
            'Required field cannot be left blank.')

    def __call__(self, message_template):
        """ Let you customize message template.

            >>> r = required('customized')
            >>> assert r != required
            >>> r.message_template
            'customized'
        """
        return RequiredRule(message_template)

    def validate(self, value, name, model, result, gettext):
        """
            If ``value`` is evaluated to ``False`` than it cause
            this rule to fail.

            >>> result = []
            >>> r = RequiredRule(message_template='required')
            >>> r.validate(None, None, None, result, _)
            False
            >>> result
            ['required']

            Anything that python interprets as ``True`` is passing
            this rule.

            >>> result = []
            >>> r.validate('abc', None, None, result, _)
            True
            >>> result
            []

            >>> r.validate(date.min, None, None, result, _)
            False

            ``required`` is a shortcut

            >>> assert isinstance(required, RequiredRule)
        """
        if not value or value in required_but_missing:
            result.append(gettext(self.message_template))
            return False
        return True


class MissingRule(object):
    """ Any value evaluated to boolean ``False`` pass this rule.
    """
    __slots__ = ('message_template')

    def __init__(self, message_template=None):
        self.message_template = message_template or _(
            'Field cannot have a value.')

    def __call__(self, message_template):
        """ Let you customize message template.

            >>> r = missing('customized')
            >>> assert r != missing
            >>> r.message_template
            'customized'
        """
        return MissingRule(message_template)

    def validate(self, value, name, model, result, gettext):
        """
            If ``value`` is evaluated to ``True`` than it cause
            this rule to fail.

            >>> result = []
            >>> r = MissingRule(message_template='error')
            >>> r.validate(100, None, None, result, _)
            False
            >>> result
            ['error']

            Anything that python interprets as ``False`` is passing
            this rule.

            >>> result = []
            >>> r.validate('', None, None, result, _)
            True
            >>> result
            []

            >>> r.validate(date.min, None, None, result, _)
            True

            ``missing`` is a shortcut

            >>> assert isinstance(missing, MissingRule)
        """
        if value and value not in required_but_missing:
            result.append(gettext(self.message_template))
            return False
        return True


class LengthRule(object):
    """ Result of python function ``len()`` must fall within a range
        defined by this rule.
    """
    __slots__ = ('validate', 'min', 'max', 'message_template')

    def __init__(self, min=None, max=None, message_template=None):
        """
            Initialization selects the most appropriate validation
            strategy.

            >>> r = LengthRule(min=2)
            >>> assert r.validate == r.check_min
            >>> r = LengthRule(max=2)
            >>> assert r.validate == r.check_max
            >>> r = LengthRule()
            >>> assert r.validate == r.succeed
            >>> r = LengthRule(min=1, max=2)
        """
        if min:
            self.min = min
            if not max:
                self.min = min
                self.validate = self.check_min
                self.message_template = message_template or _(
                    'Required to be a minimum of %(min)d characters'
                    ' in length.')
            else:
                self.max = max
                self.validate = self.check
                self.message_template = message_template or _(
                    'The length must fall within the range %(min)d'
                    ' - %(max)d characters.')
        else:
            if max:
                self.max = max
                self.validate = self.check_max
                self.message_template = message_template or _(
                    'Exceeds maximum length of %(max)d.')
            else:
                self.validate = self.succeed

    def succeed(self, value, name, model, result, gettext):
        """
            >>> r = LengthRule()

            Succeed if ``value`` is None

            >>> r.validate(None, None, None, None, _)
            True

            Since no range specified it chooses ``succeed`` strategy.

            >>> r.validate('abc', None, None, None, _)
            True
        """
        return True

    def check_min(self, value, name, model, result, gettext):
        """ ``check_min`` strategy fails

            >>> result = []
            >>> r = LengthRule(min=2, message_template='min %(min)d')
            >>> r.validate('a', None, None, result, _)
            False
            >>> result
            ['min 2']

            ``check_min`` strategy succeed

            >>> result = []
            >>> r = LengthRule(min=2)
            >>> r.validate(None, None, None, result, _)
            True
            >>> r.validate('ab', None, None, result, _)
            True
            >>> result
            []
        """
        if value is None:
            return True
        if len(value) < self.min:
            result.append(gettext(self.message_template)
                          % {'min': self.min})
            return False
        return True

    def check_max(self, value, name, model, result, gettext):
        """ ``check_max`` strategy fails

            >>> result = []
            >>> r = LengthRule(max=2, message_template='max %(max)d')
            >>> r.validate('abc', None, None, result, _)
            False
            >>> result
            ['max 2']

            ``check_max`` strategy succeed

            >>> result = []
            >>> r = LengthRule(max=2)
            >>> r.validate(None, None, None, result, _)
            True
            >>> r.validate('ab', None, None, result, _)
            True
            >>> result
            []
        """
        if value is None:
            return True
        if len(value) > self.max:
            result.append(gettext(self.message_template)
                          % {'max': self.max})
            return False
        return True

    def check(self, value, name, model, result, gettext):
        """ ``check`` strategy fails

            >>> r = LengthRule(min=2, max=3,
            ...         message_template='range %(min)d-%(max)d')
            >>> result = []
            >>> r.validate('a', None, None, result, _)
            False
            >>> result
            ['range 2-3']

            ``check`` strategy succeed

            >>> result = []
            >>> r = LengthRule(min=1, max=2)
            >>> r.validate(None, None, None, result, _)
            True
            >>> r.validate('ab', None, None, result, _)
            True
            >>> result
            []

            ``length`` is shortcut

            >>> assert length is LengthRule
        """
        if value is None:
            return True
        l = len(value)
        if l < self.min or l > self.max:
            result.append(gettext(self.message_template)
                          % {'min': self.min, 'max': self.max})
            return False
        return True


class CompareRule(object):
    """ Compares attribute being validated with some other attribute value.
    """
    __slots__ = ('validate', 'comparand', 'message_template')

    def __init__(self, equal=None, not_equal=None, message_template=None):
        """
            Initialization selects the most appropriate validation
            strategy.

            >>> r = CompareRule(equal='confirm_password')
            >>> assert r.validate == r.check_equal

            >>> r = CompareRule(not_equal='other')
            >>> assert r.validate == r.check_not_equal
        """
        if equal:
            self.comparand = equal
            self.validate = self.check_equal
            self.message_template = message_template or _(
                'The value failed equality comparison'
                ' with "%(comparand)s".')
        elif not_equal:
            self.comparand = not_equal
            self.validate = self.check_not_equal
            self.message_template = message_template or _(
                'The value failed not equal comparison'
                ' with "%(comparand)s".')
        else:
            self.validate = self.check

    def check(self, value, name, model, result, gettext):
        """
            No any comparer selected

            >>> r = CompareRule()
            >>> r.validate('abc', None, None, None, _)
            True
        """
        return True

    def check_equal(self, value, name, model, result, gettext):
        """
            ``check_equal`` strategy succeed.

            >>> result = []
            >>> r = CompareRule(equal='confirm_password')
            >>> model = {
            ...         'confirm_password': 'x'
            ... }
            >>> r.validate('x', None, model, result, _)
            True

            ``check_equal`` strategy fails.

            >>> result = []
            >>> r.validate('z', None, model, result, _)
            False
        """
        getter = ref_getter(model)
        comparand_value = getter(model, self.comparand)
        if value != comparand_value:
            result.append(gettext(self.message_template)
                          % {'comparand': self.comparand})
            return False
        return True

    def check_not_equal(self, value, name, model, result, gettext):
        """ ``check_not_equal`` strategy succeed.

            >>> result = []
            >>> r = CompareRule(not_equal='previous_password')
            >>> model = {
            ...         'previous_password': 'x'
            ... }
            >>> r.validate('y', None, model, result, _)
            True

            ``check_not_equal`` strategy fails.

            >>> result = []
            >>> r.validate('x', None, model, result, _)
            False
        """
        getter = ref_getter(model)
        comparand_value = getter(model, self.comparand)
        if value == comparand_value:
            result.append(gettext(self.message_template)
                          % {'comparand': self.comparand})
            return False
        return True


class PredicateRule(object):
    """ Fails if predicate return False. Predicate is any callable
        of the following contract::

            def predicate(model):
                return True

        >>> r = PredicateRule(lambda model: model is not None)
        >>> result = []
        >>> r.validate('', None, 'x', result, _)
        True
        >>> r.validate('', None, None, result, _)
        False
    """
    __slots__ = ('predicate', 'message_template')

    def __init__(self, predicate, message_template=None):
        self.predicate = predicate
        self.message_template = message_template or _(
            'Required to satisfy validation predicate condition.')

    def validate(self, value, name, model, result, gettext):
        if not self.predicate(model):
            result.append(gettext(self.message_template))
            return False
        return True


class RegexRule(object):
    """ Search for regular expression pattern.
    """
    __slots__ = ('validate', 'regex', 'message_template')

    def __init__(self, regex=None, negated=False, message_template=None):
        """
            ``regex`` - a regular expression pattern to search for
            or a pre-compiled regular expression.

            >>> result = []
            >>> r = regex(re.compile(r'\w+'))
            >>> r.validate('x', None, None, result, _)
            True
        """
        if isinstance(regex, regex_pattern):
            self.regex = re.compile(regex)
        else:
            self.regex = regex
        if negated:
            self.validate = self.check_not_found
            self.message_template = message_template or _(
                'Required to not match validation pattern.')
        else:
            self.validate = self.check_found
            self.message_template = message_template or _(
                'Required to match validation pattern.')

    def check_found(self, value, name, model, result, gettext):
        """
            >>> result = []
            >>> r = RegexRule(r'\d+')
            >>> r.validate(None, None, None, result, _)
            True
            >>> r.validate('1234', None, None, result, _)
            True
            >>> r.validate('x', None, None, result, _)
            False
        """
        if value is None:
            return True
        if not self.regex.search(value):
            result.append(gettext(self.message_template))
            return False
        return True

    def check_not_found(self, value, name, model, result, gettext):
        """
            >>> result = []
            >>> r = RegexRule(r'\d+', negated=True)
            >>> r.validate(None, None, None, result, _)
            True
            >>> r.validate('x', None, None, result, _)
            True
            >>> r.validate('1234', None, None, result, _)
            False
        """
        if value is None:
            return True
        if self.regex.search(value):
            result.append(gettext(self.message_template))
            return False
        return True


class SlugRule(RegexRule):
    """ Ensures only letters, numbers, underscores or hyphens.

        >>> r = slug
        >>> result = []
        >>> r.validate('x14', None, None, result, _)
        True
        >>> r.validate('x%', None, None, result, _)
        False
    """
    __slots__ = ()

    def __init__(self, message_template=None):
        super(SlugRule, self).__init__(
            r'^[-\w]+$', False,
            message_template or _(
                'Invalid slug. The value must consist of letters, '
                'digits, underscopes and/or hyphens.'))

    def __call__(self, message_template):
        """ Let you customize message template.

            >>> r = slug('customized')
            >>> assert r != slug
            >>> r.message_template
            'customized'
        """
        return SlugRule(message_template)


class EmailRule(RegexRule):
    """ Ensures a valid email.

        >>> r = email
        >>> result = []
        >>> r.validate('x.14@somewhere.org', None, None, result, _)
        True
        >>> r.validate('x.14@somewhere.or g', None, None, result, _)
        False
        >>> r.validate('x%', None, None, result, _)
        False
    """
    __slots__ = ()

    def __init__(self, message_template=None):
        super(EmailRule, self).__init__(
            re.compile(r'^[A-Z0-9._%-]+@[A-Z0-9.-]+\.[A-Z]{2,5}$',
                       re.IGNORECASE), False,
            message_template or
            _('Required to be a valid email address.'))

    def __call__(self, message_template):
        """ Let you customize message template.

            >>> r = email('customized')
            >>> assert r != slug
            >>> r.message_template
            'customized'
        """
        return EmailRule(message_template)


class RangeRule(object):
    """ Ensures value is in range defined by this rule.

        Works with any numbers including decimal.

        >>> from decimal import Decimal
        >>> result = []
        >>> r = range(max=Decimal('15.79'))
        >>> r.validate(Decimal('10'), None, None, result, _)
        True
        >>> r.validate(Decimal('20'), None, None, result, _)
        False
    """
    __slots__ = ('validate', 'min', 'max', 'message_template')

    def __init__(self, min=None, max=None, message_template=None):
        """
            Initialization selects the most appropriate validation
            strategy.

            >>> r = RangeRule(min=2)
            >>> assert r.validate == r.check_min
            >>> r = RangeRule(max=2)
            >>> assert r.validate == r.check_max
            >>> r = RangeRule()
            >>> assert r.validate == r.succeed
            >>> r = RangeRule(min=1, max=2)
        """
        if min:
            self.min = min
            if not max:
                self.min = min
                self.validate = self.check_min
                self.message_template = message_template or _(
                    'Required to be greater or equal to %(min)s.')
            else:
                self.max = max
                self.validate = self.check
                self.message_template = message_template or _(
                    'The value must fall within the range %(min)s'
                    ' - %(max)s')
        else:
            if max:
                self.max = max
                self.validate = self.check_max
                self.message_template = message_template or _(
                    'Exceeds maximum allowed value of %(max)s.')
            else:
                self.validate = self.succeed

    def succeed(self, value, name, model, result, gettext):
        """
            >>> r = RangeRule()

            Succeed if ``value`` is None

            >>> r.validate(None, None, None, None, _)
            True

            Since no range specified it chooses ``succeed`` strategy.

            >>> r.validate(100, None, None, None, _)
            True
        """
        return True

    def check_min(self, value, name, model, result, gettext):
        """ ``check_min`` strategy fails

            >>> result = []
            >>> r = RangeRule(min=10, message_template='min %(min)s')
            >>> r.validate(1, None, None, result, _)
            False
            >>> result
            ['min 10']

            ``check_min`` strategy succeed

            >>> result = []
            >>> r = RangeRule(min=10)
            >>> r.validate(None, None, None, result, _)
            True
            >>> r.validate(10, None, None, result, _)
            True
            >>> result
            []
        """
        if value is None:
            return True
        if value < self.min:
            result.append(gettext(self.message_template)
                          % {'min': self.min})
            return False
        return True

    def check_max(self, value, name, model, result, gettext):
        """ ``check_max`` strategy fails

            >>> result = []
            >>> r = RangeRule(max=10, message_template='max %(max)s')
            >>> r.validate(11, None, None, result, _)
            False
            >>> result
            ['max 10']

            ``check_max`` strategy succeed

            >>> result = []
            >>> r = RangeRule(max=10)
            >>> r.validate(None, None, None, result, _)
            True
            >>> r.validate(10, None, None, result, _)
            True
            >>> result
            []
        """
        if value is None:
            return True
        if value > self.max:
            result.append(gettext(self.message_template)
                          % {'max': self.max})
            return False
        return True

    def check(self, value, name, model, result, gettext):
        """ ``check`` strategy fails

            >>> r = RangeRule(min=2, max=3,
            ...         message_template='range %(min)s-%(max)s')
            >>> result = []
            >>> r.validate(1, None, None, result, _)
            False
            >>> result
            ['range 2-3']

            ``check`` strategy succeed

            >>> result = []
            >>> r = RangeRule(min=1, max=2)
            >>> r.validate(None, None, None, result, _)
            True
            >>> r.validate(2, None, None, result, _)
            True
            >>> result
            []

            ``length`` is shortcut

            >>> assert length is LengthRule
        """
        if value is None:
            return True
        if value < self.min or value > self.max:
            result.append(gettext(self.message_template)
                          % {'min': self.min, 'max': self.max})
            return False
        return True


class AndRule(object):
    """ Applies all ``rules`` regardless of validation result.

        >>> result = []
        >>> r = and_(required, range(1, 5))
        >>> r.validate(1, None, None, result, _)
        True
        >>> r.validate(0, None, None, result, _)
        False
        >>> len(result)
        2
    """
    __slots__ = ('rules')

    def __init__(self, *rules):
        """ Initializes rule by converting ``rules`` to tuple.
        """
        assert len(rules) > 1
        self.rules = tuple(rules)

    def validate(self, value, name, model, result, gettext):
        """ Iterate over each rule and check whenever any item in value fail.

            ``value`` - iteratable.
        """
        succeed = True
        for rule in self.rules:
            succeed &= rule.validate(value, name, model, result, gettext)
        return succeed


class OrRule(object):
    """ Succeed if at least one rule in ``rules`` succeed.

        >>> result = []
        >>> r = or_(range(1, 5), range(11, 15))
        >>> r.validate(1, None, None, result, _)
        True
        >>> r.validate(12, None, None, result, _)
        True
        >>> r.validate(0, None, None, result, _)
        False
        >>> len(result)
        2
    """
    __slots__ = ('rules')

    def __init__(self, *rules):
        """ Initializes rule by converting ``rules`` to tuple.
        """
        assert len(rules) > 1
        self.rules = tuple(rules)

    def validate(self, value, name, model, result, gettext):
        """ Iterate over each rule and check whenever value fail.
            Stop on first succeed.
        """
        succeed = True
        r = []
        for rule in self.rules:
            succeed = rule.validate(value, name, model, r, gettext)
            if succeed:
                return True
        result.extend(r)
        return succeed


class IteratorRule(object):
    """ Applies ``rules`` to each item.

        >>> result = []
        >>> r = iterator([required, range(1, 5)])
        >>> r.validate(None, None, None, result, _)
        True
        >>> r.validate([1, 2, 3], None, None, result, _)
        True
        >>> r.validate([1, 7], None, None, result, _)
        False
    """
    __slots__ = ('rules', 'stop')

    def __init__(self, rules, stop=True):
        """ Initializes rule by converting ``rules`` to tuple.
        """
        assert rules
        self.rules = tuple(rules)
        self.stop = stop

    def validate(self, value, name, model, result, gettext):
        """ Iterate over each rule and check whenever any item in value fail.

            ``value`` - iteratable.
        """
        if value is None:
            return True
        succeed = True
        for rule in self.rules:
            for item in value:
                rule_succeed = rule.validate(item, name, model,
                                             result, gettext)
                succeed &= rule_succeed
                if not rule_succeed and self.stop:
                    break
        return succeed


class OneOfRule(object):
    """ Value must match at least one element from ``items``.

        >>> result = []
        >>> r = one_of([1, 2, 3, None])
        >>> r.validate(3, None, None, result, _)
        True
        >>> r.validate(None, None, None, result, _)
        True
        >>> r.validate(7, None, None, result, _)
        False
        >>> r = one_of([1, 2, 3])
        >>> r.validate(None, None, None, result, _)
        False
    """
    __slots__ = ('items', 'message_template')

    def __init__(self, items, message_template=None):
        """
        """
        self.items = tuple(items)
        self.message_template = message_template or _(
            'The value does not belong to the list of known items.')

    def validate(self, value, name, model, result, gettext):
        """ Check whenever value belongs to ``self.items``.
        """
        if value not in self.items:
            result.append(gettext(self.message_template))
            return False
        return True


class RelativeDeltaRule(object):
    """ Check if value is in relative date/time range.

        >>> r = RelativeDeltaRule()
        >>> r.now() # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        NotImplementedError: ...
    """
    __slots__ = ('validate', 'min', 'max', 'message_template')

    def __init__(self, min=None, max=None, message_template=None):
        """
        """
        if min:
            self.min = min
            if not max:
                self.min = min
                self.validate = self.check_min
                self.message_template = message_template or _(
                    'Required to be above a minimum allowed.')
            else:
                self.max = max
                self.validate = self.check
                self.message_template = message_template or _(
                    'Must fall within a valid range.')
        else:
            if max:
                self.max = max
                self.validate = self.check_max
                self.message_template = message_template or _(
                    'Exceeds maximum allowed.')
            else:
                self.validate = self.succeed

    def now(self):
        raise NotImplementedError('Subclasses must override method now()')

    def succeed(self, value, name, model, result, gettext):
        return True

    def check_min(self, value, name, model, result, gettext):
        if value is None:
            return True
        if value < self.now() + self.min:
            result.append(gettext(self.message_template)
                          % {'min': self.min})
            return False
        return True

    def check_max(self, value, name, model, result, gettext):
        if value is None:
            return True
        if value > self.now() + self.max:
            result.append(gettext(self.message_template)
                          % {'max': self.max})
            return False
        return True

    def check(self, value, name, model, result, gettext):
        if value is None:
            return True
        now = self.now()
        if value < now + self.min or value > now + self.max:
            result.append(gettext(self.message_template)
                          % {'min': self.min, 'max': self.max})
            return False
        return True


class RelativeDateDeltaRule(RelativeDeltaRule):
    """
        No range succeed.

        >>> result = []
        >>> r = relative_date()
        >>> r.validate(date.today(), None, None, result, _)
        True

        Min range strategy

        >>> from datetime import timedelta
        >>> result = []
        >>> r = relative_date(min=timedelta(days=-7))
        >>> r.validate(None, None, None, result, _)
        True
        >>> r.validate(date.today(), None, None, result, _)
        True
        >>> d = date.today() - timedelta(days=8)
        >>> r.validate(d, None, None, result, _)
        False

        Max range strategy

        >>> r = relative_date(max=timedelta(days=7))
        >>> r.validate(None, None, None, result, _)
        True
        >>> r.validate(date.today(), None, None, result, _)
        True
        >>> d = date.today() + timedelta(days=8)
        >>> r.validate(d, None, None, result, _)
        False

        Min - Max range strategy

        >>> result = []
        >>> r = relative_date(min=timedelta(days=-7), max=timedelta(days=7))
        >>> r.validate(None, None, None, result, _)
        True
        >>> r.validate(date.today(), None, None, result, _)
        True
        >>> d = date.today() - timedelta(days=8)
        >>> r.validate(d, None, None, result, _)
        False
        >>> d = date.today() + timedelta(days=8)
        >>> r.validate(d, None, None, result, _)
        False
    """
    __slots__ = ()

    def now(self):
        return date.today()


class RelativeDateTimeDeltaRule(RelativeDeltaRule):
    """
        No range succeed.

        >>> result = []
        >>> r = relative_datetime()
        >>> r.validate(datetime.today(), None, None, result, _)
        True

        Min range strategy

        >>> from datetime import timedelta
        >>> result = []
        >>> r = relative_datetime(min=timedelta(days=-7))
        >>> r.validate(datetime.today(), None, None, result, _)
        True
        >>> d = datetime.today() - timedelta(days=8)
        >>> r.validate(d, None, None, result, _)
        False

        Max range strategy

        >>> r = relative_datetime(max=timedelta(days=7))
        >>> r.validate(datetime.today(), None, None, result, _)
        True
        >>> d = datetime.today() + timedelta(days=8)
        >>> r.validate(d, None, None, result, _)
        False

        Min - Max range strategy

        >>> result = []
        >>> r = relative_datetime(min=timedelta(days=-7),
        ...                     max=timedelta(days=7))
        >>> r.validate(datetime.today(), None, None, result, _)
        True
        >>> d = datetime.today() - timedelta(days=8)
        >>> r.validate(d, None, None, result, _)
        False
        >>> d = datetime.today() + timedelta(days=8)
        >>> r.validate(d, None, None, result, _)
        False
    """
    __slots__ = ()

    def now(self):
        return datetime.now()


required = RequiredRule()
missing = optional = empty = MissingRule()
length = LengthRule
compare = CompareRule
predicate = PredicateRule
regex = RegexRule
slug = SlugRule()
email = EmailRule()
range = RangeRule
and_ = AndRule
or_ = OrRule
iterator = IteratorRule
one_of = OneOfRule
relative_date = RelativeDateDeltaRule
relative_datetime = RelativeDateTimeDeltaRule
