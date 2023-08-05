zopyx.smartprintng.server
=========================

``zopyx.smartprintng.server`` is a Pyramid based server implementation 
and implements the server side functionality of the Produce & Publish platform.
It is know as the ``Produce & Publish Server``.

Requirements
------------

* Python 2.6, 2.7 (no Python 3 support)

Installation
------------

- create an ``virtualenv`` environment (Python 2.6) - either within your
  current (empty) directory or by letting virtualenv create one for you. 
  (``easy_install virtualenv`` if ``virtualenv`` is not available on your system)::

    virtualenv --no-site-packages .

  or:: 

    virtualenv --no-site-packages smartprintng

- install the SmartPrintNG server::

    bin/easy_install zopyx.smartprintng.server

- create a ``server.ini`` configuration file (and change it according to your needs)::

    [DEFAULT]
    debug = true

    [app:main]
    use = egg:zopyx.smartprintng.server#app
    reload_templates = true
    debug_authorization = false
    debug_notfound = false

    [server:main]
    use = egg:Paste#http
    host = 127.0.0.1
    port = 6543

- start the server (in foreground)::

    bin/pserve server.ini 

- or start it in background::

    bin/pserve server.ini  --daemon

Upgrading
---------

For upgrading an existing SmartPrintNG server you should try the following inside
your virtualenv environment::

    bin/easy_install -U zopyx.smartprintng.server
    bin/easy_install -U zopyx.convert2
   

XMLRPC API
----------

The SmartPrintNG server exposes several methods through XMLRPC::

    def convertZIP(auth_token, zip_archive, converter_name):
        """ 'zip_archive' is ZIP archive (encoded as base-64 byte string).
            The archive must contain exactly *one* HTML file to be converted
            including all related resources like stylesheets and images.
            All files must be stored flat within the archive (no subfolders).
            All references to externals resources like the 'src' attribute
            of the IMG tag or references to the stylesheet(s) must use
            relative paths. The method returns the converted output file
            also as base64-encoded ZIP archive.
        """

    def convertZIPEmail(auth_token, context, zip_archive, converter_name='pdf-prince', 
                        sender=None, recipient=None, subject=None, body=None):
        """ Similar to convertZIP() except that this method will send the 
            converted output document to a recipient by email. 'subject' and
            'body' parameters *must* be utf-8 encoded.
        """

    def availableConverters():
        """ Returns a list of available converter names on the 
            SmartPrintNG backend.
        """

    def authenticate(username, password):
        """ Log into the server. Returns an auth_token. authenticate()
            must be called before calling any of the methods above.
        """

    def ping():
        """ says 'pong' - or something similar """

Email configuration
-------------------

For using the email support through the ``convertZIPEmail()`` the email server must be
configured through a dedicated configuration file. An ``email.ini`` may look like this::

    [mail]
    hostname = smtp.gmail.com
    username = some_username
    password = some_password
    force_tls = False
    no_tls = False

You have to pass the name of the email configuration file to ``pserve`` when starting
then server::

    bin/pserve server.ini mail_config=/path/to/email.ini

Source code
-----------

https://github.com/zopyx/zopyx.smartprintng.server/

Bug tracker
-----------

https://github.com/zopyx/zopyx.smartprintng.server/issues

Support
-------

Support for Produce & Publish Server is currently only available on a project basis.


Contact
-------

| ZOPYX Limited
| Hundskapfklinge 33
| D-72074 Tuebingen, Germany
| info@zopyx.com
| www.zopyx.com


