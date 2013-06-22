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
import tools
import logging
_logger = logging.getLogger(__name__)
import openerp.addons.decimal_precision as dp
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


def log_time():
    tstamp = datetime.now() #datetime.now(timezone('Europe/Zagreb'))
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
        tr_cards = le_cards = es_cards = 0
        for evid in self.browse(cr, uid, ids):
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
            'report_name': 'translation.evidention.smir',
            'datas': datas,
            'nodestroy' : True
        }
    
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
                evid_['date_recived'] = datetime.now(timezone('Europe/Zagreb')) #log_time()
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
            task_obj.write(cr, uid, t[0], t[1])
        doc_obj=self.pool.get('translation.document')
        for d in doc_list:
            doc_obj.write(cr, uid, d[0], d[1])
        for e in evid_list:
            self.write(cr, uid, e[0], e[1]) 
        return True
    
    
        
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
    
    def _my_task_work_status(self, cr, uid, ids, field_name, field_value, context=None):
        res={}
        emp_id = get_employee_from_uid(self, cr, uid)
        for task in self.browse(cr, uid, ids):
            status = _('No status')
            for trans in task.translate_ids:
                if emp_id == trans.id:
                    status = _('Assigned')
                    status = self.check_my_status(emp_id, status, task.work_ids )
            res[task.id]=status
        return res
    
    def check_my_status(self, emp_id, status, jobs):
        for job in jobs:
            if emp_id == job.employee_id.id:
                if job.work_type == 'lect':
                    if job.job_done: 
                        status =  _('Lectoring finished')
                    elif job.job_stop : 
                        status = _('Lectoring paused')
                    else: 
                        return _('Lectoring')
                elif job.work_type == 'trans':
                    if job.job_done: 
                        status = _('Translating finished')
                    elif job.job_stop : 
                        status = _('Translating paused')
                    else: 
                        status = _("Translating")
        return status
        
    
    def _my_task_competence(self, cr, uid, ids, field_name, field_value, context=None):
        res={}
        emp_id = get_employee_from_uid(self, cr, uid)
        employee=self.pool.get('hr.employee').browse(cr, uid, emp_id)
        for task in self.browse(cr, uid, ids):
            l_from=task.language_origin.id
            l_to=task.language_id.id
            ok_from, ok_to = False, False
            for lang in employee.language_ids:
                if l_from == lang.id: ok_from = True
                if l_to == lang.id: ok_to = True
            if ok_from and ok_to:
                res[task.id] = True
            else : res[task.id] = False
        return res
    
    
    def onchange_lang_select_competent(self, cr, uid, ids, language_id, context=None):
        return {'domain':{'translate_ids':[('language_ids','in',language_id)]}}
    
    def _get_task_description(self, cr, uid, ids, field_name, field_value, context=None):
        tasks=self.browse(cr, uid, ids)
        res={}
        for t in tasks:
            res[t.id]=' '.join([t.document_id.name,_('from'),
                               t.language_origin.trans_from,_('to'),
                               t.language_id.trans_to])
        return res
    
    
    
    _columns = {
                'name':fields.char('Name',size=64),
                'description':fields.function(_get_task_description, string="Description", type="char"),
                'document_id':fields.many2one('translation.document','Document'),
                'language_origin':fields.many2one('hr.language','Translate from'),
                'language_id':fields.many2one('hr.language','Translate to', required=True, domain="[('employee_ids','!=',False)]"),
                'type_id':fields.many2one('translation.type','Type'),
                'partner_id':fields.many2one('res.partner','Partner'),
                'lectoring':fields.boolean ('Mandatory lectoring'),
                'state':fields.selection (_document_task_status,'Translation status'),
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
                'user_status':fields.function(_my_task_work_status, string='My status', type="char"),
                'user_competent':fields.function(_my_task_competence, string="Competent", type="boolean")
                }
    
    _defaults = {
                 'state': lambda *a:'draft',
                 'lectoring':True,
                 }

    _order = "id desc"
    
    
    
    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('state') and vals.get('state')=='draft' and vals.get('translate_ids'):
            vals['state'] = 'assig'
        return super(translation_document_task, self).write(cr, uid, ids, vals, context)
    
    def button_pause(self, cr, uid, ids, context=None):
        assert len(ids) == 1
        task_obj = self.browse(cr, uid, ids[0])
        state = task_obj.user_status
        if state not in ('Translating', 'Lectoring'): return False
        emp_id = get_employee_from_uid(self, cr, uid)
        job_id = False
        for job in task_obj.work_ids :
            if job.employee_id.id == emp_id:
                if not job.job_stop:
                    job_id = job.id
        if not job_id : return False
        time = log_time() #datetime.now(timezone('Europe/Zagreb')) #log_time()
        self.pool.get('translation.work').write(cr, uid, job_id,{'job_stop':time})
        return True
        
        
    
    def button_resume(self, cr, uid, ids, context=None):
        assert len(ids) == 1
        task_obj = self.browse(cr, uid, ids[0])
        state = task_obj.user_status
        if state not in ('Translating paused', 'Lectoring paused'): return False
        emp_id = get_employee_from_uid(self, cr, uid)
        time= log_time() #datetime.now(timezone('Europe/Zagreb')) #log_time()
        if state == 'Translating paused':
            self.translation_work_create(cr, uid, ids[0], 'trans', emp_id, time)
            #task_obj.write({'state':'trans'})
        elif state == "Lectoring paused":
            self.translation_work_create(cr, uid, ids[0], 'lect', emp_id, time)
            #task_obj.write({'state':'lect'})
        return True
    
    
    
    def button_lecture_finish(self, cr, uid, ids, context=None):
        time= log_time() #datetime.now(timezone('Europe/Zagreb')) #log_time()
        task = self.browse(cr, uid, ids[0])
        if task.user_status != 'Lectoring':
            return False
        emp_id = get_employee_from_uid(self, cr, uid)
        for job in task.work_ids:
            if (job.work_type == 'lect') and not job.job_stop and (job.employee_id == emp_id):
                self.pool.get('translation.work').write(cr, uid, job_id,{'job_stop':time, 'job_done':True})
        
        
        return True
    
    def button_lecture_start(self, cr, uid, ids, context=None):
        assert len(ids) == 1 # should be run only one task at a time
        task_obj=self.browse(cr, uid, ids[0])
        if not task_obj.user_competent:
            raise osv.except_osv(_('Error!'), _('You are not competent on this task!'))
        ##jel gotov prevod?
        if not (task_obj.state in ('lect_w','lect')):
            return False
        time= log_time() #datetime.now(timezone('Europe/Zagreb')) #log_time()
        emp_id = get_employee_from_uid(self, cr, uid)
        if len(self.browse(cr, uid, ids[0]).lecture_ids) == 0:
            self.write(cr, uid, ids[0], {'lecture_ids':[(4, emp_id)]})
        else:
            le_list=[emp_id]
            for lec in  task_obj.lecture_ids:
                le_list.append(lec.id)
            self.write(cr, uid, ids[0],{'lecture_ids':[(6,0,le_list)]})
        self.translation_work_create(cr, uid, ids[0], 'lect', emp_id, time)
        self.write(cr, uid, ids[0],{'state':'lect','lect_start':time})
        return True
    
    def button_translate_start(self, cr, uid, ids, context=None):
        assert len(ids) == 1 ,'should be run only one task at a time'
        task_obj = self.browse(cr, uid, ids[0])
        if not task_obj.user_competent:
            raise osv.except_osv(_('Error!'), _('You are not competent on this task!'))
        if not (task_obj.user_status in (_('No status'),_('Assigned'))):
            return False
        emp_id = get_employee_from_uid(self, cr, uid)
        if task_obj.translate_ids == []:
            self.write(cr, uid, ids[0],{'translate_ids':[(4, emp_id)]})
        else:
            if task_obj.user_status == _('No status'):
                tr_list=[emp_id]
                for tr in  task_obj.translate_ids:
                    tr_list.append(tr.id)
                self.write(cr, uid, ids[0],{'translate_ids':[(6,0,tr_list)]})
        time =  log_time() #datetime.now(timezone('Europe/Zagreb')) #log_time()
        self.translation_work_create(cr, uid, ids[0], 'trans', emp_id, time)
        
        if task_obj.document_id.state != 'process':
            doc_id = task_obj.document_id.id
            self.pool.get('translation.document').write( cr, uid, doc_id, {'state':'process'})
        if task_obj.document_id.evidention_id.state != 'process':
            evid_id = task_obj.document_id.evidention_id.id
            self.pool.get('translation.evidention').write(cr, uid, evid_id, {'state':'process'})
        my_vals = {}
        if task_obj.state in ('draft','assign'):
            my_vals['state']='trans'
        if not task_obj.trans_start:
            my_vals['trans_start'] = time
        if my_vals != {}:
            self.write(cr,uid,ids[0],{'state':'trans','trans_start':time })
        return True
    
    def translation_work_create(self, cr, uid, task, type, employee, start, context=None):
        work_vals = {
                'task_id':task,
                'work_type': type,
                'employee_id': employee,
                'job_start' : start,
                }
        return self.pool.get('translation.work').create(cr, uid, work_vals)
    

def time_diff_formatter(self, timedelta):
    res =""
    if timedelta.days > 0 :
        res = "%s days" % (timedelta.days)
    sec = timedelta.seconds
    hours, remain =divmod(sec, 3600)
    mins, secs = divmod(remain, 60)
    res += " %s:%s:%s" % (hours, mins, secs)
    return res

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

def get_employee_from_uid(self, cr,  uid, context=None):
    return self.pool.get('hr.employee').search(cr, uid, [('resource_id.user_id','=', uid)] )[0]



"""    
def get_trans_group_ids(self, cr, uid, context=None):
    group_obj=self.pool.get('res.groups')
    translator_ids=group_obj.search(cr, uid, [('name','=','Translator')])
    office_ids=group_obj.search(cr, uid, [('name','=','Translator Office')])
    manager_ids=group_obj.search(cr, uid, [('name','=','Translation Manager')])
    return translator_ids, office_ids, manager_ids
    
def get_user_groups(self, cr, uid, context=None ):
    user=self.pool.get('res.users').browse(cr, uid, uid)
    user_group = []
    for grp in user.groups_id:
        user_group.append(grp.id)
    return user_group   
"""



def check_document_finish(self, cr, uid, doc_id, context=None):
    document = self.pool.get('translation.document').browse(cr, uid, doc_id)
    finished = True
    for task in document.task_ids:
        if task.state != 'finish':
            finished = False
    return finished

def check_evidention_finish(self, cr, uid, evid_id, context=None):
    evidention = self.pool.get('translation.evidention').browse(cr, uid, evid_id)
    finished = True
    for doc in evidention.document_ids:
        if doc.state != 'finish':
            finished = False
            
    return finished
    
