
""" ``authorization`` module.
"""

from wheezy.security.errors import SecurityError


def authorized(wrapped=None, roles=None):
    """ Demand the user accessing protected resource is
        authenticated and optionally in one of allowed ``roles``.

        Requires wrapped object to provide attribute principal.

        ``roles`` - a list of authorized roles.

        >>> from wheezy.security.principal import Principal
        >>> class Context(object):
        ...     principal = None
        ...
        ...     @authorized
        ...     def op_a(self):
        ...         return True
        ...
        ...     @authorized(roles=('operator',))
        ...     def op_b(self):
        ...         return True
        >>> c = Context()
        >>> c.op_a() # doctest: +ELLIPSIS +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
            ...
        SecurityError: ...
        >>> c.principal = Principal()
        >>> c.op_a()
        True
        >>> c.principal = None
        >>> c.op_b() # doctest: +ELLIPSIS +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
            ...
        SecurityError: ...
        >>> c.op_b() # doctest: +ELLIPSIS +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
            ...
        SecurityError: ...
        >>> c.principal = Principal(roles=('user',))
        >>> c.op_b() # doctest: +ELLIPSIS +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
            ...
        SecurityError: ...
        >>> c.principal = Principal(roles=('user', 'operator'))
        >>> c.op_b()
        True
    """
    def decorate(func):
        if roles:
            def check_roles(context, *args, **kwargs):
                principal = context.principal
                if principal:
                    principal_roles = principal.roles
                    for role in roles:
                        if role in principal_roles:
                            break
                    else:
                        raise SecurityError('Not authorized.')
                    return func(context, *args, **kwargs)
                else:
                    raise SecurityError('Not authorized.')
            return check_roles
        else:
            def check_authenticated(context, *args, **kwargs):
                if context.principal:
                    return func(context, *args, **kwargs)
                else:
                    raise SecurityError('Not authorized.')
            return check_authenticated
    if wrapped is None:
        return decorate
    else:
        return decorate(wrapped)
