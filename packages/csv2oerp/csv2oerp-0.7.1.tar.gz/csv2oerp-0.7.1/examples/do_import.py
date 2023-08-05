#!/usr/bin/env python
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
host = '172.24.1.169'
port = 8069
dbname = 'csv2oerp07'
user = 'admin'
pwd = 'admin'
lang = 'fr_FR'
oerp = Openerp(host, port, user, pwd, dbname, lang)

#===============================================================================
# res_partner_address
#===============================================================================
# 0: Address Type
# 1: City
# 2: Contact Name
# 3: Country Name
# 4: Customer
# 5: E-Mail
# 6: Phone
# 7: Street
# 8: Street2
# 9: Supplier
# 10: Title
# 11: Zip
# 12: Partner Name
# 13: Partner Language
# 14: Partner Country Name
# 15: Partner City
# 16: Salesman Name
# 17: Salesman Email
res_partner_address = Session(u'res_partner_address', 'res_partner_address.csv',
        delimiter=';', quotechar='"', encoding='utf8')

salesman = Model(u'res.users', fields=[
    Field('name', [16]),
    Field('user_email', [17]),
    Field('login', [17]),
    ], update=False, search=['name', 'user_email'])

country_partner = Model(u'res.country', fields=[
    Field('name', [3]),
    ], update=False, search=['name'])

country_address = Model(u'res.country', fields=[
    Field('name', [14]),
    ], update=False, search=['name'])

partner_title = Model(u'res.partner.title', fields=[
    Field('name', [10]),
    ], update=False, search=['name'])

partner = Model(u'res.partner', fields=[

    Field('customer', [4], callbacks=[cb.to_boolean()]),
    Field('supplier', [9], callbacks=[cb.to_boolean()]),
    Field('name', [12]),
    Field('lang', [13]),
    
    Field('user_id', relation=salesman),
    Field('country', relation=country_partner),

    ], search=['name', 'city'])

addresses = Model(u'res.partner.address', fields=[

    Field('type', [0]),
    Field('city', [1]),
    Field('name', [2]),
    Field('email', [5]),
    Field('phone', [6]),
    Field('street', [7]),
    Field('street2', [8]),
    Field('zip', [11]),

    Field('partner_id', relation=partner),
    Field('country_id', relation=country_address),
    Field('title', relation=partner_title),

    ], search=['type', 'partner_id'])

res_partner_address.join(oerp, [addresses, ])

# Show statistics
csv2oerp.show_stats()
