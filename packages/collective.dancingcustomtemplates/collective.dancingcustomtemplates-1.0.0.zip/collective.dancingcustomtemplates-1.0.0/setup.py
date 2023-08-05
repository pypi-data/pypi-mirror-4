from setuptools import setup, find_packages
import os

version = '1.0.0'

setup(name='collective.dancingcustomtemplates',
      version=version,
      description="A product that customize some templates for S&D",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        "Framework :: Plone :: 3.3",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.2",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='newsletter custom singing dancing',
      author='RedTurtle',
      author_email='sviluppoplone@redturtle.it',
      url='http://plone.org/products/collective.dancingcustomtemplates',
      license='gpl',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.monkeypatcher',
          'collective.dancing',
      ],
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
