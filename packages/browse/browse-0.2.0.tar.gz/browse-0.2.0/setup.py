import os, sys, glob
pj = os.path.join

from setuptools import setup, find_packages
from distutils.core import Extension




_MAJOR               = 0
_MINOR               = 2
_MICRO               = 0
version              = '%d.%d.%d' % (_MAJOR, _MINOR, _MICRO)
release              = '%d.%d' % (_MAJOR, _MINOR)


data_files = [ (pj('share', 'data'), glob.glob(os.path.join('share','data', '*.dat')))]

setup(
    name="browse",
    version=version,
    description="Open a web page in a browser, as simple as that...",
    long_description="""""",
    author="Thomas Cokelaer",
    author_email="cokelaer@gmail.com",
    license='LGPL',


    packages = find_packages('src'),
    package_dir={ '' : 'src' },

    # Dependencies
    install_requires = [],
    data_files = data_files,
    platforms=["Linux"],
    classifiers=["Development Status :: 6 - Mature",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
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

