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

from openerp.osv import fields, osv




class hr_employee(osv.osv):
    _inherit = "hr.employee"
    
    def _competence_name(self, cr, uid, ids, field_name, field_value, context=None):
        
        competence_obj = self.pool.get('hr.language.competence')
        records = self.browse(cr,uid, ids)
        res={}
        for r in records:
            temp_name = ''
            competence_ids=competence_obj.search(cr, uid,[('employee_id','=',r.id)])
            for id in competence_ids:
                if competence_obj.browse(cr, uid, id).language_id:
                    temp_name='-'.join([temp_name, competence_obj.browse(cr, uid, id).language_id.iso_code2.upper()])
            if r.name != temp_name:
                res[r.id] = temp_name
            
        return res
    
    def onchange_language_ids(self, cr, uid, ids, language_ids, context=None):
  #      res = super(hr_employee, self).onchange_language_ids(cr, uid, ids, language_ids, context=None)
        #return True
        emp_obj = self.browse(cr, uid, ids[0])
        comp_obj = self.pool.get('hr.language.competence')
        values=[]
        if len(emp_obj.competence_ids) == 0 :
            lang_list = language_ids[0][2]
            for l in lang_list:
                vals = {
                        'employee_id':emp_obj.id,
                        'language_id':l,
                        'speak':'5', 'read':'5', 'write':'5'
                        }
                values.append((0,0,vals))
            emp_obj.write( {'competence_ids':values})
            #comp_obj.create(cr, uid, vals)
        else:
            #provjeri pa dodja po potrebi
            pass
        return True    
    
    
    _columns = {
                'primary_lang':fields.many2one('hr.language', 'Primary language'),
                'competence':fields.function(_competence_name, type="char", size=128, method=True, string="Competence"),
                'competence_ids':fields.one2many('hr.language.competence', 'employee_id', 'Language competence'),
                'language_ids':fields.many2many('hr.language','hr_employee_language_rel','hr_employee_language_ids','hr_language_employee_ids','Languages')
                }
    
   
    
    def onchange_primary_lang(self, cr, uid, ids, primary_lang, context=None):
        if context == None: 
            Context={}
            
        langs = self.resolve_2many_commands(cr, uid,'language_ids', language_ids_langs,['language_id','employee_id'])
        return True
        res={}
        if primary_lang: 
            values={
                    'employee_id': ids[0],
                    'language_id': primary_lang,
                    }
            if len(language_competence) == 0:
                res = {'value':{'language_competence':[(0,0,values)]}}
            else :
                #curr_competence=language_competence[2]
                #test = language_competence.append([1,ids[0],values])
                res = {'value':{'language_competence':language_competence.append([0,'False',values])}} 
                #TODO : nadopuniti ne zamijeniti listu!
        return res 
    
    