from anthrax.container import Container

PATTERN_EQUIVALENTS = [
    ('%d', 'dd'),
    ('%m', 'MM'),
    ('%Y', 'yyyy'),
]

def escape_to_single_quote(value):
    """Escapes the given string to be displayed in js single quotes.
    TODO: escaping all possible stuff."""
    return value.replace("'", r"\'")

def is_container(item):
    return isinstance(item, Container)

def render_requirements(requirements):
    return ', '.join(sorted(("'{0}'".format(req) for req in requirements)))

def render_spinner_constraints(field):
    result = []
    if field.min is not None:
        result.append('min: ' + str(field.min))
    if field.max is not None:
        result.append('max: ' + str(field.max))
    return ', '.join(result)

def render_textbox_constraints(field, form):
    result = []
    if field.regexp is not None:
        result.append("regExp: /{0}/".format(field.regexp))
        result.append("invalidMessage: '{0}'".format(
            escape_to_single_quote(field.regexp_message)
        ))
    if field.min_len is not None:
        result.append('minLen: ' + str(field.min_len))
        result.append("minLenMessage: '{0}'".format(
            escape_to_single_quote(field.min_len_message)
        ).format(
            min_len=field.min_len
        ))
    if field.max_len is not None:
        result.append('maxLen: ' + str(field.max_len))
        result.append("maxLenMessage: '{0}'".format(
            escape_to_single_quote(field.max_len_message)
        ).format(
            max_len=field.max_len
        ))
    error = form.__errors__[field.name]
    if error is not None:
        result.append("initialError: '{0}'".format(error.message))
    return ', '.join(result)

def _date_pattern2dojo(pattern):
    for py_symbol, dojo_symbol in PATTERN_EQUIVALENTS:
        pattern = pattern.replace(py_symbol, dojo_symbol)
    return pattern

def render_date_box_constraints(field):
    result = []
    result.append(
        "datePattern: '{0}'".format(_date_pattern2dojo(field.date_format))
    )
    return ', '.join(result)
