from setuptools import setup, find_packages
import sys, os

version = '0.2.3'

readme = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'README.txt')

if os.path.exists(readme):
  description = file(readme).read()
else:
  description = ''

setup(name='bzconsole',
      version=version,
      description='console API to bugzilla',
      long_description=description,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Jeff Hammel',
      author_email='jhammel@mozilla.com',
      url='http://k0s.org/mozilla/hg/bzconsole',
      license='MPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
        'simplejson'
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      bz = bzconsole.main:main
      """,
      )
