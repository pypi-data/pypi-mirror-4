==========
KittyStore
==========

:Author: Pierre-Yves Chibon <pingou@pingoured.fr>
:Author: Aurélien Bompard <abompard@fedoraproject.org>


KittyStore is the archiving library for `HyperKitty`_, the Mailman 3 archiver.
It provides an interface to different storage systems. Currenty only the
`Storm ORM`_ system is supported.

.. _HyperKitty: https://fedorahosted.org/hyperkitty
.. _Storm ORM: http://storm.canonical.com


Populating the database
=======================

- Retrieve the archives using the ``get_mbox.py`` script
- Load the archives by calling ``kittystore-import``.

This might be memory intensive, so you may want to do 2 or 3 years per run and
split the runs.

Alternatively, to load the data you may want to do something like::

    for i in lists/devel-*; do kittystore-import -l devel@fp.o $i; done;


License
=======

.. _GPL v2.0: http://www.gnu.org/licenses/gpl-2.0.html

``KittyStore`` is licensed under the `GPL v2.0`_
