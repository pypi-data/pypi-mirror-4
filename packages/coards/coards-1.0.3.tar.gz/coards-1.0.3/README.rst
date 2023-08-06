A COADS compliant time parser
=============================

This module is intended to help parse time values represented using the `COARDS convention <http://ferret.wrc.noaa.gov/noaa_coop/coop_cdf_profile.html>`_. Here is a simple example::

    >>> from coards import parse
    >>> a = [1, 2, 3]
    >>> units = 'days since 1998-03-01 12:00:00'
    >>> b = [parse(value, units) for value in a] 
    >>> print b
    [datetime.datetime(1998, 3, 2, 12, 0), datetime.datetime(1998, 3, 3, 12, 0), datetime.datetime(1998, 3, 4, 12, 0)]

Credits
-------

- `Distribute`_
- `Buildout`_
- `modern-package-template`_

.. _Buildout: http://www.buildout.org/
.. _Distribute: http://pypi.python.org/pypi/distribute
.. _`modern-package-template`: http://pypi.python.org/pypi/modern-package-template
