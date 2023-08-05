Creation of your Columns mapping
********************************

Base mapping structure
======================

Model of the skeleton::
        
        def callback_func_skip(session, model, value, line_num):
            return True or False

        def callback_func(session, model, value, line_num):
            return value

        Model('model.name', fields=[
            
            # All field types
            Field(name="field_name1", columns=[0]),
            Field(name="field_name2", columns=[1], callbacks=[callback_func]),
            Field(name="field_name3", columns=[2], callbacks=[callback_func_skip], skip=True),

            ])


Field declaration arguments
===========================

.. rubric:: model.name (str)

OpenERP osv model name (`res.partner.address` for example).

.. rubric:: field_name (str)

OpenERP field name (`partner_id` for example).

Special cases::

   skip 
        Skip line if callback return True, nothing if False

.. rubric:: columns (list)

Columns number from the CSV file. If a list is provided, a concatenation will
be used.

.. rubric:: callback (lambda or None)

Function called with get back value from `column` index.

Creating relations between models
=================================

`csv2oerp` also allows you to virtually create the relationship that fields
would have between them.

A `res.partner` object has a relation to `res.partner.address`. If these two
objects's field are on the same line (in the CSV file), then you can define a
relationship directly into the mapping.

examples::

    +-------------+                                        +-------------------+
    | res.partner |                                        |res.partner.address|
    +-------------+                                        +-------------------+
    |             |                                        |                   |
    |             | addresses                   partner_id |                   |
    |             +----------------------------------------+                   |
    |             | *                                    1 |                   |
    |             |                                        |                   |
    +-------------+                                        +-------------------+

A simple relationship between `res.partner` to `res.partner.address`::

        partner_model = Model('res.partner', fields=[Some fields])

        Model('res.partner.address', fields=[
            Field('type', default='default'),
            ...

            # Many2one or One2one
            Field(name="partner_id", relation=partner_model),

            ])


The same relationship between `res.partner.address` to `res.partner`::
    
        address_default = Model('res.partner', fields=[
            Field('type', default='default'),
            ...
            ])

        address_delivery = Model('res.partner', fields=[
            Field('type', default='delivery'),
            ...
            ])

        Model('model.name', fields=[
            
            # Many2one or One2one
            Field(name="partner_id", relation=[
                address_default, address_delivery
                ]),

            ])

