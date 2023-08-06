
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
        You can extend this validator by supplying additional
        false values to ``required_but_missing`` list.
    """
    __slots__ = ('message_template')

    def __init__(self, message_template=None):
        self.message_template = message_template or _(
            'Required field cannot be left blank.')

    def __call__(self, message_template):
        """ Let you customize message template.
        """
        return RequiredRule(message_template)

    def validate(self, value, name, model, result, gettext):
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
        """
        return MissingRule(message_template)

    def validate(self, value, name, model, result, gettext):
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
        """
        if min:
            self.min = min
            if not max:
                self.min = min
                self.validate = self.check_min
                self.message_template = message_template or _(
                    'Required to be a minimum of %(min)d characters'
                    ' in length.')
            elif min == max:
                self.validate = self.check_equal
                self.message_template = message_template or _(
                    'The length must be exactly %(len)d'
                    ' characters.')
            else:
                self.max = max
                self.validate = self.check_range
                self.message_template = message_template or _(
                    'The length must fall within the range %(min)d'
                    ' - %(max)d characters.')
        elif max:
            self.max = max
            self.validate = self.check_max
            self.message_template = message_template or _(
                'Exceeds maximum length of %(max)d.')
        else:
            self.validate = self.succeed

    def succeed(self, value, name, model, result, gettext):
        return True

    def check_min(self, value, name, model, result, gettext):
        if value is None:
            return True
        if len(value) < self.min:
            result.append(gettext(self.message_template)
                          % {'min': self.min})
            return False
        return True

    def check_max(self, value, name, model, result, gettext):
        if value is None:
            return True
        if len(value) > self.max:
            result.append(gettext(self.message_template)
                          % {'max': self.max})
            return False
        return True

    def check_equal(self, value, name, model, result, gettext):
        if value is None:
            return True
        if len(value) != self.min:
            result.append(gettext(self.message_template)
                          % {'len': self.min})
            return False
        return True

    def check_range(self, value, name, model, result, gettext):
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
        """ Initialization selects the most appropriate validation
            strategy.
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
            self.validate = self.succeed

    def succeed(self, value, name, model, result, gettext):
        return True

    def check_equal(self, value, name, model, result, gettext):
        getter = ref_getter(model)
        comparand_value = getter(model, self.comparand)
        if value != comparand_value:
            result.append(gettext(self.message_template)
                          % {'comparand': self.comparand})
            return False
        return True

    def check_not_equal(self, value, name, model, result, gettext):
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


class ValuePredicateRule(object):
    """ Fails if predicate return False. Predicate is any callable
        of the following contract::

            def predicate(value):
                return True
    """
    __slots__ = ('predicate', 'message_template')

    def __init__(self, predicate, message_template=None):
        self.predicate = predicate
        self.message_template = message_template or _(
            'Required to satisfy validation value predicate condition.')

    def validate(self, value, name, model, result, gettext):
        if not self.predicate(value):
            result.append(gettext(self.message_template))
            return False
        return True


class RegexRule(object):
    """ Search for regular expression pattern.
    """
    __slots__ = ('validate', 'regex', 'message_template')

    def __init__(self, regex, negated=False, message_template=None):
        """ `regex` - a regular expression pattern to search for
            or a pre-compiled regular expression. The pattern is
            searched to be found if `negated` is `False`. If
            `negated` is `True` the rule succeed if the pattern
            not found.
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
        if value is None:
            return True
        if not self.regex.search(value):
            result.append(gettext(self.message_template))
            return False
        return True

    def check_not_found(self, value, name, model, result, gettext):
        if value is None:
            return True
        if self.regex.search(value):
            result.append(gettext(self.message_template))
            return False
        return True


class SlugRule(RegexRule):
    """ Ensures only letters, numbers, underscores or hyphens.
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
        """
        return SlugRule(message_template)


class EmailRule(RegexRule):
    """ Ensures a valid email.
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
        """
        return EmailRule(message_template)


class RangeRule(object):
    """ Ensures value is in range defined by this rule.

        Works with any numbers including `Decimal`.
    """
    __slots__ = ('validate', 'min', 'max', 'message_template')

    def __init__(self, min=None, max=None, message_template=None):
        """ Initialization selects the most appropriate validation
            strategy.
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
                self.validate = self.check_range
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
        return True

    def check_min(self, value, name, model, result, gettext):
        if value is None:
            return True
        if value < self.min:
            result.append(gettext(self.message_template)
                          % {'min': self.min})
            return False
        return True

    def check_max(self, value, name, model, result, gettext):
        if value is None:
            return True
        if value > self.max:
            result.append(gettext(self.message_template)
                          % {'max': self.max})
            return False
        return True

    def check_range(self, value, name, model, result, gettext):
        if value is None:
            return True
        if value < self.min or value > self.max:
            result.append(gettext(self.message_template)
                          % {'min': self.min, 'max': self.max})
            return False
        return True


class AndRule(object):
    """ Applies all ``rules`` regardless of validation result.
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
    """ Applies ``rules`` to each item in value list.
    """
    __slots__ = ('rules', 'stop')

    def __init__(self, rules, stop=True):
        """ Initializes rule by converting ``rules`` to tuple. If
            `stop` is `True` (default), the rule returns on first
            fail, otherwise all errors.
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
        Checks are case sensitive if items are strings.
    """
    __slots__ = ('items', 'message_template')

    def __init__(self, items, message_template=None):
        """ Initializes rule by supplying valid `items`.
        """
        assert items
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
                self.validate = self.check_range
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

    def check_range(self, value, name, model, result, gettext):
        if value is None:
            return True
        now = self.now()
        if value < now + self.min or value > now + self.max:
            result.append(gettext(self.message_template)
                          % {'min': self.min, 'max': self.max})
            return False
        return True


class RelativeDateDeltaRule(RelativeDeltaRule):
    """ Check if value is in relative date range local time.
    """
    __slots__ = ()

    def now(self):
        return date.today()


class RelativeUTCDateDeltaRule(RelativeDeltaRule):
    """ Check if value is in relative date range UTC time.
    """
    __slots__ = ()

    def now(self):
        return datetime.utcnow().date()


class RelativeTZDateDeltaRule(RelativeDeltaRule):
    """ Check if value is in relative date range TZ time.
    """
    __slots__ = ('tz')

    def __init__(self, min=None, max=None, tz=None,
                 message_template=None):
        super(RelativeTZDateDeltaRule, self).__init__(
            min, max, message_template)
        self.tz = tz

    def now(self):
        return datetime.now(self.tz).date()


class RelativeDateTimeDeltaRule(RelativeDeltaRule):
    """ Check if value is in relative datetime range local time.
    """
    __slots__ = ()

    def now(self):
        return datetime.now()


class RelativeUTCDateTimeDeltaRule(RelativeDeltaRule):
    """ Check if value is in relative datetime range UTC time.
    """
    __slots__ = ()

    def now(self):
        return datetime.utcnow()


class RelativeTZDateTimeDeltaRule(RelativeDeltaRule):
    """ Check if value is in relative date range TZ time.
    """
    __slots__ = ('tz')

    def __init__(self, min=None, max=None, tz=None,
                 message_template=None):
        super(RelativeTZDateTimeDeltaRule, self).__init__(
            min, max, message_template)
        self.tz = tz

    def now(self):
        return datetime.now(self.tz)


class IgnoreRule(object):
    """ The idea behind this rule is to be able to substitute
        any validation rule by this one that always succeed:

            from wheezy.validation.rules import ignore as regex

        This way all `regex` rules are ignored within a scope of
        import.
    """

    def __init__(self, *args, **kwargs):
        pass

    def validate(self, value, name, model, result, gettext):
        """ Always succeed.
        """
        return True


required = RequiredRule()
missing = optional = empty = MissingRule()
length = LengthRule
compare = CompareRule
model_predicate = predicate = PredicateRule
value_predicate = must = ValuePredicateRule
regex = RegexRule
slug = SlugRule()
email = EmailRule()
range = RangeRule
and_ = AndRule
or_ = OrRule
iterator = IteratorRule
one_of = OneOfRule
relative_date = RelativeDateDeltaRule
relative_utcdate = RelativeUTCDateDeltaRule
relative_tzdate = RelativeTZDateDeltaRule
relative_datetime = RelativeDateTimeDeltaRule
relative_utcdatetime = RelativeUTCDateTimeDeltaRule
relative_tzdatetime = RelativeTZDateTimeDeltaRule
ignore = IgnoreRule
