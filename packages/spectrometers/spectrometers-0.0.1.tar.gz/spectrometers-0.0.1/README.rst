spectrometers
~~~~~~~~~~~~~~~

Spectroid is a simple python API for working with
spectrometers/spectrophotometers. This is inspired by `openSpectrometer`_.

.. _`openSpectrometer`: http://openspectrometer.com/

Example usage
----------

here you go

.. code-block:: python

    from spectrometers.devices import Nanodrop

    nanodrop = Nanodrop()

    wavelengths = nanodrop.capture()

    >>> wavelengths
    [0.500, 0.520]

Install
----------

.. code-block:: bash

    sudo pip install spectrometers

or maybe you hate package managers,

.. code-block:: bash

    sudo python setup.py install

Testing
----------

.. code-block:: bash

    make test

Changelog
----------

* 0.0.1: basic python module

License
----------

BSD
