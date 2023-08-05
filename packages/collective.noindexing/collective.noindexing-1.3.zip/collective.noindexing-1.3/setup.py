from setuptools import setup, find_packages

version = '1.3'

setup(name='collective.noindexing',
      version=version,
      description="Ignore all indexing operations",
      long_description=(open("README.txt").read() + "\n" +
                        open("CHANGES.rst").read()),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Framework :: Plone :: 3.3",
          "Framework :: Plone :: 4.0",
          "Framework :: Plone :: 4.1",
          "Programming Language :: Python",
          ],
      keywords='',
      author='Maurits van Rees',
      author_email='m.van.rees@zestsoftware.nl',
      url='https://github.com/collective/collective.noindexing',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.Archetypes',
          'Products.CMFCore',
      ],
      extras_require={
          'test': ['plone.app.testing',
                   'unittest2',
                   'zope.configuration',
                   'zope.component'],
      },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
