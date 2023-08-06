from setuptools import setup, find_packages
import sys, os

try:
    description = file(os.path.join(os.path.dirname(__file__), 'README.txt')).read()
except:
    description = ''

version = '0.2'

setup(name='smartopen',
      version=version,
      description="open text in a browser contextually",
      long_description=description,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Jeff Hammel',
      author_email='k0scist@gmail.com',
      url='http://k0s.org/hg/smartopen',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      smartopen = smartopen.smartopen:main

      [smartopen.locations]
      URL = smartopen.handlers:URL
      GoogleMaps = smartopen.handlers:GoogleMaps
      Wikipedia = smartopen.handlers:Wikipedia
      Wiktionary = smartopen.handlers:Wiktionary
      Google = smartopen.handlers:Google
      Trac = smartopen.handlers:Trac
      Bugzilla = smartopen.handlers:Bugzilla
      FedEx = smartopen.handlers:FedEx
      MercurialRevision = smartopen.handlers:MercurialRevision
      UbuntuPackage = smartopen.handlers:UbuntuPackage
      """,
      )
