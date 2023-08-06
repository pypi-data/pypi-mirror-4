from setuptools import setup, find_packages
import os

version = '0.1.8'

setup(name='uwosh.portaltabssearchbox',
      version=version,
      description="moves search box into portal tabs",
      long_description=open("README.md").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='portal tabs,search box,viewlet',
      author='T. Kim Nguyen',
      author_email='nguyen@uwosh.edu',
      url='http://plone.org/products/uwosh.portaltabssearchbox',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['uwosh'],
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
#      setup_requires=["PasteScript"],
#      paster_plugins=["ZopeSkel"],
      )
