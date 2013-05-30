# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Module: translations_sale
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
    _inherit = 'hr.language.competence'
    
        
    _columns = {
                'translate':fields.boolean('Translate'),
                'lecture':fields.boolean('Lecture'),
                'synchro_trans':fields.boolean('Synchro trans'),
                'note':fields.text('Note'),
                #'translate_line_ids':fields.many2many('translation.evidention.line',
                #                                 'translate_evidention_line_employee_rel', 
                #                                 'hr_language_competence_translate_line_ids',
                #                                 'translation_evidention_line_translate_ids', 
                #                                 'Translated work' )
                }   