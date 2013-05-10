# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Module: lingua
#    Author: Davor Bojkić
#    mail:   bole@dajmi5.com
#    Copyright (C) 2012- Daj Mi 5, 
#                  http://www.dajmi5.com
#    Contributions: 
#                   
#                    
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class lingua_price(osv.osv):
    _name="lingua.price"
    _description = "Prices forming"
    
    _columns = {
                'name':fields.char('Price', size=64),
                'parent_id':fields.many2one('lingua.price','Parent'),
                'child_ids':fields.one2many('lingua.price','parent_id', string="Child product price"),
                'price':fields.float('Price', digits_compute=dp.get_precision('Product Price'), help="Base price for main product"),
                'discount_name':fields.char('Discount name', size=128),
                'discount':fields.integer('Discount %'),
                
                }
    
    