
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
        """ Split `mapping` by one that holds iteratable of rules and
            the other with nested validators.
        """
        rules = []
        inner = []
        for name, value in iteritems(mapping):
            if hasattr(value, '__iter__'):
                rules.append((name, tuple(value)))
            else:
                inner.append((name, value))
        self.rules = tuple(rules)
        self.inner = tuple(inner)

    def validate(self, model, results, stop=True, translations=None,
                 gettext=None):
        """ Validates given `model` with results of validation stored
            in `results`. Be default the validation stops on first
            rule fail, however with supplied `stop` argument set `False`
            the `result` will get all errors reported by a rule.

            There is a way to internationalize validation errors with
            `translations` or `gettext`.
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
