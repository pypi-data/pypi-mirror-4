from setuptools import setup, find_packages
import os

version = '0.3'

setup(name='adi.simplesite',
      version=version,
      description="Configs for small sites",
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
      author_email='contact@ida-ebkes.eu',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['adi'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'adi.dropdownmenu',
          'adi.init',
          'adi.samplecontent',
          'adi.simplestructure',
          'adi.slickstyle',
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
