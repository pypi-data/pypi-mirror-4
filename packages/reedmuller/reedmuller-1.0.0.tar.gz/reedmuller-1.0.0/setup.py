#!/usr/bin/env python

from setuptools import setup
setup(name='reedmuller',
      version='1.0.0',
      description='Implementation of Reed-Muller codes.',
      author='Sebastian Raaphorst',
      author_email='srcoding@gmail.com',
      url='http://www.site.uottawa.ca/~mraap046',
      packages=['reedmuller'],
      long_description="""
      A package providing an implementation of Reed-Muller codes for Python.
      A brief description of Reed-Muller codes can be found both on my webpage:
      http://www.site.uottawa.ca/~mraap046
      and at Wikipedia:
      http://en.wikipedia.org/wiki/Reed-Muller
      A Reed-Muller encoder / decoder RM(r,m) can be created through the class
      ReedMuller, and words (as 0-1 lists) of the appropriate size can be
      encoded / decoded.

      1.0.0: Initial release. Complete functionality implemented.
      """,
      classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'Topic :: Education',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Security :: Cryptography',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],
      keywords='reed-muller reed muller code codes coding design error-correcting binary',
      license='Apache 2.0'
      )
