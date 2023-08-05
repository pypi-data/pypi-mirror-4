##########################################################################
# zopyx.smartprintng.server
# (C) 2008, 2009, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os
import time
import tempfile
import shutil
import mimetypes
import xmlrpclib
import pkg_resources
from stat import ST_CTIME
from pyramid.renderers import render_to_response
from pyramid.view import static_view
from pyramid.view import view_config
from pyramid_xmlrpc import xmlrpc_view
from webob import Response
from models import Server
from logger import LOG

try:
    from zopyx.smartprintng.authentication import authenticateRequest, authorizeRequest
    have_authentication = True
except ImportError:
    from nullauth import authenticateRequest, authorizeRequest
    have_authentication = False

static_view = static_view('templates/static', use_subpath=True)


##################
# HTTP views
##################

@view_config(for_=Server, request_method='GET', permission='read')
class index(object):
    """ The default view providing some system information """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        converters = self.context.availableConverters()
        version = pkg_resources.require('zopyx.smartprintng.server')[0].version 
        params =  dict(context=self.context,
                       project='zopyx.smartprintng.server',
                       version=version,
                       converters=converters)
        return render_to_response('templates/index.pt',
                                  params,
                                  request=self.request)

@view_config(for_=Server, request_method='GET', permission='read', name='selftest')
class selftest(object):
    """ Server selftest """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, converter=None):
        converter = self.request.params['converter']
        test_file = os.path.join(os.path.dirname(__file__), 'test_data', 'test.html')
        result = self.context._convert(test_file, converter)
        if result['status'] == 0:
            output_filename = result['output_filename']
            ct, dummy = mimetypes.guess_type(output_filename)
            basename, ext = os.path.splitext(output_filename)
            headers = [('content-disposition','attachment; filename=selftest-%s%s' % (converter,ext)),
                       ('content-type', ct)]
            return Response(body=file(output_filename, 'rb').read(),
                            content_type=ct,
                            headerlist=headers
                        )
        raise RuntimeError


@view_config(for_=Server, name='deliver')
def deliver(context, request):
    """ Send out a generated output file """

    filename = request.params['filename']
    prefix = request.params.get('prefix')
    dest_filename = os.path.abspath(os.path.join(context.spool_directory, filename))

    # various (security) checks
    if not os.path.exists(dest_filename):
        return Response(status=404)

    if not dest_filename.startswith(context.spool_directory):
        return Response(status=404)

    if time.time() - os.stat(dest_filename)[ST_CTIME] >= context.delivery_max_age:
        return Response(status=404)

    ct, dummy = mimetypes.guess_type(dest_filename)
    filename = os.path.basename(filename)
    if prefix:
        filename = prefix + os.path.splitext(filename)[1]
    headers = [('content-disposition','attachment; filename=%s' % filename),
               ('content-type', ct)]
    return Response(body=file(dest_filename, 'rb').read(),
                    content_type=ct,
                    headerlist=headers
                    )


##################
# XMLRPC views
##################

@view_config(name='authenticate', for_=Server)
@xmlrpc_view
def authenticate(context, username, password):

    if not have_authentication:
        return True

    try:
        return authenticateRequest(username, password)
    except Exception, e:
        msg = 'Authentication failed (%s)' % e
        LOG.error(msg, exc_info=True)
        return xmlrpclib.Fault(123, msg)

@view_config(name='convertZIP', for_=Server)
@xmlrpc_view
def convertZIP(context, auth_token, zip_archive, converter_name='pdf-prince'):

    if not authorizeRequest(auth_token):
        msg = 'Authorization failed'
        LOG.error(msg, exc_info=True)
        return xmlrpclib.Fault(123, msg)

    try:
        return context.convertZIP(zip_archive, converter_name)
    except Exception, e:
        msg = 'Conversion failed (%s)' % e
        LOG.error(msg, exc_info=True)
        return xmlrpclib.Fault(123, msg)


@view_config(name='convertZIPEmail', for_=Server)
@xmlrpc_view
def convertZIPEmail(context, auth_token, zip_archive, converter_name='pdf-prince', sender=None, recipient=None, subject=None, body=None):

    if not authorizeRequest(auth_token):
        msg = 'Authorization failed'
        LOG.error(msg, exc_info=True)
        return xmlrpclib.Fault(123, msg)

    try:
        return context.convertZIPEmail(zip_archive, converter_name, sender, recipient, subject, body)
    except Exception, e:
        msg = 'Conversion failed (%s)' % e
        LOG.error(msg, exc_info=True)
        return xmlrpclib.Fault(123, msg)


@view_config(name='convertZIPandRedirect',  for_=Server)
@xmlrpc_view
def convertZIPandRedirect(context, auth_token, zip_archive, converter_name='prince-pdf', prefix=None):
    """ This view appects a ZIP archive through a POST request containing all
        relevant information (similar to the XMLRPC API). However the converted
        output file is not returned to the caller but delivered "directly" through
        the SmartPrintNG server (through an URL redirection). The 'prefix'
        parameter can be used to override the basename of filename used within the
        content-disposition header.
        (This class is only a base class for the related http_ and xmlrpc_
         view (in order to avoid redudant code).)
    """

    if not authorizeRequest(auth_token):
        msg = 'Authorization failed'
        LOG.error(msg, exc_info=True)
        return xmlrpclib.Fault(123, msg)

    try:
        output_archivename, output_filename = context._processZIP(zip_archive, converter_name)
        output_ext = os.path.splitext(output_filename)[1]

        # take ident from archive name
        ident = os.path.splitext(os.path.basename(output_archivename))[0]

        # move output file to spool directory
        dest_filename = os.path.join(context.spool_directory, '%s%s' % (ident, output_ext))
        rel_output_filename = dest_filename.replace(context.spool_directory + os.sep, '')
        shutil.move(output_filename, dest_filename)
        host = 'localhost'
        port = 6543
        prefix = prefix or ''
        location = 'http://%s:%s/deliver?filename=%s&prefix=%s' % (host, port, rel_output_filename, prefix)
        return location
    except Exception, e:
        msg = 'Conversion failed (%s)' % e
        LOG.error(msg, exc_info=True)
        return xmlrpclib.Fault(123, msg)


@view_config(name='availableConverters', for_=Server)
@xmlrpc_view
def availableConverters(context):
    return context.availableConverters()


@view_config(name='ping', for_=Server)
@xmlrpc_view
def ping(context):
    return 'zopyx.smartprintng.server'

