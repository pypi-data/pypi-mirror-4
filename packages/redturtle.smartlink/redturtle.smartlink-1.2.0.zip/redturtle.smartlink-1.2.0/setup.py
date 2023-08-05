# -*- coding: utf-8 -*-

import os, sys
from setuptools import setup, find_packages

version = '1.2.0'

tests_require = ['zope.testing', 'Products.PloneTestCase']

install_requires = ['setuptools', 'plone.app.imaging']
# what I read there seems not working propery for Plone 3.3
# http://plone.org/documentation/manual/upgrade-guide/version/upgrading-plone-4.0-to-4.1/referencemanual-all-pages
if sys.version_info < (2, 6):
    install_requires.append('Plone')
    install_requires.append('collective.relateditems')
else:
    install_requires.append('Products.CMFPlone')

setup(name='redturtle.smartlink',
      version=version,
      description=("An advanced Link content type for Plone, "
                   "with image field, customizable content icon and internal link feature"),
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Plone',
        'Framework :: Plone :: 3.3',
        'Framework :: Plone :: 4.0',
        'Framework :: Plone :: 4.1',
        'Framework :: Plone :: 4.2',
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='plone archetype link internal content plonegov',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='http://plone.org/products/redturtle.smartlink',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['redturtle', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='redturtle.smartlink.tests.test_docs.test_suite',
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
