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

class lingua_languages (osv.Model):
    _name = 'lingua.languages'
    _description = 'Languages for translation'
    
    _columns = {
                'name':fields.char('Language name', size=64),
                'iso_code1':fields.char('ISO 1', size=3),
                'iso_code2':fields.char('ISO 2', size=3),
                'iso_code3':fields.char('ISO 3', size=2),
                'employee_ids':fields.many2many('hr.employee','hr_employee_lingua_languages_res','hr_employee_id','lingua_languages_id')
                }
    
class hr_employee(osv.osv):
    _inherit = "hr.employee"
    _columns = {
                'languages_ids':fields.many2many('lingua.languages','hr_employee_lingua_languages_res','hr_employee_id','lingua_languages_id')
                }