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


class account_invoice(osv.Model):
    _inherit = "account.invoice"
    
    
    def _get_default_bank(self, cr, uid, ids, context=None):
        return self.pool.get('res.partner.bank').search(cr, uid, [('company_id','=',1)])[0]
    
        
    _columns = {
                'oib_check':fields.related('partner_id','vat',type='char', string='OIB/VAT' )
                }
    
    _defaults={
              'partner_bank_id':_get_default_bank,
              #'double_check':False
              }
    
    
    
        
    def invoice_memo(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.write(cr, uid, ids, {'sent': True}, context=context)
        datas = {
             'ids': ids,
             'model': 'account.invoice',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'invoice_wo_h',
            'datas': datas,
            'nodestroy' : True
        }
        
    def invoice_print(self, cr, uid, ids, context=None):
        
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.write(cr, uid, ids, {'sent': True}, context=context)
        datas = {
             'ids': ids,
             'model': 'account.invoice',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'invoice_new',
            'datas': datas,
            'nodestroy' : True
            
        }
        
account_invoice()