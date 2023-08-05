
""" ``model`` module.
"""

from datetime import date
from datetime import datetime
from datetime import time
from decimal import Decimal
from time import strptime

from wheezy.validation.comp import null_translations
from wheezy.validation.comp import ref_gettext
from wheezy.validation.format import decimal_separator
from wheezy.validation.format import default_date_input_format
from wheezy.validation.format import default_datetime_input_format
from wheezy.validation.format import default_time_input_format
from wheezy.validation.format import fallback_date_input_formats
from wheezy.validation.format import fallback_datetime_input_formats
from wheezy.validation.format import fallback_time_input_formats
from wheezy.validation.format import thousands_separator


def try_update_model(model, values, results, translations=None):
    """
        ``values`` - a dict of lists or strings

        >>> class User(object):
        ...     name = ''
        ...     def __init__(self):
        ...         self.age = 0
        ...         self.balance = Decimal(0)
        ...         self.birthday = date.min
        ...         self.lunch_time = time.min
        ...         self.last_visit = datetime.min
        ...         self.accepted_policy = False
        ...         self.prefs = []
        ...         self.prefs2 = [0]
        >>> user = User()
        >>> values = {'name': 'abc', 'balance': ['0.1'],
        ...     'age': ['33'], 'birthday': ['1978/4/9'],
        ...     'lunch_time': ['13:05'], 'last_visit': ['2012/2/4 16:14:52'],
        ...     'accepted_policy': ['1'], 'prefs': ['1', '2'],
        ...     'prefs2': ['1', '2']}
        >>> results = {}
        >>> try_update_model(user, values, results)
        True
        >>> user.name
        'abc'
        >>> assert Decimal('0.1') == user.balance
        >>> user.age
        33
        >>> user.birthday
        datetime.date(1978, 4, 9)
        >>> user.lunch_time
        datetime.time(13, 5)
        >>> user.last_visit
        datetime.datetime(2012, 2, 4, 16, 14, 52)
        >>> user.accepted_policy
        True
        >>> user.prefs
        ['1', '2']
        >>> user.prefs2
        [1, 2]

        ``model`` can be dict.

        >>> user = {'name': '', 'age': '0'}
        >>> try_update_model(user, values, results)
        True
        >>> user['name']
        'abc'
        >>> user['age']
        '33'

        Invalid values:

        >>> values = {'balance': ['x'], 'age': ['x'], 'birthday': ['4.2.12'],
        ...         'prefs2': ['1', 'x']}
        >>> user = User()
        >>> try_update_model(user, values, results)
        False
        >>> len(results['balance'])
        1
        >>> assert Decimal(0) == user.balance
        >>> len(results['age'])
        1
        >>> user.age
        0
        >>> user.prefs2
        [0]
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


# value_provider => lambda str_value, gettext: parsed_value

def int_value_provider(str_value, gettext):
    """ Converts string value to ``int``.

        >>> int_value_provider('100', lambda x: x)
        100
        >>> int_value_provider('1,000', lambda x: x)
        1000

        Empty string value is converted to ``None``.

        >>> int_value_provider(' ', lambda x: x)
    """
    str_value = str_value.strip()
    if str_value:
        return int(str_value.replace(thousands_separator(gettext), ''))
    else:
        return None


def decimal_value_provider(str_value, gettext):
    """ Converts string value to ``Decimal``.

        >>> assert Decimal('100') == decimal_value_provider('100',
        ...         lambda x: x)
        >>> assert Decimal('1000') == decimal_value_provider('1,000',
        ...         lambda x: x)
        >>> assert Decimal('1007.85') == decimal_value_provider('1,007.85',
        ...         lambda x: x)

        Empty string value is converted to ``None``.

        >>> decimal_value_provider(' ', lambda x: x)
    """
    str_value = str_value.strip()
    if str_value:
        str_value = str_value.replace(thousands_separator(gettext), '')
        str_value = '.'.join(str_value.split(decimal_separator(gettext), 1))
        return Decimal(str_value)
    else:
        return None


BOOLEAN_TRUE_VALUES = ['1', 'True']


def bool_value_provider(str_value, gettext):
    """ Converts string value to ``boolean``.

        >>> bool_value_provider('1', lambda x: x)
        True
        >>> bool_value_provider('0', lambda x: x)
        False

        Empty string value is converted to ``False``.

        >>> bool_value_provider(' ', lambda x: x)
        False
    """
    str_value = str_value.strip()
    return str_value in BOOLEAN_TRUE_VALUES


def float_value_provider(str_value, gettext):
    """ Converts string value to ``float``.

        >>> float_value_provider('1.5', lambda x: x)
        1.5
        >>> float_value_provider('4,531.5', lambda x: x)
        4531.5

        Empty string value is converted to ``None``.

        >>> float_value_provider(' ', lambda x: x)
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

        >>> date_value_provider('2012/2/4', lambda x: x)
        datetime.date(2012, 2, 4)
        >>> date_value_provider('2/4/2012', lambda x: x)
        datetime.date(2012, 2, 4)
        >>> date_value_provider('2012-2-4', lambda x: x)
        datetime.date(2012, 2, 4)
        >>> date_value_provider('2/4/12', lambda x: x)
        datetime.date(2012, 2, 4)

        Empty string value is converted to ``None``.

        >>> date_value_provider(' ', lambda x: x)

        If none of known formats match raise ValueError.

        >>> date_value_provider('2.4.12', lambda x: x)
        Traceback (most recent call last):
            ...
        ValueError
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

        >>> time_value_provider('15:40', lambda x: x)
        datetime.time(15, 40)
        >>> time_value_provider('15:40:11', lambda x: x)
        datetime.time(15, 40, 11)

        Empty string value is converted to ``None``.

        >>> time_value_provider(' ', lambda x: x)

        If none of known formats match raise ValueError.

        >>> time_value_provider('2.45.17', lambda x: x)
        Traceback (most recent call last):
            ...
        ValueError
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

        >>> datetime_value_provider('2008/5/18 15:40', lambda x: x)
        datetime.datetime(2008, 5, 18, 15, 40)

        If none of known formats match try date_value_provider.

        >>> datetime_value_provider('2008/5/18', lambda x: x)
        datetime.datetime(2008, 5, 18, 0, 0)

        Empty string value is converted to ``None``.

        >>> datetime_value_provider(' ', lambda x: x)

        If none of known formats match raise ValueError.

        >>> datetime_value_provider('2.4.12', lambda x: x)
        Traceback (most recent call last):
            ...
        ValueError

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
