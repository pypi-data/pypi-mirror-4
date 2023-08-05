RELEASE = True

from setuptools import setup, find_packages
import sys, os

classifiers = """\
Development Status :: 5 - Production/Stable
Environment :: Console
Intended Audience :: Developers
Intended Audience :: Science/Research
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python
Topic :: Scientific/Engineering
Topic :: Software Development :: Libraries :: Python Modules
"""

version = '0.1.6'

setup(
        name='Puppy',
        version=version,
        description="DSL for creating NetCDF files",
        long_description="""\
A DSL for creating NetCDF files. Here's a simple example::

    from pup import *

    class Test(NetCDF):
        # NC_GLOBAL attributes go here
        history = 'Created for a test'

        # dimensions need to be set explicitly only when they
        # have no variable associated with them
        dim0 = Dimension(2)

        # variables that don't specify dimensions are assumed to
        # be their own dimension
        time = Variable(range(10), record=True, units='days since 2008-01-01')

        # now a variable with dimensions (time,)
        temperature = Variable(range(10), (time,), units='deg C')

    Test.save('simple.nc')

This will produce the following NetCDF file::

    netcdf simple {
    dimensions:
        dim0 = 2 ;
        time = UNLIMITED ; // (10 currently)
    variables:
        int time(time) ;
            time:units = "days since 2008-01-01" ;
        int temperature(time) ;
            temperature:units = "deg C" ;

    // global attributes:
            :history = "Created for a test" ;
    data:

     time = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ;

     temperature = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ;
    }

By default it uses pupynere for creating files, but this can be overloaded; we
can use the netCDF4 module, for example, which allows us to specify groups::

    from netCDF4 import Dataset

    class Test(NetCDF):
        loader = Dataset
        ...

        foo = Group(
            dim = Dimension(10),
            var = Variable(range(10)),
            ...
        )
    Test.save('simple.nc', format='NETCDF4')

Changelog:

:0.1.6:   Fix bug in dimension name.
:0.1.5:   Added support for Groups when using netcdf4.
:0.1.4:   Added support for masked arrays.
:0.1.3:   Pass keyword arguments in save() to the loader.
:0.1.2:   Improved optional loader detection.
:0.1.1:   Added pupynere dependency.
:0.1:     Initial release.

""",
        classifiers=filter(None, classifiers.split("\n")),
        keywords='netcdf data array math',
        author='Roberto De Almeida',
        author_email='roberto@dealmeida.net',
        url='http://bitbucket.org/robertodealmeida/puppy/',
        download_url = "http://cheeseshop.python.org/packages/source/p/Puppy/Puppy-%s.tar.gz" % version,
        license='MIT',
        py_modules=['pup'],
        include_package_data=True,
        zip_safe=True,
        test_suite = 'nose.collector',
        install_requires=[
            'numpy',
            'pupynere',
        ],
        extras_require={
            'test': ['nose'],
        },
)
