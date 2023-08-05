from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='adi.slickstyle',
      version=version,
      description="A slick style for Plone portals, easily extendable for your own styles.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Ida Ebkes',
      author_email='contactqida-ebkes.eu',
      url='http://svn.plone.org/svn/collective/adi.slickstyle',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['adi'],
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
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
