"""
PhreeqPy
---------

Python tools for PHREEQC.

PhreeqPy allows to use the IPhreeqc interface
without the need to run a COM server and
therefore also works on non-Windows systems.


* `website <http://www.phreeqpy.com/>`_


"""
from setuptools import setup


setup(
    name='phreeqpy',
    version='0.2.0',
    url='http://www.phreeqpy.com/',
    license='BSD',
    author='Mike Mueller',
    author_email='mmueller@hydrocomputing.com',
    description='Python tools for PHREEQC.',
    long_description=open('README.rst').read(),
    packages=['phreeqpy', 'phreeqpy.iphreeqc'],
    package_data={'phreeqpy': ['iphreeqc/*.dll',
                               'iphreeqc/*.so.*',
                               'iphreeqc/*.dylib']},
    zip_safe=False,
    platforms='any',
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: IronPython',
        'Programming Language :: Python :: Implementation :: Jython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
