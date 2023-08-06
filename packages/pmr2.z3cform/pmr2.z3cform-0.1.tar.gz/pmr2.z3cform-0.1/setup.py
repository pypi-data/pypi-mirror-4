from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='pmr2.z3cform',
      version=version,
      description="Customized z3c.form and plone.z3cform library for PMR2",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("pmr2", "z3cform", "form.rst")).read() + "\n" +
                       open(os.path.join("pmr2", "z3cform", "page.rst")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.rst")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Tommy Yu',
      author_email='tommy.yu@auckland.ac.nz',
      url='https://github.com/PMR2/pmr2.z3cform',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pmr2'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'plone.z3cform>=0.7.7',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
