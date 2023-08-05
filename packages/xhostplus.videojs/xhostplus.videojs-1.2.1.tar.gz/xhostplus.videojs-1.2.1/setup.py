# -*- coding: utf-8 -*-
"""
This module contains the tool of xhostplus.videojs
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.2.1'

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    )

tests_require=['zope.testing']

setup(name='xhostplus.videojs',
      version=version,
      description="A javascript videoplayer with flash fallback",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='plone zope videojs html5 flash multimedia',
      author='Andreas Stocker',
      author_email='andreas.stocker@xhostplus.at',
      url='http://www.xhostplus.at/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['xhostplus', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        # -*- Extra requirements: -*-
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'xhostplus.videojs.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*-
      [distutils.setup_keywords]
      paster_plugins = setuptools.dist:assert_string_list

      [egg_info.writers]
      paster_plugins.txt = setuptools.command.egg_info:write_arg
      """,
      paster_plugins = ["ZopeSkel"],
      )
