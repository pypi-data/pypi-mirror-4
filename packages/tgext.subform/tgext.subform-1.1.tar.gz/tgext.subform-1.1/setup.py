from setuptools import setup, find_packages
import os

version = '1.1'

long_description = (
    open('README.txt').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='tgext.subform',
      version=version,
      description="Allows users to create TG applications with CRUD-cabable ajax subforms.",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='turbogears tg tgext crud admin',
      author='Christopher Perkins',
      author_email='chris@percious.com',
      url='http://svn.plone.org/svn/collective/',
      license='mit',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['tgext', 'tgext.subform'],
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
