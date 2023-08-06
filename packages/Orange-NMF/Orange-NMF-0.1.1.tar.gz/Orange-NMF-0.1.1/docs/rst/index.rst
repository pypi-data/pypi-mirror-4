Orange NMF Add-on Documentation
===================================

Orange NMF is an add-on for `Orange`_ data mining software package. It
provides modules and widgets for matrix factorization (NMF and SVD).

.. _Orange: http://orange.biolab.si/addons


Installation
------------

`Install Orange`_ data mining suite from the Orange website. Also, `install NIMFA`_, a Python library for non-negative
matrix factorization, which includes implementations of initialization and factorization algorithms along with quality
measures. Start Orange Canvas, navigate to Options / Add-ons, and check the NMF add-on.

To install from PyPi_ run::

    pip install orange-nmf

To install from source code run::

    python setup.py install

To build Python egg run::

    python setup.py bdist_egg

To install add-on in `development mode`_ run::

    python setup.py develop

.. _development mode: http://packages.python.org/distribute/setuptools.html#development-mode
.. _PyPi: http://pypi.python.org/pypi
.. _Install Orange: http://orange.biolab.si/download
.. _install NIMFA: http://nimfa.biolab.si/#installation

