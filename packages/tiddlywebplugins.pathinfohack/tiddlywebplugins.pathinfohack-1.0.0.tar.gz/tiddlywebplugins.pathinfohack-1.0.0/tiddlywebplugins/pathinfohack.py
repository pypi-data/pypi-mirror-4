"""
A plugin that remedies an URI encoding problem
encountered when running TiddlyWeb under Apache.
The plugin reverts the path in the PATH_INFO variable
to its undecoded form.

The problem being addressed occurs with URIs containing
%2F characters (encoded forward slashes).

Currently Apache and many other servers supply the PATH_INFO
variable in decoded form.

As a result, all instances of %2F in the URI are replaced
with a / character in PATH_INFO. The Selector is then
thrown off since it depends on forward slashes to match
handlers. No match, and the requested PUT, GET, DELETE,
etc., operation goes unhandled.

Install the plugin by adding 'tiddlywebplugins.pathinfohack' to
'system_plugins' in tiddlywebconfig.py.

config = {
    'system_plugins': ['tiddlywebplugins.pathinfohack'],
}
"""

from tiddlyweb.web.query import Query


class PathInfoHack(object):
    """
    WSGI environment manipulator that replaces
    the decoded path in PATH_INFO with an undecoded
    copy from the original request URI.
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        self._undecode_path_info(environ)
        return self.application(environ, start_response)

    def _undecode_path_info(self, environ):
        """
        Compare the request URI with PATH_INFO and use
        the non-SCRIPT_NAME part of it directly.

        Yes, we really do want the actual URI.
        """
        request_uri = environ.get('REQUEST_URI', environ.get('RAW_URI', ''))
        if '%2F' in request_uri or '%2f' in request_uri:
            path_info = environ.get('PATH_INFO', '')
            script_name = environ.get('SCRIPT_NAME', '')
            query_string = environ.get('QUERY_STRING', '')

            path_info = request_uri.replace(script_name, "", 1)
            path_info = path_info.replace('?' + query_string, "", 1)
            environ['PATH_INFO'] = path_info


def init(config):
    """
    Add the middleware to the WSGI stack.
    """
    if PathInfoHack not in config['server_request_filters']:
        config['server_request_filters'].insert(
                config['server_request_filters'].index(Query) + 1,
                PathInfoHack)
