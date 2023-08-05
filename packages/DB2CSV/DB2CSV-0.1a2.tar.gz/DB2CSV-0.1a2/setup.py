import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'SQLAlchemy == 0.7.9'
    ]

setup(name='DB2CSV',
      version='0.1a2',
      description='Tool to dump all database tables into csv files.',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Database"
        ],
      author='Stefano Fontanelli',
      author_email='s.fontanelli@asidev.com',
      url='',
      keywords='database sqlalchemy archive tools',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="tests",
      entry_points = "",
      scripts=['scripts/db2csv_archive']
      )

