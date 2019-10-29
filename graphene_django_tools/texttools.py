"""Django graphene model mutation"""

import re


def camel_case(text: str, is_lower=False) -> str:
    """Convert text to camel case.

    Args:
        text (str)

    Returns:
        str
    """

    ret = ''.join(x[0].title() + x[1:] for x in text.split('_'))
    if is_lower:
        ret = ret[0].lower() + ret[1:]
    return ret


def snake_case(text: str) -> str:
    """Convert text to snake case.

    Args:
        text (str)

    Returns:
        str
    """

    ret = text
    ret = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', ret)
    ret = re.sub('([a-z0-9])([A-Z])', r'\1_\2', ret)
    ret = ret.lower()
    return ret
