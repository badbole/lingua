# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Module: lingua_co_
#    Author: Davor Bojkić
#    mail:   bole@dajmi5.com
#    Copyright (C) 2012- Daj Mi 5, 
#                  http://www.dajmi5.com
#
#    Description : totaly usless part, made upon request of customer 
#                   Only description in this module is quoting George Carlin - 
#Never argue with an idiot. 
#They will only bring you down to their level 
#and beat you with experience.
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

class res_partner(osv.Model):
    _inherit = "res.partner"
    
    def _get_clean_oib(self, cr, uid, ids, field_name, field_value, context=None):
        res={}
        for p in self.browse(cr, uid, ids):
            res[p.id]=False
            if p.vat and p.vat[:2]=="HR":
                res[p.id] = p.vat[2:] 
        return res
        
    _columns = {
                'OIB':fields.function(_get_clean_oib, string='OIB', type="char")
                }