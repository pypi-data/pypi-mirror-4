
""" ``mixin`` module.
"""


class ValidationMixin(object):
    """ Used primary by service layer to validate domain model.

        Requirements:
        - self.errors
        - self.translations

        Example::

            class MyService(ValidationMixin):

                def __init__(self, repository, errors, translations, locale):
                    # ...

                def authenticate(self, credential):
                    if not self.validate(credential, credential_validator):
                        return False
                    # ...
                    return True
    """

    def error(self, message):
        """ Add `message` to error summary.
        """
        self.errors.setdefault('__ERROR__', []).append(message)

    def validate(self, model, validator):
        """ Validate given `model` using `validator`.
        """
        return validator.validate(
            model,
            self.errors,
            translations=self.translations['validation'])
