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
Functions tools module.

"""
import os
import sys
import unicodedata

from csv2oerp import unicode_csv
from csv2oerp.constants_and_vars import STATS

def purge_stats():
    u"""Re-initialize objects activities resume

    """
    global STATS
    STATS = {
        u'objects':{} 
        }

def show_stats():
    u"""Show objectu's model activities resume.
    At the end of an import for example.

    """
    sys.stdout.write(u'\n')
    sys.stdout.write(u'*'*79 + u'\n')
    sys.stdout.write(u'* Objects activities :' + u' '*32 + u'Written Created Skipped *\n')
    sys.stdout.write(u'*'*79 + u'\n')
    for model_name in STATS[u'objects'].keys():
        sys.stdout.write(u'%(name)-51s : %(written)7s %(created)7s %(skipped)7s' %
                STATS[u'objects'][model_name])
        sys.stdout.write(u'\n')
    sys.stdout.write(u'\n')

def strip_accents(string, normalize=u'NFD', category=u'Mn'):
    u""" Replace accents from string with non accented char

    """
    res = (c for c in unicodedata.normalize(normalize, string)
            if unicodedata.category(c) != category)
    return u''.join(res)

def clean_line(line, encode_from=u'utf-8'):
    u""" Encode a list in ``encode_from`` encoding

    """
    return [clean(col, encode_from) for col in line]

def clean_lines(lines, encode_from=u'utf-8'):
    u""" Encode a list of list in ``encode_from`` encoding

    """
    return [clean_line(line, encode_from) for line in lines]

def clean(string, encode_from=u'cp1252'):
    u""" Clean a string by removing returns and double quotes.

    """
    try:
        string = unicode(string)
    except:
        pass
    string.replace(u'\n', u' ').replace(u'"', u'\'')
    try:
        string = strip_accents(string)
    except IndexError:
        pass

    return string 

def generate_code(filenames=(), header=True, mode=u'stdout',  delimiter=u',',
        quotechar=u'"', encoding=u'utf-8'):
    u"""Return a template's skeleton code

    prerequisites: 
        
        Having a columns header to the CSV file
    
    
    :param filenames: Name tuple of filenames to generate the importation code from
    :type filename: tuple
    :param header: First line column's title or not
    :type header: bool
    :param stdout: Printing mode (``stdout``, ``file``)
    :type stdout: str
    
    """
    if mode != u'stdout':
        if os.path.isfile(mode) \
                and raw_input(u'`%s` already existed. Overwrites ?' % mode) in (u'y', u'Y', u'o', u'O'):
            f = open(mode, u'wb')
        else:
            exit()
    else:
        f = sys.stdout

    # HEADERS + SOME CALLBACKS
    f.write(u"""#!/usr/bin/env python
# -*- coding: utf8 -*-
################################################################################
#
# Copyright (c) 2012 STEPHANE MANGIN. (http://le-spleen.net) All Rights Reserved
#                    Stephane MANGIN <stephane.mangin@freesbee.fr>
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
import csv2oerp
from csv2oerp import Field, Model, Session, Openerp
from csv2oerp import callbacks as cb

# OpenERP configuration
host = u'localhost'
port = 8069
dbname = u'database'
user = u'admin'
pwd = u'admin'
lang = u'fr_FR'
oerp = Openerp(host, port, user, pwd, dbname, lang)

""")
    for filename in filenames:
        # Get file name without extention, replace space by underscore
        var = unicode(os.path.splitext(filename)[0].replace(u' ', u'_').replace(u'.', u'_'))
        lines = list(unicode_csv.Reader(filename, delimiter=delimiter, quotechar=quotechar, encoding=encoding))
        #===================================================================
        # Header
        #===================================================================
        f.write(u"#" + u"="*79 + "\n")
        f.write(u"# %s\n" % var)
        f.write(u"#" + u"="*79 + u"\n")
        #===================================================================
        # Mapping
        #===================================================================
        i = 0
        for item in lines[0]:
            f.write(u"# %s: %s\n" % (i, item))
            i += 1
        #===================================================================
        # Functionnal mapping
        #===================================================================
        f.write(u"""%s = Session(u'%s', u'%s',
    delimiter=u'%s', quotechar=u'%s', encoding=u'%s')\n""" %\
            (var, var, filename, delimiter, quotechar, encoding))
        f.write(u"model_name = Model(u'model.name', fields=[\n\n")
        i = 0
        for item in lines[0]:
            f.write(u"    Field(name=u'%s', columns=[%s], callbacks=[]),\n" % (i, item))
            i += 1
        f.write(u'\n')
        f.write(u"    ], update=True, create=True, search=[])\n")
        f.write(u"\n")

    for filename in filenames:
        #===================================================================
        # Start lines
        #===================================================================
        var = unicode(os.path.splitext(filename)[0].replace(u' ', u'_'))
        f.write(u"%s.join(oerp, [, ])\n" % var)
        f.write(u"%s.start()\n" % var)

    #=======================================================================
    # Stats
    #=======================================================================
    f.write(u"\n")
    f.write(u"# Show statistics\n")
    f.write(u"csv2oerp.show_stats()\n")
    if mode != u'stdout':
        f.close()
    print(u'Finished.')
    return

