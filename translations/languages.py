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

from openerp.osv import fields, osv

class hr_language (osv.Model):
    _inherit = 'hr.language'
    _description = 'Languages for translation'
    
    _columns = {
                'trans_from':fields.char('Translate from', size=64),
                'trans_to':fields.char('Translate to', size=64),
                }
    
class hr_language_competence (osv.Model):
    _inherit = 'hr.language.competence'
        
    _columns = {
                'translate':fields.boolean('Translate'),
                'lecture':fields.boolean('Lecture'),
                'synchro_trans':fields.boolean('Synchro trans'),
                'note':fields.text('Note'),
                }   
    
