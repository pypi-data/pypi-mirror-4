ParsePkgtxt
###########

A Python Class to parse a Slackware linux PACKAGES.TXT file in order to build
a dictionnary with packages names as keys and packages detailed informations
as values.

You can install it via pip:

.. code-block:: sh

    pip install ParsePkgtxt


Usage example:
==============

.. code-block:: python

    >>> from ParsePkgtxt import Package
    >>> for k, v in Package.parse(Package(), 'PACKAGES.TXT').iteritems():
    >>> ....print ';'.join([k,v[0],v[9])


Output:
-------

.. code-block::

    package1_name;package1_version;package1_description
    package2_name;package2_version;package2_description
    ...
    ...

