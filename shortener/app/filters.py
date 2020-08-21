from flask import current_app


UNITS = ['', 'K', 'M', 'B']


@current_app.template_filter()
def humanize_number(string: str) -> str:
    """Convert a standard integer into a human readable value.

    Args:
        string (str): the string that requires the filter.

    Returns:
        str: a formatted string, or the original if there was an error.
    """
    try:
        string_as_float = float(string)
        for unit in UNITS[:-1]:
            if abs(string_as_float) < 1000.0:
                return "%3.0f%s" % (string_as_float, unit)
            string_as_float /= 1000.0
        return "%.0f%s" % (string_as_float, UNITS[-1])
    except Exception as exception:
        current_app.logger.warning('Error converting string: ' + exception)
        return string
