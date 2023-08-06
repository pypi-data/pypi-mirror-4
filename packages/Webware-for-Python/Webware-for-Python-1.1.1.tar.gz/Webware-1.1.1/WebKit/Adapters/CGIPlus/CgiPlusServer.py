"""CGIPlusServer"""

import os

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from time import time

from WebKit.CgiPlusAppServer import Handler, CPASStreamOut


class CgiPlusHandler(object):
    """Handle incoming requests.

    Recreated with every request. Abstract base class.

    """

    def __init__(self, env, rfile, wfile):
        self.env = env
        self.rfile = rfile
        self.wfile = wfile
        self._discardOutput = False

    def handleRequest(self):
        """Handle the request.

        Actually performs the request, creating the environment and
        calling self.doTransaction(env, myInput) to perform the response.

        """
        myInput = ''
        self._discardOutput = False
        if 'CONTENT_LENGTH' in self.env:
            length = int(self.env['CONTENT_LENGTH'])
            if length > 0:
                myInput += self.rfile.read(length)
        self.doTransaction(self.env, myInput)

    def processResponse(self, data):
        """Process the request.

        Takes a string (like what a CGI script would print) and
        sends the actual HTTP response (response code, headers, body).

        """
        if self._discardOutput:
            return
        self.wfile.write(data)
        self.wfile.flush()

    def doLocation(self, headers):
        """Set status for location header.

        If there's a Location header and no Status header,
        we need to add a Status header ourselves.

        """
        if 'Location' in headers:
            if 'Status' not in headers:
                headers['Status'] = '301 Moved Temporarily'

    def sendStatus(self, headers):
        status = headers.pop('Status', '200 OK')
        status = status.split(None, 1)
        code = int(status[0])
        message = len(status) > 1 and status[1].rstrip() or ''
        self.wfile.write("Status: %d %s\n" % (code, message))

    def sendHeaders(self, headers):
        for header, value in headers.items():
            self.send_header(header, value)
        self.end_headers()

    def send_header(self, keyword, value):
        """Send a MIME header."""
        self.wfile.write("%s: %s\n" % (keyword, value))

    def sendBody(self, bodyFile):
        self.wfile.write(bodyFile.read())
        bodyFile.close()
        self.wfile.flush()

    def end_headers(self):
        """Send the blank line ending the MIME headers."""
        self.wfile.write("\n")
        self.wfile.flush()


class CgiPlusAppServerHandler(Handler, CgiPlusHandler):
    """Handler for CgiPlusAppServer.

    Adapters CgiPlusHandler to fit with CgiPlusAppServer's
    model of an adapter.

    """

    protocolName = 'CgiPlus'

    def handleRequest(self):
        CgiPlusHandler.__init__(self, os.environ, os.sys.stdin, os.sys.__stdout__)
        CgiPlusHandler.handleRequest(self)

    def doTransaction(self, env, myInput):
        streamOut = CPASStreamOut(os.sys.__stdout__)
        requestDict = dict(format='CGI', time=time(), environ=env,
            input=StringIO(myInput), requestID=self._requestID)
        self.dispatchRawRequest(requestDict, streamOut)
        self.processResponse(streamOut._buffer)

    def dispatchRawRequest(self, requestDict, streamOut):
        transaction = self._server._app.dispatchRawRequest(requestDict, streamOut)
        streamOut.close()
        transaction._application = None
        transaction.die()
        del transaction
