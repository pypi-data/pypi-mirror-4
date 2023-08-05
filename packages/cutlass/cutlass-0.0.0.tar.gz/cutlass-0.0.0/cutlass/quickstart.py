"""Conveniences to make it easier to jump in quickly from the docs.

This isn't intended for serious use in production; there are many good WSGI
servers you should be using for test and/or production.
"""
import sys

def run(app, host="127.0.0.1", port=8000):
    """Quickly run a WSGI application callable.

    Just for learning, demos and similar quick and dirty stuff - please don't
    use this in production, there are far better servers which are very easy to
    install and use.
    """
    from wsgiref.simple_server import make_server
    server = make_server(host, port, app)
    print("Browse to http://{host}:{port}\nHit Ctrl-C to halt".format(
            host=host, port=port))
    server.serve_forever()


# Support 'python -m cutlass.quickstart foo:app'
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide an additional argument "
              "specifying a module and callable name, e.g. foo:app")
        sys.exit(1)
    pieces = sys.argv[1].rsplit(":", 1)
    module_name = pieces[0]
    module = __import__(module_name, fromlist=[''])
    if len(pieces) > 1:
        app_name = pieces[1]
        app = getattr(module, app_name)
    else:
        app = getattr(module, 'app')
    run(app)
