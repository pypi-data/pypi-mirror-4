import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = """por.gdata
=============

for more details visit: http://getpenelope.github.com/"""
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'gdata==2.0.14',
    'PasteScript',
    'python-dateutil==1.5'
    ]

if sys.version_info[:3] < (2,5,0):
    requires.append('pysqlite')

setup(name='por.gdata',
      version='1.6',
      description='Penelope gdata integration',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Penelope Team',
      author_email='penelopedev@redturtle.it',
      url='http://getpenelope.github.com',
      keywords='web wsgi bfg pylons pyramid',
      namespace_packages=['por'],
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='por.gdata',
      install_requires = requires,
      entry_points = """\
      """,
      )

