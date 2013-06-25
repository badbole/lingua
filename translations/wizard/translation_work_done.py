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
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


def log_time():
    tstamp = datetime.now(timezone('Europe/Zagreb'))
    return tstamp.strftime(DEFAULT_SERVER_DATETIME_FORMAT )

class translations_work_done(osv.osv_memory):
    _name = "translations.work.done"
    _description = "Enter number of cards done"
    
    _columns = {
                'cards':fields.float('Translated cards', required=True),
                }
    
    def enter_number_cards(self, cr, uid, ids, context):
        cards=self.browse(cr, uid, ids[0]).cards
        if cards == 0 : #ili mozda je moguće???
            raise osv.except_osv(_('Error !'), _('Finishing work with 0 cards done is not possible'))
        caller_id=context.get('active_id',False)
        work_obj = self.pool.get('translation.work').browse(cr, uid, caller_id)
        job_start = work_obj.job_start or log_time()
        work_vals = {
                     'job_start':job_start,
                     'job_stop':log_time(),
                     'cards_done':cards,
                     'job_done':True
                     }
        work_obj.write(work_vals) 
        type=work_obj.work_type
        w_finished = work_obj.check_task_type_finish(work_obj.task_id.id , type)
        task_vals={}
        
        if type=='trans':
            task_vals['trans_cards'] = cards + work_obj.task_id.trans_cards
            if not work_obj.task_id.trans_start:
                task_vals['trans_start']=log_time()
            if w_finished : task_vals['trans_finish']=log_time()
        elif type=='lect':
            task_vals['lect_cards'] = cards + work_obj.task_id.lect_cards
            if not work_obj.task_id.lect_start:
                task_vals['lect_start']=log_time()
            if w_finished : task_vals['lect_finish']=log_time()
        task_obj=self.pool.get('translation.document.task')
        task_obj.write(cr, uid, work_obj.task_id.id, task_vals)
        task_obj.check_task_state(cr, uid, work_obj.task_id.id)
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'translations', 'translation_document_task_form_view')
        view_id = view_ref and view_ref[1] or False,
        return {
                'type': 'ir.actions.act_window',
                'name': _('Translation task'),
                'res_model': 'translation.document.task',
                'res_id': work_obj.task_id.id,
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id,
                'target': 'current',
                'nodestroy': True,
                }
    

    def finish_task(self, cr , uid, task, caller_id, context=None):
        if context == None: context={}
        task_vals={}
        type = context.get('type',False)
        if type == 'trans':
            if task.lectoring:
                task_vals['state']='lect_w'
            else:
                task_vals['state']='finish'
            task_vals['trans_finish']= log_time()
            task_vals['trans_cards']=self.get_total_cards(cr, uid, type, caller_id, context)
        elif type == 'lect':
            task_vals={'state':'finish','lect_finish':log_time()}
            task_vals['lect_cards']=self.get_total_cards(cr, uid, type, caller_id, context)
            
        self.pool.get('translation.document.task').write(cr, uid, caller_id, task_vals)
        if self.check_document_finish(cr, uid, task.document_id.id, context):
            self.finish_document(cr, uid, task.document_id.id, 
                                          task.document_id.evidention_id.id, context)
        return True
    
translations_work_done()
    