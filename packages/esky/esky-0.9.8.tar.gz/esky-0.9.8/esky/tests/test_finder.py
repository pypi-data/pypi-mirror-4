#  Copyright (c) 2009-2010, Cloud Matrix Pty. Ltd.
#  All rights reserved; available under the terms of the BSD License.

from __future__ import with_statement

import unittest

import os
import tempfile
import threading
from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import HTTPServer

import esky.finder
from esky.util import really_rmtree


if not hasattr(HTTPServer,"shutdown"):
    import socket
    def socketserver_shutdown(self):
        try:
            self.socket.close()
        except socket.error:
            pass
    HTTPServer.shutdown = socketserver_shutdown


class TestVersionFinder(unittest.TestCase):

    def setUp(self):
        self.workdir = tempfile.mkdtemp()
        self.origdir = os.path.abspath(os.curdir)
        os.chdir(self.workdir)
        self.server = HTTPServer(("localhost", 8000), SimpleHTTPRequestHandler)
        self.server_url = "http://localhost:8000"
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def tearDown(self):
        os.chdir(self.origdir)
        self.server.shutdown()
        self.server_thread.join()
        really_rmtree(self.workdir)

    def test_issue35(self):
        #open("CouchPotato-2.0.3.macosx-10_6-intel.zip", "w").close()
        #open("CouchPotato-2.0.3.win32.installer.exe", "w").close()
        #open("CouchPotato-2.0.3.win32.zip", "w").close()
        #open("CouchPotato-2.0.2.macosx-10_6-intel.zip", "w").close()
        #open("CouchPotato-2.0.2.win32.installer.exe", "w").close()
        #open("CouchPotato-2.0.2.win32.zip", "w").close()
        open("CouchPotato-2.0.1.1.macosx-10_6-intel.zip", "w").close()
        open("CouchPotato-2.0.1.1.win32.installer.exe", "w").close()
        open("CouchPotato-2.0.1.1.win32.zip", "w").close()
        class app:
            name = "CouchPotato"
            platform = "win32"
            version = "0"
        finder = esky.finder.DefaultVersionFinder(self.server_url)
        self.assertEquals(finder.find_versions(app), ["2.0.1.1"])
        raise RuntimeError(finder.version_graph._links)

