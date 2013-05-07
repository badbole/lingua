# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Module: l10n_hr_fiskal
#    Author: Davor Bojkić
#    mail:   bole@dajmi5.com
#    Copyright (C) 2012- Daj Mi 5, 
#                  http://www.dajmi5.com
#    Contributions: Hrvoje ThePython - Free Code!
#                   Goran Kliska (AT) Slobodni Programi
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
from datetime import datetime
from pytz import timezone
import tools


def zagreb_now():
    return datetime.now(timezone('Europe/Zagreb'))

class lingua_evidencija(osv.osv):
    _name = 'lingua.evidencija'
    _description = 'Evidention of translations'
    
    _translation_status = [('draft','Draft')
                   ,('open','Open')
                   ,('process','In process')
                   ,('finished','Finished')
                   ,('delivered','Delivered')
                   ,('canceled','Canceled')
                   ]
    
    
    
    _columns = {
        'name': fields.char('Name', size=128 , select=1),
        'seq_no':fields.char('Number', size=64),
        'broj_evidencije':fields.char('Evidention number',size=64),
        'fiskal_prostor_id':fields.many2one('fiskal.prostor',string='Chapter name'),
        'broj_evidencija_pod': fields.char('Chapter evidention number', size=32),
        'partner_id':fields.many2one('res.partner','partner_id', 'Partner'),
        #'employee_id':fields.many2one('hr.employee', 'employee_id','Employee'),
        'lang_origin':fields.many2one('lingua.language','language_id','Origin language'),
        'lang_translate':fields.many2many('lingua.language','lingua_tranlslate_to_res','lingua_languages_id','lingua_evidencija_id'),
        'date_recived':fields.datetime('Recived', help="Date and time of recieving, leave empty for current date/time"),
        'date_due':fields.datetime('Deadline'),
        'note':fields.text('Note'),
        
        'state':fields.selection (_translation_status,'Evidention status'),
        'evidencija_line_ids':fields.one2many('lingua.evidencija.line','evidencija_id','Translations')
                }

    _defaults = {
                 'state':"draft",
                 }
    
    def onchange_lang_origin (self, cr, uid, ids, lang_origin=False, context=None):
        #result = super(lingua_evidencija,self).onchange_lang_origin(cr, uid, ids, lang_origin=lang_origin, context=context)
        if lang_origin:
            if not self.pool.get('hr.employee').search(cr,uid,[('language_ids','=',lang_origin)]):
                raise osv.except_osv(_('Error!'), _('No available translators for this language!.'))
                
            evidention=self.pool.get('lingua.evidencija').browse(cr, uid, ids)[0]
            
            #result = super(lingua_evidencija,self, cr, uid, ids)
            #result['domain']= result.get('domain',{})
            #result['domain'].update({'evidencija_line_ids':[('','=',prostor_id )]})
        return True
    
    def button_recive(self, cr, uid, ids, context=None):
        evidention=self.pool.get('lingua.evidencija').browse(cr, uid, ids)[0]
        evidention_line=self.pool.get('lingua.evidencija.line').search(cr, uid, [('evidencija_id', '=', evidention.id)])
        langs=self.pool.get('lingua.languages')
        
        if not evidention.evidencija_line_ids:
            raise osv.except_osv(_('Error !'), _('No chosen languages for translation!'))
        if not evidention.partner_id:
            raise osv.except_osv(_('Error !'), _('Choose a partner first!'))
        vals={}
        
        seq_no=self.pool.get('ir.sequence').get(cr,uid,'lingua_order')
        if not evidention.date_recived:
            time=zagreb_now()
            self.pool.get('lingua.evidencija').write(cr, uid, evidention.id, {'date_recived':time})
        for line in evidention_line:
            origin = evidention.lang_origin.iso_code2
            trans = self.pool.get('lingua.evidencija.line').browse(cr, uid, line).language_id.iso_code2
            line_name = '-'.join([seq_no, origin, trans]) 
            line_vals={
                       'name':line_name,
                       'partner_id':evidention.partner_id.id
                       }
            self.pool.get('lingua.evidencija.line').write(cr, uid, line, line_vals)
            
        vals={
              'state':'open',
              'seq_no':seq_no
              }
                
        result=self.pool.get('lingua.evidencija').write(cr, uid, evidention.id, vals)
        return True
    
class lingua_evidencija_line (osv.Model):
    _name = 'lingua.evidencija.line'
    _description = 'Signle langugae for translations'
    
    _translation_line_status =[('new',"New")
                               ,('asigned',"Asigned")
                               ,('translation',"Translation in progress")
                               ,('lectoring',"Lectoring in progress")
                               ,('finished',"Finished")
                               ,('paused',"Paused")
                               ,('cancel',"Canceled")
                               ]
    
    
    _columns = {
                'name':fields.char('Name',size=64),
                'evidencija_id':fields.many2one('lingua.evidencija','Evidevtion reference'),
                'language_id':fields.many2one('lingua.language','Translated language', required=True),
                'employee_id':fields.many2one('hr.employee','Translator'),
                'partner_id':fields.many2one('res.partner','partner_id', 'Partner'),
                'lectoring':fields.boolean ('Mandatory lectoring'),
                'state':fields.selection (_translation_line_status,'Translation status'),
                'translated_cards':fields.integer('Cards translated'),  #broj prevedenih kartica .. jel mozda treba gledati na decimalu?
                'translation_start':fields.datetime('Translation start'),
                'translation_finish':fields.datetime('Translation finished'),
                'lectoring_start':fields.datetime('Lectoring start'),
                'lectoring_finish':fields.datetime('Lectoring finished')
                }
    
    _defaults = {
                 'state':"new"
                 }
    
    def onchange_employee_id(self, cr, uid, ids, employee_id):
        evid_line = self.pool.get('lingua.evidencija.line').browse(cr,uid,ids)[0]
        evidention = self.pool.get('lingua.evidencija').browse(cr, uid, evid_line.evidencija_id.id) 
        if evidention.state=='open':
            self.pool.get('lingua.evidencija').write(cr, uid, evidention.id, {'state':'process'})
        
        if evid_line.state=='new':
            res = self.pool.get('lingua.evidencija.line').write(cr, uid, evid_line.id, {'state':'asigned'})
        return True
    
    def button_translation_start(self, cr, uid, ids, context=None):
        evid_line=self.pool.get('lingua.evidencija.line').browse(cr, uid, ids)[0]
        if evid_line.translation_start:
            #već postoji datum? kaj sad
            return True
        else:
            time=zagreb_now()
            values = {'translation_start':time,
                      'state':'translation'
                      }
        return self.pool.get('lingua.evidencija.line').write(cr, uid, evid_line.id, values)
    
    def button_translation_finish(self, cr, uid, ids, context=None):
        evid_line=self.pool.get('lingua.evidencija.line').browse(cr, uid, ids)[0]
        if evid_line.translation_finish:
            #već postoji datum? kaj sad
            return True
        else:
            time=zagreb_now()
            if evid_line.lectoring:
                values = {'translation_finish':time,
                          'state':'lectoring'}
            else:
                self.pool.get('lingua.evidencija').write(cr, uid, evid_line.evidencija_id.id, {'state':'finished'})
                values = {'translation_finish':time,
                          'state':'finished'}
        return self.pool.get('lingua.evidencija.line').write(cr, uid, evid_line.id,values )
    
    def button_translation2product(self, cr, uid, ids, context=None):
        
        raise osv.except_osv(_('TO DO!'), _('This function is not ready yet!'))
        return True
    
"""    
    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        default.update({
            'fiskal_log_ids':False,
            'uredjaj_ids':False,
            'state':False
        })
        return super(fiskal_prostor, self).copy(cr, uid, id, default, context)
"""   
