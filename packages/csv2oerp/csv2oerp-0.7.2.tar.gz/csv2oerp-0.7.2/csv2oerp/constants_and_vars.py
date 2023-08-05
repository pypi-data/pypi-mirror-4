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
"""
csv2oerp Constants ans variables.

"""

EXIT_OK = 0
EXIT_WARNING = 1
EXIT_ERROR = 2
EXIT_UNKNOWN = 3
LOGGER = None
STATS = {
    u'duration': 0,
    u'objects': {}
    }
FORMAT=u'%(asctime)-15s %(name)s row[%(line_num)4s] col[%(col_num)2s] %(levelname)-8s %(message)s'

ACTION_PATTERN = {
    u'skip': u'SKIP',
    u'replace': u'REPLACE',
    u'ignore': u'IGNORE',
    u'noupdate': u'NO_UPDATE',
    u'nocreate': u'NO_CREATE',
    u'unique': u'UNIQUE',
    u'required': u'REQUIRED',
    u'router': u'ROUTER',
    }

