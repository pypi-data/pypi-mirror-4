"""Helpers for making HTTP responses with little boilerplate.
"""

import re
import logging
from wsgiref.headers import Headers

try:
    basestring
except:
    basestring = str  # pylint: disable-msg=W0622

# Don't change these here. Use constructors/attributes on the relevant objects.
DEFAULT_MIME_TYPE = "text/html"
DEFAULT_CHARSET = "utf-8"
DEFAULT_HTTP_VERSION = "1.1"


class UnknownHTTPVersion(object):
    def __init__(self, version):
        self.version = version

HTTP_STATUS_CLASSES = {
  "1": "Informational",
  "2": "Success",
  "3": "Redirection",
  "4": "Client Error",
  "5": "Server Error",
}

# HTTP 1.0: http://www.w3.org/Protocols/HTTP/1.0/spec.html#Status-Codes
HTTP10_STATUS_CODES = {
  200: ("OK",
   "The request has succeeded."),

  201: ("Created",
   "The request has been fulfilled and resulted in a new resource being "
   "created."),

  202: ("Accepted",
   "The request has been accepted for processing, but the processing has not "
   "been completed."),

  # "The server has fulfilled the request but does not need to return an
  # entity-body, and might want to return updated metainformation. ")
  204: ("No Content",
   "The server has fulfilled the request but there is no new information to "
   "send back."),

 #300: ("Multiple Choices", " The requested resource is available at one "
 #                          "or more locations."),

  301: ("Moved Permanently",
   "The requested resource has been assigned a new permanent URL and any "
   "future references to this resource should be done at the new URL."),

  302: ("Moved Temporarily",
   "The requested resource resides temporarily under a different URL."),

  304: ("Not Modified",
   "The client has performed a conditional GET request and access is allowed, "
   "but the document has not been modified."),

  400: ("Bad Request",
   "The request could not be understood by the server due to malformed "
   "syntax."),

  401: ("Unauthorized",
   "The request requires user authentication."),

  403: ("Forbidden",
   "The server understood the request, but is refusing to fulfill it."),

  404: ("Not Found",
   "The server has not found anything matching the Request-URI."),

  500: ("Internal Server Error",
   "The server encountered an unexpected condition which prevented it "
   "from fulfilling the request."),

  501: ("Not Implemented",
   "The server does not support the functionality required to fulfill the "
   "request."),

  502: ("Bad Gateway",
   "The server, while acting as a gateway or proxy, received an invalid "
   "response from the upstream server it accessed in attempt"),

  503: ("Service Unavailable",
   "The server is currently unable to handle the request due to a "
   "temporary overloading or maintenance of the server. "),
}
HTTP10_STATUS_CODES_SET = set(HTTP10_STATUS_CODES.keys())

# HTTP 1.1, see RFC 2616 sec10, sec6
# this appears to include all the codes from HTTP1.0, so those are commented
# out to reduce overlap.
HTTP11_STATUS_CODES = HTTP10_STATUS_CODES.copy()
HTTP11_STATUS_CODES.update({
  100: ("Continue",
   "The initial part of the request has been received and has not yet been "
   "rejected by the server. The client should continue by sending the "
   "remainder of the request or, if the request has already been completed, "
   "ignore this response."),

  101: ("Switching Protocols",
   "The server understands and is willing to comply with the client's "
   "request, via the Upgrade message header field, for a change in the "
   "application protocol being used on this connection."),

  203: ("Non-Authoritative Information",
   "The returned metainformation in the entity-header is not the definitive "
   "set as available from the origin server, but is gathered from a local "
   "or a third-party copy."),

  205: ("Reset Content",
   "The server has fulfilled the request and the user agent SHOULD reset the "
   "document view which caused the request to be sent. "),

  206: ("Partial Content",
   "The server has fulfilled the partial GET request for the resource."),

  300: ("Multiple Choices",
   "The requested resource corresponds to any one of a set of "
   "representations, each with its own specific location, and agent-driven "
   "negotiation information is being provided so that the user "
   "(or user agent) can select a preferred representation and redirect its "
   "request to that location."),

  303: ("See Other",
   "The response to the request can be found under a different URI and SHOULD "
   "be retrieved using a GET method on that resource."),

  305: ("Use Proxy",
   "The requested resource MUST be accessed through the proxy given by the "
   "Location field."),

 #306: ("Unused", "Reserved"),

  307: ("Temporary Redirect",
   "The requested resource resides temporarily under a different URI."),

 #402: ("Payment Required","Reserved"),

  405: ("Method Not Allowed",
   "The method specified in the Request-Line is not allowed for the resource "
   "identified by the Request-URI."),

  406: ("Not Acceptable",
   "The resource identified by the request is only capable of generating "
   "response entities which have content characteristics not acceptable "
   "according to the accept headers sent in the request."),

  407: ("Proxy Authentication Required",
   "the client must first authenticate itself with the proxy."),

  408: ("Request Timeout",
   "The client did not produce a request within the time that the server was "
   "prepared to wait. "),

  409: ("Conflict",
   "The request could not be completed due to a conflict with the current "
   "state of the resource."),

  410: ("Gone",
    "The server knows that an old resource is permanently unavailable and has"
    " no forwarding address. This status code is commonly used when the server"
    " does not wish to reveal exactly why the request has been refused, "
    " or when no other response is applicable."),

  411: ("Length Required",
    "The server refuses to accept the request without a defined "
    "Content-Length."),

  412: ("Precondition Failed",
    "The precondition given in one or more of the request-header fields "
    "evaluated to false when it was tested on the server. This response code "
    "allows the client to place preconditions on the current resource "
    "metainformation (header field data) and thus prevent the requested "
    "method from being applied to a resource other than the one intended."
    ),

  413: ("Request Entity Too Large",
    "The server is refusing to process a request because the request entity "
    "is larger than the server is willing or able to process."
    ),

  414: ("Request-URI Too Long",
    "The server is refusing to service the request because the Request-URI "
    "is longer than the server is willing to interpret."
    ),

  415: ("Unsupported Media Type",
    "The server is refusing to service the request because the entity of the "
    "request is in a format not supported by the requested resource for the "
    "requested method."
    ),

  416: ("Requested Range Not Satisfiable",
    "The request included a Range request-header field. and none of the "
    "range-specifier values in this field overlap the current extent of the "
    "selected resource, and the request did not include an If-Range "
    "request-header field."
    ),

  417: ("Expectation Failed",
    "The expectation given in an Expect request-header field could not be "
    "met by this server"
    ),

  504: ("Gateway Timeout",
    "The server did not receive a timely response from an upstream server"
    ),

  505: ("HTTP Version Not Supported",
    "The server does not support, or refuses to support, the HTTP protocol "
    "version that was used in the request message."
    ),
})
HTTP11_STATUS_CODES_SET = set(HTTP11_STATUS_CODES.keys())


# Table for translating (some) HTTP 1.1 to HTTP 1.0 status codes.
# Degradation in the semantics of the codes (e.g. increased vagueness) is
# acceptable; ensure an HTTP 1.1 client if you need those semantics.
HTTP11_STATUS_DOWNGRADES = {
    # RFC 2616 10.1: "Since HTTP/1.0 did not define any 1xx status codes,
    # servers MUST NOT send a 1xx response to an HTTP/1.0 client except under
    # experimental conditions." 1.0 clients won't behave appropriately for
    # a 100 or 101 no matter what we do here, so refuse to downgrade.
    100: None,
    101: None,
    # 2xx codes should work fine when rendered as 200s to 1.0 clients.
    203: 200,   # "Only appropriate when the response would otherwise be 200"
    205: 200,   # This is for form resets but 200 behavior seems in-spec
    206: None,  # Really does require an HTTP 1.1 client using Range headers!
    # This one can honestly be handled pretty gracefully...
    300: 302,   # Normally provides preferred loc to redirect to, info in body
    # but these two can't really behave as intended with a 302
    303: None,  # Explicitly intends agent to redirect with GET
    307: None,  # Explicitly intends agent NOT to redirect with GET on POST
    306: None,  # reserved
    305: 302,   # seems to be only notationally different from a 302?
    402: 403,   # 'Payment Required' reserved anyway, means forbidden
    405: 403,   # Method not allowed, could be forbidden too
    406: 400,   # Not acceptable - this is about accept headers
    407: None,  # Not really understandable at all w/o proxy
    408: None,  # Not really understandable to a 1.0 client. 400, 403?
    409: None,  # fancy version control semantics here
    410: 404,   # 404 Not Found is just non-permanent version of Gone
    411: 400,   # 'Length required' is like bad request, anyway client is rude
    412: 403,   # Preconditions are like forbidding yourself conditionally
    413: 400,   # Too big is as good as malformed
    414: 400,   # Too-long URI is as good as malformed
    415: 400,   # Unsupported media type is like malformed...
    416: None,  # 1.0 clients shouldn't be asking about Ranges
    417: 403,   # Expectations are like forbidding yourself conditionally
    504: 500,   # Gateway timeout only a little better than 'problem on my end'
    505: 500,   # 'I don't want to support that major version' = 'my problem'
    }


# no \8 or \9 but \10 is valid
_NO_CTL_RE = re.compile("^[^\x00-\x1f\n\x7f]*\Z")
_NO_SEP_RE = re.compile(r'^[^()<>@,;:\\"/\[\]?={} \t]*\Z')


def contains_control_characters(some_string):
    """Helper for finding whether string contains RFC 2616 control chars.
    """
    if _NO_CTL_RE.match(some_string):
        return False
    return True


def contains_separators(some_string):
    """Helper for finding whether string contains RFC 2616 separators
    """
    if _NO_SEP_RE.match(some_string):
        return False
    return True


def valid_status_code(code, valid_codes=None, version=None):
    """Check whether a string code is not obviously an HTTP status code
    such as 400.

    May additionally check whether code falls into given valid_codes
    or is valid for a given version of HTTP.
    """
    if isinstance(code, int):
        int_code = code
        str_code = str(int_code)
    elif isinstance(code, basestring):
        str_code = code
        try:
            int_code = int(str_code)
        except ValueError:
            return False
    else:
        return False

    if not re.match('\d\d\d', str_code) or not len(str_code) == 3:
        return False

    if str_code[0] not in HTTP_STATUS_CLASSES:
        return False

    if valid_codes is not None:
        if (str_code not in valid_codes) and (int_code not in valid_codes):
            return False
    if version is not None:
        if isinstance(version, float):
            version = str(version)
        if version == "1.0":
            known_codes = HTTP10_STATUS_CODES_SET
        elif version == "1.1":
            known_codes = HTTP11_STATUS_CODES_SET
        else:
            # This function can't live up to its contract, so break flow
            # (version should really be checked ahead of time)
            raise UnknownHTTPVersion(version)
        if code not in known_codes:
            return False

    return True


def valid_status_string(status_string, require_reason=False):
    """Return True if a status_string is valid for an HTTP response.
    """
    if not status_string or not isinstance(status_string, basestring):
        return False
    # Expected format is 3-digit integer result code, then space, then
    # whatever: 000 Example Here
    if len(status_string) < 4:
        return False
    if status_string[3] not in (b" ", " "):
        return False
    if not valid_status_code(status_string[:3]):
        return False
    if require_reason and not status_string[3:].strip():
        return False
    # The string must not contain control characters, and must not be
    # terminated with a carriage return, linefeed, or combination thereof.
    if contains_control_characters(status_string[4:]):
        return False
    return True


def parse_protocol(protocol_string):
    """Split a string like 'HTTP/1.1' into components: protocol, major version,
    and minor version.
    """
    protocol, tail = protocol_string.split("/")
    major, minor = tail.split(".")
    return protocol, major, minor


def parse_content_type(content_type, no_dups=True):
    """Parse a Content-Type (or CGI CONTENT_TYPE) value into components.

    This is handy for turning text into a structured value that can easily be
    inspected, manipulated and re-rendered.

    :arg no_dups:
        if True, use a faster method for extracting parameters which
        clobbers duplicate keys (assuming you had some in your Content-Type)
        and returns a dict mapping keys to values.
        if False, use the slower method that keeps all values for each key,
        and returns a dict mapping keys to lists of values.

    :returns: a special (mime_type, parms) tuple, e.g.:
        ("text/html", {'charset':'utf-8'})
    """
    # Format from RFC3875 4.1.3, also RFC2616 3.7
    result = content_type.split(";", 1)
    if len(result) == 1:
        return result[0], {}
    mime_type = result[0]
    tail = result[1].strip()
    if no_dups:
        # Quicker way, but eliminates duplicate parms.
        parms = dict([(item.strip() for item in parm.split("="))
                      for parm in tail.split(";")])
    else:
        parms = {}
        # Slower way, keeps duplicate parms in lists by key
        for parm in tail.split(";"):
            key, value = parm.split("=")
            key = key.strip()
            if key in parms:
                parms[key] = parms[key] + [value]
            else:
                parms[key] = [value]
    return mime_type, parms


def render_content_type(mime_type, charset=None, parms=None):
    """Render a Content-Type value from its components.

    If the optional charset parameter is specified and no parms parameter is
    specified, a simpler method can be used to render.
    """
    if parms:
        parm_tuples = list(parms.items())
        if charset and 'charset' not in parms:
            parm_tuples.insert(0, ('charset', charset))
        return "%s; %s" % (mime_type,
                "; ".join(["%s=%s" % item for item in parm_tuples]))
    else:
        if charset:
            return "%s; charset=%s" % (mime_type, charset)
        return mime_type


def get_reason(status_code, version=None):
    """Get a reason-phrase for a status code.
    """
    first_char = str(status_code)[0]
    if version is None:
        version = DEFAULT_HTTP_VERSION
    if float(version) >= 1.1:
        phrase, _ = HTTP11_STATUS_CODES.get(status_code,
                (HTTP_STATUS_CLASSES.get(first_char, ""), ""))
    else:
        phrase, _ = HTTP10_STATUS_CODES.get(status_code,
                (HTTP_STATUS_CLASSES.get(first_char, ""), ""))
    return phrase


class StatusProperty(object):  # pylint: disable-msg=R0903
    """An overall status attribute that is computed from separate status_code
    and reason attributes.

    Setting the object's status_code and reason will always affect this
    property, and vice versa.
    """
    def __init__(self):
        pass

    def __get__(self, obj, cls=None):
        if not obj:
            status_code = cls.status_code
            reason = cls.reason
        else:
            status_code = obj.status_code
            reason = obj.reason
        reason = reason or get_reason(status_code)
        return "%s %s" % (status_code, reason)

    def __set__(self, obj, status):
        status_code, reason = status.split(" ", 1)
        status_code = int(status_code)
        obj.status_code, obj.reason = status_code, reason


class StatusCodeProperty(object):  # pylint: disable-msg=R0903
    """Intercept changes to status_code to update reason as appropriate.
    """

    def __init__(self, default=200):
        self.default = default
        self.values = {}

    def __get__(self, obj, cls=None):
        if not obj:
            return self.default
        else:
            return self.values.get(obj, self.default)

    def __set__(self, obj, value):
        value = int(value)
        old_value = self.values.get(obj)
        if value == old_value:
            return
        self.values[obj] = value

        obj.reason = get_reason(value)


class ContentTypeProperty(object):  # pylint: disable-msg=R0903
    """Let an object have a content type and its components always in sync.

    Pass default values to the constructor to set a class default for the
    kind of object the property is declared on.

    sets the following attributes on the hosting instance: mime_type, charset,
    content_type_params and also modifies headers['Content-Type'].
    """
    def __init__(self, mime_type="text/plain", charset="iso-8859-1",
            parms=None, content_type=None):
        if content_type is not None:
            mime_type, parms = parse_content_type(content_type)
            charset = parms.get('charset', None)
        self.mime_type = mime_type
        self.charset = charset
        self.parms = parms

    def __get__(self, obj, cls=None):
        if obj:
            try:
                mime_type, charset = obj.mime_type, obj.charset
                parms = obj.content_type_params
                return render_content_type(mime_type, charset, parms)
            except AttributeError:
                pass
        mime_type, charset = self.mime_type, self.charset
        parms = self.parms
        return render_content_type(mime_type, charset, parms)

    def __set__(self, obj, value):
        mime_type, parms = parse_content_type(value)
        obj.mime_type = mime_type
        charset = parms.get('charset', None)
        obj.charset = charset
        obj.content_type_params = parms
        obj.headers.setitem('Content-Type', self.__get__(obj))


class DownloadAsProperty(object):
    header_format = 'attachment; filename="%s"'
    filename_regex = '(?:"(.*)"|(.*))'
    header_regex = re.compile(
              '^' + header_format.replace('"%s"', filename_regex) + '\Z')

    def __init__(self):
        pass

    def extract_header(self, obj=None):
        if not obj:
            return None
        return obj.headers.get('Content-Disposition', None)

    def extract_filename(self, header):
        if not header:
            return None
        match = self.header_regex.match(header)
        if not match:
            return None
        filename = match.group(1) or match.group(2)
        return filename

    def looks_safe(self, filename):
        # see http://greenbytes.de/tech/tc2231 for test cases on browsers
        # some browsers can't handle more than 1024 chars; it's a bad idea too.
        if not filename or not (len(filename) < 1024):
            return False
        # leading slash has unpredictable results, won't be kept by browser.
        # same with leading backslash, which is also ambiguous with an escape.
        if re.match(r'^[/\\]', filename):
            return False
        # any backslash has unpredictable results: not handled as beginning of
        # escape in IE8/9/Safari, doesn't escape dquotes in most browsers.
        # as a result browsers handle dquote consistently and may terminate
        # filename early.
        # semicolon may terminate filenames prematurely in IE8/9.
        # and we don't want control characters here.
        if re.match(r'^[^\\";\0-\x1f\x7f]+\Z', filename):
            return True
        return False

    def __get__(self, obj, cls=None):
        header = self.extract_header(obj)
        filename = self.extract_filename(header)
        if not self.looks_safe(filename):
            return None
        return filename

    class BadFilename(Exception):
        pass

    def __set__(self, obj, value):
        if not self.looks_safe(value):
            raise DownloadAsProperty.BadFilename(value)
        header = self.header_format % value
        obj.headers.setitem('Content-Disposition', header)


class HeadersProxy(Headers, object):
    """Intercept requests to change headers directly, so that certain headers
    can stay in sync with items on the object to which the proxy is attached.

    This allows components of a header to be stored separately on an object for
    easy reading and manipulation (without repeatedly parsing into components
    and re-rendering), while a whole dict-like headers attribute stays in sync
    whenever it's checked.
    """
    def __init__(self, obj, data=None):
        Headers.__init__(self, data or [])
        self.obj = obj

    def setitem(self, key, value):
        "Set value without sync behavior"
        # n.b.: HeadersProxy subclasses object because otherwise super() won't
        # work here.
        super(HeadersProxy, self).__setitem__(key, value)

    def __setitem__(self, key, value):
        """Set an item in headers, keeping certain Response attributes in sync.
        """
        # Keep Response.content_type in sync
        if key.lower() == 'content-type':
            self.obj.content_type = value
        self.setitem(key, value)


class BodyProperty(object):
    """Allow response.body to return a collapsed app_iter attr if defined.
    """
    def __init__(self):
        self.values = {}

    def collapse(self, iterable):  # pylint: disable-msg=R0201
        "Collapse the iterable into one string"
        # this is a method so that it can be overridden in subclasses
        return "".join(iterable)

    def get(self, obj):
        "Store the body value for a particular host object"
        return self.values[obj]

    def __get__(self, obj, cls=None):
        if cls and not obj:
            return self
        # Warnings about auto-collapsing app_iter upon access to body attr:
        # 1. the iterable may be consumed here. this can't be prevented without
        # possibly making the use of an iterable pointless, but it also means
        # you won't be able to reuse some kinds of iterables.
        # 2. collapsing app_iter into a single in-memory value may mean using
        # a lot of RAM. If you are accessing body, this is intentional.
        # Always consume app_iter if it matters.
        # 3. collapsing app_iter will fail appropriately if the iterable yields
        # stuff which won't work with str.join, like numbers; this may be some
        # time after app_iter is set
        if obj:
            # Top priority is to return a collapsed app_iter if we have one
            app_iter = obj.app_iter
            if app_iter:
                return self.collapse(app_iter)
            # Otherwise return the stowed data
            return self.get(obj)
        return ""

    def __set__(self, obj, value):
        """Set the body (and clear the app_iter).
        """
        self.values[obj] = value
        if value:
            obj.app_iter = []


class AppIterProperty(object):  # pylint: disable-msg=R0903
    """Allow response.app_iter to return [body] if there is no iterable.

    (The name 'app_iter' is used to have a WebOb-compatible interface for
    getting an iterable, even though it's a very arbitrary name.)
    """
    def __init__(self):
        self.values = {}

    def __get__(self, obj, cls=None):
        if cls and not obj:
            return self
        # Top priority is to return a real iterator if we have it
        app_iter = self.values.get(obj)
        if app_iter:
            return app_iter
        # Otherwise, iter-ize the body attr
        body = cls.body.get(obj)  # obj.body
        return [body] if body else []

    def __set__(self, obj, value):
        """Set the app_iter (and clear the body).
        """
        try:
            iter(value)
        except TypeError:
            raise AssertionError(
                    "No point setting app_iter to a non-iterable value.")
        assert not isinstance(value, basestring), (
                "You probably don't want app_iter to be a string, "
                "because it will yield one-character chunks.")
        self.values[obj] = value
        if value:
            obj.body = None


class HeadersProperty(object):  # pylint: disable-msg=R0903
    """Make a HeadersProxy look like a simple attribute, so that the interface
    on the Response object looks normal but header changes can be hooked to
    update other attributes.
    """
    def __get__(self, obj, cls=None):
        if obj:
            # Create the proxy & storage on demand - won't always be needed
            if not hasattr(obj, "_headers"):
                obj._headers = HeadersProxy(obj)
                # Don't give out a headers object without setting content-type
                obj._headers['Content-Type'] = obj.content_type
            return obj._headers
        elif cls:
            return {}
        else:
            raise Exception("Need an instance or class")


def render_response(status="200 OK", version="1.1", charset=None,
                    mime_type=None, body="", headers=None):
    """Return a string rendering of an HTTP response.
    """
    headers = correct_headers(headers, mime_type, charset)
    body = render_body(body, charset=charset)
    assert type(body) == type(b'')

    # n.b.: headers better be a dict-like with case-insensitive keys,
    # but checking here would be dumb and slow
    if not body:
        body = b""
    if not 'Content-Length' in headers:
        headers['Content-Length'] = str(len(body))

    header = render_header(status, version=version, headers=headers)
    assert type(header) == type(b'')

    return header + body


def render_header(status="200 OK", version="1.1", headers=None):
    """Render just the header portion of an HTTP response.

    This is 'dumb' - it doesn't check or fix headers, it just formats them.
    """
    # Status-Line with CRLF
    # Header lines, each terminated with CRLF
    # Mandatory CRLF
    status_line = "HTTP/%s %s\r\n" % (version, status)
    if not headers:
        final = ("%s\r\n" % status_line)
    else:
        final = "%s%s\r\n" % (status_line,
            "".join(["%s: %s\r\n" % (k, str(v)) for k, v in headers.items()]))
    return final.encode('ISO-8859-1')


def render_body(data, charset=None):
    """Render (a piece of) the body portion of an HTTP response.
    """
    if not isinstance(data, basestring):
        data = str(data)
    return data.encode(charset or DEFAULT_CHARSET)


def correct_status(status, version="1.0", table=None):
    """If needed and possible, convert a status code/reason from one protocol
       version to another, in order not to use the wrong code for a version.
       If everything is OK, just return the original code and reason.
    """
    if table is None:
        table = HTTP11_STATUS_DOWNGRADES
    code, reason = status.split(" ", 1)
    code = int(code)
    if not valid_status_code(code, version=version):
        new_code = table.get(code)
        # if STILL not valid, raise an exception
        if not valid_status_code(new_code, version=version):
            raise NoDowngradeError(
                    "Invalid status code for HTTP version %s: %s"
                    % (version, new_code))
        code = new_code
    return "%s %s" % (str(code), reason)


def correct_headers(headers, mime_type=None, charset=None):
    """

    headers is a dict-like, but it's expected to do case-insensitive indexing,
    so we don't end up normalizing the whole thing repetitively every time we
    mean to find a header.

    mime_type and charset say what to supply if something isn't in there
    already, or fails to parse. Otherwise, they are ignored.

    """
    if headers is None:
        headers = Headers([])
    # Set Content-Type header
    # We will fill in defaults if Content-Type is not set or doesn't parse.
    parms = None
    if 'Content-Type' in headers:
        content_type = headers.get('Content-Type', '')
        if content_type:
            parsed_mime_type, parms = parse_content_type(content_type)
            if parsed_mime_type:
                mime_type = parsed_mime_type
    if mime_type or parms:
        headers['Content-Type'] = render_content_type(
                mime_type, charset, parms=parms)
    return headers


def detect_version(environ):
    request_protocol = environ.get('SERVER_PROTOCOL', None)
    if request_protocol in ("HTTP/1.1", "HTTP/1.0"):
        version = request_protocol.split("/")[1]
    else:
        protocol, major, minor = parse_protocol(request_protocol)
        major, minor = int(major), int(minor)
        if protocol == "HTTP":
            if (major > 1) or (major == 1 and minor > 1):
                version = "1.1"
    return version


class Response(object):
    """Encapsulate all the information needed to render an HTTP response.
    """
    # accessing app_iter gives iterable, or defaults to [body].
    # accessing body gives collapsed app_iter, or body.
    body = BodyProperty()
    app_iter = AppIterProperty()
    # sets _headers lazily, on first request for headers attribute
    headers = HeadersProperty()
    # sets status_code, reason on instance when set
    status = StatusProperty()
    # sets reason when set independently
    status_code = StatusCodeProperty(default=200)
    reason = None
    # sets mime_type, charset, content_type_params on instance
    content_type = ContentTypeProperty("text/html", "utf-8")
    # just exposes content-disposition header more conveniently
    download_as = DownloadAsProperty()

    def __init__(self, body="", app_iter=None, status=None, code=None,
            reason=None, version=None, environ=None, content_type=None,
            mime_type=None, charset=None, download_as=None):

        if isinstance(body, Response):
            app_iter = body.app_iter

        # Set status all at once, or by parts
        if status is not None:
            self.status = status
        else:
            self.status_code = code or 200
            self.reason = reason or None

        # Set content type all at once, or by parts
        if content_type is not None:
            # All at once
            self.content_type = content_type
        else:
            self.mime_type = mime_type or DEFAULT_MIME_TYPE
            self.charset = charset or DEFAULT_CHARSET
            self.content_type_params = None

        # Accept app_iter or else body
        if app_iter is None:
            self.body = body
        self.app_iter = app_iter or []

        # If no version was forced in the constructor and an environ was
        # provided, use it to set an appropriate protocol version
        # (per RFC2145 2.3: use highest version <= version in request).
        # If this failed for any reason, don't guess, just set to None
        if version is None and environ:
            version = detect_version(environ)
        self.version = version

        if download_as:
            self.download_as = download_as

    def render(self):
        """Return a string rendering of this response suitable for HTTP.
        """
        # Just reuse render_response so the underlying imperative API can
        # be exposed for users who don't want to use this class.
        return render_response(status=self.status, body=self.body,
                               headers=self.headers, mime_type=self.mime_type,
                               charset=self.charset)

    def send(self, start_response):
        """Send out this response data on a WSGI interface.

        The returned value has to be returned to the server by the
        caller somehow, there is no sane way of doing that here.
        """
        start_response(self.status, self.headers.items())
        return self.app_iter


class OK(Response):
    """Shortcut for returning 200 OK response.

    200 is also returned by default by @WSGI handlers which didn't throw an
    error or return another response type.
    """
    status = "200 OK"


class Error(Exception, Response):
    """Represents an error returned by a script. This is for use by scripts.

    Can be either returned or raised, depending on what seems more natural.
    """
    status = "500 Internal Server Error"

    def __init__(self, message="", body="", *args, **kwargs):
        Exception.__init__(self)
        Response.__init__(self, *args, **kwargs)
        self.message = message
        self.body = body
        self.status = Error.status

    def __str__(self):
        return self.message


class Redirect(Response):  # pylint: disable-msg=R0903
    """Return this when you want to correct the used URL to something else.

    This should usually generate a request of the same method, so
    basically you are saying "do that over there," e.g. submit the form
    somewhere more appropriate. That's different from SeeOther, which
    says "now look over there."

    Pass temporary=True if you want the old URL to keep being tried.
    """
    status = "301 Moved Permanently"

    # 307 seems to be handled consistently across modern browsers.
    # 302 isn't consistently handled and may change the method.
    # Use SeeOther to change the method less ambiguously, more consistently.
    def __init__(self, location, temporary=True, **kwargs):
        self.headers['location'] = location
        if temporary:
            self.status = "307 Temporary Redirect"
        Response.__init__(self, **kwargs)
        self.status = Redirect.status


class SeeOther(Response):
    """Return this when you want to ensure that there is a GET to the other
    location, e.g. after a form POST when you want to show the resulting state.
    """
    status = "303 See Other"

    def __init__(self, location, **kwargs):
        self.headers['location'] = location
        Response.__init__(self, **kwargs)
        self.status = SeeOther.status


class BadRequest(Error):
    """Shortcut for telling client that request was bad"""
    status = "400 Bad Request"


class NotFound(Error):  # pylint: disable-msg=R0903
    """Scripts should return this when a URI wasn't found.
    """
    status = "404 Not Found"

    def __init__(self, **kwargs):
        Error.__init__(self, **kwargs)
        self.status = NotFound.status


class Forbidden(Error):  # pylint: disable-msg=R0903
    """Scripts should return this when access was forbidden.
    """
    status = "403 Forbidden"

    def __init__(self, **kwargs):
        Error.__init__(self, **kwargs)
        self.status = Forbidden.status


def json_array_iterator(items, chaff=None, obj_key=None):
    """Yield one item of a JSON array at a time.
    """
    from json import dumps
    index, last = 0, None
    if obj_key is not None:
        yield "{ %s: " % obj_key
    if chaff is not None:
        yield chaff
    for item in items:
        if index == 0:
            pass
        elif index == 1:
            yield "[" + dumps(last)
        else:
            yield "," + dumps(last)
        last = item
        index += 1
    if index == 0:
        yield "[]"
    last_item = dumps(last)
    if index == 1:
        yield "[" + last_item + "]"
    else:
        yield "," + dumps(last) + "]"
    if obj_key:
        yield "}"


class JSON(Response):
    """High-level helper to return a response as JSON.

    If it receives a non-dictlike iterable of objects, it tries to stream their
    serializations as an array (using json_array_iterator to provide app_iter)
    """
    def __init__(self, obj=None, status=None, code=None,
                 reason=None, version=None, environ=None, charset="utf-8",
                 chaff="{}&&", obj_key=None, attachment=True):
        import json
        Response.__init__(self, status=status, code=code, reason=reason,
                          version=version, mime_type="application/json",
                          charset=charset)
        # Reduce chances of this class being used as a vector for XSS;
        # this doesn't affect normal use of the JSON data by APIs, etc.
        if attachment:
            self.headers['Content-Disposition'] = 'attachment'
        self.chaff = chaff
        self.obj_key = obj_key
        iterable = False
        try:
            iter(obj)
            iterable = True
        except TypeError:
            pass
        if iterable and not (hasattr(obj, 'keys') or hasattr(obj, 'get')):
            self.app_iter = json_array_iterator(obj, chaff=chaff,
                    obj_key=obj_key)
        else:
            self.body = (chaff or "") \
                        + json.dumps({obj_key: obj} if obj_key else obj)


class NoDowngradeError(Exception):
    """Raised when a protocol downgrade is requested, but none is found.

    Halts control flow to signal that this really shouldn't happen.
    """
    def __init__(self, message=""):
        Exception.__init__(self)
        self.message = message

    def __str__(self):
        return self.message


def downgrade_middleware(app, version=DEFAULT_HTTP_VERSION,
                         table=None):
    """Decorator/WSGI middleware to downgrade HTTP status codes which
    lower-version clients wouldn't understand.

    Setting version=1.0 will force everything down to 1.0. Otherwise, forcing
    should only occur if the remote asks for 1.0, and the particular status
    code isn't recognized for 1.0.

    Pass the table arg to use a different table of downgrades.

    If an exception occurs in the app, it is not caught; that is for
    a framework, @WSGI, error-catching middleware, etc. to do.
    """
    if table is None:
        table = HTTP11_STATUS_DOWNGRADES

    def interceptor(status, headers, exc_info=None):
        """Fake start_response used to gather the header data.
        """
        interceptor.status = status
        interceptor.headers = headers
        interceptor.exc_info = exc_info

    def downgrade_wrapper(environ, start_response):
        """Substitute for the app which calls it and adapts response.
        """
        # Check client's announced HTTP version (SERVER_PROTOCOL)
        request_version = environ.get("SERVER_PROTOCOL", "")
        if not request_version:
            raise NoDowngradeError("No SERVER_PROTOCOL defined")
        request_version = request_version.replace("HTTP/", "").strip()
        response_version = version
        if (version != request_version):
            if float(version) > float(request_version):
                assert request_version in ("1.0", "1.1")
                response_version = request_version

        # Cue app about the desired version in case it can act intelligently
        environ['SERVER_PROTOCOL'] = "HTTP/%s" % response_version

        # Run app, collect its output with the interceptor start_respons
        iterable = app(environ, interceptor)
        status = interceptor.status
        headers = interceptor.headers
        exc_info = interceptor.exc_info

        # TODO: headers in only HTTP/1.1: Cache-Control header etc.

        # Use standalone API function rather than doing it all inside here
        old_status = status
        status = correct_status(status, version=response_version,
                                table=table)
        # Warn about shift
        if status != old_status:
            logging.warning("status %s downgraded for version %s: -> %s",
                            repr(old_status), repr(response_version),
                            repr(status))
        if exc_info:
            start_response(status, headers, exc_info=exc_info)
        else:
            start_response(status, headers)
        return iterable

    return downgrade_wrapper
