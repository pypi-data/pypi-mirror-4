"""Test infrastructure for Cutlass.

This should shortly be split out into Shoring
"""
import re
import logging
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
try:
    callable = callable
except NameError:
    callable = lambda f: hasattr(f, "__call__")

_BYTESTRING = type(b'')
_NO_CTL_RE = re.compile("^[^\0-\x1f\x7f]*\Z")

def warn(message):
    logging.warning(message)


class Unset(object):
    "Unset is not None"
    pass


def check_exc_info(obj):
    if not type(obj) == tuple:
        yield "exc_info is not a tuple"
        return
    elif not len(obj) == 3:
        yield "exc_info does not have 3 values"


def no_control_characters(data):
    if _NO_CTL_RE.match(data):
        return True
    return False


def check_latin1(data):
    """Checked on arguments to start_response: status and response headers
    """
    # Also referenced as RFC 2616 encoding; text encoded per RFC 2047 is
    # encoded in a subset of latin-1, and few people will use it anyway.
    try:
        data.decode('ISO 8859-1').encode('ISO 8859-1')
    except UnicodeEncodeError:
        yield "could not be encoded as ISO 8859-1"
    except AttributeError:
        # implying it's already bytes
        pass


def check_bytestring(data):
    """Check that argument is a valid bytestring.
    """
    if not (type(data) == _BYTESTRING):
        yield ("%s should be bytestring, but is %s"
               % (repr(data), repr(type(data))))
        return


def check_native_string(data):
    """Check that argument is a valid native string.
    """
    if not (type(data) == str):
        yield "native string must be of type str"
        return
    for issue in check_latin1(data):
        yield "native string " + issue
    for char in data:
        if not (ord(char) >> 8) == 0:
            yield ("native string should not use more than 8 bits"
                   % repr(data))


def check_status(status):
    "Check status arg to start_response"
    for item in check_native_string(status):
        yield "status " + item
    if not status[3] == ' ':
        yield "status[3] was not a space"
        return
    if ' ' not in status:
        yield "status does not have a space"
    if not (status.strip() == status):
        yield "status surrounded by extra whitespace"
    if not (no_control_characters(status)):
        yield "status %s contains control characters" % repr(status)
    for item in check_latin1(status):
        yield ("status %s " % repr(status)) + item


def check_headers(headers):
    if not type(headers) == list:
        yield "headers is not a Python list"
    for header in headers:
        if not type(header) == tuple:
            yield ("headers header %s is not a Python tuple"
                   % repr(header))
        if not len(header) == 2:
            yield ("headers header %s has length != 2"
                   % repr(header))
            continue
        header_name, header_value = header
        for item in check_header_name(header_name):
            yield item
        for item in check_header_value(header_value):
            yield item


def check_header_name(name):
    if not no_control_characters(name):
        yield "header name contains control characters"
    for item in check_latin1(name):
        yield item


def check_header_value(value):
    if '\n' in value:
        yield "value contains newline"
    if '\r' in value:
        yield "value contains carriage return"
    if not no_control_characters(value):
        yield "value contains control characters"
    for item in check_latin1(value):
        yield item


def check_iterable(iterable):
    """Routine checks on an object returned from a call to a WSGI app object.
    """
    if not iterable:
        yield "WSGI iterable has to be something, at least ['']"
        return
    elif isinstance(iterable, str):
        yield ("WSGI iterable should not be a str - this will be sent out "
               " one character at a time, yielding terrible performance")
        return
    elif isinstance(iterable, bytes):
        yield ("WSGI iterable should not be a bytes - this will be sent out "
               " one character at a time, yielding terrible performance")
        return
    try:
        iter(iterable)
    except TypeError:
        yield "object should be a WSGI iterable, but is not iterable"
        return
    try:
        reported_length = len(iterable)
    except TypeError:
        return
    copy = [item for item in iterable]
    if not (reported_length == len(copy)):
        yield ("iterable reported length (%s) != "
               "number of items yielded (%s)"
               % (reported_length, len(copy)))
    for value in copy:
        for issue in check_iterable_value(value):
            yield issue
    for item in copy:
        if not type(item) is type(b''):
            yield ("item {0} is a {1} but should be a bytestring "
                   "(bytes in Python 3.x, str in earlier versions)").format(
                   repr(item), type(item))
        for issue in check_latin1(item):
            yield issue


def check_iterable_value(value):
    """Check one of the values returned by the iterable.
    """
    for issue in check_bytestring(value):
        yield issue


class LogIntercept(object):
    """Simple context manager to intercept whatever is logged.

    This is handy for testing what an app logs.
    """
    def __init__(self):
        self.stream = StringIO()
        self.handler = None

    def value(self):
        return self.stream.getvalue()

    def __enter__(self):
        self.handler = logging.StreamHandler(self.stream)
        root = logging.getLogger()
        root.addHandler(self.handler)
        return self

    def __exit__(self, typ=None, value=None, traceback=None):
        root = logging.getLogger()
        root.removeHandler(self.handler)
        self.handler.flush()
        self.stream.flush()


class Callable(object):
    """Mock callable which records and can check calls to itself.
    """
    def __init__(self, fail_immediately=False):
        """
        :arg fail_immediately:
            If True, a check will be done during each call to the instance, and
            the first issue (if any) will be raised as an AssertionError.
        """
        self.call_count = 0
        self.args = []
        self.kwargs = []
        self.fail_immediately = fail_immediately

    def __call__(self, *args, **kwargs):
        """When called, just store whatever was passed.
        """
        self.call_count += 1
        self.args.append(args)
        self.kwargs.append(kwargs)
        if self.fail_immediately:
            for issue in self.check_call(self.call_count - 1):
                raise AssertionError(issue)

    def check_call(self, index):
        """Check the nth call, yielding issues one at a time.

        IndexError will bubble up if there was no such call.
        """
        if (index + 1) > self.call_count:
            raise IndexError("was not called %d times" % (index + 1))

    def check_calls(self):
        """Check all the calls made, yielding all found issues.
        """
        for index in range(1, len(self.args)):
            for item in self.check_call(index):
                yield item

    def issues(self, index):
        """Return a list of all the issues from run n.

        This is for times when it seems gratuitous to have a 'for item in
        obj.check_call(n): yield item' construction, and you just want to pass
        all the issues for a given run.

        Normally there should be no need to override this.

        If this wasn't called (index) times, IndexError will bubble up.
        """
        if (index + 1) > self.call_count:
            raise IndexError("was not called %d times" % (index + 1))
        return [item for item in self.check_call(index)]

    def all_issues(self):
        """Return a list of all the issues in the call history.

        This is for times when it seems gratuitous to have a 'for item in
        obj.check_calls(): yield item' construction, and you just want to pass
        all the issues.

        Normally there should be no need to override this.
        """
        return [item for item in self.check_calls()]


class Write(Callable):
    """Generate dummy write() callables which record how they're used.

    Good for returning from a start_response() callable tailored for testing.
    """
    def __init__(self):
        Callable.__init__(self)
        self.iterating = False
        self.iterating_history = []

    def __call__(self, *args, **kwargs):
        Callable.__call__(self, *args, **kwargs)
        self.iterating_history.append(self.iterating)
        # Important: server must set self.iterating just before starting
        # to iterate, so that write can red-flag any calls during iteration.
        # this can also be done by the iterator wrapper if it gets access to
        # the Write instance.

    def check_call(self, index):
        """Check the nth call, yielding issues one at a time.

        IndexError will bubble up if there was no such call.
        """
        if (index + 1) > self.call_count:
            raise IndexError("was not called %d times" % (index + 1))

        args = self.args[index]
        kwargs = self.kwargs[index]
        if self.iterating_history[index] != False:
            yield "write() called after iteration started"
        if len(args) < 1 or len(args) > 1:
            yield "write callable must take one positional parameter."
        elif len(args) == 1:
            body_data = args[0]
            if not type(body_data) == type(b''):
                yield "write argument should be bytestring"
        if len(kwargs) != 0:
            warn("write callable probably shouldn't take keyword parameters.")
        if index > 0:
            warn("write() should generally not be used")


class StartResponse(Callable):
    """Generate dummy start_response callables for checking whether WSGI apps
    use start_response() and its returned write() appropriately.
    """
    def __init__(self, call_count=0):
        Callable.__init__(self)
        self.call_count = call_count
        self.write = Write()
        self.status = []
        self.headers = []
        self.exc_info = []

    def __call__(self, *args, **kwargs):
        Callable.__call__(self, *args, **kwargs)
        status = args[0] if len(args) >= 1 else Unset
        headers = args[1] if len(args) >= 2 else Unset
        exc_info = args[2] if len(args) >= 3 else Unset
        self.status.append(status)
        self.headers.append(headers)
        self.exc_info.append(exc_info)
        return self.write

    def check_call(self, index):
        """Check if a particular past call was WSGI-compliant.
        """
        Callable.check_call(self, index)

        args = self.args[index]
        kwargs = self.kwargs[index]

        # check overall number of calls as of indexed point in time -
        # start_response should usually be called once, perhaps twice
        if not (index > 0):
            yield "start_response() must be called by app at least once"
        elif not (index <= 2):
            yield "start_response() must be called by app at most twice"

        if len(kwargs) > 0:
            yield ("start_response() was called using %d keyword argument(s)"
                   " (should only use positional arguments)"
                   % len(kwargs))

        if len(args) < 2:
            yield ("start_response() requires at least two positional "
                   "arguments (status, headers)")
        elif len(args) > 3:
            yield ("start_response() accepts at most three positional "
                   "arguments (status, headers, "
                   "and an optional exc_info argument).")
        # Don't bother checking the arg types unless the signature looks OK,
        # to avoid giving spurious advice when the misunderstanding is basic
        else:
            status, headers = args[0], args[1]
            if len(args) > 2:
                exc_info = args[2]
            else:
                exc_info = kwargs.get('exc_info', Unset)
            if index >= 2:
                if exc_info is Unset:
                    yield "start_response was called again without exc_info"
                elif not exc_info:
                    yield ("start_response was called again with exc_info "
                           "evaluating to False")
            for item in check_status(status):
                yield item
            for item in check_headers(headers):
                yield item
            if exc_info is not Unset:
                for item in check_exc_info(exc_info):
                    yield item
