from setuptools import setup, find_packages
import os

version = '2.0.1'

setup(name='redturtle.portlet.contextualsearch',
      version=version,
      description="A contextual search portlet",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone portlet search contextual',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='http://svn.plone.org/svn/collective/redturtle.portlet.contextualsearch/trunk',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['redturtle', 'redturtle.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
