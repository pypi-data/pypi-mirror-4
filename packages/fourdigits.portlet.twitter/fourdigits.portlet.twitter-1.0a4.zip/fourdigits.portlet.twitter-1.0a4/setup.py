from setuptools import setup, find_packages
import os

version = '1.0a4'

setup(name='fourdigits.portlet.twitter',
      version=version,
      description="Twitter portlet with multi search, filter, language\
                  filter functionality and number limiter",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='social media twitter 2.0',
      author='Ralph Jacobs',
      author_email='ralph@fourdigits.nl',
      url='http://plone.org/products/fourdigits.portlet.twitter',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['fourdigits', 'fourdigits.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'simplejson',
          'oauth2',
          'collective.js.moment'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
