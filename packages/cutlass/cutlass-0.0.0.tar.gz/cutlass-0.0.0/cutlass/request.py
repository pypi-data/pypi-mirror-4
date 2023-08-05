"""Conveniences for working with HTTP request data.
"""

import logging
import inspect
from functools import update_wrapper

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
    from StringIO import StringIO
except ImportError:
    # pylint:disable-msg=W0404
    from io import StringIO
try:
    basestring
except NameError:
    basestring = str
try:
    callable
except NameError:
    callable = lambda f: hasattr(f, "__call__")


def _iteritems(iterable):
    """Get an items iterable in a portable way.

    Not really for external use
    """
    try:
        return iterable.iteritems()
    except AttributeError:
        return iterable.items()


def parse_form_data(environ, mem_limit=None):
    """Define the default way that request.py parses form data.

    Arguments:
        environ (or something which acts similar, like a request.Request)

    Returns:
        tuple of two MultiDicts: (form data, files data).
    """
    import multipart
    if not mem_limit and mem_limit != 0:
        return multipart.parse_form_data(environ)
    else:
        return multipart.parse_form_data(environ, mem_limit=mem_limit)


class Request(object):
    """Store and provide convenient access to CGI/WSGI environment data.
    """
    _key_translation = maketrans(b" -", b"__")

    def __init__(self, initial=None, max_body=(2**20)):
        """Initialize an allocated request object.

        :arg initial: a dict-like from which to source initial cache contents.
          if None, then the Request is blank.

        """
        # Set mutable attributes - done in a funky way to avoid recursion
        object.__setattr__(self, "_data", {})
        object.__setattr__(self, "_cache", {})
        object.__setattr__(self, "_cookies", None)
        object.__setattr__(self, "_query", None)
        object.__setattr__(self, "_routing_args", None)
        object.__setattr__(self, "_form", None)
        object.__setattr__(self, "_files", None)
        object.__setattr__(self, "_mem_limit", max_body)

        # "Protected" names are accessible with request.get() and request.set()
        # but NOT with attribute access, because the actual request object has
        # those attributes at import time, and it would be too confusing to
        # think you'd set one of those on the actual object when really you'd
        # just set a key in the cache.
        object.__setattr__(self, "_protected",
                set([item for item in dir(self)]))

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

    def _get_routing_args(self):
        routing_args = object.__getattribute__(self, "_routing_args")
        if routing_args:
            return routing_args
        args, kwargs = self.get('wsgiorg.routing_args', ([], {}))
        routing_args = kwargs.copy()
        if args:
            routing_args.update(dict((index, value)
                 for (index, value) in enumerate(args)))
        object.__setattr__(self, "_routing_args", routing_args)
        return routing_args

    routing_args = property(_get_routing_args)

    def _get_files(self):
        files = object.__getattribute__(self, "_files")
        if files is None:
            return self._get_form_data()[1]

    files = property(_get_files)

    def _get_form(self):
        form = object.__getattribute__(self, "_form")
        if form is None:
            return self._get_form_data()[0]

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
        return _iteritems(self.data)

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


def read_request_body(environ, max_length=None, log=False, stream=None):
    """Helper to get the HTTP request body from a stream (as for CGI/WSGI).

    This consumes the input. If you need the input again, you can use this and
    put its result into a StringIO to seek around.

    :returns:
        a string of the data that was read.
        If there was some error, None will be returned.
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
        return ""
    # If it's too big, return None instead of truncating or raising
    # This could be reported as HTTP/1.1 413; see RFC3875 9.6
    if max_length is not None and content_length > max_length:
        if log:
            logging.warning("CONTENT_LENGTH %d > max_length %d",
                content_length, max_length)
        return None
    else:
        # RFC 3875 4.2: must not read more than CONTENT_LENGTH.
        if log:
            logging.info("Reading %d bytes", content_length)
        return stream.read(content_length)


def expected_args(function):
    """Determine what arguments a function specifically "expects."
    """
    args, varargs, keywords, defaults = inspect.getargspec(function)
    optional = []
    if varargs:
        varargs = True
    if keywords:
        keywords = True
    if args:
        # Anything in defaults is not required.
        if defaults:
            required = args[:len(defaults) + 1]
            optional = args[-len(defaults):]
        else:
            required = args
        return required, optional, varargs, keywords, defaults
    else:
        required = []
        if not (varargs or keywords):
            return required, [], varargs, keywords, defaults
        return required, [], varargs, keywords, defaults


def gather_args(sources, env, pick_one=None, copy_body=True,
        max_body=(2**20)):
    """Look for names in a series of env-derived sources (supplier functions).

    Called inside other code to provide argument finding. Calls each function
    in via in sequence, asking it for the requested names. Values for names
    found earlier take precedence.

    :arg sources:
        mapping from variable names to sequences of functions which should be
        used to look for variables with those names.
    :arg env:
        environment to use to search (e.g. to extract query, form, etc. from)
    :arg pick_one:
      if False, only return mappings to lists of values.
      if True, only return mappings to single values.
      if None, let the supplier function use its own default.
        (of the default functions, only get_form returns lists of values by
        default).
    :arg copy_body:
        if False, allow the body stream (e.g. wsgi.input) to be consumed
        normally. if True, copy it in memory and put the copy back into env
        so that the same data can be read by downstream consumers of env.
    :arg max_body:
        Maximum body size to allow before generating an error. Set this to some
        number that is big enough for your app in order to protect against
        resources being exhausted by clients sending giant responses.
        Set it to None to disable the limit - at your own risk.
    :returns:
        a dict mapping found names to their values.
        If a name can be found in two or more sources, the value from the first
        source is kept and the rest ignored.
    """
    if copy_body:
        stream = StringIO(read_request_body(env, log=True,
            max_length=max_body))
        env['wsgi.input'] = stream

    # Batch all the variable names going into each function, so each function
    # can be called only once with a big batch. Much faster for non-trivial
    # supplier functions.
    batches = {}
    for name, functions in sources.items():
        for function in functions:
            this_list = batches.get(function)
            if not this_list:
                batches[function] = [name]
            else:
                this_list.append(name)

    # Do the batch searches - this could be parallelized
    results = {}
    for function, names in batches.items():
        result = function(set(names), env, pick_one=pick_one)
        if copy_body:
            stream.seek(0)
        if result:
            results[function] = result

    # For each name, decide which batch of results to draw from by using
    # the supplier ordering given in 'sources'
    gathered = {}
    for name, functions in sources.items():
        for function in functions:
            result = results.get(function)
            if result and name in result:
                gathered[name] = result[name]
                break
    return gathered


def from_env(keys, env, pick_one=None):
    """Supplier function to extract environment variables.

    (Usually CGI or WSGI variables, but extension stuff might also be stored in
    there)
    """
    if pick_one is None:
        pick_one = True
    if pick_one:
        return dict((k, v) for (k, v) in _iteritems(env) if k in keys)
    else:
        return dict((k, [v]) for (k, v) in _iteritems(env) if k in keys)


def from_query(keys, env, pick_one=None):
    """Supplier function to get parms from the query string.
    """
    if pick_one is None:
        pick_one = True
    query_string = env.get('QUERY_STRING')
    if query_string:
        query = parse_qs(query_string)
        if pick_one:
            return dict((k, query[k][0]) for k in keys)
        return dict((k, query[k]) for k in keys)
    return {}


def from_form(keys, env, pick_one=None):
    """Supplier to get parms from a body on wsgi.input (e.g. POST/PUT).

    If you are using this with any other supplier function that reads
    wsgi.input, you should really pass copy_body=True to gather_args or
    supply_args, or else the second supplier function will get an
    already-consumed file yielding no data.
    """
    if pick_one is None:
        pick_one = False
    content_type = env.get('CONTENT_TYPE')
    if not content_type:
        logging.error("no CONTENT_TYPE")
        return {}
    if content_type.startswith('application/x-www-form-urlencoded'):
        raw_data = read_request_body(env, log=True)
        if not raw_data:
            logging.error("no data in form")
            return {}
        form = parse_qs(raw_data, keep_blank_values=True)
    else:
        logging.error("unknown content type %s", content_type)
        return {}
    if pick_one:
        return dict((k, form[k][0]) for k in keys)
    return dict((k, form[k]) for k in keys)


def from_routing_args(keys, env, pick_one=None):
    """Get named parameters extracted during routing into wsgiorg.routing_args.
    """
    if pick_one is None:
        pick_one = True
    args_tuple = env.get('wsgiorg.routing_args')
    if not args_tuple:
        return {}
    args, kwargs = args_tuple
    if not pick_one:
        data = dict((k, [kwargs[k]]) for k in keys)
    else:
        data = dict((k, kwargs[k]) for k in keys)
    return data


def from_cookies(keys, env, pick_one=None):
    """Supplier to get parms from cookie values.
    """
    from cookies import Cookies
    if pick_one is None:
        pick_one = True
    cookie_data = env.get('HTTP_COOKIE', '')
    cs = Cookies.from_request(cookie_data, ignore_bad_cookies=True)
    cookies = [(key, cs.get(key)) for key in keys]
    tuples = [(key, cookie.value) for (key, cookie) in cookies if cookie]
    if pick_one:
        return dict((k, v) for (k, v) in tuples)
    else:
        return dict((k, [v]) for (k, v) in tuples)


class ArgumentsNotFoundError(Exception):
    """Raised when required argument(s) were not found.
    """
    pass


def supply_args(required=None, optional=None, pick_one=None, copy_body=True,
        max_body=(2**20)):
    """Decorate function to provide arguments by name from specified sources.

    Apply @supply_args(...) to a callable which takes a WSGI environ or similar
    object as a first parameter, and it will round up just the request
    variables you need from wherever you need them. This separates the
    specification of the handler gets variables from how it uses them.

    The required and optional parameters are both dicts, mapping variable names
    to one or more 'suppliers'. When the wrapped function is called, the
    suppliers are called to find their variables, which are then passed to the
    inner function. If a required variable is missing, an error is thrown, and
    if an optional one is missing then None is passed.

    The following defines a normal WSGI app using @supply_args(...); it
    requires x to be in the form and passes any value it finds for y in the
    query. supply_args provides x and y and just passes start_response as-is.

        @supply_args(required={'x': from_form}, optional={'y': from_query})
        def app(start_response, x, y=None):  # does this weird signature work?
            start_response("200 OK", [])
            return ["x={x}, y={y}".format(x=x, y=y)]

    You can easily write and use your own supplier functions to implement new
    ways of extracting bits of data from environ - check out from_env for the
    pattern.

    :arg required:
        A mapping of variable names to functions to look them up with. If
        a sequence of functions is supplied, each will be tried in order.
        If one is missing, an error will be raised.
    :arg optional:
        Another mapping like `required`, but provides a value of None instead
        of raising an error if it can't find a variable.
    :arg copy_body:
        If False, a supplier which reads the request body will consume it and
        the same data will not be readable to downstream suppliers.
        If True, the request body is copied in memory and put back inside env
        as a StringIO, so that downstream suppliers can use it.
    :arg max_body:
        Maximum body size to allow before generating an error. Set this to some
        number that is big enough for your app in order to protect against
        resources being exhausted by clients sending giant responses.
        Set it to None to disable the limit - at your own risk.
    :arg pick_one:
        If False, the supplied values will all be lists.
        If True, the supplied values will be individual items; in the event
        that there were multiple items, one is chosen arbitrarily (do not rely
        on it being any particular one).
        If None, each supplier will use its own default to decide whether to
        return a list or an item: for example, get_query defaults to an item,
        while from_form defaults to a list.
    """
    # Prebuild a dict for how to find things - required overrides optional.
    sources = {}
    if optional:
        sources.update(optional)
    else:
        optional = {}
    if required:
        logging.error("required %s", repr(required))
        sources.update(required)
    for key, value in sources.items():
        try:
            iter(value)
            sources[key] = value
        except TypeError:
            sources[key] = [value]

    def make_supply_args_wrapper(function):
        """Generate a wrapped version of a specific function.
        """
        assert callable(function), (
            "make_supply_args_wrapper got a non-callable. "
            "make sure you use @supply_args() and not just @supply_args"
        )
        # Prebuild the sets that will be used.
        # If nothing was specified, find out what the function wants
        if not sources:
            needed, wanted, _, keywords, _ = expected_args(
                getattr(function, "__wraps__", function))
            expected = needed + wanted
            needed_set, wanted_set = set(needed), set(wanted)
            del needed, wanted
        else:
            expected = None
            needed_set = set(required.keys())
            wanted_set = set(optional.keys())
        needed_or_wanted = needed_set | wanted_set

        def supply_args_wrapper(env, *args, **kwargs):
            """Find args for function in env, then call function.
            """
            # Delegate to gather_args to get what it can from env
            gathered = gather_args(sources, env, pick_one=pick_one,
                                   copy_body=copy_body, max_body=max_body)
            logging.error('gathered %s from sources %s env %s', gathered,
                          sources, env)
            # Override with passed args, possibly filling in more info
            gathered.update(kwargs)
            # If we still need something, see if ordered args can supply it
            # - only possible if we inspected the function, however
            still_wanted = (needed_or_wanted) - set(gathered.keys())
            if still_wanted and args and expected:
                result = dict(zip((expected)[:len(args)], args))
                if result:
                    gathered.update(result)
                    still_wanted -= set(result.keys())
                    args = args[len(result):]
            # We've exhausted our methods of getting variables,
            # so generate an error for any necessary thing we didn't find
            still_wanted = (needed_or_wanted) - set(gathered.keys())
            missing_keys = still_wanted & needed_set
            if missing_keys:
                raise ArgumentsNotFoundError(
                    ("Couldn't get required arguments for %s: " "%s" % \
                        (function.__name__, ", ".join(missing_keys))))

            # Anything passed in ** gets reordered by Python
            return function(*args, **gathered)

        update_wrapper(supply_args_wrapper, function)
        supply_args_wrapper.__wraps__ = function
        return supply_args_wrapper
    return make_supply_args_wrapper
