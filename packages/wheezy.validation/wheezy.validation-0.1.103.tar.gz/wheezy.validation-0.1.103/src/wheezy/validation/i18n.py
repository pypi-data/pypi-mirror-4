
""" ``i18n`` module.
"""

# thousands separator
thousands_separator = lambda gettext: gettext(',')
# decimal point separator
decimal_separator = lambda gettext: gettext('.')
# default date input format: 2008/5/18.
default_date_input_format = lambda gettext: gettext('%Y/%m/%d')
# fallback date input formats: 5/18/2008. Use | to separate multiple values.
fallback_date_input_formats = lambda gettext: gettext(
    '%m/%d/%Y|%Y-%m-%d|%m/%d/%y')
# default time input format: 16:34.
default_time_input_format = lambda gettext: gettext('%H:%M')
# fallback time input formats: 16:34:52. Use | to separate multiple values.
fallback_time_input_formats = lambda gettext: gettext('%H:%M:%S')
# default datetime input format: 2008/5/18 16:34
default_datetime_input_format = lambda gettext: gettext('%Y/%m/%d %H:%M')
# fallback datetime input formats: 2008/5/18 16:34:52. Use | to separate.
fallback_datetime_input_formats = lambda gettext: gettext(
    '%Y/%m/%d %H:%M:%S|%m/%d/%Y %H:%M|%m/%d/%Y %H:%M:%S|'
    '%Y-%m-%d %H:%M|%Y-%m-%d %H:%M:%S|%m/%d/%y %H:%M|%m/%d/%y %H:%M:%S')
