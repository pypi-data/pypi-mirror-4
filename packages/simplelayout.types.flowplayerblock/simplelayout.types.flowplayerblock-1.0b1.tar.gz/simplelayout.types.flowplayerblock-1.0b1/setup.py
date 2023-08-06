from setuptools import setup, find_packages
import os

version = '1.0b1'

tests_require = ['ftw.testing',
                 'plone.app.testing', ]

setup(name='simplelayout.types.flowplayerblock',
      version=version,
      description="Flow-player support for simplelayout file blocks.",
      long_description=open("README.rst").read() + "\n" +
          open(os.path.join("docs", "HISTORY.txt")).read(),

      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],

      keywords='',
      author='4teamwork GmbH',
      author_email='mailto:info@4teamwork.ch',
      url='https://github.com/4teamwork/simplelayout.types.flowplayerblock',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['simplelayout', 'simplelayout.types'],
      include_package_data=True,
      zip_safe=False,
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),

      install_requires=[
        'setuptools',
        'simplelayout.base',
        'collective.flowplayer',
        'ftw.upgrade',
        # -*- Extra requirements: -*-
        ],

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
