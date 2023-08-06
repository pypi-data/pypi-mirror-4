import re
from collections import namedtuple, deque

# This module based on rfc3986.


# Validation errors.

class InvalidScheme(ValueError): pass
class InvalidAuthority(ValueError): pass
class InvalidUserinfo(InvalidAuthority): pass
class InvalidHost(InvalidAuthority): pass
class InvalidPath(ValueError): pass
class InvalidQuery(ValueError): pass


URLTuple = namedtuple('URLBase', 'scheme host path query fragment '
                                 'userinfo port')


class URL(URLTuple):
    """
    Class for manipulation with escaped parts of url.
    It can parse any url from string or can be constructed with provided parts.
    If source of url not trusted, method validate() can be used to check url.
    """
    __slots__ = ()

    # This is not validating regexp.
    # It splits url to unambiguous parts according RFC.
    _split_re = re.compile(r'''
        (?:([^:/?#]+):)?            # scheme
        (?://                       # authority
            (?:([^/?\#@]*)@)?       # userinfo
            ([^/?\#]*)()            # host:port
        )?
        ([^?\#]*)                   # path
        \??([^\#]*)                 # query
        \#?(.*)                     # fragment
        ''', re.VERBOSE | re.DOTALL).match

    def __new__(cls, url=None, scheme='', host='', path='', query='',
                fragment='', userinfo='', port=''):
        if url is not None:
            # All other arguments are ignored.
            (scheme, userinfo, host, port,
             path, query, fragment) = cls._split_re(url).groups('')

            # Host itself can contain digits and ':', so we cant use regexp.
            # It is bit different from other behaviors: instead of splitting
            # as is, and raise on validate, we split port only with digits.
            # I believe this is expected behavior.
            _port_idx = host.rfind(':')
            if _port_idx >= 0:
                _port = host[_port_idx + 1:]
                if not _port or _port.isdigit():
                    host, port = host[:_port_idx], _port

        # | Although schemes are case-insensitive, the canonical form
        # | is lowercase. An implementation should only produce lowercase
        # | scheme names for consistency.
        scheme = scheme.lower()

        # | Although host is case-insensitive, producers and normalizers
        # | should use lowercase for registered names and hexadecimal
        # | addresses for the sake of uniformity.
        # TODO: while only using uppercase letters for percent-encodings
        host = host.lower()

        return tuple.__new__(cls, (scheme, host, path, query, fragment,
                                   userinfo, str(port)))

    ### Serialization

    def __unicode__(self):
        base = self.authority
        path = self.path

        if base:
            base = '//' + base

            # Url with authority can not be relative.
            if path and path[0] != '/':
                base += '/'

        # Escape paths with slashes by adding explicit empty host.
        elif path[0:2] == '//':
            base = '//'

        if self.scheme:
            base = self.scheme + ':' + base

        # if url starts with path
        elif not base and ':' in path.partition('/')[0]:
            base = './'

        return base + self.full_path

    as_string = __unicode__

    def __reduce__(self):
        return type(self), (None,) + tuple(self)

    ### Missing properties

    @property
    def authority(self):
        authority = self.host
        userinfo, port = self[5:7]
        if port:
            authority += ':' + port
        if userinfo:
            return userinfo + '@' + authority
        return authority

    @property
    def full_path(self):
        path, query, fragment = self[2:5]
        if query:
            path += '?' + query
        if fragment:
            path += '#' + fragment
        return path

    ### Information

    def __nonzero__(self):
        return any(self)

    def has_authoruty(self):
        return bool(self.host or self.userinfo or self.port)

    def is_relative(self):
        # In terms of rfc relative url have no scheme.
        # See is_relative_path().
        return not self.scheme

    def is_relative_path(self):
        # Absolute path always starts with slash. Also paths with authority
        # can not be relative.
        return not self.path.startswith('/') and not (
            self.scheme or self.has_authoruty())

    def is_host_ipv4(self):
        if not self.host.startswith('['):
            parts = self.host.split('.')
            if len(parts) == 4 and all(part.isdigit() for part in parts):
                if all(int(part, 10) < 256 for part in parts):
                    return True
        return False

    def is_host_ip(self):
        if self.is_host_ipv4():
            return True

        if self.host.startswith('[') and self.host.endswith(']'):
            return True

        return False

    ### Validation

    _valid_scheme_re = re.compile(r'^[a-z][a-z0-9+\-.]*$').match
    # '[' and ']' the only chars not allowed in userinfo and not delimiters
    _valid_userinfo_re = re.compile(r'^[^/?\#@\[\]]+$').match
    _valid_reg_name_re = re.compile(r'^[^/?\#@\[\]:]+$').match
    _valid_path_re = re.compile(r'^[^?\#]+$').match
    _valid_query_re = re.compile(r'^[^\#]+$').match
    # This primitive regular expression not match complicated ip literal.
    _valid_ip_literal_re = re.compile(r'''
        ^(?:
            v[a-f0-9]+\.[a-z0-9\-._~!$&'()*,;=:]+
            |
            [a-f0-9:\.]+
        )$
        ''', re.VERBOSE | re.IGNORECASE).match

    def validate(self):
        if self.scheme:
            if not self._valid_scheme_re(self.scheme):
                raise InvalidScheme()

        if self.userinfo:
            if not self._valid_userinfo_re(self.userinfo):
                raise InvalidUserinfo()

        if self.host:
            host = self.host
            if host.startswith('[') and host.endswith(']'):
                if not self._valid_ip_literal_re(host[1:-1]):
                    raise InvalidHost()

            # valid ipv4 is also valid reg_name
            elif not self._valid_reg_name_re(host):
                raise InvalidHost()

        # Acording rfc there is two cases when path can be invalid:
        # There should be no scheme and authority and first segment of path
        # should contain ':' or starts with '//'. But this library not about
        # punish user. We can escape this paths when formatting string.
        if self.path:
            if not self._valid_path_re(self.path):
                raise InvalidPath()

        if self.query:
            if not self._valid_query_re(self.query):
                raise InvalidQuery()

        return self

    ### Manipulation

    def __add__(self, other):
        # This method designed with one issue. By rfc delimeters without
        # following values are matter. For example:
        # 'http://ya.ru/page' + '//?none' = 'http:'
        # 'http://ya.ru/page?param' + '?' = 'http://ya.ru/page'
        # But the parser makes no distinction between empty and undefined part.
        # 'http://ya.ru/page' + '//?none' = 'http://ya.ru/page?none'
        # 'http://ya.ru/page?param' + '?' = 'http://ya.ru/page?param'
        # Same bug also present in urllib.parse.urljoin.
        # I hope it will be fixed in future yurls.
        # TODO: call remove_dot_segments() when path not modified.

        if not isinstance(other, URLTuple):
            try:
                other = URL(other)  # try string
            except TypeError:
                raise NotImplementedError()

        if not other:
            return self

        if other.scheme or not self:
            return other

        if other.has_authoruty():
            return tuple.__new__(type(self), (self.scheme,) + other[1:])

        if other.path:
            if other.path[0] == '/':
                path = other.path
            else:
                path = self.path.rpartition('/')
                path = path[0] + path[1] + other.path
            query = other.query
        else:
            path = self.path
            query = other.query or self.query

        return tuple.__new__(type(self), (self.scheme, self.host,
                                          self.remove_dot_segments(path),
                                          query, other.fragment,
                                          self.userinfo, self.port))

    def __radd__(self, left):
        # if other is instance of URL(), __radd__() should not be called.
        if type(left) == URLTuple:
            return URL.__add__(left, self)

        try:
            left = URL(left)  # try string
        except TypeError:
            raise NotImplementedError()

        # We can't call own constructor, but we need own instance.
        left.__class__ = type(self)
        return left.__add__(self)

    def replace(self, scheme=None, host=None, path=None, query=None,
                fragment=None, userinfo=None, port=None, authority=None,
                full_path=None):
        if authority is not None:
            if host or userinfo or port:
                raise TypeError()

            # Use original URL just for parse.
            _, host, _, _, _, userinfo, port = URL('//' + authority)

        if full_path is not None:
            if path or query or fragment:
                raise TypeError()

            # Use original URL just for parse.
            path, query, fragment = URL(full_path)[2:5]

        return tuple.__new__(type(self), (
            self.scheme if scheme is None else scheme.lower(),
            self.host if host is None else host.lower(),
            self.path if path is None else path,
            self.query if query is None else query,
            self.fragment if fragment is None else fragment,
            self.userinfo if userinfo is None else userinfo,
            self.port if port is None else str(port),
        ))

    def replace_from(self, other):
        if not isinstance(other, URLTuple):
            other = URL(other)

        return tuple.__new__(type(self), (
            other.scheme or self.scheme,
            other.host or self.host,
            other.path or self.path,
            other.query or self.query,
            other.fragment or self.fragment,
            other.userinfo or self.userinfo,
            other.port or self.port,
        ))

    def setdefault(self, scheme='', host='', path='', query='', fragment='',
                   userinfo='', port=''):
        return tuple.__new__(type(self), (
            self.scheme or scheme.lower(),
            self.host or host.lower(),
            self.path or path,
            self.query or query,
            self.fragment or fragment,
            self.userinfo or userinfo,
            self.port or str(port),
        ))

    ### Utils

    @classmethod
    def remove_dot_segments(cls, path):
        stack = deque()
        last = 0
        for segment in path.split('/'):
            if segment == '.':
                pass
            elif segment == '..':
                if len(stack):
                    stack.pop()
            else:
                stack.append(segment)
        if path.endswith(('/.', '/..')):
            stack.append('')
        return '/'.join(stack)

    ### Python 2 to 3 compatibility

    import sys
    if sys.version_info > (3, 0):
        # Rename __unicode__ function to __str__ in python 3.
        __str__ = __unicode__
        del __unicode__
        # Rename __nonzero__ function to __bool__ in python 3.
        __bool__ = __nonzero__
        del __nonzero__
    else:
        # Convert unicode to bytes in python 2.
        __str__ = lambda self: self.__unicode__().encode('utf-8')
    del sys


class CachedURL(URL):
    __slots__ = ()
    _cache = {}
    _cache_size = 20

    def __new__(cls, url=None, *args, **kwargs):
        # Cache only when parsing.
        if url is None:
            return URL.__new__(cls, None, *args, **kwargs)

        self = cls._cache.get(url)

        if self is None:
            if len(cls._cache) >= cls._cache_size:
                cls._cache.clear()

            # Construct and store.
            self = URL.__new__(cls, url)
            cls._cache[url] = self

        return self
