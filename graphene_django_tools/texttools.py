"""Django grapehe model mutation"""

import re


def camel_case(text: str) -> str:
    """Convert text to camel case.

    Args:
        text (str)

    Returns:
        str
    """

    components = text.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


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
