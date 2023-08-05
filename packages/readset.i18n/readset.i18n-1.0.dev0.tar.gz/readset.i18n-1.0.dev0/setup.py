from setuptools import setup, find_packages
import os

version = '1.0.dev0'

setup(name='readset.i18n',
      version=version,
      description="This package provides a Normalizer for Chinese character",
      long_description=open("README.rst").read() + "\n" +
                       open("CHANGES.rst").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Environment :: Web Environment",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        ],
      keywords='i18n l10n Plone',
      author='Jian Aijun',
      author_email='jianaijun@gmail.com',
      url='http://pypi.python.org/pypi/readset.i18n',
      license='GPL version 2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['readset'],
      include_package_data=True,
      zip_safe=False,
      test_suite="readset.i18n",
      install_requires=[
          'setuptools',
          'zope.interface',
          'plone.memoize',
          'plone.i18n',
      ],
      extras_require={
          'test': [
                   'zope.component [zcml]',
                   'zope.configuration',
                   'plone.app.testing',
                   ]
      },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
)
