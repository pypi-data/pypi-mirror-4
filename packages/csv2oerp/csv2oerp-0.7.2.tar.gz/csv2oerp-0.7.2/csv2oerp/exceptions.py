# -*- coding: utf8 -*-
##############################################################################
#
# Copyright (c) 2012 STEPHANE MANGIN. (http://le-spleen.net) All Rights Reserved
#                    Stéphane MANGIN <stephane.mangin@freesbee.fr>
# Copyright (c) 2012 OSIELL SARL. (http://osiell.com) All Rights Reserved.
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
# as published by the Free Software Foundation; either version 2
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
##############################################################################

u"""
Exceptions used in csv2oerp.

"""

from pprint import pformat

class BadFieldType(BaseException):
    u"""Exception used when a field is a relation and not relationnal in Oerp
    
    """
    def __init__(self, model, field, type_):
        u"""
        :param model: Object model
        :type model: str
        :param field: Field required
        :type field: str
        :param type_: Field type 
        :type type_: str

        """
        msg = u"Model(%s) field(%s) is not a relationnal field.Skipping." % (model, field, type_)
        super(BadFieldType, self).__init__(msg)


class RequiredFieldError(BaseException):
    u"""Exception used when a column index has not be found 
    
    """
    def __init__(self, model, field):
        u"""
        :param model: Object model
        :type model: str
        :param field: Field required
        :type field: str

        """
        msg = u"Required model(%s) field(%s) has null value. Skipping." % (model, field)
        super(RequiredFieldError, self).__init__(msg)


class FieldDefinitionError(BaseException):
    """Exception used when a model is not conform
    
    """
    def __init__(self, msg=u""):
        """
        :param model: Object model
        :type model: str
        :param msg: Message to be printed
        :type msg: str

        """
        super(FieldDefinitionError, self).__init__(msg)


class ModelDefinitionError(BaseException):
    """Exception used when a model is not conform
    
    """
    def __init__(self, msg=u""):
        """
        :param model: Object model
        :type model: str
        :param msg: Message to be printed
        :type msg: str

        """
        super(ModelDefinitionError, self).__init__(msg)


class ColumnIndexError(IndexError):
    """Exception used when a column index has not be found 
    
    """
    def __init__(self, msg=u""):
        """
        :param model: Object model
        :type model: str
        :param msg: Message to be printed
        :type msg: str

        """
        super(ColumnIndexError, self).__init__(msg)


class SkipLineException(BaseException):
    """Exception used when a subfunction need to skip a entire particular line
    
    Usefull into lambda statement with field definition
    """
    def __init__(self, msg=u""):
        """
        :param model: Object model
        :type model: str
        :param msg: Message to be printed
        :type msg: str

        """
        super(SkipLineException, self).__init__(msg)


class SkipObjectException(BaseException):
    """Exception used when a subfunction need to skip a particular object
    
    Usefull into lambda statement with field definition

    """
    def __init__(self, msg=u""):
        """
        :param model: Object model
        :type model: str
        :param msg: Message to be printed
        :type msg: str

        """
        super(SkipObjectException, self).__init__(msg)

class FatalException(BaseException):
    """Exception used when a fatal error occurs 
    
    """
    def __init__(self, error, line, model, state, search, data, content):
        """
        :param model: Object model
        :type model: str
        :param msg: Message to be printed
        :type msg: str

        """
        msg = u"""

FATAL ERROR line n° %s (%s)
--------------------------------------------------------------------------------
  line: %s 
 model: %s
 state: %s
search: %s
  data:
%s
            """ % (line, error, pformat(content), model, state, search, pformat(data))
        super(FatalException, self).__init__(msg)

