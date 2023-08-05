# -*- coding: utf-8 -*-
import sys

#from distutils.core import setup
from setuptools import setup

version = '1.0.0'

setup(name="PySpotCam", version=version,
      author=u'Pierre Cladé', author_email="pierre.clade@spectro.jussieu.fr",
      maintainer=u'Pierre Cladé',
      maintainer_email="pierre.clade@spectro.jussieu.fr",
      url='http://packages.python.org/PySpotCam/',
      license='''\
This software can be used under one of the following two licenses: \
(1) The BSD license. \
(2) Any other license, as long as it is obtained from the original \
author.''',

      description='Interface to the SpotCam driver.',

      long_description=u'''\
Overview
========

This module provides a Python interface to the SpotCam driver from `SPOT Imaging Solutions`_

Installation
============

You need to install the driver from `SPOT Imaging Solutions`_.

To install PySpotCam, download the `package`_ and run the command 

.. code-block:: sh

   python setup.py install

You can also directly **move** the :file:`PySpotCam` directory to a location
that Python can import from (directory in which scripts 
using :mod:`PyDAQmx` are run, etc.)

Usage
=====

Here is a small example ::

    from PySpotCam.spot import SpotClass

    Spot = SpotClass()

    Spot.BitDepth = max(Spot.BitDepths) # Set the BitDepth to the max value
    Spot.ExternalTriggerMode = 1
    Spot.SetExposure(gain=1, time=2)

    image = Spot.GetImage()

    print Spot.VersionInfo2

Almost all the functions described in the SPOTCam API are implemented.

Contact
=======

Please send bug reports or feedback to `Pierre Cladé`_.

.. _SPOT Imaging Solutions: http://www.spotimaging.com/
.. _package: http://pypi.python.org/pypi/PySpotCam/
.. _Pierre Cladé: mailto:pierre.clade@spectro.jussieu.fr
'''
,  
      keywords=['SpotCam', 'SPOT Imaging Solutions', 'Camera'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Other Audience',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'], 
     packages=["PySpotCam"]
)
