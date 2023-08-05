"""Wrappers to transform a function's arguments and return values.

Typical applications include converting and validating values.
"""

import re
from functools import update_wrapper
try:
    callable
except NameError:
    callable = lambda f: hasattr(f, "__call__")


def ensure_iterable(arg):
    """Verify that arg is an iterable and/or return it as an iterable.

    Used to let source/target be either single functions (syntactic sugar) or
    lists of them.
    """
    if not arg:
        return []
    try:
        arg = (item for item in arg)
    except TypeError as exception:
        if not re.match("^'(.+)' object is not iterable\Z", str(exception)):
            raise
        arg = [arg]
    return arg


def transformed(original, source=None, target=None):
    """Wrap a function to convert its arguments and/or return values.

    This performs arbitrary signature and return value transformations using
    sequences of functions: argument transformations in source, and
    return-value transformations in target.

    The wrapper function produced by an @transform decoration takes any
    arguments and calls a series of functions on them (source), each function
    operating on the output of the previous function in the series and
    returning (args, kwargs). The original function is then called with these
    arguments, and its return value is collected. The return value value is
    then put through a series of functions (target), and the final value is
    returned by the wrapper.

    This has less call overhead and fewer gotchas than chaining decorators
    together, and it's generally easier to write or find transformation
    functions than to write or find good decorators to do the same things.

    :arg function:
        function to be transformed.

    :arg source: function or sequence of functions used to transform arguments.
        each can take arbitrary arguments but should return (args, kwargs). if
        return value is NOT a tuple, it is returned as the first arg (this is
        to support simple functions like json.loads)

    :arg target: function or sequence of functions to transform return value.
        E.g.: if the wrapped function is named 'foobar' and takes no
        args, then [a, b, c] computes a return value just like
        'c(b(a(foobar())))'. if return value is a tuple, it is unpacked
        for the next function, so you can build pipelines of tuples.

    :returns:

        A wrapper which takes any arguments acceptable to the first function in
        'source' and returns the return value produced by the last function in
        'target'.
    """
    assert callable(original)
    if not source and not target:
        raise TypeError("specify source or target")
    sources = list(ensure_iterable(source))
    targets = list(ensure_iterable(target))

    def transformed_wrapper(*args, **kwargs):
        """wrapper function produced by transformed().
        """
        for source in sources:
            provided = source(*args, **kwargs)
            # source functions should normally return tuples of length 2, where
            # the first item is an args sequence and the second is a kwargs
            # dict. If it's a bad tuple then generate a natural exception here.
            if isinstance(provided, tuple):
                args, kwargs = provided
                assert iter(args)
                assert kwargs.keys and kwargs.__getitem__
            # Non-tuple return values are passed through as a single arg, to
            # allow usage of existing functions like json.loads.
            else:
                args, kwargs = (provided,), {}

        result = original(*args, **kwargs)

        for target in targets:
            if isinstance(result, tuple):
                result = target(*result)
            else:
                result = target(result)
        return result


    update_wrapper(transformed_wrapper, original)
    transformed_wrapper.__wraps__ = original
    return transformed_wrapper

def transform(source=None, target=None):
    """Decorator to transform a function at the time it's defined.

    Example::

        @transform(source=str, target=int)
        def double(some_string):
            return some_string * 2

        assert double(4) == '44'

    This uses transformed() to generate the wrapper (this way, it can be used
    conveniently either as a decorator or just as a function).
    """
    # To explain how this works for those who do not find it obvious:
    # The call to this function, e.g. '@transform(...)', returns a lambda.
    # Python's decorator syntax then automatically calls that lambda with the
    # function; the result of that call will be the replacement function.
    # When the lambda is called, it calls transformed() to generate the
    # wrapper which replaces the original function.
    return lambda original: transformed(original, source, target)
