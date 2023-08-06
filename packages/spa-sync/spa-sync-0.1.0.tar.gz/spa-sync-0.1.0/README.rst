================================
Linksys/Sipura SPA IP Phone Sync
================================

Command line tool to sync your Linksys/Sipura SPA IP Phone with contact
directories from OSX Contacts, MS Outlook and Highrise. It uses `spa-phone-api`
for communication with the phone.


Installation
============

Installation with ``pip``:
::

    $ pip install spa-sync


Command Line Usage
==================

Update the address book from OS X Contacts. Defaults to sync all contacts, but
an optional group paramater can be specified.
::

    $ spa-sync ip-address [--group GROUP]


Notes for Windows
=================

Accessing Outlook (Windows)
---------------------------
To access Outlook on Windows, you need ``pywin32``, which can be downloaded
from `sourceforge <https://sourceforge.net/projects/pywin32/files/pywin32/>`_.
Make sure to download the correct version matching your python version and
architecture. To install ``pywin32`` in your virtualenv, install it using
``easy_install`` in the activated virtualenv
::

    $ Scripts\activate.bat
    (env)$ easy_install [py2win]

Building EXEs (Windows)
-----------------------
To build EXEs on Windows, you need ``py2exe``, which can be downloaded from
`sourceforge <https://sourceforge.net/projects/py2exe/files/py2exe/>`_. The
same install instructions as ``pywin32`` apply.


Contributions
=============

Contributions welcome!
