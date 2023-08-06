#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'yadtreceiver',
          version = '0.1.10',
          description = 'Executes yadtshell commands triggered by a yadtbroadcaster.',
          long_description = '''''',
          author = "Arne Hilmann, Maximilien Riehl, Michael Gruber",
          author_email = "arne.hilmann@gmail.com, maximilien.riehl@gmail.com, aelgru@gmail.com",
          license = 'GNU GPL v3',
          url = 'https://github.com/yadt/yadtreceiver',
          scripts = [],
          packages = ['yadtreceiver'],
          classifiers = ['Development Status :: 3 - Alpha', 'Programming Language :: Python'],
          data_files = [('/etc/twisted-taps/', ['yadtreceiver/yadtreceiver.tac']), ('/etc/init.d/', ['yadtreceiver/yadtreceiver'])],
          
          install_requires = [ "PyYAML", "Twisted", "yadtbroadcast-client" ],
          
          zip_safe=True
    )
