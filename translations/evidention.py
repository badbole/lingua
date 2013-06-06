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
from datetime import datetime, date
from pytz import timezone
import tools
import logging
_logger = logging.getLogger(__name__)
import openerp.addons.decimal_precision as dp


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
                   ,('finish','Finished')
                   ,('cancel','Canceled')
                   ]
    
    def _get_total_evid_cards(self, cr, uid, ids, field_name, field_value, context=None):
        res={}
        total = 0
        for id in self.browse(cr, uid, ids):
            total=0
            for doc in id.document_ids :
                total += doc.cards_estm
            res[id.id] = total
        return res
    
    _columns = {
        'name': fields.char('Name', size=128 , select=1),
        'sequence':fields.char('Number', size=64, select=1),
        'partner_id':fields.many2one('res.partner','Partner', required=1),
        'date_recived':fields.datetime('Recived', help="Date and time of recieving, leave empty for current date/time"),
        'date_due':fields.datetime('Deadline'),
        'note':fields.text('Note'),
        'state':fields.selection (_translation_status,'Evidention status'),
        'document_ids':fields.one2many('translation.document','evidention_id','Documents', required=1),
        'total_cards':fields.function(_get_total_evid_cards, string='Total cards', type="float")
                }

    _defaults = {
                 'sequence':'Draft Evidention',
                 'name':'Translation ',
                 'state':"draft",
                 }
    
    _order = "id desc"
    
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
    
    def action_evidention_add_document(self, cr, uid, ids, context=None):
        #dodaje zaboravljeni dokument
        #u već zaprimljenu evidenciju
        return True
    
    def action_evidention_recive(self, cr, uid, ids, context=None):
        self.check_before_recive(cr, uid, ids)
        evid_list, doc_list, task_list = [], [], []
        for evidention in self.browse(cr, uid, ids):
            evid_={}
            evid_['id'] = evidention.id
            if not evidention.date_recived: 
                evid_['date_recived'] = zagreb_now()
            evid_['sequence'] = self.pool.get('ir.sequence').get(cr, uid, 'translation_evidention')
            evid_['state'] = 'open'
            for doc in evidention.document_ids:
                doc_={}
                doc_['sequence'] = '-'.join([evid_['sequence'],str(len(doc_list)+1)])
                doc_['partner_id'] = evidention.partner_id.id
                for task in doc.task_ids:
                    task_={}
                    task_name = '-'.join([doc_['sequence'], 
                                          doc.language_id.iso_code2.upper(), 
                                          task.language_id.iso_code2.upper(),  'T'])
                    if task.lectoring : task_name = ''.join([task_name,'L'])
                    task_['name']=task_name
                    if task.translate_ids : 
                        task_['state'] = 'assign'
                        doc_['state'] = 'open' 
                    task_['partner_id'] = evidention.partner_id.id,
                    task_['language_origin'] = doc.language_id.id
                    task_list.append ([task.id, task_])
                doc_list.append ([doc.id, doc_])
            evid_list.append([evidention.id, evid_])
            self.write_recived_all(cr, uid, task_list, doc_list, evid_list)
        
            
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
    
    def write_recived_task_send_note(self, cr, uid, context=None):
        
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
                'sequence':fields.char('Sequence', size=128),
                'evidention_id':fields.many2one('translation.evidention','Evidention'),
                'language_id':fields.many2one('hr.language','Origin language', required=1, domain="[('competence_ids','!=',False)]"),
                'type_id':fields.many2one('translation.type', 'Type'),
                'cards_estm':fields.float('Text cards', help="Estimated number of cards for translating"),
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
                           ,('trans_p','Translation paused')
                           ,('lect_w','Ready for lectoring')
                           ,('lect','Lectoring in progress')
                           ,('lect_p','Lectoring paused')
                           ,('finish',"Finished")
                           ,('cancel',"Canceled")
                           ]
    
    
        
        #get user rights
    def get_translators_domain(self, cr, uid, ids, context=None):
        res={}
                    
        for id in self.browse(cr, uid, ids):
            competence_obj=self.pool.get('hr.language.competence')
            emp_obj = self.pool.get('hr.employee')
            lang_in = competence_obj.search(cr, uid,[('language_id','=', id.language_origin.id)])
            lang_out= competence_obj.search(cr, uid,[('language_id','=', id.language_id.id)])
            test=competence_obj.search(cr, uid, [('language_id.id','in',[id.language_id.id, id.language_origin.id ])])
            
            emp_in = emp_obj.search(cr, uid,[('competence','like',id.language_id.iso_code2)])
            emp_out = emp_obj.search(cr, uid,[('competence','like',id.language_origin.iso_code2)])
            if test == lang_in.append(lang_out):
                pass 
            #comp_t = competence_obj.read(cr, uid, comp_all, ['language_id', 'employee_id'])
            
            translator_id, office_id, manager_id = get_trans_group_ids(self, cr, uid)
            """
            user_group = get_user_groups(self, cr, uid)
            test= id.translate_ids
            if (manager_id[0] in user_group) :
                pass
            elif (office_id[0] in user_group):
                pass
            elif (translator_id[0] in user_group):
                pass
            """
        return res
    
    def _get_possible_translators(self, cr, uid, ids, context=None): # for task assign
        res={}
        l_trans, l_from, l_to = [], [], []
        for task in self.browse(cr, uid, ids):
            for user in self.pool.get('hr.employee').browse(cr, uid, ids):
                for uc in user.competence_ids:
                    if (uc.language_id == task.language_id):
                        l_from.append(user.id)
        
        
        return res
    
    
    _columns = {
                'name':fields.char('Name',size=64),
                'document_id':fields.many2one('translation.document','Document'),
                'language_origin':fields.many2one('hr.language','Translate from'),
                'language_id':fields.many2one('hr.language','Translate to', required=True),
                'type_id':fields.many2one('translation.type','Type'),
                'partner_id':fields.many2one('res.partner','Partner'),
                'lectoring':fields.boolean ('Mandatory lectoring'),
                'state':fields.selection (_document_task_status,'Translation status'),
                'note':fields.text('Note'),
                'translate_ids':fields.many2many('hr.employee',
                                                 'translate_task_translate_employee_rel',
                                                 'translation_document_task_translate_ids',
                                                 'hr_employee_translate_task_ids', 
                                                 'Translator', ), #selection='_get_translators'
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
                'work_ids':fields.one2many('translation.work','task_id','Work log')
                }
    
    _defaults = {
                 'state':"draft",
                 'lectoring':True,
                 'trans_cards':1,
                 'lect_cards':1,
                 }

    _order = "id desc"
    
    def button_pause(self, cr, uid, ids, context=None):
        state=self.browse(cr, uid, ids[0]).state
        work_ids = self.browse(cr, uid, ids[0]).work_ids
        time = zagreb_now()
        emp_id = get_employee_from_uid(self, cr, uid)
        work_id = translation_work_select(self, cr, uid, ids, work_ids)
        self.pool.get('translation.work').write(cr, uid, work_id,{'job_stop':time})
        if state == 'trans':
            self.write(cr,uid,ids[0],{'state':'trans_p'})
        elif state == "lect":
            self.write(cr,uid,ids[0],{'state':'lect_p'})
        return True
    
    def button_resume(self, cr, uid, ids, context=None):
        state=self.browse(cr, uid, ids[0]).state
        emp_id = get_employee_from_uid(self, cr, uid)
        time= zagreb_now()
        
        if state == 'trans_p':
            translation_work_create(self, cr, uid, ids[0], 'trans', emp_id, time)
            self.write(cr,uid,ids[0],{'state':'trans'})
        elif state == "lect_p":
            translation_work_create(self, cr, uid, ids[0], 'lect', emp_id, time)
            self.write(cr,uid,ids[0],{'state':'lect'})
        return True
    
    
    
    def button_task_finish(self, cr, uid, ids, lecture, context=None):
        time=zagreb_now()
        work_id = translation_work_select(self, cr, uid, ids)
        task_obj = self.browse(cr, uid, ids[0])
        if task_obj.state == 'trans':
            #broj kartica i file!
            if lecture : 
                work_id =translation_work_select(self, cr, uid, ids)
                self.pool.get('translation.work').write(cr, uid, work_id[0],{'job_stop':time})
                self.write(cr,uid,ids[0],{'state':'lect_w','trans_finish':time})
            else:
                
                self.write(cr,uid,ids[0],{'state':'finish','trans_stop':time})
        elif task_obj.state == 'lect':
            work_id =translation_work_select(self, cr, uid, ids)
            self.pool.get('translation.work').write(cr, uid, work_id[0],{'job_stop':time})
            self.write(cr,uid,ids[0],{'state':'finish','lect_stop':time})
        if check_document_finish(self, cr, uid, task_obj.document_id.id):
            self.pool.get('translation.document').write(cr, uid, task_obj.document_id.id, {'state':'finish'})
            if check_evidention_finish(self, cr, uid, task_obj.document_id.evidention_id.id):
                self.pool.get('translation.evidention').write(cr, uid, task_obj.document_id.evidention_id.id, {'state':'finish'} )
            pass
        return True
    
    
    
    def button_lecture_start(self, cr, uid, ids, context=None):
        time=zagreb_now()
        emp_id = get_employee_from_uid(self, cr, uid)
        if len(self.browse(cr, uid, ids[0]).lecture_ids) == 0:
            self.write(cr, uid, ids[0], {'lecture_ids':[(4, emp_id)]})
            pass
        else:
                #provjeri jel na popisu, ak nije dodaj ga
            pass
        translation_work_create(self, cr, uid, ids[0], 'lect', emp_id, time)
        self.write(cr,uid,ids[0],{'state':'lect','lect_start':time})
        return True
    
    
    
    def button_translate_start_send_note(self, cr, uid, ids, context=None):
        message = _("Translation started")
        self.message_post(cr, uid, ids[0], body=message, context=context)
        return True
    
    def button_translate_start(self, cr, uid, ids, context=None):
        emp_id = get_employee_from_uid(self, cr, uid)
        if check_user_employee_competence(self, cr, uid, ids):
            if len(self.browse(cr, uid, ids[0]).translate_ids) == 0:
                self.write(cr, uid, ids[0],{'translate_ids':[(4, emp_id)]})
            else:
                #provjeri jel na popisu, ak nije dodaj ga
                pass
        else:
            raise osv.except_osv(_('Error!'), _('You cannot start this translation, one of languages needed for this translation is missing in your competence!'))
        time = zagreb_now()
        #self.button_translate_start_send_note(self, cr, uid, ids, context=context)
        translation_work_create(self, cr, uid, ids[0], 'trans', emp_id, time)
        task_obj = self.browse(cr, uid, ids[0])
        doc_id = task_obj.document_id.id
        evid_id = task_obj.document_id.evidention_id.id
        self.pool.get('translation.document').write( cr, uid, doc_id, {'state':'process'})
        self.pool.get('translation.evidention').write(cr, uid, evid_id, {'state':'process'})
        self.write(cr,uid,ids[0],{'state':'trans','trans_start':time })
        return True

def translation_work_select(self, cr, uid, ids, context=None):
    emp_id = get_employee_from_uid(self, cr, uid)
    work_id = self.pool.get('translation.work').search(cr, uid, [('task_id','=',ids[0]),('employee_id','=',emp_id),('job_stop','=',False)])
    return work_id

def translation_work_create(self, cr, uid, task, type, employee, start, context=None):
    work_vals = {
                'task_id':task,
                'work_type': type,
                'employee_id': employee,
                'job_start' : start,
                }
    return self.pool.get('translation.work').create(cr, uid, work_vals)
    
class translation_work(osv.Model):
    _name = 'translation.work'
    _description = 'Work of translators'
    
    _get_work_type=[('trans','Translating'),
                    ('lect','Lectoring'),
                    ('other','Other')]
    
    def _get_time_spent(self, cr, uid, ids, field_name, field_values, context=None):
        res = {}
        
        for job in self.pool.get('translation.work').browse(cr, uid, ids):
            delta=job.job_stop.strptime() - job.job_start.strptime()
            res[job.id]=[job.id, delta]
        return res
    
    _columns = {
                'name':fields.char('Name',size=128),
                'task_id':fields.many2one('translation.document.task','Translation task'),
                'work_type':fields.selection(_get_work_type,'Type of work'),
                'employee_id':fields.many2one('hr.employee','Employee'),
                'job_start':fields.datetime('Start'),
                'job_stop':fields.datetime('Stop'),
                'cards_done':fields.float('Cards done',help="Enter value for this session or leave blank"),
                'cards_total':fields.float('Total done'),
                #'time_spent':fields.function(_get_time_spent,'Time on job')
                } 
    
    _order = "id desc"

def get_employee_from_uid(self, cr, uid, context=None):
    return self.pool.get('hr.employee').search(cr, uid, [('resource_id.user_id','=', uid)] )[0]

def check_user_employee_competence(self, cr, uid, ids, context=None):
    employee_id = get_employee_from_uid(self, cr, uid)
    employee=self.pool.get('hr.employee').browse(cr, uid, employee_id)
    if employee.language_ids == []:
        raise osv.except_osv(_('Error!'), _('This user has no language competences entered, please update user data!'))
    l_from = self.browse(cr, uid, ids[0]).language_origin.id
    l_to = self.browse(cr, uid, ids[0]).language_id.id
    ok_from, ok_to = False, False
    for lang in employee.language_ids:
        if l_from == lang.id:
            ok_from = True
        if l_to == lang.id:
            ok_to = True
    if ok_from and ok_to:
        return True
    else:
        return False

def zagreb_now():
    return datetime.now(timezone('Europe/Zagreb'))

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
    
