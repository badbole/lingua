# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Module: lingua_co
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
import psycopg2

class translation_evidention(osv.Model):
    _inherit = 'translation.evidention'
    
    def get_default_prostor_id(self, cr, uid, id, context=None):
        return self.pool.get('res.users').browse(cr, uid, uid).prostor_id.id or False
    
    _columns = {
                'prostor_id':fields.many2one('fiskal.prostor','Podružnica'),
                'dogovorena_cijena':fields.char('Dogovorena cijena', size=64)
                }
    
    _defaults = {
                 'prostor_id':get_default_prostor_id
                 }
    
    def print_smir(self, cr, uid, ids, context=None):
        '''
        This function prints the SMIR envelope
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        datas = {
             'ids': ids,
             'model': 'translation.evidention',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'smir',
            'datas': datas,
            'nodestroy' : True
        }
    

    