
""" ``validator`` module.
"""

from wheezy.validation.comp import iteritems
from wheezy.validation.comp import null_translations
from wheezy.validation.comp import ref_gettext
from wheezy.validation.comp import ref_getter


class Validator(object):
    """ Container of validation rules that all together provide
        object validation.
    """
    __slots__ = ('rules', 'inner')

    def __init__(self, mapping):
        # Split mapping by one that holds iteratable of rules and
        # the other with nested validator
        rules = []
        inner = []
        for (name, value) in iteritems(mapping):
            if hasattr(value, '__iter__'):
                rules.append((name, tuple(value)))
            else:
                inner.append((name, value))
        self.rules = tuple(rules)
        self.inner = tuple(inner)

    def validate(self, model, results, stop=True, translations=None,
                 gettext=None):
        """
            Here is a class and object we are going to validate.

            >>> class User(object):
            ...     name = None
            >>> user = User()

            setup validation

            >>> from wheezy.validation.rules import required
            >>> from wheezy.validation.rules import length
            >>> v = Validator({
            ...	    'name': [required, length(min=4)]
            ... })

            Let validate user. By default validation stops on fist
            fail.

            >>> results = {}
            >>> v.validate(user, results)
            False
            >>> len(results['name'])
            1
            >>> user.name = 'abc'
            >>> results = {}
            >>> v.validate(user, results)
            False

            >>> len(results['name'])
            1

            However you can get all fails by settings optional
            ``stop`` to ``False``.

            >>> user.name = ''
            >>> results = {}
            >>> v.validate(user, results, stop=False)
            False
            >>> len(results['name'])
            2

            You can nest other validator for composite objects

            >>> class Registration(object):
            ...     user = User()
            >>> registration_validator = Validator({
            ...         'user': v
            ... })
            >>> r = Registration()
            >>> registration_validator.validate(r, results)
            False

            Validation succeed

            >>> user.name = 'abcde'
            >>> results = {}
            >>> v.validate(user, results)
            True
            >>> results
            {}
            >>> r.user.name = 'abcde'
            >>> registration_validator.validate(r, results)
            True

            Validatable can be a dict.

            >>> user = {'name': None}
            >>> results = {}
            >>> v.validate(user, results)
            False
        """
        if gettext is None:
            if translations is None:
                translations = null_translations
            gettext = ref_gettext(translations)
        succeed = True
        getter = ref_getter(model)
        for name, rules in self.rules:
            value = getter(model, name)
            result = []
            for rule in rules:
                rule_succeed = rule.validate(value, name,
                                             model, result, gettext)
                succeed &= rule_succeed
                if not rule_succeed and stop:
                    break
            if result:
                results[name] = result
        for name, validator in self.inner:
            succeed &= validator.validate(getter(model, name),
                                          results, stop, None, gettext)
        return succeed
