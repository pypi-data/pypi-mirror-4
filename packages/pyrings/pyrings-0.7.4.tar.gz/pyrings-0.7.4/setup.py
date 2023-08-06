# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import os
import sys
from distutils import log

here = os.path.abspath(os.path.dirname(__file__))
README = "." #open(os.path.join(here, 'README.rst')).read()
NEWS = "." #open(os.path.join(here, 'NEWS.txt')).read()

install_requires = [
    'numpy>=1.1', 
    'fluid'
]

version = '0.7.4'

setup(
    name = 'pyrings',
    version = version,
    description = "Procedures to handle coherent vortexes in the ocean",
    long_description=README + '\n\n' + NEWS,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    keywords='rings, eddies, ADCP, Gradient Balance',
    author='Guilherme Castelao, Luiz Irber',
    author_email='guilherme@castelao.net, luiz.irber@gmail.com',
    url='http://pyrings.castelao.net',
    license='PSF',
    #download_url="https://github.com/castelao/pyrings/archive/master.zip",
    #download_url="http://cheeseshop.python.org/packages/source/P/rings/rings-%s.tar.gz" % version,
    #download_url="https://pypi.python.org/packages/source/r/rings/rings-%s.tar.gz" % version,
    #download_url="https://pypi.python.org/packages/source/r/rings/",
    download_url="https://pypi.python.org/packages/source/p/pyrings/",
    #py_modules=['rings.rings','rings_plots','rings.okuboweiss','okuboweiss_plot','rings.EddyTracking'],
    py_modules=['rings.ring', 'rings.utils', 'rings.fitt','rings.misc.montecarlo'],
    #packages=find_packages(),
    #packages=['rings'],
    zip_safe=True,
    install_requires=install_requires,
    platforms = ['any']
)
