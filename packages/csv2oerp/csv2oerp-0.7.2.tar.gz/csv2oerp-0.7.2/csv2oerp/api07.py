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

u"""
csv2oerp Access Programming Interface v0.7.

"""
import csv2oerp
from csv2oerp.models.connector import Openerp
from csv2oerp.tools import show_stats, purge_stats

class Model(csv2oerp.models.Model):

    def __init_(self, model, fields, search=None, update=True, create=True,
            context=None):
        return super(Model, self).__init__(model, fields, search, update,
                create, context)

    def check(self, session):
        u"""Check for model validity.

        :param server: Server connection to use
        :type server: object
        :raises: Exception

        """
        return super(Model, self).check(session)

    def get_id(self, session):
        u"""Return model's id.
       
        :param server: Server connection to use
        :type server: Server_instance
        :returns: list

        """
        return super(Model, self).get_id(session)
    
    def _is_model(self, session):
        u"""Check model validity
       
        :param server: Server connection to use
        :type server: Server_instance
        :returns: bool

        """
        return super(Model, self)._is_model(session)
    
    def get_data(self, session, line):
        u"""Return data of the model applied in the line.
        
        :param server: Server connection to use
        :type server: Server_instance
        :returns: dict

        """
        return super(Model, self).get_data(session, line)

    def get_field(self, name):
        u"""Return the relative field named `name`
        
        :param name: The name of the field to return
        :type name: str
        :returns: Field or None

        """
        return super(Model, self).get_field(name)


class Session(csv2oerp.models.Session):
    def __init__(self, name, filename, delimiter=u';', quotechar=u'"',
            encoding=u'utf-8', offset=0, limit=None, quiet=False, debug=False,
            **kwargs):
        return super(Session, self).__init__(name, filename, delimiter, quotechar,
                encoding, offset, limit, quiet, debug, **kwargs)
        
        
    #===========================================================================
    # Accessors
    #===========================================================================
    def set_mapping(self, mapping):
        return super(Session, self).set_mapping(mapping)

    def set_lang(self, code=u'fr_FR'):
        return super(Session, self).set_lang(code)
    
    def set_logger(self, syslog=False):
        return super(Session, self).set_logger(syslog)

    def set_preconfigure_script(self, filename):
        return super(Session, self).set_preconfigure_script(filename)


    #===========================================================================
    # Tools
    #===========================================================================
    def get_line_from_index(self, line_num):
        return super(Session, self).get_line_from_index(line_num)
    
    def get_lines_from_value(self, column, value):
        return super(Session, self).get_lines_from_value(column, value)
    
    def get_index_from_value(self, column, value, withcast=True):
        return super(Session, self).get_index_from_value(column, value, withcast)
    
    #===========================================================================
    # Public methods
    #===========================================================================
    def log(self, level, msg, line=None, model=None):
        return super(Session, self).log(level, msg, line, model)

    def bind(self, server=None, models=[]):
        return super(Session, self).bind(server, models)
    
    join = bind



class Field(csv2oerp.models.fields.Field):
    u""" Specify the column number (or custom value) and some special treatments
    from which the current model's field will be allocated to the object's creation.
    
    :param column: The column number to map to
    :type column: int
    :param field: The actual field name to map to
    :type field: str
    :param callback: The callback function to apply to returned value
    :type callback: function
    :param search: Search for same value before object creation
    :type search: bool
    :param default: Default value if no value found or if custom value (column=None)
    :type default: object
    :param required: Is this field is required
    :type required: bool
    :param skip: Is this field is skippable
    :type skip: bool
    :param ignore: Is this field is ignorable (So object creation is skipped)
    :type ignore: bool
    :param replace: Is this field is replaceable (So it can be redifined)
    :type replace: bool
    :param update: Is this field have not to be updated if existing in database
    :type update: bool
    :param unique: Is this field value must be unique inside current model
    :type unique: bool
    :param relation: Relation to link to (Model object or list of Model Object)
    :type relation: Model
    :param overwrite: Overwrite the field value in OpenERP (relation)
    :type overwrite: bool

    """
    
    def __init__(self, name, columns=None, default=None, callbacks=None,
            relation=None, required=False, readonly=False, skip=False,
            ignore=False, replace=False, update=False, unique=False,
            overwrite=True, context=None):
        
        return super(Field, self).__init__(name, columns, default, callbacks,
                relation, required, readonly, skip, ignore, replace, update,
                unique, context)
        
        
    def check(self, session, model, context=None):
        u"""Check field access fr openerp server
        
        :param session: The import session used for the test
        :type session: Session
        :param model: The model used for the test
        :type model: Model

        """
        return super(Field, self).check(session, model, context)

    def get_metadata(self, session, model, context=None):
        u"""Get metadatas from fields_get methods

        :param session: The import session used for the test
        :type session: Session
        :param model: The model used for the test
        :type model: Model
        :returns: dict

        """
        return super(Field, self).get_metadata(session, model, context)

    def _is_readonly(self, session, model, context=None):
        u"""Check field access
        
        :param session: The import session used for the test
        :type session: Session
        :param model: The model used for the test
        :type model: Model
        :returns: bool

        """
        return super(Field, self)._is_readonly(session, model, context)

    def _is_required(self, session, model, context=None):
        u"""Check field requirability
        
        :param session: The import session used for the test
        :type session: Session
        :param model: The model used for the test
        :type model: Model
        :returns: bool

        """
        return super(Field, self)._is_required(session, model, context)

    def _is_field(self, session, model, context=None):
        u"""Check field validity
        
        :param session: The import session used for the test
        :type session: Session
        :param model: The model used for the test
        :type model: Model
        :returns: bool

        """
        return super(Field, self)._is_field(session, model, context)
    
    def get_data(self, session, model, line):
        u"""Return the value relative to the line in argument.

        :param server: The server to interact with
        :type server: Oerp_instance
        :param line: The line to search for
        :type line: list
        :raises: SkipLineException, SkipObjectException, RequiredFieldError
        :returns: object

        """
        return super(Field, self).get_data(session, model, line)


class Router(csv2oerp.models.fields.Router):
    u""" Specify the column number and special treatments from which the current
    model's field will be allocated to the object's creation.
    
    :param column: The actual column number (mandatory)
    :type column: int
    :param callback: The actual callback function
    :type callback: function

    """
    
    def __init__(self, column, callback):
        return super(Router, self).__init__(column, callback)
        

    def configure(self, server):
        return super(Router, self).configure(server)
