PhreeqPy - Python Tools for PHREEQC
====================================


Introduction
------------

PhreeqPy is Open Source software and provides Python tools to work with
PHREEQC_.

Currently it provides access to the new IPhreeqc_ interface without the need to
run a COM server and therefore also works on non-Windows systems.
IPhreeqc is described in more detail in this publication_.

`Please let us know`_ what you do with PhreeqPy or if things do not work
as expected. There is a 
`mailing list for PhreeqPy <https://groups.google.com/forum/#!forum/phreeqpy-users>`_.
Just `sent us you email address`_ to subscribe with the header `subscribe to phreeqpy list`. 

`Download latest version of this documentation as PDF <phreeqpy.pdf>`_


**License**: BSD

.. _installation:

Installation
------------

**Pythons (tested)**: Python 2.6, 2.7, 3.3, PyPy

**Pythons (untested but should work since using ctypes)**: IronPython, Jython 2.7

**Platforms**: Unix/Posix and Windows

**PyPI package name**: `phreeqpy <http://pypi.python.org/pypi/phreeqpy>`_


1.) Installation options::

    pip install -U phreeqpy # or
    easy_install -U phreeqpy
    

2.) Download:: 

    wget http://www.phreeqpy.com/download/phreeqpy0.2.zip
    tar -xzvf phreeqpy0.2.zip
    cd phreeqpy0.2
    sudo python setup install
    
You need a a IPhreeqc shared libray for your operating system. PhreeqPy comes
with shared libraries for 32-bit Windows, 32-bit Linux and 64-bit Mac OS X.
More shared libraries for differnet platforms will come with following releases.

You may download an appropriate library from here:
ftp://brrftp.cr.usgs.gov/pub/charlton/iphreeqc/

For example for Linux::

    wget ftp://brrftp.cr.usgs.gov/pub/charlton/iphreeqc/iphreeqc-2.18.4-6386.tar.gz
    tar -xzvf iphreeqc-2.18.4-6386.tar.gz
    cd iphreeqc-2.18.4-6386
    ./configure
    make
    make check
    sudo make install


Then either use the full path to the shared libray when making an instance of
``phreeqc_dll.IPhreeqc``

.. code-block:: python

    phreeqc = phreeqpy.iphreeqc.phreeqc_dll.IPhreeqc('/full/path/to/libiphreeqc.so')


or copy the shared object into ``phreeqpy/iphreeqc`` replacing the existing
one. For example::

    sudo cp /usr/local/lib/libiphreeqc.so  /path/to/site-pacges/PhreeqPy-0.2.0-py2.7.egg/phreeqpy/iphreeqc/libiphreeqc.so.0.0.0



.. _PHREEQC: http://wwwbrr.cr.usgs.gov/projects/GWC_coupled/phreeqc/index.html
.. _IPhreeqc: ftp://brrftp.cr.usgs.gov/pub/charlton/iphreeqc/IPhreeqc.pdf
.. _publication: http://www.sciencedirect.com/science/article/pii/S0098300411000653
.. _`MODFLOW and More 2011`: http://igwmc.mines.edu/conference/schedule.html
.. _`Please let us know`: contact
.. _`sent us you email address`: contact


   
   


