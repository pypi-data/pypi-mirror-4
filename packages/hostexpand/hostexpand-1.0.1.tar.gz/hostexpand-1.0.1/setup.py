#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'hostexpand',
          version = '1.0.1',
          description = 'A tool to expand hostnames based on a pattern language and DNS resolution',
          long_description = '''''',
          author = "Arne Hilmann, Alexander Metzner, Udo Juettner",
          author_email = "arne.hilmann@gmail.com, alexander.metzner@gmail.com, udo.juettner@gmail.com",
          license = 'GNU GPL v3',
          url = 'https://github.com/yadt/hostexpand',
          scripts = ['scripts/hostexpand'],
          packages = ['hostexpand'],
          classifiers = ['Development Status :: 5 - Production/Stable', 'Environment :: Console', 'Intended Audience :: Developers', 'Intended Audience :: System Administrators', 'License :: OSI Approved :: GNU General Public License (GPL)', 'Programming Language :: Python', 'Topic :: System :: Networking', 'Topic :: System :: Software Distribution', 'Topic :: System :: Systems Administration'],
          
          
          install_requires = [ "dnspython==1.9.4" ],
          
          zip_safe=True
    )
