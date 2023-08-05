from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='ploomcake.xhtmlstrict_theme',
      version=version,
      description="This theme adds a xhtml strict templates to ploomcake.theme",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Maurizio Lupo',
      author_email='maurizio.lupo@redomino.com',
      url='https://github.com/ploomcake/ploomcake.xhtmlstrict_theme',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ploomcake'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'ploomcake.theme' 
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
#      setup_requires=["PasteScript"],
#      paster_plugins=["ZopeSkel"],
      )
