import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'readme.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
]

development_requires = [
    'nose',
    'flake8',
    'coverage',
]

setup(name='hashish',
      version='0.1.1',
      description='Password Hashing Library',
      long_description=README + '\n\n' +  CHANGES,
      py_modules=['hashish'],
      author='Russell Hay',
      author_email='me@russellhay.com',
      url='https://bitbucket.org/russellhay/hashish',
      keywords='',
      include_package_data=True,
      zip_safe=False,
      test_suite='tests',
      install_requires=requires,
      tests_require=development_requires,
      )
