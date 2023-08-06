#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'yadtbroadcast-client',
          version = '1.1.1',
          description = 'YADT - an Augmented Deployment Tool - The Broadcast Client Part',
          long_description = '''Yet Another Deployment Tool - The Broadcast Client Part
- sends state information to a Yadt Broadcast Server instance
- sends information on start/stop/status/update
''',
          author = "Arne Hilmann",
          author_email = "arne.hilmann@gmail.com",
          license = 'GNU GPL v3',
          url = 'http://github.com/yadt/yadtbroadcast-client',
          scripts = [],
          packages = ['yadtbroadcastclient'],
          classifiers = ['Development Status :: 4 - Beta', 'Environment :: Console', 'Intended Audience :: Developers', 'Intended Audience :: System Administrators', 'License :: OSI Approved :: GNU General Public License (GPL)', 'Programming Language :: Python', 'Topic :: System :: Networking', 'Topic :: System :: Software Distribution', 'Topic :: System :: Systems Administration'],
          
          
          install_requires = [ "Twisted", "autobahn" ],
          
          zip_safe=True
    )
