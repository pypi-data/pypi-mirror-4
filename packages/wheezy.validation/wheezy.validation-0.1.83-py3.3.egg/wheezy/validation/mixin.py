"""
"""


class ValidationMixin(object):
    """
        Requirements:
        1. self.errors
        2. self.translations

        >>> class MyService(ValidationMixin):
        ...     def __init__(self):
        ...         self.errors = {}
        ...         self.translations = {'validation': None}
        >>> service = MyService()

        >>> service.error('message')
        >>> service.errors
        {'__ERROR__': ['message']}

        >>> from wheezy.validation.rules import required
        >>> from wheezy.validation.validator import Validator
        >>> v = Validator({
        ...	    'name': [required]
        ... })
        >>> user = {'name': 'abc'}
        >>> service.validate(user, v)
        True
        >>> user = {'name': None}
        >>> service.validate(user, v)
        False
    """

    def error(self, message):
        self.errors.setdefault('__ERROR__', []).append(message)

    def validate(self, model, validator):
        return validator.validate(
            model,
            self.errors,
            translations=self.translations['validation'])
