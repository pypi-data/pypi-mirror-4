import os
from distutils.core import setup

# Utility function to read the README file.  
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="tate_bilinear_pairing",
    version="0.6",
    author="Homer Hsing",
    author_email="homer.hsing@gmail.com",
    description=("a library for calculating Tate bilinear pairing especially on super-singular"
                   "elliptic curve E:y^2=x^3-x+1 in affine coordinates defined over a Galois Field GF(3^m)"
                   ),
    license="LGPL",
    keywords="Tate bilinear pairing elliptic curve",
    url="http://pypi.python.org/pypi/tate_bilinear_pairing/",
    packages=['tate_bilinear_pairing', 'tests'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
)
