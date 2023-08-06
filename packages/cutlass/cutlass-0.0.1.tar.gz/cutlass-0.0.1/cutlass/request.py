"""Conveniences for working with HTTP request data.
"""

import logging
try:
    from string import maketrans
except ImportError:
    maketrans = bytes.maketrans
try:
    from urlparse import parse_qs
except ImportError:
    # pylint:disable-msg=E0611,F0401
    from urllib.parse import parse_qs
try:
    basestring
except NameError:
    basestring = str
try:
    callable
except NameError:
    callable = lambda f: hasattr(f, "__call__")


def read_request_body(environ, max_length=None, log=False, stream=None):
    """Helper to get the HTTP request body from a stream (as for CGI/WSGI).

    This consumes the input and caches it all in memory. If you need the
    input again, you can use this and put its result into a BytesIO to
    seek around. If you call this yourself, pass max_length to make sure
    this doesn't use some crazy amount of memory.

    :arg environ:
        environ dict containing request data.
    :arg max_length:
        If present, not more than this many bytes of the request body
        will be read. If there are too many bytes for the limit, None is
        returned.
    :arg stream:
        If present, this should be a stream to read from instead of
        wsgi.input. Metadata from environ, like CONTENT_LENGTH, is still
        used.
    :returns:
        bytes of the data that was read, or  None. If there was no data
        to read (zero or unset CONTENT_LENGTH) then b'' will be
        returned. If there was some error, None will be returned.
    """
    if stream is None:
        stream = environ.get('wsgi.input', None)
        if stream is None or stream.closed:
            if log:
                logging.warning("failed read to None/closed stream: %s",
                                stream)
            return None
    # per RFC 3875 4.1.3, CONTENT_TYPE may be empty or absent;
    # however, guessing is awful and this is a problem
    content_type = environ.get("CONTENT_TYPE", None)
    if content_type is None:
        if log:
            logging.warning("no CONTENT_TYPE set")
        return None
    content_length = environ.get('CONTENT_LENGTH', 0)
    if content_length:
        # If it doesn't parse, return None instead of raising
        try:
            content_length = int(content_length)
        except ValueError:
            if log:
                logging.warning("could not parse CONTENT_LENGTH")
            return None
    if not content_length:
        if log:
            logging.debug("no CONTENT_LENGTH: %s", content_length)
        return b""
    # If it's too big, return None instead of truncating or raising
    # This could be reported as HTTP/1.1 413; see RFC3875 9.6
    if max_length is not None and content_length > max_length:
        if log:
            logging.warning("CONTENT_LENGTH %d > max_length %d",
                content_length, max_length)
        return None
    # RFC 3875 4.2: must not read more than CONTENT_LENGTH.
    if log:
        logging.info("Reading %d bytes", content_length)
    # reading more than content_length may cause us to block.
    data = stream.read(content_length)
    return data


def parse_form_data(environ, mem_limit=None):
    """Define the default way that request.py parses form data.

    Arguments:
        environ (or something which acts similar, like a request.Request)

    Returns:
        tuple of two MultiDicts: (form data, files data).
    """
    from . import multipart
    if not mem_limit and mem_limit != 0:
        return multipart.parse_form_data(environ)
    else:
        return multipart.parse_form_data(environ, mem_limit=mem_limit)


class Request(object):
    """Store and provide convenient access to CGI/WSGI environment data.
    """
    _key_translation = maketrans(b" -", b"__")

    def __init__(self, initial=None, max_body=(2 ** 20)):
        """Initialize an allocated request object.

        :arg initial: a dict-like from which to source initial cache contents.
          if None, then the Request is blank.

        """
        # Set mutable attributes - done in a funky way to avoid recursion
        object.__setattr__(self, "_data", {})
        object.__setattr__(self, "_cache", {})
        object.__setattr__(self, "_cookies", None)
        object.__setattr__(self, "_query", None)
        object.__setattr__(self, "_route_args", None)
        object.__setattr__(self, "_route_kwargs", None)
        object.__setattr__(self, "_body", None)
        object.__setattr__(self, "_form", None)
        object.__setattr__(self, "_files", None)
        object.__setattr__(self, "_mem_limit", max_body)

        # "Protected" names are accessible with request.get() and request.set()
        # but NOT with attribute access, because the actual request object has
        # those attributes at import time, and it would be too confusing to
        # think you'd set one of those on the actual object when really you'd
        # just set a key in the cache.
        protected = set([item for item in dir(self)])
        object.__setattr__(self, "_protected", protected)

        # Populate the data dict - from arg or environment. This is the state
        # which .reset() will roll back to.
        my_data = object.__getattribute__(self, "_data")
        if initial is None:
            pass
        elif isinstance(initial, Request):
            # Directly transfer representation, bypassing self.update
            his_data = object.__getattribute__(initial, "_data")
            his_cache = object.__getattribute__(initial, "_cache")
            my_data.update(his_data)
            my_data.update(his_cache)
        else:
            self.update(initial)
            my_data.update(self._cache)
            self.reset()

    def update(self, dictionary):
        """Update cache with contents of a dictionary.
        """
        # First detect if some of the new stuff should not be written to
        forbidden = set(dictionary.keys()) \
                & object.__getattribute__(self, "_protected")
        if len(forbidden):
            raise ProtectedError(forbidden)

        # Unfortunately we have to translate each name, since the source
        # dictionary might not normalize as we need to do internally
        cache = object.__getattribute__(self, "_cache")
        for key, value in dictionary.items():
            new_key = self._translate_name(key)
            cache[new_key] = value

    def reset(self):
        """Wipe the mutable cache to restore initial state."""
        object.__setattr__(self, "_cache", {})

    def __contains__(self, key):
        """Provides syntax: 'keyname' in request"""
        # Otherwise, search cache before searching data.
        if key in object.__getattribute__(self, "_protected"):
            return False
        if key in object.__getattribute__(self, "_cache"):
            return True
        if key in object.__getattribute__(self, "_data"):
            return True
        return False

    def has_key(self, key):
        "Legacy method for emulating dict."
        return (key in self)

    def peek(self, key, default=None, raise_keyerror=False):
        """Get a value from the original immutable state.

        :arg default:
            value to return if key is not found.
        :arg raise_keyerror:
            if True, then throw an exception when there was no
            value. Otherwise, default for missing keys.
        """
        key = self._translate_name(key)
        data = self.__getattribute__("_data")
        if key in data:
            return data[key]
        elif raise_keyerror:
            raise KeyError(key)
        return default

    def get(self, key, default=None, raise_keyerror=False):
        """Get an arbitrary stored value.

        :arg default:
            value to return if key is not found.
        :arg raise_keyerror:
            if True, then throw an exception when there was no
            value. Otherwise, return default for missing keys.
        :returns:
            The value defined for the given key.
        """
        key = self._translate_name(key)
        data = self.__getattribute__("_data")
        cache = self.__getattribute__("_cache")
        if key in cache:
            value = cache[key]
        elif key in data:
            value = data[key]
        else:
            if raise_keyerror:
                raise KeyError(key)
            value = default
        return value

    def set(self, key, value):
        """Set a single value in the mutable cache.
        """
        key = self._translate_name(key)
        cache = self.__getattribute__("_cache")
        cache[key] = value

    def __getattr__(self, key):
        key = self._translate_name(key)
        # Raise error when they try to read an attribute like __getattr__;
        # they should not think they are getting the object's attribute when
        # they are actually getting something out of the cache!
        protected = object.__getattribute__(self, "_protected")
        if key in protected:
            raise ProtectedError([key])
        return self.get(key)

    def __setattr__(self, key, value):
        """Intercept attribute sets and store them in the cache instead.

           This method should prevent ANY import-time attribute on the request
           object from being set by downstream consumers. This is intentional,
           as it prevents members and parts of the interface from being somehow
           clobbered inadvertently by users who prefer attribute access.

           In addition, this raises an error if there is an attempt to change
           an import-time member, because the result of that would only be to
           change something in the cache, which would not have the expected
           result: e.g., "request.__setattr__ = 3" would only update the cache.
        """
        key = self._translate_name(key)
        if key in object.__getattribute__(self, "_protected"):
            raise ProtectedError([key])
        self.set(key, value)

    def __getitem__(self, key):
        """Provides syntax: request['keyname'].
        """
        return self.get(key)

    def __setitem__(self, key, value):
        """Provides syntax: request['keyname'] = value

        This imitates a dict and allows names to be set which can't be
        referenced through attribute access.
        """
        return self.set(key, value)

    def setdefault(self, key, default=None):
        """Get a value and set it to a default iff it is not already set.
        """
        if key not in self:
            self.set(key, default)
        return self.get(key)

    @classmethod
    def _translate_name(cls, key):
        """Generate a normalized key name for a value stored on the request.

        This lets spaces and cases be used without making life difficult.
        """
        if not issubclass(type(key), basestring):
            return key
        # n.b.: this could be implemented much more efficiently
        key = key.lower()
        key = key.translate(Request._key_translation)
        return key

    def _get_data(self):
        """Get a 'copy' of current mutable state.

        Generated lazily because this isn't a typical use.
        """
        data = object.__getattribute__(self, "_cache")
        cache = object.__getattribute__(self, "_data")
        copy = data.copy()
        copy.update(cache)
        return copy

    def _set_data(self, new_data):
        """Replace current mutable state.
        """
        # Clear cache.
        self.reset()
        # Add in the stuff from new_data to the cache, as an 'overlay' on
        # initial data.
        self.update(new_data)

    data = property(_get_data, _set_data)

    def _get_cookies(self):
        "Parse HTTP_COOKIE into a cookies.Cookies() at first demand"
        from . cookies import Cookies
        my_cookies = object.__getattribute__(self, "_cookies")
        if my_cookies:
            return my_cookies
        cookie_header = self.get("HTTP_COOKIE", None)
        if cookie_header:
            my_cookies = Cookies.from_request(cookie_header)
        else:
            my_cookies = Cookies()
        object.__setattr__(self, "_cookies", my_cookies)
        return my_cookies

    cookies = property(_get_cookies)

    def _get_query(self):
        "Parse QUERY_STRING into dict at first demand"
        my_query = object.__getattribute__(self, "_query")
        if my_query:
            return my_query
        data = self.get("QUERY_STRING", None)
        my_query = parse_qs(data, keep_blank_values=True) if data else {}
        object.__setattr__(self, "_query", my_query)
        return my_query

    query = property(_get_query)

    def _get_route_args(self):
        "Caching descriptor logic for route_args"
        args = object.__getattribute__(self, "_route_args")
        if args:
            return args
        args, kwargs = self.get('wsgiorg.routing_args', ([], {}))
        object.__setattr__(self, "_route_args", args)
        object.__setattr__(self, "_route_kwargs", kwargs)
        return args

    route_args = property(_get_route_args)

    def _get_route_kwargs(self):
        "Caching descriptor logic for route_kwargs"
        kwargs = object.__getattribute__(self, "_route_kwargs")
        if kwargs:
            return kwargs
        args, kwargs = self.get('wsgiorg.routing_args', ([], {}))
        object.__setattr__(self, "_route_args", args)
        object.__setattr__(self, "_route_kwargs", kwargs)
        return kwargs

    route_kwargs = property(_get_route_kwargs)

    def _get_body(self):
        "Caching descriptor logic for body"
        body = object.__getattribute__(self, "_body")
        if body is not None:
            return body
        body = read_request_body(self)
        object.__setattr__(self, "_body", body)
        return body

    body = property(_get_body)

    def _get_files(self):
        "Caching descriptor logic for files"
        files = object.__getattribute__(self, "_files")
        if files is None:
            return self._get_form_data()[1]
        return files

    files = property(_get_files)

    def _get_form(self):
        "Caching descriptor logic for form"
        form = object.__getattribute__(self, "_form")
        if form is None:
            return self._get_form_data()[0]
        return form

    form = property(_get_form)

    def parse_form_data(self):
        """Stub for subclasses to use different form data parsers.

        Other implementations should pass _mem_limit in order to limit
        request body sizes.
        """
        return parse_form_data(self,
                mem_limit=object.__getattribute__(self, "_mem_limit"))

    def _get_form_data(self):
        "Private helper to read in and cache form data."
        form, files = self.parse_form_data()
        object.__setattr__(self, "_form", form)
        object.__setattr__(self, "_files", files)
        return form, files

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return self.data.__iter__()

    def iteritems(self):
        try:
            return self.data.iteritems()
        except AttributeError:
            return self.data.items()

    def iterkeys(self):
        return self.data.iterkeys()

    def itervalues(self):
        return self.data.itervalues()

    def keys(self):
        return self.data.keys()

    def items(self):
        return self.data.items()

    def values(self):
        return self.data.values()

    def copy(self):
        return self.data.copy()

    @classmethod
    def fromkeys(cls, keys, value=None):
        return dict.fromkeys(keys, value)


class ProtectedError(Exception):
    """Raised when there is an attempt to access a protected attribute on
    a Request.

    Request intercepts attribute gets and sets to any name; most of the time,
    this should not cause any problem and makes it convenient as a bag of
    values concerning the request. (No need to write methods for every possible
    variable, and no need to write out ``['']`` at every access.) However, it
    introduces a corner case where setting a key which shares a name with
    a member (e.g., __init__) would (desirably) fail as the value was written
    to the cache instead of the object attribute (__dict__); the problem is
    that this failure would be silent and only discovered later, if at all, due
    to some surprise. To prevent this, members present at initialization are
    internally marked as "protected," and this error breaks program flow
    whenever a protected attribute is accessed, to let the user know that they
    should not expect to overwrite (say) a request's __init__ at runtime.
    """
    def __init__(self, attributes=None):
        """
        """
        Exception.__init__(self)
        if attributes is None:
            self.attributes = set([])
        else:
            self.attributes = set(attributes)

    def __str__(self):
        attributes = sorted(self.attributes)
        return "Can't access: " + ", ".join([str(item) for item in attributes])
