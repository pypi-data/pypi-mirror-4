from setuptools import setup, find_packages
import os

version = '1.2'

setup(name='collective.local.userlisting',
      version=version,
      description="Provides a view on contents that displays the list of users having a role on it.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords="auth, project",
      author="Thomas Desvenain",
      author_email="thomas.desvenain@gmail.com",
      url="http://svn.plone.org/svn/collective/collective.local.userlisting",
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
