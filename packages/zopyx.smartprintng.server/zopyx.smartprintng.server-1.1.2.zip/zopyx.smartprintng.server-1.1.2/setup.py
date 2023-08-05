##########################################################################
# zopyx.smartprintng.server
# (C) 2008, 2009, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import sys
import os
from setuptools import setup, find_packages

if sys.version_info < (2,6):
    raise RuntimeError('Please use Python 2.6.X or 2.7.X')

version = '1.1.2'

setup(name='zopyx.smartprintng.server',
      version=version,
      description="ZOPYX SmartPrintNG Server",
      long_description=open(os.path.join('docs', 'source', 'README.rst')).read() + "\n" +
                       open(os.path.join('docs', 'source', 'HISTORY.rst')).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='SmartPrintNG Conversion Pyramid',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      url='http://www.zopyx.com/projects/smartprintng',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zopyx', 'zopyx.smartprintng'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'pastescript',
          'pyramid',
          'pyramid_zcml',
          'pyramid_xmlrpc==0.1',
          'uuid',
          'zopyx.convert2',
          'zope.sendmail',
          'transaction',
          # -*- Extra requirements: -*-
      ],
      test_suite='nose.collector',
      tests_require=('nose',),
      entry_points="""\
      [paste.app_factory]
      app = zopyx.smartprintng.server.run:app
      """
      )
