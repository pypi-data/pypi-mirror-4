
""" ``principal`` module.
"""


class Principal(object):
    """ Container of user specific security information
    """

    def __init__(self, id='', roles=(), alias='', extra=''):
        self.id = id
        self.roles = roles
        self.alias = alias
        self.extra = extra

    def dump(self):
        """
            >>> p = Principal()
            >>> s = p.dump()
            >>> assert 3 == len(s)
            >>> s
            '\\x1f\\x1f\\x1f'
            >>> p = Principal(id='79053',
            ...         roles=('a', 'b'),
            ...         alias='John',
            ...         extra='anything')
            >>> p.dump()
            '79053\\x1fa;b\\x1fJohn\\x1fanything'
        """
        return '\x1f'.join([
            self.id,
            ';'.join(self.roles),
            self.alias,
            self.extra])

    @classmethod
    def load(cls, s):
        """
            >>> p = Principal.load('\x1f\x1f\x1f')
            >>> assert p
            >>> p = Principal.load('79053\\x1fa;b\x1fJohn\\x1fanything')
            >>> p.id
            '79053'
            >>> p.roles
            ('a', 'b')
            >>> p.alias
            'John'
            >>> p.extra
            'anything'
        """
        id, roles, alias, extra = s.split('\x1f', 3)
        return cls(id, tuple(roles.split(';')), alias, extra)
