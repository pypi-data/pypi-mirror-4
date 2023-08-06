from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='quintagroup.silogroup',
      version=version,
      description="SiloGroup allows to generate custom navigation menu titles,"
                  " hide or make them visible.",
      long_description=open("README.rst").read() + "\n" +
      open(os.path.join("docs", "HISTORY.rst")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
      ],
      keywords='navigation title',
      author='Quintagroup',
      author_email='support@quintagroup.com',
      url='https://github.com/quintagroup/quintagroup.silogroup',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['quintagroup'],
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
