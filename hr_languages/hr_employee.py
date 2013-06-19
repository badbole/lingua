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

from osv import fields, osv




class hr_employee(osv.osv):
    _inherit = "hr.employee"
    """ not needed at this point
    def onchange_language_ids(self, cr, uid, ids, language_ids, competence_ids, context=None):
        res={}
        values=[]
        lang_list = language_ids[0][2]
        for l in lang_list:
            vals = {
                    'employee_id':ids[0],
                    'language_id':l,
                    'speak':'5', 'read':'5', 'write':'5'
                    }
            values.append(vals)
        #TODO WRITE RIGHT VALS!    
        #languages=self.resolve_2many_commands(cr, uid, 'language_ids', ['employee_id', 'language_id','speak', 'read', 'write'])
        
        res['competence_ids'] = [(6,0,values)]
        return res  
    """
    
    _columns = {
                'competence_ids':fields.one2many('hr.language.competence', 'employee_id', 'Language competence'),
                'language_ids':fields.many2many('hr.language','hr_employee_language_rel','hr_employee_language_ids','hr_language_employee_ids','Languages')
                }
    
   
    
    