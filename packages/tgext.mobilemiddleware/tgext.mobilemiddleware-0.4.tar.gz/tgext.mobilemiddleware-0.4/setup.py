from setuptools import setup, find_packages
import os

version = '0.4'

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
except IOError:
    README = ''

setup(name='tgext.mobilemiddleware',
      version=version,
      description="Mobile Middleware utilities for Turbogears 2 detects mobile browsers",
      long_description=README,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Environment :: Web Environment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: TurboGears"
        ],
      keywords='turbogears2.extension pylons',
      author='Alessandro Molina',
      author_email='alessandro.molina@axant.it',
      url='http://bitbucket.org/_amol_/tgext.mobilemiddleware',
      license='LGPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['tgext'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        "TurboGears2 >= 2.2.0"
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
