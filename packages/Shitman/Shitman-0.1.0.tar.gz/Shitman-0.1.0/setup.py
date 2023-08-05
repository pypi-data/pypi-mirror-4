#!/usr/bin/env python
from setuptools import setup, find_packages


setup(name='Shitman',
      version='0.1.0',
      description='Yet Another IRC bot',
      author='Sameer Rahmani',
      author_email='lxsameer@gnu.org',
      url='https://bitbucket.org/lxsameer/shitman/overview',
      license='GPL v2',
      scripts=["shitman"],
      keywords="IRC bot",
      install_requires=["twisted", ],
      packages=find_packages(),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities',
          ]
)
