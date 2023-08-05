from setuptools import setup, find_packages
import os

version = '1.0.6'

setup(name='Products.PloneboardComments',
      version=version,
      description="Tool for connecting Ploneboard to content, to make it discussable in Ploneboard forums",
      long_description=open(os.path.join("Products", "PloneboardComments", "README.txt")).read() + '\n\n' +\
          open(os.path.join("Products", "PloneboardComments", "CHANGES.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='python plone ploneboard discussion',
      author='Morten W. Petersen',
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
