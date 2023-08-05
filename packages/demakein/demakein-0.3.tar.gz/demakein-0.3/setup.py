#!/usr/bin/env python

from distutils.core import setup

setup(name='demakein',
      version='0.3',
      description='Design woodwind instruments and make them with a 3D printer or CNC mill.',
      
      packages = [
          'demakein', 
          'demakein.raphs_curves',
      ],
      
      scripts=[
          'scripts/demakein'
      ],

      classifiers = [
          'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
      ],
      
      install_requires = [ 
          'nesoni', 
          'cffi' ,
      ],
      
      url = 'http://www.logarithmic.net/pfh/design',
      author = 'Paul Harrison',
      author_email = 'pfh@logarithmic.net',
)
