##########################################################################
# zopyx.smartprintng.server
# (C) 2008, 2009, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

# Monkey patches

import xmlrpclib
def parse_xmlrpc_request(request):
    """ original code without DOS check """
    params, method = xmlrpclib.loads(request.body)
    return params, method

import pyramid_xmlrpc
pyramid_xmlrpc.parse_xmlrpc_request = parse_xmlrpc_request

# initialize mimetypes on our own to avoid stupid
# recursion error in guess_type()
import mimetypes
mimetypes.init()

# init email subsystem
import mail_util
