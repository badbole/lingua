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
from osv import osv, fields
from openerp.tools.translate import _
from datetime import datetime, date
from pytz import timezone
import tools, time
import logging
_logger = logging.getLogger(__name__)
import openerp.addons.decimal_precision as dp
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


def log_time():
    
    #set UTC time on server an use this
    tstamp = datetime.now(timezone('Europe/Zagreb')) 
    # if server timezone is set use:
    #tstamp = datetime.now() #
    return tstamp.strftime(DEFAULT_SERVER_DATETIME_FORMAT )


class translation_type(osv.Model):
    _name = "translation.type"
    _decription = "Possible translation types"
    _columns = {
                'name':fields.char('Type', size=128),
                'description':fields.text('Type description')
                #'evidention_ids':fields.one2many('lingua.evidencija', 'type_id', 'Evidentions'),
                #'employee_ids':fields.many2many('hr.employee', 'lingua_translation_type_hr_employee_rel', 'lingua_translation_type_id', 'hr_employee_id', 'Specialized translators'),
                }

class translation_evidention(osv.osv):
    _name = 'translation.evidention'
    _inherit = ['mail.thread']
    _description = 'Evidention of translations'
    _translation_status = [('draft','Draft')
                   ,('open','Open')
                   ,('process','In process')
                   ,('deliver','For delivery')
                   ,('finish','Finished')
                   ,('cancel','Canceled')
                   ]
    
    def _get_total_cards(self, cr, uid, ids, field_names, field_value, context=None):
        """
        returns number of cards translated and lectured as entered by employees
        """
        res={}
        
        for evid in self.browse(cr, uid, ids):
            tr_cards = le_cards = es_cards = 0
            for document in evid.document_ids:
                for task in document.task_ids:
                    tr_cards += task.trans_cards
                    le_cards += task.lect_cards
                    es_cards += task.est_cards
            res[evid.id] = {'tr_cards':tr_cards, 'le_cards':le_cards, 'total_cards':es_cards}
        return res
    
        
    def _get_number_of_days(self, date_from, date_to):
        """Returns a float equals to the timedelta between two dates given as string."""
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        #from_dt = datetime.strptime(date_from, DATETIME_FORMAT)
        to_dt = datetime.strptime(date_to, DATETIME_FORMAT)
        timedelta = to_dt - date_from #from_dt
        diff_day = timedelta.days #+ float(timedelta.seconds) / 86400
        return diff_day
    
    def _get_deadline(self, cr, uid, ids, field_name, field_value, context=None):
        res={}
        for id in self.browse(cr, uid, ids):
            if id.state == 'finish':
                res[id.id] = False
            else:
                if id.date_due == False:
                    res[id.id] = False
                else:
                    diff = self._get_number_of_days(datetime.now(),id.date_due )
                    if diff == 0:
                        time_remain="Today!"
                    elif diff == 1:
                        time_remain = "Tomorow"
                    elif diff >1 :
                        time_remain = "%d days" %(diff)
                    elif diff<0:
                        time_remain="Late %d days!" %(diff)
                    res[id.id] = time_remain
        return res
    
    _columns = {
        'name': fields.char('Name', size=128 , select=1),
        'ev_sequence':fields.char('Evidention Number', size=64, select=1),
        'partner_id':fields.many2one('res.partner','Partner', required=1),
        'date_recived':fields.datetime('Recived', help="Keep empty to use the current date"),
        'date_due':fields.datetime('Deadline'),
        'note':fields.text('Note'),
        'state':fields.selection (_translation_status,'Evidention status'),
        'document_ids':fields.one2many('translation.document','evidention_id','Documents', required=1),
        'total_cards':fields.function(_get_total_cards, string='Est cards', type="float",multi="Cards"),
        'tr_cards':fields.function(_get_total_cards, string='Translated cards', type="float", multi="Cards"),
        'le_cards':fields.function(_get_total_cards, string='Lectured cards', type="float", multi="Cards"),
        'time_remain':fields.function(_get_deadline, string="Deadline", type="char")
                }

    _defaults = {
                 'ev_sequence':'Draft Evidention',
                 'name':'Translation ',
                 'state':"draft",
                 }
    
    _order = "id desc"
    
    def check_evidention_state(self, cr, uid, evid_id, context=None):
        evidention = self.pool.get('translation.evidention').browse(cr, uid, evid_id)
        finished = True
        for doc in evidention.document_ids:
            if doc.state != 'finish':
                finished = False
        if finished :evidention.write({'state':'deliver'})
        return finished
    
    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'state': 'draft',
            'sequence': False,
            'date_recived': False,
            'document_ids': False,
            'total_cards': False
        })
        return super(translation_evidention, self).copy(cr, uid, id, default, context=context)
    
    def check_before_recive(self, cr, uid, ids, context=None):
        if not ids: return False
        for evidention in self.browse(cr, uid, ids):
            if not evidention.document_ids:
                raise osv.except_osv(_('Error !'), _('No documents found, nothing to recive!') )
            for doc in evidention.document_ids:
                if not doc.task_ids:
                    raise osv.except_osv(_('Warning !'), _('No languages for translation\n document : %s!') % (doc.name))
        return True
    
    def action_evidention_recive(self, cr, uid, ids, context=None):
        self.check_before_recive(cr, uid, ids)
        evid_list, doc_list, task_list = [], [], []
        for evidention in self.browse(cr, uid, ids):
            evid_={}
            evid_['id'] = evidention.id
            if not evidention.date_recived: 
                evid_['date_recived'] = log_time() #datetime.now(timezone('Europe/Zagreb')) #log_time()
            evid_['ev_sequence'] = self.pool.get('ir.sequence').get(cr, uid, 'translation_evidention')
            evid_['state'] = 'open'
            for doc in evidention.document_ids:
                doc_={}
                doc_['doc_sequence'] = '-'.join([evid_['ev_sequence'],str(len(doc_list)+1)])
                doc_['partner_id'] = evidention.partner_id.id
                for task in doc.task_ids:
                    task_={}
                    task_name = '-'.join([doc_['doc_sequence'], 
                                          doc.language_id.iso_code2.upper(), 
                                          task.language_id.iso_code2.upper(),  'T'])
                    if task.lectoring : task_name = ''.join([task_name,'L'])
                    task_['name']=task_name
                    if task.translate_ids : 
                        task_['state'] = 'assign'
                        doc_['state'] = 'open' 
                    task_['est_cards'] = doc.cards_estm
                    task_['partner_id'] = evidention.partner_id.id,
                    task_['language_origin'] = doc.language_id.id
                    task_list.append ([task.id, task_])
                doc_list.append ([doc.id, doc_])
            evid_list.append([evidention.id, evid_])
            self.write_recived_all(cr, uid, task_list, doc_list, evid_list)
            self.write(cr, uid, evidention.id,{})
        return True
    
    
    
    def write_recived_all(self,cr, uid, task_list, doc_list, evid_list, context=None ):
        task_obj=self.pool.get('translation.document.task')
        for t in task_list:
            """
            task = task_obj.browse(cr, uid, t[0])
            if task.translate_ids:
                t[1]['translate_ids'] = write_many2many(self,task.translate_ids)
            if task.lecture_ids:
                t[1]['lecture_ids'] = write_many2many(self, task.lecture_ids)
            """
            task_obj.write(cr, uid, t[0], t[1])
        doc_obj=self.pool.get('translation.document')
        for d in doc_list:
            doc_obj.write(cr, uid, d[0], d[1])
        for e in evid_list:
            self.write(cr, uid, e[0], e[1]) 
        return True
    
def write_many2many(self, browse_list, context=None):
    """
    function returns correct many2many tuple from browse record in many2many
    """
    list=[]
    for l in browse_list:
        list.append(l.id)
    return [[6,0,list]]
        
        
class translation_document(osv.Model):
    _name = 'translation.document'
    _inherit = ['mail.thread']
    _description = 'Document for translation' 
    
    _document_status =[('draft',"Draft")
                      ,('open',"Open")
                      ,('process',"In process")
                      ,('finish',"Finished")
                      ,('cancel',"Canceled")
                      ]
    
    _merge_with = [('original','Original'),
                   ('copy','Copy')]
    
    _columns = {
                'name':fields.char('Document', size=256, required="1", search="1",
                                   help="Some descriptive name for document, like: TV Manual, High school diploma..."),
                'doc_sequence':fields.char('Sequence', size=128),
                'evidention_id':fields.many2one('translation.evidention','Evidention'),
                'language_id':fields.many2one('hr.language','Origin language', required=1, domain="[('employee_ids','!=',False)]"),
                'type_id':fields.many2one('translation.type', 'Type'),
                'cards_estm':fields.float('Text cards', help="Estimated number of cards for translating" , required="1"),
                'date_due':fields.datetime('Deadline'),
                'task_ids':fields.one2many('translation.document.task','document_id','Translate to'),
                'state':fields.selection(_document_status, 'Document status'),
                'partner_id':fields.many2one('res.partner','Partner'),
                'certified':fields.boolean('Certified'),
                'merge_with':fields.selection(_merge_with,'Merge with'),
                
                }
    
    def check_document_state(self, cr, uid, doc_id, context=None):
        document = self.pool.get('translation.document').browse(cr, uid, doc_id)
        finished = True
        for task in document.task_ids:
            if task.state != 'finish':
                finished = False
        if finished: 
            document.write({'state':'finish'})
            self.pool.get('translation.evidention').check_evidention_state(cr, uid, document.evidention_id.id)
        return finished

    _defaults = {
                 'cards_estm':1,
                 'state':'draft',
                 }
    _order = "id desc"
    
class translation_document_task (osv.Model):
    _name = 'translation.document.task'
    _inherit = ['mail.thread']
    _description = 'Signle langugae for translation'
    
    
    _document_task_status =[('draft',"Draft")
                           ,('assign',"Assigend")
                           ,('trans',"Translation in progress")
                           ,('lect_w','Ready for lectoring')
                           ,('lect','Lectoring in progress')
                           ,('finish',"Finished")
                           ,('cancel',"Canceled")
                           ]
    
    def onchange_lang_select_competent(self, cr, uid, ids, language_id, context=None):
        return {'domain':{'translate_ids':[('language_ids','in',language_id)]}}
    
    def _get_task_description(self, cr, uid, ids, field_name, field_value, context=None):
        if len(ids)==0:return False
        tasks=self.browse(cr, uid, ids)
        res={}
        for t in tasks:
            res[t.id]=' '.join([t.document_id.name,'\n',_('from'),
                               t.language_origin.trans_from,_('to'),
                               t.language_id.trans_to])
        return res
    
    def check_task_state(self, cr, uid, task_id, context=None):
        task = self.browse(cr, uid, task_id)
        status = 'draft'
        if task.translate_ids and task.translate_ids[0]:
            status = 'assign'
            if task.trans_start and not task.trans_finish:
                status='trans'
            if task.trans_finish:
                status='finish'
                if task.lectoring:
                    status='lect_w'
        if status=='lect_w':
            if task.lect_start:
                status='lect'
                if task.lect_finish:
                    status="finish"
        if task.state != status:
            task.write({'state':status})
        if status == 'finish':
            self.pool.get('translation.document').check_document_state(cr, uid, task.document_id.id)
        return status #task.write({'state':status})        
    
    _columns = {
                'name':fields.char('Name',size=64),
                'description':fields.function(_get_task_description, string="Description", type="char"),
                'document_id':fields.many2one('translation.document','Document'),
                'language_origin':fields.many2one('hr.language','Translate from'),
                'language_id':fields.many2one('hr.language','Translate to', required=True, domain="[('employee_ids','!=',False)]"),
                'type_id':fields.many2one('translation.type','Type'),
                'partner_id':fields.many2one('res.partner','Partner'),
                'lectoring':fields.boolean('Mandatory lectoring'),
                'state':fields.selection (_document_task_status,'Translation status'),
                #'state':fields.function(check_task_state,'Translation status'),
                'note':fields.text('Note'),
                'est_cards':fields.float('Cards estimate'),
                'translate_ids':fields.many2many('hr.employee',
                                                 'translate_task_translate_employee_rel',
                                                 'translation_document_task_translate_ids',
                                                 'hr_employee_translate_task_ids', 
                                                 'Translator', ),
                'trans_start':fields.datetime('Date/time start'),
                'trans_finish':fields.datetime('Date/time finish'),
                'trans_cards':fields.float('Cards translated'),
                'lecture_ids':fields.many2many('hr.employee',
                                                 'translate_task_lecture_employee_rel',
                                                 'translation_document_task_lecture_ids',
                                                 'hr_employee_lecture_task_ids', 
                                                 'Translator', ), #selection='_get_translators'
                'lect_start':fields.datetime('Date/time start'),
                'lect_finish':fields.datetime('Date/time finish'),
                'lect_cards':fields.float('Cards lectured'),
                'certified':fields.boolean('Certified'),
                'work_ids':fields.one2many('translation.work','task_id','Work log'),
                #'user_status':fields.function(_my_task_work_status, string='My status', type="char"),
                #'user_competent':fields.function(_my_task_competence, string="Competent", type="boolean")
                }
    
    _defaults = {
                 'state': lambda *a:'draft',
                 'lectoring':True,
                 }

    _order = "id desc"
    
    def translation_work_create(self, cr, uid, task, type, employee, context=None):
        work_vals = {
                'task_id':task,
                'work_type': type,
                'employee_id': employee,
                }
        return self.pool.get('translation.work').create(cr, uid, work_vals)
    
    def open_employee_work_log(self, cr, uid, ids, w_list, type, context=None):
        work = self.pool.get('translation.work')
        emp_list= w_list[0][2] 
        task_obj=self.browse(cr, uid, ids[0])
        for emp_id in emp_list:
            write_it = True
            for job in task_obj.work_ids:
                if emp_id==job.employee_id.id and type==job.work_type:
                    write_it=False
            if write_it : self.translation_work_create(cr, uid, ids[0], type, emp_id)
        return True
    
    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, int):
            ids=[ids]
        translate_ids = vals.get('translate_ids')
        lecture_ids = vals.get('lecture_ids')
        if lecture_ids and (lecture_ids[0][0]==6 ):
            self.open_employee_work_log(cr, uid, ids, lecture_ids, 'lect')
        if translate_ids and (translate_ids[0][0]==6 ):
            self.open_employee_work_log(cr, uid, ids, translate_ids, 'trans')
        if self.browse(cr, uid, ids[0]).state=='draft' and lecture_ids or translate_ids:
            vals['state']='assign'
        return super(translation_document_task, self).write(cr, uid, ids, vals, context)
    
    
class translation_work(osv.Model):
    _name = 'translation.work'
    _description = 'Work of translators'
    
    _get_work_type=[('trans','Translating'),
                    ('lect','Lectoring'),
                    ('other','Other')]

    def _get_time_spent(self, cr, uid, ids, field_name, field_values, context=None):
        res = {}
        for job in self.browse(cr, uid, ids):
            if job.job_stop: 
                time_from=datetime.strptime(job.job_start, DEFAULT_SERVER_DATETIME_FORMAT)
                time_to = datetime.strptime(job.job_stop, DEFAULT_SERVER_DATETIME_FORMAT)
                delta = time_to - time_from
                if delta.days > 0:
                    diff = time_diff_formatter(self,delta) 
                else:
                    diff = time_diff_formatter(self,delta) 
                res[job.id]=[diff]
            else:
                res[job.id]=False
        return res
    
    _columns = {
                'name':fields.char('Name',size=128),
                'task_id':fields.many2one('translation.document.task','Translation task'),
                'work_type':fields.selection(_get_work_type,'Type of work'),
                'employee_id':fields.many2one('hr.employee','Employee'),
                'job_start':fields.datetime('Start'),
                'job_stop':fields.datetime('Stop'),
                'cards_done':fields.float('Cards done',help="Enter value for this session or leave blank"),
                'job_done':fields.boolean('Finished'),
                'cards_total':fields.float('Total done'),
                'time_spent':fields.function(_get_time_spent, string='Time on job', type="char"),
                } 
    
    _order = "id desc"
    
    def copy(self, cr, uid, id, default=None, context=None):
        result= super(translation_work, self).copy(cr, uid, id, default, context=context)
        if not default:
            default = {}
        default.update({
            'job_start': False,
            'job_stop': False,
            'cards_total': False,
        })
        return result #super(translation_work, self).copy(cr, uid, id, default, context=context)
    
    # button in every work log line 
    def button_start(self, cr, uid, ids, context=None):
        work_obj = self.browse(cr, uid, ids[0])
        task_id = work_obj.task_id.id
        work_type=work_obj.work_type
        task_obj = self.pool.get('translation.document.task')
        if work_type=='trans':
            if not work_obj.task_id.trans_start:
                task_obj.write(cr, uid, task_id, {'trans_start':log_time()})
                self.pool.get('translation.document').write(cr, uid, work_obj.task_id.document_id.id, {'state':'process'})
        elif work_type=='lect':
            if not work_obj.task_id.lect_start:
                task_obj.write(cr, uid, task_id, {'lect_start':log_time()})
        self.write(cr, uid, ids[0], {'job_start':log_time()})
        task_obj.check_task_state(cr, uid, task_id )

        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'translations', 'translation_document_task_form_view')
        view_id = view_ref and view_ref[1] or False,
        return {
                'type': 'ir.actions.act_window',
                'name': _('Translation task'),
                'res_model': 'translation.document.task',
                'res_id': task_id,
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id,
                'target': 'current',
                'nodestroy': True,
                }
        
    def check_task_type_finish(self, cr, uid, ids, task_id, work_type, context=None):
        works = self.search(cr, uid, [('task_id','=',task_id),('work_type','=',work_type)])
        finish=True
        for w in self.browse(cr, uid, works):
            if not w.job_done: finish=False
        return finish

def get_employee_from_uid(self, cr,  uid, context=None):
    return self.pool.get('hr.employee').search(cr, uid, [('resource_id.user_id','=', uid)] )[0]

def time_diff_formatter(self, timedelta):
    res =""
    if timedelta.days > 0 :
        res = "%s days" % (timedelta.days)
    sec = timedelta.seconds
    hours, remain =divmod(sec, 3600)
    mins, secs = divmod(remain, 60)
    res += " %s:%s:%s" % (hours, mins, secs)
    return res
    
