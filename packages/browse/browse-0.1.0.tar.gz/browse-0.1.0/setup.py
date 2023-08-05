import os, sys, glob
pj = os.path.join

from setuptools import setup, find_packages
from distutils.core import Extension




_MAJOR               = 0
_MINOR               = 1
_MICRO               = 0
version              = '%d.%d.%d' % (_MAJOR, _MINOR, _MICRO)
release              = '%d.%d' % (_MAJOR, _MINOR)


data_files = [ (pj('share', 'data'), glob.glob(os.path.join('share','data', '*.dat')))]

setup(
    name="browse",
    version=version,
    description="open a web page in a browser",
    long_description="""""",
    author="Thomas Cokelaer",
    author_email="cokelaer@gmail.com",
    url='http://www.assembla.com/spaces/PySpectrum/wiki',
    license='LGPL',


    packages = find_packages('src'),
    package_dir={ '' : 'src' },

    # Dependencies
    install_requires = [],
    data_files = data_files,
    platforms=["Linux"],
    classifiers=["Development Status :: 1 - Planning",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Telecommunications Industry",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
        "Programming Language :: Python :: 2.7",
        "Topic :: Scientific/Engineering",
        ]   ,

 entry_points = {
        'console_scripts': [
            'browse=browse.browser:main',
        ]
        },


)

