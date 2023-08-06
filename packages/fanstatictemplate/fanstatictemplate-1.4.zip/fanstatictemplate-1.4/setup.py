import sys
import os
from setuptools import setup, find_packages

version = '1.4'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(name='fanstatictemplate',
      version=version,
      description="Fanstatic package template",
      long_description=long_description,
      author='Fanstatic Developers',
      author_email='fanstatic@googlegroups.com',
      url='http://fanstatic.org',
      license='BSD',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'PasteScript',
      ],
      extras_require=dict(test=['pytest',]),
      entry_points={
          'paste.paster_create_template':
              ['fanstatic = fanstatictemplate:Template']},
      )
