Creation of your Columns mapping
********************************

Base mapping structure
======================

def callback_func_skip(session, model, value, line_num):
    # Return True = skip field
    # Return False = allocate field
    return True or False

def callback_func(session, model, value, line_num):
    return value

Model('model.name', fields=[
    
    # All field types
    Field(name="field_name1", columns=[0]),
    Field(name="field_name2", columns=[1], callbacks=[callback_func]),
    Field(name="field_name3", columns=[2], callbacks=[callback_func_skip], skip=True),

    ])


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
            
            # one2many or many2many
            Field(name="partner_id", relation=[
                address_default, address_delivery
                ]),

            ])

