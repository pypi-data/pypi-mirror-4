#!/usr/bin/env python
version = '1.0.27'
from setuptools import setup, find_packages
if __name__ == '__main__':
    setup(name='couchdb-python-curl',
          version=version,
          description='CouchDB-python wrapper (using cURL library)',
          author='Alexey Loshkarev',
          author_email='elf2001@gmail.com',
          url='http://code.google.com/p/couchdb-python-curl/',
          packages=find_packages(),
          license='GPL',
          classifiers=[
              "Development Status :: 5 - Production/Stable", 
              "Intended Audience :: Developers",
              "License :: OSI Approved :: GNU General Public License (GPL)",
              "Natural Language :: English",
              "Programming Language :: Python",
              "Topic :: Software Development :: Libraries :: Python Modules",
              "Topic :: Database :: Front-Ends",
              ],
#          install_requires=['pycurl'],
          entry_points={
              'console_scripts': [
                  'couchdb-curl-pinger = couchdbcurl.pinger:main',
                  'couchdb-curl-dbcompact = couchdbcurl.dbcompact:main',
                  'couchdb-curl-viewserver = couchdbcurl.view:main',
                  'couchdb-curl-dump = couchdbcurl.tools.dump:main',
                  'couchdb-curl-load = couchdbcurl.tools.load:main',
                  'couchdb-curl-replicate = couchdbcurl.tools.replication_helper:main'
              ]
          }
          )
