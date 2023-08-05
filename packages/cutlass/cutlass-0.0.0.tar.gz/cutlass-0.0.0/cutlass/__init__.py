"""Top-level package file.

The presence of this file allows cutlass to be recognized as a Python
package. Its contents are run the first time something is imported from
cutlass, e.g. 'from cutlass import wsgi'.

Holger Krekel's apipkg is used to expose a set of orthogonal, high-level tools
at the top level (e.g. 'from cutlass import Dispatcher'). Lower-level
imperative APIs and the like are kept inside their individual modules.
"""
from . apipkg import initpkg

__version__ = "0.0.0"

initpkg('cutlass', {
        'WSGI': 'cutlass.wsgi:WSGI',
        'Middleware': 'cutlass.wsgi:Middleware',
        'StartResponse': 'cutlass.wsgi:StartResponse',
        'IterableWrapper': 'cutlass.wsgi:IterableWrapper',
        'Request': 'cutlass.request:Request',
        'Response': 'cutlass.response:Response',
        'Dispatcher': 'cutlass.routing:Dispatcher',
        'Bundle': 'cutlass.config:Bundle',
        'Cascade': 'cutlass.routing:Cascade',
        'resource': 'cutlass.routing:resource',
        'Resource': 'cutlass.routing:Resource',
        'transform': 'cutlass.transform:transform',
        'transformed': 'cutlass.transform:transformed',
        'Cookies': 'cutlass.cookies:Cookies',
        'Cookie': 'cutlass.cookies:Cookie',
        'JSON': 'cutlass.response:JSON',
        'Redirect': 'cutlass.response:Redirect',
        'NotFound': 'cutlass.response:NotFound',
        'Forbidden': 'cutlass.response:Forbidden',
        'Error': 'cutlass.response:Error',
        # Let pytest find cutlass.cutlass to match cutlass/cutlass/
        # discovered due to __init__.py at repo root.
        'cutlass': 'cutlass',
        })
