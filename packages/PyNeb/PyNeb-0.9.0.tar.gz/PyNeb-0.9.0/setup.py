#!/usr/bin/env python

from distutils.core import setup
import pyneb

setup(name='PyNeb', 
      version=pyneb.__version__,
      description='Nebular tools',
      author='Christophe Morisset, Valentina Luridiana, Dick Shaw',
      author_email='pynebular@gmail.com',
      url='',
      py_modules=['pyneb.test.unitTest'],
      packages=['pyneb','pyneb.core','pyneb.plot','pyneb.utils','pyneb.extinction',
                ],
      package_data={'pyneb':['atomic_data_fits/*.fits'],
                    'pyneb.extinction':['*.txt'],
                    }
     )

