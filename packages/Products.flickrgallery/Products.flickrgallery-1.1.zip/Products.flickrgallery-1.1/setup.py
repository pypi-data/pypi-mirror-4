from setuptools import setup, find_packages
import os

version = '1.1'

setup(name='Products.flickrgallery',
      version=version,
      description="A Gallery product for Plone, powered by Flickr",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='david@alteroo.com',
      url='https://github.com/collective/Products.flickrgallery',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.DataGridField',
          'collective.colorbox',
          'flickrapi',
          # -*- Extra requirements: -*-
      ],
      extras_require = {'test':['plone.app.testing']},
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
