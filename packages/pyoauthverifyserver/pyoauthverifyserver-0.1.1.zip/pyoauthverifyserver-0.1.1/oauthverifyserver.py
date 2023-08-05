from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import TCPServer
import urlparse


class _CallbackHttpRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_params = urlparse.urlparse(self.path)
        query_parsed = urlparse.parse_qs(parsed_params.query)

        retval = self.server._verify(query_parsed)

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()

        self.wfile.write('done')
        self.wfile.close()

        if retval:
            self.server.shutdown()

    def log_message(self, *args, **kw):
        return

class OAuthCallbackServer(TCPServer):
    def __init__(self, port, callback):
        TCPServer.__init__(self, ("", port), _CallbackHttpRequestHandler)
        self._callback = callback

    def _verify(self, query_string):
        self._verifier = query_string['oauth_verifier']
        print "ServerVT = ", self._verifier
        self._callback('')
        self._done = True

    def wait(self):
        self._done = False
        while not self._done:
            self.handle_request()

    @property
    def verify_token(self):
        return self._verifier