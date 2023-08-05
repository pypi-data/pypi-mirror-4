#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'yadtshell',
          version = '1.3.12',
          description = 'YADT - an Augmented Deployment Tool - The Shell Part',
          long_description = '''YADT - an Augmented Deployment Tool - The Shell Part
- regards the dependencies between services, over different hosts
- updates artefacts in a safe manner
- issues multiple commands in parallel on severall hosts

for more documentation, visit http://code.google.com/p/yadt/wiki/YadtCommands
''',
          author = "Arne Hilmann",
          author_email = "arne.hilmann@gmail.com",
          license = 'GNU GPL v3',
          url = 'https://github.com/yadt/yadtshell',
          scripts = ['scripts/yadtshell-activate', 'scripts/yadtshell', 'scripts/yadtshellrc', 'scripts/sync_logs_of_target.py', 'scripts/init-yadtshell', 'scripts/sync_logs_of_all_targets'],
          packages = ['yadtshell'],
          classifiers = ['Development Status :: 4 - Beta', 'Environment :: Console', 'Intended Audience :: Developers', 'Intended Audience :: System Administrators', 'License :: OSI Approved :: GNU General Public License (GPL)', 'Programming Language :: Python', 'Topic :: System :: Networking', 'Topic :: System :: Software Distribution', 'Topic :: System :: Systems Administration'],
          
          
          install_requires = [ "PyYAML", "Twisted", "hostexpand" ],
          
          zip_safe=True
    )
