from setuptools import setup, find_packages
import os

version = '1.0a'

setup(name='Products.AccessibleReferenceBrowserWidget',
      version=version,
      description="Provides an accessible (for visually impaired) users based on HTML only (no Javascript).",
      long_description=open(os.path.join("Products", "AccessibleReferenceBrowserWidget", "readme.txt")).read() + '\n\n' +\
                       open(os.path.join("Products", "AccessibleReferenceBrowserWidget", "changes.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='python zope plone accessibility reference',
      author='Morten W. Petersen',
      author_email='morten@nidelven-it.no',
      url='http://www.nidelven-it.no/d',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products', 'Products.AccessibleReferenceBrowserWidget'],
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
