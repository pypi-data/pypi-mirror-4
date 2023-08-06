# Copyright (C) 2010-2013 Sebastian Rahlf and others (see AUTHORS).
#
# This program is release under the MIT license. You can find the full text of
# the license in the LICENSE file.

import BaseHTTPServer
import cgi
import gzip
import StringIO
import sys
import threading

import pytest_localserver

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
    """
    Handler for HTTP requests serving files specified by server instance.
    """
    
    # The server software version.  You may want to override this.
    # The format is multiple whitespace-separated strings,
    # where each string is of the form name[/version].
    server_version = 'pytest_localserver.http/%s' % pytest_localserver.VERSION

    def log_message(self, format, *args):
        """
        Overrides standard logging method.
        """
        if self.server.logging:
            sys.stdout.write("%s - - [%s] %s\n" % (self.address_string(), 
                self.log_date_time_string(), format % args))

    def send_head(self):
        """
        Common code for GET and HEAD commands. This sends the response code and
        other headers (like MIME type).
        """
        self.send_response(self.server.code)
        for key, val in self.server.headers.items():
            self.send_header(key, val)
        self.end_headers()

    def do_HEAD(self):
        """
        Serve a HEAD request.
        """
        self.send_head()

    def do_GET(self):
        """
        Serve a GET request. Response will be ``self.server.content`` as
        message.
        """
        if ('gzip' in self.headers.get('accept-encoding', '')
        and self.server.allow_gzip):
            zipped = StringIO.StringIO()
            fp = gzip.GzipFile(fileobj=zipped, mode='wb')
            fp.write(self.server.content or '')
            fp.close()
            self.server.headers['content-encoding'] = 'gzip'
            content = zipped.getvalue()
        else:
            content = self.server.content

        self.send_head()
        self.wfile.write(content)

    def do_POST(self):
        """
        Serve POST request. If ``self.server.show_post_vars`` is ``True``, 
        submitted vars will be returned. Otherwise the response will be 
        ``self.server.content``.
        """
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        if (ctype == 'application/x-www-form-urlencoded'
        and self.server.show_post_vars):
            length = int(self.headers['content-length'])
            postvars = cgi.parse_qs(
                self.rfile.read(length), keep_blank_values=1)
            self.send_head()
            self.wfile.write(postvars)
        else:
            self.do_GET()


class Server (BaseHTTPServer.HTTPServer):

    """
    Small test server which can be taught which content (i.e. string) to serve
    with which response code. Try the following snippet for testing API calls::
        
        server = Server(port=8080)
        server.start()
        print 'Test server running at http://%s:%i' % server.server_address
        server.content = 'Hello World!'
        server.code = 503
        # any call to http://localhost:8080 will get a 503 response.
        # ...
        
    """

    def __init__(self, host='localhost', port=0, 
                 threadname=None, handler=RequestHandler):
        BaseHTTPServer.HTTPServer.__init__(self, (host, port), handler)

        # Workaround for Python 2.4: using port 0 will bind a free port to the 
        # underlying socket. The server_address, however, is not reflecting 
        # this! So we need to adjust it manually.
        if self.server_address[1] == 0: 
            self.server_address = (self.server_address[0], self.server_port)

        self.content, self.code = (None, 204) # HTTP 204: No Content
        self.headers = {}
        self.allow_gzip = True
        self.logging = False
        self.show_post_vars = False

        self._running = False

        # initialise thread
        self.threadname = threadname or self.__class__
        self._thread = threading.Thread(
                name=self.threadname, target=self.serve_forever)

        # support for Python 2.4 and 2.5
        if sys.version_info[:2] < (2, 6):

            def stop():
                # since BaseHTTPServer.serve_forever is potentially blocking 
                # (i.e. it needs to handle a request before stopping), we need
                # to kill it! 
                self._running = False
                self._thread.join(0) # DIE THREAD! DIE!

            # Luckily, threads in daemon mode will exit gracefully.
            self._thread.setDaemon(True)
            self.stop = stop

    def __del__(self):
        self.stop()

    def __repr__(self):
        return '<http.Server %s:%s>' % self.server_address

    @property
    def url(self):
        if self.server_port == 80:
            return 'http://%s' % self.server_name
        return 'http://%s:%s' % self.server_address

    def start(self):
        """
        Starts the test server.
        """
        self._thread.start()
        self._running = True

    def stop(self, timeout=None):
        """
        Stops test server.

        :param timeout: When the timeout argument is present and not None, it
        should be a floating point number specifying a timeout for the operation
        in seconds (or fractions thereof).
        """
        self.shutdown()
        self._thread.join(timeout)
        self._running = False

    def is_running(self):
        """
        Is server still/already running?
        """
        return self._running

    # DEPRECATED!
    is_alive = is_running

    def serve_content(self, content, code=200, headers=None,
                      show_post_vars=False):
        """
        Serves string content (with specified HTTP error code) as response to
        all subsequent request.
        """
        self.content, self.code, = (content, code)
        self.show_post_vars = show_post_vars

        if headers:
            self.headers = headers


if __name__ == '__main__':
    import os.path
    import time

    server = Server()
    server.start()
    server.logging = True

    print 'HTTP server is running at http://%s:%i' % (server.server_address)
    print 'Type <Ctrl-C> to stop'

    try:
        path = sys.argv[1]
    except IndexError:
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '..', 'README')

    server.serve_content(open(path).read(), 302)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print '\rstopping...'
    server.stop()
