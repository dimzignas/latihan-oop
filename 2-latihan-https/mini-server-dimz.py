'''
Code from http://aosabook.org/en/500L/a-simple-web-server.html
with some modification by dimz
'''

from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import TCPServer
import os
# import socket
import ssl
import base64
import json
from urllib.parse import urlparse, parse_qs
# import inspect


# ------Class Cases------------------------------
class base_case(object):
    '''Parent for case handlers.'''

    # Handle file
    def handle_file(self, handler, path):
        try:
            # sementara hanya bisa buka send text file
            with open(path, 'r') as reader:
                content = reader.read()
            handler.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(path, msg)
            handler.handle_error(msg, 503, 'json')

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        assert False, 'Not implemented.'

    def act(self, handler):
        assert False, 'Not implemented.'


class case_no_auth(base_case):
    '''No Authorization header'''

    def test(self, handler):
        return handler.headers.get('Authorization') is None

    def act(self, handler):
        handler.set_is_auth(False)
        handler.set_status(401)
        raise ServerException("No auth header received.")


class case_basic_auth(base_case):
    '''Basic Authorization header'''

    def test(self, handler):
        return handler.headers.get('Authorization') == 'Basic ' +\
         handler.server.get_auth_key()

    def act(self, handler):
        handler.set_is_auth(True)


class case_auth_always_fail(base_case):
    '''Base Case if Authorization header always failed'''

    def test(self, handler):
        return True

    def act(self, handler):
        handler.set_is_auth(False)
        handler.set_status(401)
        raise ServerException("Invalid credential.")


class case_no_file(base_case):
    '''File or directory does not exist.'''

    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        handler.set_status(404)
        raise ServerException("'{0}' not found".format(handler.base_path))


class case_cgi_file(base_case):
    '''Something runnable.'''

    def test(self, handler):
        return os.path.isfile(handler.full_path) and \
               handler.full_path.endswith('.py')

    def act(self, handler):
        handler.run_cgi(handler.full_path)


class case_existing_file(base_case):
    '''File exists.'''

    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        self.handle_file(handler, handler.full_path)


class case_directory_index_file(base_case):
    '''Serve index.html page for a directory.'''

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
            os.path.isfile(self.index_path(handler))

    def act(self, handler):
        self.handle_file(handler, self.index_path(handler))


class case_directory_no_index_file(base_case):
    '''Serve listing for a directory without an index.html page.'''

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
            not os.path.isfile(self.index_path(handler))

    def act(self, handler):
        handler.list_dir(handler.full_path)


class case_always_fail(base_case):
    '''Base case if nothing else worked.'''

    def test(self, handler):
        return True

    def act(self, handler):
        handler.set_status(404)
        raise ServerException("Unknown object '{0}''".format(handler.base_path))


# ------Class Error------------------------------
# ---------https://docs.python.org/3/tutorial/errors.html#tut-userexceptions-------------------------------------------------------
class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class ServerException(Error):
    """Exception raised for errors in the Server.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
# ----------------------------------------------------------------------


# ------Class RequestHandler------------------------------
class RequestHandler(BaseHTTPRequestHandler):
    '''Handle HTTP requests by returning a 'page'.
        If the requested path maps to a file, that file is served.
        If anything goes wrong, an error page is constructed.
    '''

    AuthCases = [
            case_no_auth,
            case_basic_auth,
            case_auth_always_fail
        ]

    FileCases = [
            case_no_file,
            case_cgi_file,
            case_existing_file,
            case_directory_no_index_file,
            case_directory_index_file,
            case_always_fail
        ]

    base_path = ''  # simpan path tanpa param dan query
    path_query = ''  # simpan query dalam path
    path_param = ''  # simpan param dalam path

# How to display a directory listing.
    Listing_Page = ''' \
        <html>
        <body>
        <ul>
        {0}
        </ul>
        </body>
        </html>
        '''

    Error_Page = ''' \
        <html>
        <body>
        <h1>Error accessing {path}</h1>
        <p>{msg}</p>
        </body>
        </html>
        '''

    status = 200
    is_auth = False

    # Classify and handle a GET request.
    def do_GET(self):
        try:

            # Figure out what exactly is being requested.
            this_cwd = os.getcwd()
            # this_cwd = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
            # this_cwd = "C:\\Users\\creator\\myPy\\OOP\\2-latihan-https"

            # self.path masih ada param dan query string-nya
            self.set_base_path(urlparse(self.path).path)
            self.set_full_path(os.path.normpath(this_cwd + self.base_path))
            self._parse_GET()

            # Figure out how to handle it (Authorization Header).
            for authCase in self.AuthCases:
                aCaseHandler = authCase()
                if aCaseHandler.test(self):
                    aCaseHandler.act(self)
                    break

            # If Authorization has been confirmed (True), figure out what next
            if self.is_auth:
                # Figure out how to handle it (file or directory).
                for fileCase in self.FileCases:
                    fCaseHandler = fileCase()
                    if fCaseHandler.test(self):
                        fCaseHandler.act(self)
                        break

        # Handle errors.
        except Exception as msg:
            self.handle_error(msg, 'json')

    # Create list of a directory
    def list_dir(self, path):
        try:
            entries = os.listdir(path)
            bullets = ['<li>{0}</li>'.format(e)
                for e in entries if not e.startswith('.')]
            page = self.Listing_Page.format('\n'.join(bullets))
            # page = self.base_path
            self.send_content(page)
        except OSError as msg:
            msg = "'{0}' cannot be listed: {1}".format(self.path, msg)
            self.handle_error(msg)

    # Run CGI script
    def run_cgi(self, path):
        '''
        cmd = "python " + path
        child_stdin, child_stdout = os.popen2(cmd)
        child_stdin.close()
        data = child_stdout.read()
        child_stdout.close()
        '''
        data = "Here Python execution's result should be."
        self.send_content(data)

    # Handle unknown objects.
    def handle_error(self, msg, type):
        if type == 'html':
            content = self.Error_Page.format(path=self.path, msg=msg)
            self.send_content(content)
        elif type == 'json':
            content = {
                'status': self.status,
                'message': str(msg)
            }
            self.send_content(json.dumps(content), 'application/json')

    # Send actual content.
    def send_content(self, content, content_type='text/html'):
        self.send_response(self.status)
        if not self.is_auth:  # kalau Authorization Basic tanpa key
            self.send_header('WWW-Authenticate', 'Basic realm="Demo Realm"')
        self.send_header("Content-type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(bytes(content, 'utf-8'))

    # set base_path _dimz_
    def set_base_path(self, base_path):
        self.base_path = base_path

    # set base_path _dimz_
    def set_full_path(self, full_path):
        self.full_path = full_path

    # set connection status
    def set_status(self, status):
        self.status = status

    # set flag as True if Authorization confirmed
    def set_is_auth(self, is_auth):
        self.is_auth = is_auth

    # parsing query in path
    def _parse_GET(self):
        self.path_query = parse_qs(urlparse(self.path).query)
        return self.path_query


class MyServer(TCPServer):
    key = ''

    def __init__(self, address, handlerClass=RequestHandler):
        super().__init__(address, handlerClass)

    def set_auth(self, username, password):
        self.key = base64.b64encode(
            bytes('%s:%s' % (username, password), 'utf-8')).decode('ascii')

    def get_auth_key(self):
        return self.key


if __name__ == '__main__':
    port = 8060
    serverAddress = ('', port)

    '''
    # dengan HTTPServer
    with HTTPServer(serverAddress, RequestHandler) as server:
        server.socket = ssl.wrap_socket(server.socket,
            # keyfile=os.getcwd() + "/key.pem",
            # certfile=os.getcwd() + "/cert.pem",
            certfile=os.getcwd() + "/server.pem",
            server_side=True)
        print("serving at port", port)
        server.serve_forever()

    # dengan socketserver.TCPServer
    with TCPServer(serverAddress, RequestHandler) as server:
        server.socket = ssl.wrap_socket(server.socket,
            certfile=os.getcwd() + "/server.pem",
            server_side=True)
        print("serving at port", port)
        server.serve_forever()
    '''
    # dengan MyServer
    with MyServer(serverAddress, RequestHandler) as server:
        server.socket = ssl.wrap_socket(server.socket,
            certfile=os.getcwd() + "/server.pem",
            server_side=True)
        server.set_auth('demo', 'demo')
        print("serving at port", port)
        server.serve_forever()
    # dz = RequestHandler
    # dz.do_GET
