##########################################################################
# zopyx.smartprintng.server
# (C) 2008, 2009, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os
import base64
import xmlrpclib
import unittest
import zipfile
import tempfile
from pyramid import testing
from models import Server

xml = """<?xml version="1.0"?>
<methodCall>
   <methodName>ping</methodName>
</methodCall>
"""
xml2 = """<?xml version="1.0"?>
<methodCall>
   <methodName>convertZIP</methodName>
    %s
</methodCall>
"""

xml3 = """<?xml version="1.0"?>
<methodCall>
   <methodName>convertZIPandRedirect</methodName>
    %s
</methodCall>
"""

class ViewTests(unittest.TestCase):

    """ These tests are unit tests for the view.  They test the
    functionality of *only* the view.  They register and use dummy
    implementations of pyramid functionality to allow you to avoid
    testing 'too much'"""

    def setUp(self):
        """ cleanUp() is required to clear out the application registry
        between tests (done in setUp for good measure too)
        """
        self.config = testing.setUp()

    def tearDown(self):
        """ cleanUp() is required to clear out the application registry
        between tests
        """
        testing.tearDown()

    def test_index(self):
        from zopyx.smartprintng.server.views import index
        context = Server()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer('templates/index.pt')
        response = index(context, request)
        print response


class ViewIntegrationTests(unittest.TestCase):
    """ These tests are integration tests for the view.  These test
    the functionality the view *and* its integration with the rest of
    the pyramid framework.  They cause the entire environment to be
    set up and torn down as if your application was running 'for
    real'.  This is a heavy-hammer way of making sure that your tests
    have enough context to run properly, and it tests your view's
    integration with the rest of Pyramid.  You should not use this style
    of test to perform 'true' unit testing as tests will run faster
    and will be easier to write if you use the testing facilities
    provided by Pyramid and only the registrations you need, as in the
    above ViewTests.
    """

    def setUp(self):
        """ This sets up the application registry with the
        registrations your application declares in its configure.zcml
        (including dependent registrations for pyramid itself).
        """
        self.config = testing.setUp()
        import zopyx.smartprintng.server
        import zope.configuration.xmlconfig

    def tearDown(self):
        """ Clear out the application registry """
        testing.tearDown()

    def test_index(self):
        from zopyx.smartprintng.server.views import index
        context = Server()
        request = testing.DummyRequest()
        view = index(context, request)
        result = view()
        self.assertEqual(result.status, '200 OK')
        body = result.app_iter[0]
        self.assertEqual(len(result.headerlist), 2)
        self.assertEqual(result.headerlist[0],
                         ('Content-Type', 'text/html; charset=UTF-8'))
        self.assertEqual(result.headerlist[1], ('Content-Length',
                                                str(len(body))))

    def test_xmlrpc_ping(self):
        from zopyx.smartprintng.server.views import ping
        context = Server()
        headers = dict()
        headers['content-type'] = 'text/xml'
        request = testing.DummyRequest(headers=headers, post=True)
        request.body = xml
        result = ping(context, request)
        self.assertEqual(result.status, '200 OK')
        body = result.app_iter[0]
        params, methodname = xmlrpclib.loads(result.body)
        self.assertEqual(params[0], 'zopyx.smartprintng.server')

    def test_xmlrpc_convertZIP(self):
        from zopyx.smartprintng.server.views import convertZIP
        context = Server()
        headers = dict()
        headers['content-type'] = 'text/xml'
        request = testing.DummyRequest(headers=headers, post=True)
        zip_archive = os.path.join(os.path.dirname(__file__), 'test_data', 'test.zip')
        zip_data = file(zip_archive, 'rb').read()
        params = xmlrpclib.dumps(('', base64.encodestring(zip_data), 'pdf-prince'))
        request.body = xml2 % params
        result = convertZIP(context, request)
        self.assertEqual(result.status, '200 OK')
        body = result.app_iter[0]
        params, methodname = xmlrpclib.loads(result.body)
        output_zipdata = base64.decodestring(params[0])
        output_zip_filename = tempfile.mktemp()
        file(output_zip_filename, 'wb').write(output_zipdata)
        ZIP = zipfile.ZipFile(output_zip_filename, 'r')
        self.assertEqual('output.pdf' in ZIP.namelist(), True)

    def test_xmlrpc_convertZIPandRedirect(self):
        from zopyx.smartprintng.server.views import convertZIPandRedirect
        context = Server()
        headers = dict()
        headers['content-type'] = 'text/xml'
        request = testing.DummyRequest(headers=headers, post=True)
        zip_archive = os.path.join(os.path.dirname(__file__), 'test_data', 'test.zip')
        zip_data = file(zip_archive, 'rb').read()
        params = xmlrpclib.dumps(('', base64.encodestring(zip_data), 'pdf-prince'))
        request.body = xml3 % params
        result = convertZIPandRedirect(context, request)
        self.assertEqual(result.status, '200 OK')
        body = result.app_iter[0]
        params, methodname = xmlrpclib.loads(result.body)
        location = params[0]
        self.assertEqual('deliver?' in location, True)

    def test_deliver_non_existing_filename(self):
        from zopyx.smartprintng.server.views import deliver
        context = Server()
        request = testing.DummyRequest(params=dict(filename='does-not-exist.pdf'))
        result = deliver(context, request)
        self.assertEqual(result.status, '404 Not Found')

    def test_deliver_existing_filename(self):
        from zopyx.smartprintng.server.views import deliver
        context = Server()
        file(os.path.join(context.spool_directory, 'foo.pdf'), 'wb').write('foo')
        request = testing.DummyRequest(params=dict(filename='foo.pdf'))
        result = deliver(context, request)
        self.assertEqual(result.status, '200 OK')
        self.assertEqual(('content-type', 'application/pdf') in result.headerlist, True)
        self.assertEqual(('content-disposition', 'attachment; filename=foo.pdf') in result.headerlist, True)

    def test_deliver_existing_filename_with_prefix(self):
        from zopyx.smartprintng.server.views import deliver
        context = Server()
        file(os.path.join(context.spool_directory, 'foo.pdf'), 'wb').write('foo')
        request = testing.DummyRequest(params=dict(filename='foo.pdf', prefix='bar'))
        result = deliver(context, request)
        self.assertEqual(result.status, '200 OK')
        self.assertEqual(('content-disposition', 'attachment; filename=bar.pdf') in result.headerlist, True)
