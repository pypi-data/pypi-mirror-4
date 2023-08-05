Changelog
=========

1.1.2 (2012/10/14)
------------------
* documentation updated

1.1.1 (2012/02/03)
------------------
* better self-test page (more text, some images)
* updated dependencies

1.1.0 (2011/08/22)
------------------
* compatibility with Pyramid 1.1

1.0.1 (2011/01/30)
------------------
* compatibility with Pyramid 1.0b3+

1.0.0 (2011/01/16)
------------------
* final release
* fixed test fixtures

0.7.1 (2011/01/10)
------------------
* pinned pyramid_xmlrpc 0.1

0.7.0 (2010/12/11)
------------------
* converted to Pyramid

0.6.7 (2010/07/18)
------------------
* adjusted company name

0.6.6 (2010/05/15)
------------------
* include conversion result into ZIP file

0.6.5 (2010/02/04)
------------------
* fixed racing condition in cleanup code

0.6.4 (2009/12/25)
------------------
* minor fixes
* documentation cleanup

0.6.3 (2009/11/29)
------------------
* compatiblity with BFG 1.2

0.6.1 (2009/10/04)
------------------
* fixed bug in code for cleaning up the spool_directory

0.6.0 (2009/09/15)
------------------
* authentication and authorization support

0.5.2 (2009/09/05)
------------------
* adjusted to newest zopyx.convert2 version


0.6.0 (2009/09/15)
------------------
* added authentication and authorization support

0.5.2 (2009/09/05)
------------------
* adjusted to newest zopyx.convert2 version

0.5.1 (2009/08/01)
------------------

* added convertZIPandRedirect() method
* added deliver() method
* moved base.ServerCore to models.py
* delivered files must be younger than 'delivery_max_age' seconds
* cleanup code
* internal refactoring
* more tests

0.5.0 (2009/07/23)
------------------
* now requires Python 2.6

0.4.3 (2009/07/22)
------------------

* removed most of the ZCML configuration
* tests, tests, tests
 
0.4.2 (2009/07/19)
------------------

* switching back to zope.sendmail
* implemented asynchronous mail delivery on top of zope.sendmail


0.4.1 (2009/07/19)
------------------

* using repoze.sendmail

0.4.0 (2009/07/19)
------------------

* added convertZIPEmail() API

0.3.4 (2009/07/13)
------------------

* updated documentation


0.3.3 (2009/07/12)
------------------

* fix for missing BASE tag within HTML files

0.3.2 (2009/07/12)
------------------

* better logging


0.3.1 (2009/07/08)
------------------

* disabled check for maximum size of the request within
  parse_xmlrpc_request() since 8MB is too small for us


0.3.0 (2009/07/06)
------------------

* switched to repoze.bfg

0.2.0 (2009/07/06)
------------------

* improved handling of temporary directories


0.1.2 (2009/07/05)
------------------

* improved handling of temporary directories

0.1.1 (2009/07/05)
------------------

* improved logging and error handling

0.1 (2009/07/05)
----------------

* Initial release
