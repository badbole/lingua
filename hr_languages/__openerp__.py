# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Module: hr_language
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

{
    "name" : "HR - languages",
    "description" : """
Evidention of languages
==========================

Author: Davor Bojkić - bole @ DAJ MI 5     www.dajmi5.com

Contributions: 
Summary: 

This module adds spoken languages data to employee
Can be used as base for other language related addons, 
or for selecting and reporting on laguage related data 
of your employees    - 

""",
    "version" : "1.00",
    "author" : "DAJ MI 5",
    "category" : "Human Resources",
    "website": "http://www.dajmi5.com",

    'depends': [
                'hr',
                ],
    
    'update_xml': [
                   'hr_employee_view.xml',
                   'language_view.xml',
                   'hr_language_data.xml',
                   'security/ir.model.access.csv',
                   ],
    "active": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
