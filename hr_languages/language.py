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




class hr_language_competence (osv.Model):
    _name = 'hr.language.competence'
    _description = 'Employee competence by language'
    
    _grades = [('5','5 - Excelent'),
               ('4','4 - Good'),
               ('3','3 - Average'),
               ('2','2 - Poor'),
               ('1','1 - Bad')
               ]
    
    def _get_lang_avg(self, cr, uid, ids, field_name, field_value, context = None):
        if context == None : Context={}
        records = self.browse(cr, uid, ids)
        res={}
        for r in records:
            res[r.id] = (float(r.speak) + float(r.read) + float(r.write))/3 
        return res
    
    _columns = {
                'name':fields.char('Employee competence', size=128),
                'employee_id':fields.many2one('hr.employee','Employee'),
                'language_id':fields.many2one('hr.language','Language'),
                'speak':fields.selection(_grades,'Speak'),
                'read':fields.selection(_grades,'Read'),
                'write':fields.selection(_grades,'Write'),
                'lang_avg':fields.function(_get_lang_avg, type='float', obj='hr.language.competence', method=True , store=True, string="Average" )
                }


class hr_language (osv.Model):
    _name = 'hr.language'
    _description = 'Employee language competence'
    
    _columns = {
                'name':fields.char('Language name', size=64),
                'iso_code1':fields.char('ISO1', size=3),
                'iso_code2':fields.char('ISO2', size=3),
                'iso_code3':fields.char('ISO3', size=2),
                'competence_ids':fields.one2many('hr.language.competence', 'language_id', 'Resources'),
                'employee_ids':fields.many2many('hr.employee','hr_employee_language_rel','hr_language_employee_ids','hr_employee_language_ids','Employees')
                }
    
    
        