from setuptools import setup, find_packages
import os

version = '0.2.2'

setup(name='zettwerk.fullcalendar',
      version=version,
      description="Adding jquery.fullcalendar to plone 4",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone, view, calendar, fullcalendar',
      author='zettwerk GmbH',
      author_email='jk@zettwerk.com',
      url='http://svn.plone.org/svn/collective/zettwerk.fullcalendar',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zettwerk'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'simplejson',
          # -*- Extra requirements: -*-
      ],
      extras_require={
        'test': ['Products.PloneTestCase']
        },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
