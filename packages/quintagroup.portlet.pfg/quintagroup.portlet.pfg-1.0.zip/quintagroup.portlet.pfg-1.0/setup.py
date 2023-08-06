from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='quintagroup.portlet.pfg',
      version=version,
      description="Render form created by PloneFormGen package.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='portlet pfg',
      author='Quintagroup',
      author_email='support@quintagroup.com',
      url='http://projects.quintagroup.com/products',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['quintagroup', 'quintagroup.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.PloneFormGen',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
