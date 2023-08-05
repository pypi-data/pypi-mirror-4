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

How to use::

    Import the callback method and call it properly into the callback argument of
    a column type object, such as `Column`, `Relation`, `Custom`.

Concretlty, it's such as simple as that::

    >>> from csv2oerp.callbacks import cb_method
    >>> 'res.parter_address': {
    ...                 'partner_id': Column(25, callback=cb_method('res.partner', 'name'))
    ...             }
    ...     }


"""
from csv2oerp import unicode_csv
from csv2oerp import tools
from datetime import datetime
import re
from csv2oerp.constants_and_vars import STATS


def callback_model(session, model, field, line):
    u"""Model of the calback signature.

    :param session: Current Session instance
    :type session: Session
    :param model: Current model
    :type model: str
    :param field: Current field
    :type field: str
    :param line: Current line number
    :type line: int

    """
    pass


def get_line_from_table(csv_file, value, column, separator=u',', quote=u'"', header=True):
    u"""Search for an equivalence between value from column ``col_referer``
    and ``value`` value, and return value from column ``col_return`` index at
    the same line as matching pair ``col_referer`` values.

    :param csv_file: The name of the CSV file to search into
    :type csv_file: str
    :param value: The value to test
    :type value: type
    :param col_referer: The number of the column to compare to ``value``
    :type col_referer: int
    :param col_return: he number of the column to return if matches
    :type col_return: int
    :param separator: The CSV separator
    :type separator: str
    :param quote: The CSV quote
    :type quote: str
    :param header: CSV file has header
    :type header: bool
    :returns: list

    """

    res = []
    with open(csv_file, u'r') as f:
        filereader = unicode_csv.Reader(
            f, delimiter=separator, quotechar=quote)
        for line in filereader:
            if header:
                header = False
                continue
            if line[column] == value:
                res.append(line)

    return res


def search_table(csv_file, value, col_referer=0, col_return=1,
                 separator=u',', quote=u'"', header=True):
    u"""Search for an equivalence between value from column ``col_referer``
    and ``value`` value, and return value from column ``col_return`` index at
    the same line as matching pair ``col_referer`` values.

    :param csv_file: The name of the CSV file to search into
    :type csv_file: str
    :param value: The value to test
    :type value: type
    :param col_referer: The number of the column to compare to ``value``
    :type col_referer: int
    :param col_return: he number of the column to return if matches
    :type col_return: int
    :param separator: The CSV separator
    :type separator: str
    :param quote: The CSV quote
    :type quote: str
    :param header: CSV file has header
    :type header: bool
    :returns: list

    """

    res = []
    filereader = unicode_csv.Reader(
        csv_file, delimiter=separator, quotechar=quote)
    for item in filereader:
        if header:
            header = False
            continue
        if item[col_referer] == value:
            res.append(item[col_return])

    return res


def get_value_from_table(csv_file, col_referer=0, col_return=1,
                         separator=u',', quote=u'"', header=True):
    u"""Search for an equivalence between value from column ``col_referer`` index
    and and value from ``args[3]``, and return value from column ``col_return``
    index at the same line as matching pair ``col_referer`` values.

    .. note::

        This function is the search_table callback interface

    >>> 'address': Column(3, get_value_from_table('address.csv', 0, 1))

    :param csv_file: The name of the CSV file to search into
    :type csv_file: str
    :param col_referer: The number of the column to compare to ``args[3]``
    :type col_referer: int
    :param col_return: he number of the column to return if matches
    :type col_return: int
    :param separator: The CSV separator
    :type separator: str
    :param quote: The CSV quote
    :type quote: str
    :param header: CSV file has header
    :type header: bool
    :returns: callback_model

    """
    def _get_value_from_table(session, model, field, value, line):
        return search_table(csv_file, value, col_referer, col_return,
                            separator, quote, header)

    return _get_value_from_table


def get_ids(model, fields, op=u'&'):
    u"""Return ``model`` which one or more ``fields`` matched column ``value``

    >>> 'partner_ids': Column(56, get_ids('res.partner.address', ['street', 'street2'], op='|'))
    [100, 102]

    :param args: lambda args (ie: [session, model ,field, content, line])
    :type args: list
    :param model: The name of the model to search into
    :type model: str
    :param field: The name of the model's field
    :type field: str
    :param value: The value to compare to
    :type value: str
    :returns: callback_model

    """
    def _get_ids(session, b_model, b_field, b_value, b_line):
        search = []
        try:
            b_value = str(b_value).strip()
        except Exception:
            pass
        i = 1
        for field in fields:
            if i != len(fields):
                search.append(op)
                i += 1
            search.append((field, u'=', b_value))

        try:
            res = session.server.search(model, search)
        except RuntimeError:
            return _get_ids(b_model, b_field, b_value, b_line)
        if not res:
            session._logger.error(u"<%20s> '%s' not found in fields %s" %
                                  (model, b_value, fields), extra=STATS[session.id])
        return res

    return _get_ids


def get_id(model, fields, op=u'&'):
    u"""Return ``model`` which one or more ``fields`` matched column ``value``

    >>> 'address_ids': (21, get_ids('res.partner', ['name']))
    [99]

    :param args: lambda args (ie: [session, model ,field, content, line])
    :type args: list
    :param model: The name of the model to search into
    :type model: str
    :param field: The name of the model's field
    :type field: str
    :param value: The value to compare to
    :type value: str
    :returns: callback_model

    """
    def _get_id(*args):
        res = get_ids(model, fields, op)(*args)
        return res and res[0] or False

    return _get_id


def get_objects(model, fields, op=u'&'):
    u"""Return ``model`` instance which ``fields``'s value matched ``value``

    >>> 'parent_name': Column(2, get_objects('res.partner.address', ['ref'])[0]['name'])
    ['Toto']

    :param model: The name of the model to search into
    :type model: str
    :param fields: The name of the model's field
    :type fields: str
    :param value: The value to compare to
    :type value: str
    :returns: callback_model

    """

    def _get_objects(session, b_model, b_field, b_value, b_line):
        return session.server.read(model, get_id(model, fields, op))

    return _get_objects


def get_field(model, fields, field, op=u'&'):
    u"""Return ``model``'s ``field`` field which ``fields``'s value matched ``value``

    >>> 'parent_name': Column(2, get_field('res.partner.address', ['ref'], 'name')
    ['Toto']

    :param model: The name of the model to search into
    :type model: str
    :param fields: The name of the model's field
    :type fields: str
    :param field: The desire field's value to returned
    :type field: str
    :param value: The value to compare to
    :type value: str
    :returns: callback_model

    """

    def _get_field(*args):
        res = get_objects(model, fields, op=op)(*args)
        res = res and res[0]
        return res and field in res and res[field]

    return _get_field


def get_fields(model, fields, op=u'&'):
    u"""Return ``model`` instance which one or more ``fields`` matched column ``value``

    >>> 'parent_name': Column(2, get_fields('res.partner.address', ['ref']))
    'Toto'

    :param model: The name of the model to search into
    :type model: str
    :param fields: The name of the model's field
    :type fields: str
    :param value: The value to compare to
    :type value: str
    :returns: callback_model

    """

    def _get_fields(session, b_model, b_field, b_value, b_line):
        ids = get_ids(
            model, fields, op)(session, b_model, b_field, b_value, b_line)
        res = session.server.read(model, ids)
        return res

    return _get_fields


def to_boolean(true=u'1', false=u'0', none=u''):
    u"""Return a boolean depending from the input value.

    >>> 'field': Column(2, to_boolean('Y', 'N', ''))

    :param mode: First char will be used if value is True and second if False
    :type mode: str
    :param true_values: The name of the model to search into
    :type true_values: str
    :param false_values: The name of the model's field
    :type false_values: str
    :returns: callback_model

    """
    def _to_boolean(session, model, field, value, line):
        if value == str(true):
            return True
        elif value == str(false):
            return False
        elif value == str(none):
            return None

    return _to_boolean


def to_date(formatted=u'%Y-%m-%d'):
    u"""Check for a valid date and convert if needed before returning the value

    >>> 'inserted_date': Column(6, to_date())

    :param formatted: Format of this date
    :type formatted: str
    :returns: callback_model

    """
    def _to_date(session, model, field, value, line):
        date = value
        try:
            date = str(value.split('\n')[0])
        except:
            pass
        if date in (u'0000-00-00', u'0000/00/00', u'00-00-0000', u'00/00/0000', u''):
            return u''
        date = datetime.strptime(date, formatted)
        return date.strftime(u'%Y-%m-%d')

    return _to_date


def strip_accents(normalize=u'NFD', uce=u'Mn'):
    u"""Return a accents stripped string

    .. note::

        This function is a rewriting of unicodedata.normalize

    >>> 'address': Column(3, strip_accent())

    :param normalize: Normalize code
    :type normalize: str
    :param uce: Unicode category exclusion
    :type uce: str
    :returns: callback_model

    """
    def _strip_accents(session, model, field, value, line):
        return tools.string_accent(value, normalize, uce)

    return _strip_accents


def city_cedex(res=None, cedex_code=False):
    u"""Check if a cedex code is in the town name.
    Return the relative string to ``res`` argument

    >>> # initial value for column 6 = 'Paris Cedex 9'
    >>> 'city':  Column(6, city_cedex('city')) # Returns 'PARIS'
    >>> 'cedex': Column(6, city_cedex('cedex')) # Returns 'CEDEX 9'

    :param res: Relative string returned
    :type res: str
    :param cedex_code: Returns only code or full code ('6', 'CEDEX 6')
    :type cedex_code: str
    :returns: callback_model

    """
    def _city_cedex(session, model, field, value, line):
        city = value
        value = strip_accents(session, model, field, value.lower(), line)
        cedex = u""

        if value.count(u'cedex'):
            city = value.split(u'cedex')[0]
            try:
                cedex = u"cedex %s" % int(value.split(u'cedex')[1])
            except Exception:
                cedex = u"cedex"

        if res == u'city':
            return city
        elif res == u'cedex':
            return cedex
        else:
            return (city, cedex)

    return _city_cedex


def zfill(*args):
    u"""Return a zfilled string.

    .. note::

        This function is a rewriting of string.zfill, same signature

    >>> 'address': Column(3, zfill(5))

    :returns: callback_model

    """
    def _zfill(session, model, field, value, line):
        return value.zfill(*args)

    return _zfill


def upper(*args):
    u"""Return a uppered string.

    .. note::

        This function is a rewriting of string.upper, same signature

    >>> 'address': Column(3, upper())

    :returns: callback_model

    """
    def _upper(session, model, field, value, line):
        return value.upper(*args)

    return _upper


def capitalize(*args):
    u"""Return a capitalized string.

    .. note::

        This function is a rewriting of string.capitalize, same signature

    >>> 'address': Column(3, capitalize())

    :returns: callback_model

    """
    def _capitalize(session, model, field, value, line):
        return value.capitalize(*args)

    return _capitalize


def strip(*args):
    u"""Return a stripped string.

    .. note::

        This function is a rewriting of string.strip, same signature

    >>> 'address': Column(3, strip())

    :returns: callback_model

    """
    def _strip(session, model, field, value, line):
        return value.strip(*args)

    return _strip


def get_phones(type, prefix=u'+33'):
    u"""Returns numbers contained in the columns values. Numbers must be in a
    french form such as `0123456789` or '+33123456789' (No matters for spaces).
    Any other numbers must not be in the columns values.

    ..note::

        Example of a complex working string::

        "The number of Mr SMITH is 0123456789, his wife 33 234 567 894, and their son 06 24 568495"

        will returns independently of what type but with prefix `(+33)`:
        dict = {
            'phone': ['(+33) 1 23 45 67 89', '(+33) 2 34 56 78 94'],
            'mobile': ['(+33) 6 24 56 84 95'],
            'all': ['(+33) 1 23 45 67 89', '(+33) 2 34 56 78 94', '(+33) 6 24 56 84 95'],
            'value': "The number of Mr SMITH is 02XXXXXXXX, his wife 33 2XX XXXXXX, and their son 06 XX XX XX XX XX"
            }

        >>> 'phone':  Column([3, 4], get_phones('phone', prefix='+33'))
        >>> 'mobile': Column([3, 4], get_phones('mobile', prefix='+33'))
        >>> 'phone': Column([3, 4], get_phones('all', prefix='+33'))

    :param type: The format to returns
    :type type: str
    :param prefix: The prefix to insert
    :type prefix: str
    :returns: str (prefix X XX XX XX XX / prefix X XX XX XX XX ...)

    """
    assert type
    if type not in (u'phone', u'mobile', u'all', u'dict'):
        raise Exception(
            u'`type` is incorrect. Valid values are `phone`, `mobile`, `all`')

    def _get_phones(session, model, field, value, line):
        res = {u'phone': [], u'mobile': [], u'all': [], u'value': value}

        # On ne garde que les caractères numériques
        string = re.sub(u'[^0-9]', u'', value)
        stop = False
        i = 0
        while not stop:
            i += 1
            # Chaine vide donc arrêt (Cas initial ou après traitement sans numéros)
            if not string:
                stop = True
                continue

            # Traitement du premier numéro - suppression du prefix
            if string.startswith(u'0'):
                string = string[1:]
            elif string.startswith(u'33'):
                string = string[2:]
            else:
                string = string[1:]
                # Next loop
                continue

            # Le numéro est-il complet (cas de fin de chaine)
            if len(string) < 9:
                # Next loop
                continue

            # Isolement du numéro
            phone = string[:9]

            # On le découpe en paire à l'exception du premier numéro
            tel_list = [phone[0], phone[1:3], phone[3:5],
                        phone[5:7], phone[7:9]]

            # Cas du téléphone portable
            if tel_list[0] == u'6':
                res[u'mobile'].append(
                    (u'%s %s' % (prefix, u' '.join(tel_list))))
                res[u'all'].append((u'%s %s' % (prefix, u' '.join(tel_list))))
            # Autre cas
            else:
                res[u'phone'].append(
                    (u'%s %s' % (prefix, u' '.join(tel_list))))
                res[u'all'].append((u'%s %s' % (prefix, u' '.join(tel_list))))

            # Next loop
            string = string[9:]

        if type is u'dict':
            return res

        phones = res[type]
        if len(phones) > 1:
            result = u' / '.join(phones)
        elif len(phones) == 1:
            result = phones[0]

        return result

    return _get_phones
