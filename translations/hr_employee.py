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

class hr_employee(osv.Model):
    _inherit = 'hr.employee'
    
    
    
    """
    def _get_employee_cards(self, cr, uid, ids, field_name, field_value, context=None):
        work_obj = self.pool.get('translation.work')
        cc = ct = cl = 0
        for emp in self.browse(cr, uid, ids):
            for l_work in emp.translate_task_ids:
                
        return True
    """
    _columns = {
                'translate_task_ids':fields.many2many('translation.document.task',
                                                      'translate_task_translate_employee_rel',
                                                      'hr_employee_translate_task_ids', 
                                                      'translation_document_task_translate_ids',
                                                      'Translated'),
                'lecture_task_ids':fields.many2many('translation.document.task',
                                                    'translate_task_lecture_employee_rel',
                                                    'hr_employee_lecture_task_ids', 
                                                    'translation_document_task_lecture_ids',
                                                    'Lectured' ),
                #'cards_current':fields.function(_get_employee_cards, type=float, string="Cards total", multi="cards"),
                #'cards_trans':fields.function(_get_employee_cards, type=float, string="Cards translating", multi="cards"),
                #'cards_lect':fields.function(_get_employee_cards, type=float, string="Cards lectoring", multi="cards"),
                }
                