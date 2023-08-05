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
csv2oerp connector interface module.

"""

import xmlrpclib

class Server_interface(object):
    u"""Server methods interface.
    
    Reproduce create, write, search and read methods.
    
    """

    def __init__(self, host, port, user, pwd, db, lang=u'en_EN'):
        url = u'http://%s:%s/xmlrpc/' % (host, port)
        sock_common = xmlrpclib.ServerProxy(url + u'common', allow_none=True)
        self.uid = sock_common.login(db, user, pwd)
        self.host = host
        self.port = port
        self.db = db
        self.pwd = pwd
        self.lang = lang
        self.user = user
        self.server = xmlrpclib.ServerProxy(url + u'object', allow_none=True)

    def execute(self, *args, **kwargs):
        return self.server.execute(*args, **kwargs)

    def search(self, model, args=None, offset=0, limit=None, order=None,
            context=None, count=False):
        u"""Search for records based on a search domain.
        
        :param model: The OpenERP model (res.partner)
        :type model: str
        :param args: list of tuples specifying the search domain [(‘field_name’, ‘operator’, value), ...]. Pass an empty list to match all records.
        :type args: list
        :param offset: optional number of results to skip in the returned values (default: 0)
        :type offset: int
        :param limit: optional max number of records to return (default: None)
        :type limit: int
        :param order: optional columns to sort by (default: self._order=id )
        :type order: str
        :param context: context arguments, like lang, time zone
        :type context: dict

        """
        return NotImplemented

    def read(self, model, ids, context=None):
        u"""Read OpenERP record.

        :param model: The OpenERP model (res.partner)
        :type model: str
        :param ids: object id or list of object ids
        :type ids: list
        :param context: context arguments, like lang, time zone
        :type context: dict

        """
        return NotImplemented

    def create(self, model, vals=None, context=None):
        u"""Create new record with specified value.

        :param model: The OpenERP model (res.partner)
        :type model: str
        :param vals: field values for new record, e.g {‘field_name’: field_value, ...}
        :type vals:	dict
        :param context: context arguments, like lang, time zone
        :type context: dict

        """
        return NotImplemented

    def write(self, model, ids, vals=None, context=None):
        u"""Update records with given ids with the given field values.

        :param model: The OpenERP model (res.partner)
        :type model: str
        :param ids: object id or list of object ids to update according to vals
        :type ids: list
        :param vals: field values for new record, e.g {‘field_name’: field_value, ...}
        :type vals:	dict
        :param context: context arguments, like lang, time zone
        :type context: dict

        """
        return NotImplemented

    def fields_get(self, model, fields=None, context=None):
        u"""Get the description of list of fields.
        
        :param model: The OpenERP model (res.partner)
        :type model: str
        :param fields: Fields to return
        :type fields: list
        :param context: context arguments, like lang, time zone
        :type context: dict
        
        """
        return NotImplemented
    
    def __str__(self):
        return u"<Server %s:%s=%s(%s)>" %\
            (self.host, self.port, self.db, self.lang)


class Openerp(Server_interface):

    def search(self, model, args=None, offset=0, limit=None, order=None,
            context=None, count=False):
        if args is None:
            args = []
        if context is None:
            context = {u'lang': self.lang}

        return self.execute(self.db, self.uid, self.pwd, model,
                    u'search', args, 0, False, False, context, count)

    def read(self, model, ids, context=None):
        if context is None:
            context = {u'lang': self.lang}
        return self.server.execute(self.db, self.uid, self.pwd, model,
                    u'read', ids, context)

    def create(self, model, vals=None, context=None):
        if vals is None:
            vals = {}
        if context is None:
            context = {u'lang': self.lang}
        return self.execute(self.db, self.uid, self.pwd, model,
                    u'create', vals, context)

    def write(self, model, ids, vals=None, context=None):
        if vals is None:
            vals = {}
        if context is None:
            context = {u'lang': self.lang}
        return self.execute(self.db, self.uid, self.pwd, model,
                    u'write', ids, vals, context)

    def fields_get(self, model, fields=None, context=None):
        if context is None:
            context = {u'lang': self.lang}
        return self.execute(self.db, self.uid, self.pwd, model,
                    u'fields_get', fields, context)

    def __str__(self):
        return u"<Openerp %s:%s=%s(%s)>" %\
            (self.host, self.port, self.db, self.lang)



