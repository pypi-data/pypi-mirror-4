from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='collective.ptg.garagedoor',
      version=version,
      description="garagedoor for plonetruegallery",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plonetruegallery gallery plone addon',
      author='Espen Moe-Nilssen',
      author_email='espen@medialog.no',
      url='https://github.com/collective/collective.ptg.garagedoor',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.ptg'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.plonetruegallery'
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
