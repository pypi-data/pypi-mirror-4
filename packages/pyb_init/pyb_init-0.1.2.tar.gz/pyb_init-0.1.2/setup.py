#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'pyb_init',
          version = '0.1.2',
          description = '',
          long_description = '''''',
          author = "Maximilien Riehl",
          author_email = "maximilien.riehl@gmail.com",
          license = 'WTFPL',
          url = 'https://github.com/mriehl/pyb_init',
          scripts = ['pyb-init'],
          packages = ['pyb_init'],
          classifiers = ['Development Status :: 3 - Alpha', 'Programming Language :: Python'],
          
          
          install_requires = [ "docopt" ],
          
          zip_safe=True
    )
