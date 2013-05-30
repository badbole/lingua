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
    
    def action_evidention_recive(self, cr, uid, ids, context=None):
        self.check_before_recive(cr, uid, ids)
        evid_list, doc_list, task_list = [], [], []
        for evidention in self.browse(cr, uid, ids):
            evid_={}
            evid_['id'] = evidention.id
            if not evidention.date_recived: 
                evid_['date_recived'] = zagreb_now()
            evid_['sequence'] = self.pool.get('ir.sequence').get(cr, uid, 'translation_evidention')
            for doc in evidention.document_ids:
                doc_={}
                doc_['sequence'] = '-'.join([evid_['sequence'],str(len(doc_)+1)])
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
    _columns = {
                'name':fields.char('Document', size=256, required="1", search="1",
                                   help="Some descriptive name for document, like: TV Manual, High school diploma..."),
                'sequence':fields.char('Sequence', size=128),
                'evidention_id':fields.many2one('translation.evidention','Evidention'),
                'language_id':fields.many2one('hr.language','Origin language', required=1 ),
                'type_id':fields.many2one('translation.type', 'Type'),
                'cards_estm':fields.float('Text cards', help="Estimated number of cards for translating"),
                'date_due':fields.datetime('Deadline'),
                'task_ids':fields.one2many('translation.document.task','document_id','Translate to'),
                'state':fields.selection(_document_status, 'Document status'),
                'partner_id':fields.many2one('res.partner','Partner'),
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
    
    
    
    _columns = {
                'name':fields.char('Name',size=64),
                'document_id':fields.many2one('translation.document','Document'),
                'language_origin':fields.many2one('hr.language','Translate from'),
                'language_id':fields.many2one('hr.language','Translate to', required=True),
                'translate_ids':fields.many2many('hr.employee',
                                                 'translate_task_employee_rel',
                                                 'translation_document_task_translate_ids',
                                                 'hr_employee_translate_taks_ids', 
                                                 'Translator'),
                'type_id':fields.many2one('translation.type','Type'),
                'partner_id':fields.many2one('res.partner','Partner'),
                'lectoring':fields.boolean ('Mandatory lectoring'),
                'state':fields.selection (_document_task_status,'Translation status'),
                'note':fields.text('Note'),
                'trans_start':fields.datetime('Date/time start'),
                'trans_finish':fields.datetime('Date/time finish'),
                'lect_start':fields.datetime('Date/time start'),
                'lect_finish':fields.datetime('Date/time finish'),
                }
    
    _defaults = {
                 'state':"draft",
                 }

    _order = "id desc"
    
    def button_pause(self, cr, uid, ids, context=None):
        state=self.browse(cr, uid, ids[0]).state
        if state == 'trans':
            self.write(cr,uid,ids[0],{'state':'trans_p'})
        elif state == "lect":
            self.write(cr,uid,ids[0],{'state':'lect_p'})
        return True
    
    def button_resume(self, cr, uid, ids, context=None):
        state=self.browse(cr, uid, ids[0]).state
        if state == 'trans_p':
            self.write(cr,uid,ids[0],{'state':'trans'})
        elif state == "lect_p":
            self.write(cr,uid,ids[0],{'state':'lect'})
        return True
    
    def button_translate_start(self, cr, uid, ids, context=None):
        time=zagreb_now()
        #self.button_translate_start_send_note(self, cr, uid, ids, context=context)
        self.write(cr,uid,ids[0],{'state':'trans','date_start':time})
        return True
    
    def button_translate_start_send_note(self, cr, uid, ids, context=None):
        #if context == None : context={}
        self.message_post(cr, uid, ids, _('Translation started'), _("test"), context=context)
        return True
        
    
    def button_translate_finish(self, cr, uid, ids, lecture, context=None):
        time=zagreb_now()
        if lecture : 
            self.write(cr,uid,ids[0],{'state':'lect_w','date_start':time})
        else:
            self.write(cr,uid,ids[0],{'state':'finish','date_start':time})
        return True
    
    def button_lecture_start(self, cr, uid, ids, context=None):
        time=zagreb_now()
        self.write(cr,uid,ids[0],{'state':'lect','lect_start':time})
        return True
    
    def button_task_finish(self, cr, uid, ids, context=None):
        
        time=zagreb_now()   
        #TODO zapisati statistiku...
        self.write(cr,uid,ids[0],{'state':'finish','date_finish':time})
        return True

def zagreb_now():
    return datetime.now(timezone('Europe/Zagreb'))


