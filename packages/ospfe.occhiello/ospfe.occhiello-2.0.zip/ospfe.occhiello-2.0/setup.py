from setuptools import setup, find_packages
import os

version = '2.0'

tests_require = ['plone.app.testing', ]

setup(name='ospfe.occhiello',
      version=version,
      description="Add a new Plone introduction field (half-title), displayed before document title",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Plone",
        "Framework :: Plone :: 4.2",
        "Programming Language :: Python",
        ],
      keywords='plone title field plonegov half-title',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='https://github.com/RedTurtle/ospfe.occhiello',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ospfe'],
      include_package_data=True,
      zip_safe=False,
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      install_requires=[
          'setuptools',
          'archetypes.schemaextender',
          'plone.app.registry',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
