'''
Code from http://aosabook.org/en/500L/a-simple-web-server.html
with some modification by dimz
'''

from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import ssl
# import inspect


# ------Class Cases------------------------------
class base_case(object):
    '''Parent for case handlers.'''

    # Handle file
    def handle_file(self, handler, full_path):
        try:
            # sementara hanya bisa buka send text file
            with open(full_path, 'r') as reader:
                content = reader.read()
            handler.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(full_path, msg)
            handler.handle_error(msg)

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        assert False, 'Not implemented.'

    def act(self, handler):
        assert False, 'Not implemented.'


class case_no_file(base_case):
    '''File or directory does not exist.'''

    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        raise ServerException("'{0}' not found".format(handler.full_path))


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

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

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
        raise ServerException("Unknown object '{0}''".format(handler.full_path))


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

    Cases = [case_no_file,
             case_cgi_file,
             case_existing_file,
             case_directory_no_index_file,
             case_directory_index_file,
             case_always_fail]

# How to display a directory listing.
    Listing_Page = '''\
        <html>
        <body>
        <ul>
        {0}
        </ul>
        </body>
        </html>
        '''

    Error_Page = """\
        <html>
        <body>
        <h1>Error accessing {path}</h1>
        <p>{msg}</p>
        </body>
        </html>
        """

    # Classify and handle a GET request.
    def do_GET(self):
        try:

            # Figure out what exactly is being requested.
            this_cwd = os.getcwd()
            # this_cwd = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
            # this_cwd = "C:\\Users\\creator\\myPy\\OOP\\2-latihan-https"
            self.full_path = os.path.normpath(this_cwd + self.path)

            # Figure out how to handle it.
            for case in self.Cases:
                caseHandler = case()
                if caseHandler.test(self):
                    caseHandler.act(self)
                    break

        # Handle errors.
        except Exception as msg:
            self.handle_error(msg)

    # Create list of a directory
    def list_dir(self, full_path):
        try:
            entries = os.listdir(full_path)
            bullets = ['<li>{0}</li>'.format(e)
                for e in entries if not e.startswith('.')]
            page = self.Listing_Page.format('\n'.join(bullets))
            #page = self.full_path
            self.send_content(page)
        except OSError as msg:
            msg = "'{0}' cannot be listed: {1}".format(self.path, msg)
            self.handle_error(msg)

    # Run CGI script
    def run_cgi(self, full_path):
        '''
        cmd = "python " + full_path
        child_stdin, child_stdout = os.popen2(cmd)
        child_stdin.close()
        data = child_stdout.read()
        child_stdout.close()
        '''
        data = "Here Python execution's result should be."
        self.send_content(data)

    # Handle unknown objects.
    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        self.send_content(content, 404)

    # Send actual content.
    def send_content(self, content, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(bytes(content, 'utf-8'))


if __name__ == '__main__':
    serverAddress = ('', 8060)
    server = HTTPServer(serverAddress, RequestHandler)
    server.socket = ssl.wrap_socket(server.socket,
        # keyfile=os.getcwd() + "/key.pem",
        # certfile=os.getcwd() + "/cert.pem",
        certfile=os.getcwd() + "/server.pem",
        server_side=True)
    print("serving at port", 8060)
    server.serve_forever()
    # dz = RequestHandler
    # dz.do_GET
