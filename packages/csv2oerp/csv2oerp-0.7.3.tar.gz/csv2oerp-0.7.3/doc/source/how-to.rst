.. _how-to:

How to
******

In this tutorial, we will import some datas issue to this `csv` file

.. csv-table:: res_partner_address.csv

   :header: "Address type", "City", "Contact Name", "Country Name", "E-Mail", "Phone", "Street", "Street2", "Title", "Zip", "Partner name", "Partner Country Name", "Partner City"
    "default", "Paris", "Arthur Grosbonnet", "France", "a.g@wealthyandsons.com", 0268978776, "1 rue Rockfeller", , "Sir", 75016, "BML", "France", "Paris"
    "invoice", "Bruxelles", "Carl François", "Belgium", "carl.françois@bml.be", "0258256545", "89 Chaussée de Waterloo", , , 1000, "BML", "Belgium", "Bruxelles"

Declare your `csv` file
=======================

In order to bind `csv` file and `Openerp` data models, you have to instanciate a
:class:`Session <csv2oerp.models.session.Session>`, which will read the file and
map columns for each data models.

To do this simply do that::
    
    session = Session('file.csv', separator=';', quote='"')

.. note::

    Check for api to have more informations on
    :class:`Session <csv2oerp.models.session.Session>` signature.

Declare your models
===================

Bind columns with models
------------------------

To configure a `Openerp` data model, you have to instanciante a
:class:`Model <csv2oerp.models.model.Model>` in order to bind columns with fields::

    res_partner = Model('res.partner')

Then you can configure each fields inside the new model, there is 2 ways to 
do so, First::

    res_partner.set_field('name', columns=[1])
    ...

The second way is to inject fields into the signature of the
:class:`Model <csv2oerp.models.model.Model>` by instanciating
:class:`Field <csv2oerp.models.fields.Field>`::

    res_partner_address = Model('res.partner.address', fields=[
        Field(name='name', columns=[1]),
        ...
    ])

.. note::

    Check for api to have more informations on
    :class:`Field <csv2oerp.models.fields.Field>` signature.

Declare relations
-----------------

`csv2oerp` also allows you to virtually create the relationship that fields
would have between them in `Openerp` data models.

For example, a `res.partner` object has a relation to `res.partner.address`. If
these two objects's field are on the same line (in the CSV file), then you can
define a relationship directly into the mapping.

A simple relationship between `res.partner` to `res.partner.address`::
    
    +-------------+                             +-------------------+
    | res.partner |                             |res.partner.address|
    +-------------+                             +-------------------+
    |             |                             |                   |
    |             |                  partner_id |                   |
    |             +-----------------------------+                   |
    |             |                           1 |                   |
    |             |                             |                   |
    +-------------+                             +-------------------+

.. code-block:: python
    
    partner_model = Model('res.partner', fields=[...])

    partner_address = Model('res.partner.address', fields=[
        Field('type', default='default'),

        # Many2one or One2one
        Field(name="partner_id", relation=partner_model),
        ...
        ])


The same relationship between `res.partner.address` to `res.partner`::

    +-------------+                             +-------------------+
    | res.partner |                             |res.partner.address|
    +-------------+                             +-------------------+
    |             |                             |                   |
    |             | address                     |                   |
    |             +-----------------------------+                   |
    |             | *                           |                   |
    |             |                             |                   |
    +-------------+                             +-------------------+

.. code-block:: python
    
    partner_address_default = Model('res.partner.address', fields=[
        Field('type', default='default'),
        ...
        ])

    partner_address_delivery = Model('res.partner.address', fields=[
        Field('type', default='delivery'),
        ...
        ])

    partner_address_invoice = Model('res.partner.address', fields=[
        Field('type', default='invoice'),
        ...
        ])

    partner_model = Model('res.partner', fields=[
        
        # one2many or many2many
        Field(name="addresses", relation=[
            partner_address_default, partner_address_delivery, partner_address_invoice
            ]),
        ...
        ])

Setting default values
----------------------

There is two means for this functionnality.

First if a data is missing (as a column) in your `csv` file. You can then force
a value on the field you want to insert without the appropriate binded column.

.. code-block:: python

    Model('res.partner.address', fields=[
        # this will always have 'invoice' value.
        Field("type", default='invoice'),
        ...
    ])

Secondly, it can be usefull in case of temporarily missing value on a binded
column to define a default. In this example, ``type`` must have a value, but in
case of null value in a column, the default will be inject instead of it.

.. code-block:: python

    Model('res.partner.address', fields=[
        # this will have 'default' value only if column have null value.
        Field("type", columns=[12], default='default'),
        ...
    ])

Setting required value
----------------------

Coming soon ...

Setting unique value
--------------------

Coming soon ...

Column's value concatenation
----------------------------

Coming soon ...

Define custom pre-treatment
===========================

In order to let you do what you want with values issue from the `csv` file. A
pre-treatment functionnality has been integrated into the fields definition.
It's called a ``callback``. Let's see with a simple example.

First you have a value on which you want to do some treatment before injecting it
into `Openerp`. To do so, you will create a function which will take as parameter
the value you want to modify plus others metadatas. For example, the column
associated to the phone and the fax. You want to perform a check of these two
phone numbers to determine if its can be injected, reformated or just skipped.

The callback looks like that (You should respect signature)::

    def phone_check(session, model, value, line_num):
        """ Return the phone number reformatted or not if unconsistent
        """
        if not value or len(value) != 10:  # French length for phone numbers
            return None
        
        num_list = [value[:2], value [2:4], value[4:6], value[6:8], value[8:10]]
        return ' '.join(num_list)

    Field('phone', columns=[2], callbacks=[phone_check]),
    Field('fax', columns=[3], callbacks=[phone_check]),

.. note::

    See callback documentation to have more explanation on functionnalities.

For this example, you should also have used the preconfigured callback function
too (:func:`check_phone <csv2oerp.callbacks.get_phones>`)::

    from csv2oerp.callbacks import get_phones

    Field('phone', columns=[2], callbacks=[get_phones('phone')]),
    Field('fax', columns=[3], callbacks=[get_phones('fax')]),

.. note::
    
    Callbacks can be a closure too, with a proper signature usable in the field
    definition, but only the closure is used by the pre-treatment functionnality.

.. note::
    
    Callbacks can be used also to dynamically change ``CRUD`` actions. See below.

Skip a record (Field level)
---------------------------

This functionnality skip a field if the callback return True.

.. code-block:: python

    def callback_func_skip(session, model, value, line_num):
        """ Check the value and return True or False depending on action you want
        
        Return True = skip field
        Return False = allocate field
        """
        # Some tests
        return True or False

    Model('model.name', fields=[
        Field(name="field_name", columns=[1], callbacks=[callback_func_skip], skip=True),
    ])

Skip a record (Model level)
---------------------------

This functionnality skip a record if the callback return True.

.. code-block:: python

    def callback_func_skip(session, model, value, line_num):
        """ Check the value and return True or False depending on action you want
        
        Return True = skip field
        Return False = allocate field
        """
        # Some tests
        return True or False

    Model('model.name', fields=[
        
        # All field types
        Field(name="field_name1", columns=[0]),
        Field(name="field_name3", columns=[2], callbacks=[callback_func_skip], ignore=True),

        ])

Connection to OpenERP
=====================

You need an instance of the :class:`Openerp <csv2oerp.Openerp>` class to dialog with an
`OpenERP` server. Let's pretend that you want to connect as `admin` on the
`db_name` database of the local `OpenERP` server (with the `XML-RPC` service
which listens on port `8071`). First, prepare the connection::

    >>> from csv2oerp import Openerp 
    >>> oerp = Openerp(
            server='localhost',
            user='admin',
            pwd='admin',
            db='db_name',
            protocol='xmlrpc',
            port=8071)

You can then easily execute some requests with the following `CRUD` syntaxes.

Launching the importation process
=================================

Now its time to bind csv files to their appropriated data models. To do so, just
``link`` both of them.

.. code-block:: python

    session.bind(oerp, models=[
        partner_address_default,
        partner_address_delivery,
        partner_address_invoice,
    ])

.. note::
    
    As you could see, the binding between `models` and `oerp` is done by the
    `one2many` relationship, you bind only higher relations and the link will be
    automatically created while data processing.

    Doing this::
        
        session.bind(oerp, models=[
            partner_address_default,
            partner_address_delivery,
            partner_address_invoice,
            partner_model,
        ])

    Will mean the same as the previous example.
        

Full example
------------

See :ref:`examples` section.

Getting a resume
----------------

At the end of your script, you can demand a resume of actions processed during
the importation, to do so, just type the following::
    
    csv2oerp.show_stats()

It will show you a resume like this one::

    Coming soon ...
    


