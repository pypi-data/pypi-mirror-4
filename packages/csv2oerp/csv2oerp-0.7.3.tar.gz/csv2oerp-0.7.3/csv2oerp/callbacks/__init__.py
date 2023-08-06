# -*- coding: utf8 -*-
################################################################################
#
# Copyright (c) 2012 STEPHANE MANGIN. (http://le-spleen.net) All Rights Reserved
#                    Stéphane MANGIN <stephane.mangin@freesbee.fr>
# Copyright (c) 2012 OSIELL SARL. (http://osiell.com) All Rights Reserved
#                    Eric Flaux <contact@osiell.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
################################################################################

"""
Callbacks module
****************

A callback is a field's value pre-process. It can be used for various treatments,
such as striping, splitting, injecting data relative to the initial value, etc.

.. note::

    Import the callback method and call it properly into the ``callbacks`` argument
    of a :class:`Field <csv2oerp.models.field.Field>` instanciation.

    Concretely, it's such as simple as that.

    .. code-block:: python

        from csv2oerp import callbacks as cb

        Model('res.parter_address', [
            Field('partner_id', columns=[25], callbacks=[cb.get_id('res.partner', ['name'])]),
        ]


Creating a callback
===================

.. autoclass:: csv2oerp.callbacks.callback_model
    :members:
    :inherited-members:


Understanding the process
=========================

Here is the position of callbacks in the mapping hierarchy (Depending of your
configuration, of course).

.. code-block:: text

    ------   +-----+-----+---+--------+--------+---+-------+--------------+
    |C       |name |phone|fax|street  |street2 |zip|country|...           |
    |S       |-----|-----|---|--------|--------|---|-------|--------------|
    |V       |...  |...  |...|...     |...     |...|...    |...           |
    ------   +-----+-----+---+--------+--------+---+-------+--------------+
    |        |  1  |  2  | 3 |   4    |   5    | 6 |   7   |...           |
    |        +--+--+--+--+-+-+----+---+--+-----++--+--+----+--------------+
    |C          |     |    |      |      |      |     |
    |S          |     |    |      |      |      |     |
    |V       +------------------------------------------------------------+
    |2       |                   GLOBAL PRE-PROCESSES                     |
    |O       +------------------------------------------------------------+
    |E          |     |    |      |      |      |     |
    |R          |     |    |      |      |      |     |
    |P          |     |    |      |      +--+   |     |
    |           | +-------------+ |         |   |  +-------------+
    |B          | |  callbacks  | +-----+   |   |  |  callbacks  |
    |I          | +-------------+       |   |   |  +-------------+
    |N          |     |    |            |   |   |    | |
    |D          |     |    |            |   |   |    | |
    |S          |     |    +--------+   |   |   |    | |
    |           |     +---------+   |   |   |   |    | |
    |           +---------+-+   |   |   |   |   |    | |
    ------                | |   |   |   |   |   |    | |
    |                     | |   |   |   |   |   |    | |   +-----------+
    |                     | |   |   |   |   |   |    | |   |res.country|<-+
    |O                    | |   |   |   |   |   |    | |   |-----------|  |
    |P                    | |   |   |   |   |   |    | +-->|name       |  |
    |E                    | |   |   |   |   |   |    +---->|code       |  |
    |N                    | |   |   |   |   |   |          +-----------+  |
    |E      +-----------+ | |   |   |   |   |   |   +-------------------+ |
    |R      |res.partner| | |   |   |   |   |   |   |res.partner.address| |
    |P      |-----------| | |   |   |   |   |   |   |-------------------| |
    |       |       name|<+ +   |   |   |   |   +-->|zip                | |
    |M      |           |   |   |   |   |   +------>|street2            | |
    |O      |           |   |   |   |   +---------->|street             | |
    |D      |           |   |   |   +-------------->|fax                | |
    |E      |           |   |   +------------------>|phone              | |
    |L      |           |   +---------------------->|name               | |
    |S      |  addresses|-------------------------->|partner_id         | |
    |       |           |                           |         country_id|-+
    |       |           |                           |                   |
    -----   +-----------+                           +-------------------+


Preconfigured callbacks
=======================

.. automodule:: csv2oerp.callbacks.preconfigured
    :members:

"""
from csv2oerp.callbacks.preconfigured import *

def callback_model(session, model, field, line):
    """Model for the specifics callbacks class signature.

    :param session: Current :class:`Session <csv2oerp.models.session.Session>`
    :param model: Current :class:`Model <csv2oerp.models.model.Model>`
    :param field: Current :class:`Field <csv2oerp.models.fields.Field>`
    :param line: Current line number

    You can use a closure method to add specific arguments to your callback call.

    .. code-block:: python

        def my_callback(*args, **kwargs):
            \"\"\" Add some arguments to your callback

            \"\"\"
            def _callback(session, model, field, line):
                result = ""
                # Some treatments with arguments in scope
                return result

            return _callback

    """
    pass


