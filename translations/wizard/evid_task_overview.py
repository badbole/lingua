# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Module: translations
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
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import datetime, date
from pytz import timezone

class evid_task_overview(osv.osv_memory):
    _name = "evid.task.overview"
    _description = "Enter number of cards done"
    
    def _fields_get(self, cr, uid, ids, field_names, field_value,  context=None):
        assert len(ids) == 1 # one evidention at a time
        caller_id=context.get('active_id',False)
        evid = self.pool.get('translation.evidention').browse(cr, uid, ids[0])
        res, vals={}, {}
        for doc in evidention.document_ids:
            vals['document'] = doc.name
            vals['document_id']=doc.id
            vals['card_est']=doc.cards_estm
            for task in doc.task_ids:
                vals['name']=task.name
                vals['card_trans']=task.trans_cards
                vals['card_lect']=task.lect_cards
                
        res[len(res)]=[len(res),vals]
        return res
    
   
    
    _columns = {
                'sequence':fields.integer('Sequence'),
                'name':fields.char('Task code', size=128),
                'document':fields.char('Document', size=128),
                'document_id':fields.integer('document_id'),
                'task':fields.char('Task',size=64),
                'card_est':fields.float('Estimated'),
                'translators':fields.text('Translators', size=256),#prevoditelj1 (n), prevoditelj2 (n)
                'card_trans':fields.float('Translated'),
                'lectors':fields.char('Lectors', size=256),
                'cards_lect':fields.float(),
                }