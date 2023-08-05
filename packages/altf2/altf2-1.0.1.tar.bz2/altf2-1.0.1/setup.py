#!/usr/bin/env python
version = '1.0.1'
from setuptools import setup, find_packages

if __name__ == '__main__':
    setup(name='altf2',
          version=version,
          description='Simple program runner (Alt-F2 handler). Requires PyQt4',
          author='Alexey Loshkarev',
          author_email='elf2001@gmail.com',
          url='https://bitbucket.org/angry_elf/altf2',
          packages=find_packages(),
          license='GPL',
          classifiers=[
              "Development Status :: 5 - Production/Stable",
              "Environment :: X11 Applications",
              "Environment :: X11 Applications :: Qt",
              "Intended Audience :: End Users/Desktop",
              "License :: OSI Approved :: GNU General Public License (GPL)",
              "Natural Language :: English",
              "Programming Language :: Python",
              "Operating System :: POSIX",
              "Topic :: Desktop Environment",
              "Topic :: Utilities",
              ],
          entry_points={
              'console_scripts': [
                  'altf2 = altf2.app:main',
              ]
          }
          )
