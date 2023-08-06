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

Records declaration
^^^^^^^^^^^^^^^^^^^


"""
import xmlrpclib
from csv2oerp.models.fields import Field
from csv2oerp import exceptions
from csv2oerp.constants_and_vars import STATS


class Model(object):

    __slots__ = [u'id', u'name', u'server', u'metadata', u'init_state',
                 u'data']

    @property
    def model(self):
        """ Returns model name.

        """
        return self.init_state['model']

    @property
    def fields(self):
        """ Returns fields list.

        """
        return self.init_state['fields']

    @property
    def search(self):
        """ Returns model name.

        """
        return self.init_state['search']

    @property
    def update(self):
        """ Returns model name.

        """
        return self.init_state['update']

    @property
    def create(self):
        """ Returns model name.

        """
        return self.init_state['create']

    @property
    def context(self):
        """ Returns model name.

        """
        return self.init_state['context']

    def __init__(self, model, fields, search=None, update=True, create=True,
                 context=None):
        if context is None:
            context = {}
        if search is None:
            search = []
        self.init_state = {
            u'model': model,
            u'fields': fields,
            u'search': search,
            u'update': update,
            u'create': create,
            u'context': context
        }
        self.id = None
        self.metadata = None
        self.name = unicode(model)
        self.data = {}

    def reinit(self):
        for field in self.fields:
            field.reinit()
        self.__init__(**self.init_state)

    def check(self, session):
        """Check for model validity.

        :param session: An instance of :class:`csv2oerp.Session`
        :raises: Exception

        """
        if not self._is_model(session):
            raise Exception(u'Model \'%s\' doesn\'t exists !' % self.name)
        session.log(u'debug', self, u'Checking model ...')
        for field in self.fields:
            field.check(session, self)

    def get_id(self, session):
        """Return model's id.

        :param session: An instance of :class:`csv2oerp.Session`
        :returns: list

        """
        if not self.id:
            self.id = session.server.search(
                u'ir.model', [(u'model', u'=', self.name)])
        self.id = len(self.id) and self.id[0]
        return self.id

    def get_relationnal_models(self):
        """ Return all models in relation with this model

        """
        for field in self.fields:
            if field.relation:
                for model in field.relation.get_relationnal_models():
                    yield model
                yield field.relation

        raise StopIteration

    def _is_model(self, session):
        """Check model validity

        :param session: An instance of :class:`csv2oerp.Session`
        :returns: bool

        """
        return bool(self.id or self.get_id(session))

    def get_data(self, session, line):
        """Return data of the model applied in the line.

        :param session: An instance of :class:`csv2oerp.Session`
        :returns: dict

        """
        data = {}
        for field in self.fields:
            try:
                data[field.name] = field.get_data(session, self, line)
            except exceptions.SkipLineException:
                continue

            except xmlrpclib.Fault as err:
                try:
                    error = unicode(err.faultString.split(u'\n')[-2])
                except:
                    error = unicode(err.faultString + (err.faultCode or u''))\
                        or u'Unknown error (xmlrplib.Fault)'

                error = error.replace(u'\\n', u'\n').replace(u'\\', u'')
                session._logger.error(
                    u"<%-25s> %s" %
                    (self.name, error), extra=STATS[session.id])
                continue

        self.data = data
        return data

    def set_field(self, *args, **kwargs):
        """ Insert a field in this model.

        Signature is same as :class:`Field <csv2oerp.models.fields.Field>`.

        """
        self.fields.append(Field(*args, **kwargs))
        return True

    def get_field(self, name):
        """Return the relative field named `name`

        :param name: The name of the field to return
        :type name: str
        :returns: :class:`csv2oerp.Field`

        """
        for field in self.fields:
            if field.name == name:
                return field
        return None
