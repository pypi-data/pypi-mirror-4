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
csv2oerp is intended to be used to simplify data migration from CSV to OpenERP.

"""

__author__ = u'Stéphane Mangin',
__author_email__ = u'stephane.mangin@freesbee.fr',
__email__ = u'stephane.mangin@freesbee.fr',
__description__ = u'Python CSV to OpenERP importation library',
__license__ = u'LGPLv3+',
__version__ = u'0.7'

from csv2oerp import unicode_csv 
from csv2oerp import tools
from csv2oerp import callbacks
from csv2oerp import models
from csv2oerp.models import exceptions

from csv2oerp.api07 import *

