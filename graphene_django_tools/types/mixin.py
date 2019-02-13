"""Mixins for django object types.  """

from .. import core


class CustomConnectionResolveMixin:
    """Print traceback when encountered a error"""

    @classmethod
    def connection_resolver(cls, *args, **kwargs):
        """Resolve connection.  """
        try:
            return super().connection_resolver(*args, **kwargs)
        except:
            core.handle_resolve_error()
            raise
