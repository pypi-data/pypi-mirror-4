=====
ESMBC
=====

EVE Ship Maintenance Bay Calculator

Esmbc is a command line ship volume calculator for EVE online. It would
probably be of most use to EVE pilots that own and fly carriers.

Usage
----------

``$ esmbc hound:3 talwar:2 sabre:1 rupture:1 hurricane:1 tornado:1``

::

    Sabre: 43,000m3
    Talwar: 86,000m3
    Tornado: 216,000m3
    Rupture: 96,000m3
    Hound: 84,300m3
    Hurricane: 216000m3
    Total: 741,300m3

Esmbc accepts ship names and quantities with the colon character used
as a seperator.

The pairs are seperated by a single whitespace.

Ship names which contain a white space should have it replaced with an
underscore, all other special characters should not be entered.
``Republic Fleet Firetail`` should be entered as ``republic_fleet_firetail``.

Case is not important. ``Rifter``, ``RIFTER`` and ``rifter`` will all be
matched correctly.

Installation
------------

It's possible to just use esmbc without installation by just calling the
module:

``python -m esmbc``

To do so
`download a zip <https://github.com/stuartdb/esmbc/archive/master.zip>`_ of
this repo or clone it.

``git clone git://github.com/stuartdb/esmbc.git``

If you wish to actually install esmbc on your system the prefered way would
be to use pip.

``$ pip install esmbc``

or use obtain this repository as previously mentioned and:

``$ python setup.py install``

Requirements
------------

Python 3.3 is the base requirement.

If you wish to install the module then ``distribute`` is required.

Ship/Volume Data File
---------------------

The ship and volume data file that is required is supplied (``ships.json``).

You also have the option to build your own data file. This may be required in
the future as CCP release new ship types.

A script is included to access a sqlite version of the CCP community data dump
and output a JSON string of the ships and their volumes.

``$ python sqlite.py > ships.json``

License
--------------------

esmbc is released under the
`GPLv3 license <https://www.gnu.org/licenses/gpl.html>`_
