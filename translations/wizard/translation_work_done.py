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
    
    def check_me_or_other(self, cr, uid, ids, context=None):
        return True
    
    _columns = {
                'cards':fields.float('Translated cards', required=True),
                'finish':fields.boolean('Finished'),
                'employee_id':fields.many2one('hr.employee', 'Employee'),
                }
    
    def task_get(self, cr, uid, caller_id):
        return self.pool.get('translation.document.task').browse(cr, uid, caller_id)
    
    def enter_number_cards(self, cr, uid, ids, context):
        cards=self.browse(cr, uid, ids[0]).cards
        if cards == 0 : #ili mozda je moguće???
            raise osv.except_osv(_('Error !'), _('Finishing work with 0 cards done is not possible'))
        caller_id=context.get('active_id',False)
        task = self.task_get(cr, uid, caller_id)
        emp_id = self.pool.get('hr.employee').search(cr, uid, [('resource_id.user_id','=', uid)] )[0]
        assert len(task.work_ids)>0 #need at least one task present
        work_vals={}
        done = False
        for work in task.work_ids:
            if not work.job_stop:
                if work.employee_id.id == emp_id:
                    work_id = work.id
                    work_vals = {
                                 'job_stop':log_time(),
                                 'cards_done':cards,
                                 'job_done':True
                                 }
        
        self.pool.get('translation.work').write(cr, uid, work_id, work_vals) 
        self.check_task_finished(cr, uid, caller_id, context=context)
        return {'type': 'ir.actions.act_window_close'}
    
    
    def check_task_finished(self, cr, uid, caller_id, context):
        res=True
        type = context.get('type',False)
        task= self.task_get(cr, uid, caller_id)
        if type=='trans':
            workers = task.translate_ids
        elif type=='lect':
            workers = task.lecture_ids
        assert len(workers)>0 # nema smisla ako nema workera dalje ici
        
        jobs = task.work_ids
        jobs_finished=[]
        for job in jobs:
            if job.work_type==type and job.job_done :
                jobs_finished.append(job.employee_id.id)
        
        for person in workers:
            if not person.id in jobs_finished:
                res=False
        if res: 
            self.finish_task(cr, uid, task, caller_id, context)
        return res
    
    def get_total_cards(self, cr, uid, type, caller_id, context):
        res=0
        task = self.task_get(cr, uid, caller_id)
        for job in task.work_ids:
            if job.work_type == type and job.job_done: 
                res += job.cards_done
        return res
    
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
    
    def check_document_finish(self, cr, uid, doc_id, context=None):
        document = self.pool.get('translation.document').browse(cr, uid, doc_id)
        finished = True
        for task in document.task_ids:
            if task.state != 'finish': finished = False
        return finished
    
    def finish_document(self, cr, uid, doc_id, evid_id, context=None):
        document = self.pool.get('translation.document')
        document.write(cr, uid, doc_id, {'state':'finish'})
        self.check_evid_finish(cr, uid, evid_id, context)
        return True 
    
    def check_evid_finish(self, cr, uid, ev_id, context=None):
        evidention = self.pool.get('translation.evidention')
        evid = evidention.browse(cr, uid, ev_id)
        finish = True
        for doc in evid.document_ids:
            if doc.state != 'finish': finished = False
        if finish:
            evidention.write(cr, uid, ev_id, {'state':'deliver'})
        return True
    
translations_work_done()
    