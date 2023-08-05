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
Unicode CSV reader and writer module.

"""

from copy import deepcopy
import csv

def _is_null(elmt):
    if elmt in ('Null',  'NULL', 'null'):
        return ''
    else:
        return elmt

class Reader:
    u"""Return an unicode CSV reader

    Implementation of csv.reader.
    csv.reader arguments can be passed to the constructor.

    """
    def __init__(self, filename, encoding=u"utf-8", **kwds):
        # Bugfix csv while giving an unicode delimiter:
#  File "/usr/local/lib/python2.7/dist-packages/csv2oerp/models/__init__.py", line 334, in _lines
#    ucsv = unicode_csv.Reader(self.filename, delimiter=self.delimiter, quotechar=self.quotechar)
#  File "/usr/local/lib/python2.7/dist-packages/csv2oerp/unicode_csv.py", line 60, in __init__
#    self.reader = deepcopy(list(csv.reader(csvfile, dialect=dialect, **kwds)))
#TypeError: "delimiter" must be an 1-character string
        if 'delimiter' in kwds:
            kwds['delimiter'] = str(kwds['delimiter'])
        if 'quotechar' in kwds:
            kwds['quotechar'] = str(kwds['quotechar'])

        with open(filename, u"rb") as csvfile:
            if not kwds.get(u'dialect', None):
                dialect = csv.Sniffer().sniff(csvfile.read(1024))
                csvfile.seek(0)
            else:
                dialect = kwds.get(u'dialect', csv.excel)
            self.reader = deepcopy(list(csv.reader(csvfile, dialect=dialect, **kwds)))
        self.offset = 0
        self.encoding = encoding

    def next(self):
        if self.offset >= len(self.reader):
            raise StopIteration
        row = self.reader[self.offset]
        self.offset += 1
        line = [unicode(_is_null(elmt), self.encoding) for elmt in row]
        if not line:
            return self.next()
        return line

    def __iter__(self):
        return self

class Writer:
    u"""Return a unicode writer

    Implementation of csv.writer.
    csv.writer arguments can be passed to the constructor.

    """
    def __init__(self, filename, encoding=u"utf-8", **kwds):
        # Bugfix csv while giving an unicode delimiter:
#  File "/usr/local/lib/python2.7/dist-packages/csv2oerp/models/__init__.py", line 334, in _lines
#    ucsv = unicode_csv.Reader(self.filename, delimiter=self.delimiter, quotechar=self.quotechar)
#  File "/usr/local/lib/python2.7/dist-packages/csv2oerp/unicode_csv.py", line 60, in __init__
#    self.reader = deepcopy(list(csv.reader(csvfile, dialect=dialect, **kwds)))
#TypeError: "delimiter" must be an 1-character string
        if 'delimiter' in kwds:
            kwds['delimiter'] = str(kwds['delimiter'])
        if 'quotechar' in kwds:
            kwds['quotechar'] = str(kwds['quotechar'])

        self.csvfile = open(filename, u'rb')
        self.writer = csv.writer(self.csvfile, **kwds)
        self.encoding = encoding

    def writerow(self, row):
        line = [_is_null(elmt).encode(u"utf-8") for elmt in row]
        if not line:
            return False
        return self.writer.writerow(line)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
        return True

    def __del__(self):
        self.csvfile.close()
        self.writer.close()


