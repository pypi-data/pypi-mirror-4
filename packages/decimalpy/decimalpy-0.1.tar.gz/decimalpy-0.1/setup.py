#!/usr/bin/python

from distutils.core import setup

with open('README.rst') as file:
    long_description = file.read()

setup(
    name='decimalpy',
    version='0.1',
    author='Niels Henrik Bruun',
    author_email='niels.henrik.bruun@gmail.com',
    url='http://www.bruunisejs.dk/PythonHacks/',
    download_url = "http://pypi.python.org/pypi/decimalpy",
    description='decimalpy - A Decimal based version of numpy',
    long_description=long_description,
    package_dir={'decimalpy': 'decimalpy',
                 'mathematical_meta_code': 'mathematical_meta_code'
                 },
    packages=['decimalpy', 'mathematical_meta_code'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Python Software Foundation License',
        'Programming Language :: Python',
        'Topic :: Education',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Utilities'
        ],
    platforms=["Operating System :: OS Independent"],
    licence='http://www.opensource.org/licenses/PythonSoftFoundation.php'
    )
