.. csv2oerp documentation master file, created by
   sphinx-quickstart on Tue Dec 13 10:46:30 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to csv2oerp's documentation!
************************************

Introduction
============
`csv2oerp` is a convenient library to import data from CSV format to an `OpenERP`
instance.

`csv2oerp` is a simple and fast method to perform an import, through
OpenERP model's fields bound to CSV's columns. You can easily ordered your data
before coding any lines as the manner of `OpenERP`.
You can perform post-import field treatment, omit or modify it.
You can also according to criterias, skip a line or do not decide to create
an object being processed.


Quick start
===========

In a new script, for example 'your_script.py'.

Import csv2oerp and some callbacks::
    
    >>> from csv2oerp import Model, Field, Openerp, Session, show_stats
    >>> import csv2oerp.callbacks as cb

Configure OpenERP connection::

    >>> host = '198.168.0.1'
    >>> port = 8069
    >>> dbname = 'database'
    >>> user = 'admin'
    >>> pwd = 'admin'
    >>> lang = 'fr_FR'
    >>> oerp = Openerp(host, port, user, pwd, dbname, lang)

Create a new importation instance::

    >>> example = Session('example_file.csv',
            delimiter=';', quotechar='"', encoding='utf-8',
            offset=1, limit=10)

Define a custom callback(Field's value pre-treatment)::

    >>> def country_code(session, model, field, value, line_num):
    ...     """Return the first two uppered characters from current column value
    ...     """
    ...     return value[:2].upper()

Define your mapping to link both csv and OpenERP::

    >>> res_partner = Model('res.partner', fields=[

    ...         Field('name', columns=[1]),
    ...         Field('siren', columns=[2]),
    ...         Field('website', columns=[16]),
    ...         Field('comment', columns=[56]),

    ...     ], update=False, search=['siren']) # Unique by siren and no update

    >>> res_country = Model('res.country', fields=[ 

    ...         Field('code', columns=[13], callbacks=[_country_code], default='FR'),
    ...         Field('name', columns=[13], default='FRANCE'),

    ...     ], update=False, search=['code', 'name'])

    >>> res_partner_address = Model('res.partner.address', fields=[
    ...         # Custom field's value
    ...         Field('type', custom='default'),

    ...         # Simple fields
    ...         Field('zip', columns=[9], default='35000'),
    ...         Field('city', columns=[10], default='RENNES'),
    ...         Field('phone', column=[14]),
    ...         Field('fax', columns=[15]),
    ...         Field('email', columns=[17], unique=True), # Unique email 
    ...         Field('cedex', columns=[68]),
    
    ...         # Mixing columns (concatenation)
    ...         Field('street', columns=[7, 6], method='concatenate'),
    ...         Field('street2', columns=[8, 5], method='concatenate'),

    ...         # Model's relation with dynamic insertion from OpenERP database
    ...         # Not native object from OpenERP framework
    ...         Field('region_id', columns=[11],
    ...             callbacks=[cb.get_id('res.region', ['name'])])
    ...         Field('dep_id', columns=[12],
    ...             callbacks=[cb.get_id('res.dep', ['name'])])

    ...         # Model's relations not updated if exists
    ...         Field('country_id', relation=res_country),

    ...         # Model's relations with unique value between objects
    ...         Field('partner_id', relation=res_partner, required=True),

    ...     ], search=['type', 'partner_id'])


Finally join objects to the session which starts the import process::

    >>> example.bind(oerp, [res_partner_address, ])

And show statistics of objects's activities during the importation process::

    >>> csv2oerp.show_stats()

Call your script
----------------

To prevent from importing csv file headers, type the following::

    >>> ./your_script.py -o1

For command line help::
    
    >>> ./your_script --help


Download and install
====================

See :ref:`download-install` section.

Documentation
=============

See :ref:`content` section.

Supported Desktop versions
==========================

All architectures.

Supported Python versions
=========================

`csv2oerp` support Python versions 2.6 and 2.7.

License
=======

This software is made available under the LGPLv3 license.

Bugs or suggestions
===================

Please, feel free to report bugs or suggestions in the `Bug Tracker
<https://bitbucket.org/StefMangin/python-csv2oerp/issues?status=new&status=open>`_!

