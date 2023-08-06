
""" ``model`` module.
"""

from datetime import date
from datetime import datetime
from datetime import time
from time import strptime

from wheezy.validation.comp import Decimal
from wheezy.validation.comp import null_translations
from wheezy.validation.comp import ref_gettext
from wheezy.validation.i18n import decimal_separator
from wheezy.validation.i18n import default_date_input_format
from wheezy.validation.i18n import default_datetime_input_format
from wheezy.validation.i18n import default_time_input_format
from wheezy.validation.i18n import fallback_date_input_formats
from wheezy.validation.i18n import fallback_datetime_input_formats
from wheezy.validation.i18n import fallback_time_input_formats
from wheezy.validation.i18n import thousands_separator


def try_update_model(model, values, results, translations=None):
    """ Try update `model` with `values` (a dict of lists or strings),
        any errors encountered put into `results` and use `translations`
        for i18n.
    """
    if translations is None:
        translations = null_translations
    gettext = ref_gettext(translations)
    if hasattr(model, '__iter__'):
        attribute_names = model
        model_type = type(model)
        getter = model_type.__getitem__
        setter = model_type.__setitem__
    else:
        attribute_names = list(model.__dict__)
        attribute_names.extend([name for name in model.__class__.__dict__
                                if name[:1] != '_'])
        getter = getattr
        setter = setattr
    succeed = True
    for name in attribute_names:
        if name not in values:
            continue
        value = values[name]
        attr = getter(model, name)
        # Check if we have a deal with list like attribute
        if hasattr(attr, '__setitem__'):
            # Guess type of list by checking the first item,
            # fallback to str provider that leaves value unchanged.
            if attr:
                provider_name = type(attr[0]).__name__
                if provider_name in value_providers:
                    value_provider = value_providers[provider_name]
                else:  # pragma: nocover
                    continue
            else:
                value_provider = value_providers['str']
            items = []
            try:
                for item in value:
                    items.append(value_provider(item, gettext))
                attr[:] = items
            except (ArithmeticError, ValueError):
                results[name] = [gettext(
                    "Multiple input was not in a correct format.")]
                succeed = False
        else:  # A simple value attribute
            provider_name = type(attr).__name__
            if provider_name in value_providers:
                value_provider = value_providers[provider_name]
                if isinstance(value, list):
                    value = value and value[-1] or ''
                try:
                    value = value_provider(value, gettext)
                    setter(model, name, value)
                except (ArithmeticError, ValueError):
                    results[name] = [gettext(
                        "Input was not in a correct format.")]
                    succeed = False
    return succeed


# region: internal details

# value_provider => lambda str_value, gettext: parsed_value

def int_value_provider(str_value, gettext):
    """ Converts string value to ``int``.
    """
    str_value = str_value.strip()
    if str_value:
        return int(str_value.replace(thousands_separator(gettext), ''))
    else:
        return None


decimal_zero = Decimal(0)
decimal_zero_values = ['0', '0.0', '0.00']


def decimal_value_provider(str_value, gettext):
    """ Converts string value to ``Decimal``.
    """
    str_value = str_value.strip()
    if str_value:
        s = thousands_separator(gettext)
        if s in str_value:
            str_value = str_value.replace(s, '')
        s = decimal_separator(gettext)
        str_value = str_value.replace(s, '.', 1)
        if str_value in decimal_zero_values:
            return decimal_zero
        return Decimal(str_value)
    else:
        return None


boolean_true_values = ['1', 'True']


def bool_value_provider(str_value, gettext):
    """ Converts string value to ``bool``.
    """
    str_value = str_value.strip()
    return str_value in boolean_true_values


def float_value_provider(str_value, gettext):
    """ Converts string value to ``float``.
    """
    str_value = str_value.strip()
    if str_value:
        str_value = str_value.replace(thousands_separator(gettext), '')
        str_value = '.'.join(str_value.split(decimal_separator(gettext), 1))
        return float(str_value)
    else:
        return None


def date_value_provider(str_value, gettext):
    """ Converts string value to ``datetime.date``.
    """
    str_value = str_value.strip()
    if str_value:
        try:
            return date(*strptime(
                str_value,
                default_date_input_format(gettext))[:3])
        except ValueError:
            for fmt in fallback_date_input_formats(gettext).split('|'):
                try:
                    return date(*strptime(str_value, fmt)[:3])
                except ValueError:
                    continue
            raise ValueError()
    else:
        return None


def time_value_provider(str_value, gettext):
    """ Converts string value to ``datetime.time``.
    """
    str_value = str_value.strip()
    if str_value:
        try:
            return time(*strptime(
                str_value,
                default_time_input_format(gettext))[3:6])
        except ValueError:
            for fmt in fallback_time_input_formats(gettext).split('|'):
                try:
                    return time(*strptime(str_value, fmt)[3:6])
                except ValueError:
                    continue
            raise ValueError()
    else:
        return None


def datetime_value_provider(str_value, gettext):
    """ Converts string value to ``datetime.datetime``.
    """
    str_value = str_value.strip()
    if str_value:
        try:
            return datetime(*strptime(
                str_value,
                default_datetime_input_format(gettext))[:6])
        except ValueError:
            for fmt in fallback_datetime_input_formats(gettext).split('|'):
                try:
                    return datetime(*strptime(str_value, fmt)[:6])
                except ValueError:
                    continue
            value = date_value_provider(str_value, gettext)
            return datetime(value.year, value.month, value.day)
    else:
        return None


value_providers = {
    'str': lambda str_value, gettext: str_value.strip(),
    'unicode': lambda str_value, gettext: str_value.strip().decode('UTF-8'),
    'int': int_value_provider,
    'Decimal': decimal_value_provider,
    'bool': bool_value_provider,
    'float': float_value_provider,
    'date': date_value_provider,
    'time': time_value_provider,
    'datetime': datetime_value_provider
}


from wheezy.validation.patches import patch_strptime_cache_size
if not patch_strptime_cache_size():  # pragma: nocover
    from warnings import warn
    warn('Failed to patch _strptime._CACHE_MAX_SIZE')
    del warn
del patch_strptime_cache_size
