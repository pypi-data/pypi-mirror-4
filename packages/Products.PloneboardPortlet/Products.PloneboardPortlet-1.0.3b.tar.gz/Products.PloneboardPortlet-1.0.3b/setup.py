from setuptools import setup, find_packages
import os

version = '1.0.3b'

setup(name='Products.PloneboardPortlet',
      version=version,
      description="An alternative ploneboard display portlet",
      long_description=open(os.path.join("Products", "PloneboardPortlet", "readme.txt")).read() + '\n\n' +\
          open(os.path.join("Products", "PloneboardPortlet", "changes.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='python plone ploneboard portlet',
      author='Nidelven IT',
      author_email='info@nidelven-it.no',
      url='http://www.nidelven-it.no/d',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
