#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'pyb_init',
          version = '0.1.7',
          description = 'pybuilder project initialization',
          long_description = '''''',
          author = "Maximilien Riehl",
          author_email = "maximilien.riehl@gmail.com",
          license = 'WTFPL',
          url = 'https://github.com/mriehl/pyb_init',
          scripts = ['pyb-init'],
          packages = ['pyb_init'],
          classifiers = ['Development Status :: 4 - Beta', 'Intended Audience :: Developers', 'License :: Freely Distributable', 'Programming Language :: Python', 'Natural Language :: English', 'Operating System :: Unix', 'Topic :: Software Development :: Build Tools'],
          
          
          install_requires = [ "docopt" ],
          
          zip_safe=True
    )
