# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Module: translations
#    Author: Davor Bojkić
#    mail:   bole@dajmi5.com
#    Copyright (C) 2012- Daj Mi 5, 
#                  http://www.dajmi5.com
#    Contributions:  Borko Augustin   @ ABS95.com
#                    Včladinir Jerbić @ ABS95.com
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
    "name" : "Translations evidention",
    "description" : """
Evidention of translations
==========================

Author: Davor Bojkić - bole @ DAJ MI 5     www.dajmi5.com

Contributions: Borko Augustin - borko @ abs95.com
               Vlado Jerbic   - vlado @ abs95.com

Summary: 

- Translation 
    - types (medical, legal, technical, certificates, diplomas...)
    - evidention - documents - translate tasks
    
    - 

""",
    "version" : "1.00",
    "author" : "DAJ MI 5",
    "category" : "",
    "website": "http://www.dajmi5.com",

    'depends': [
                'hr_languages',
                ],
    
    'update_xml': [
                   'security/translations_security.xml',
                   'translations_base_data.xml',
                   'languages_view.xml',
                   'evidention_view.xml',
                   'translation_sequence.xml',
                   
                   'security/ir.model.access.csv',
                   ],
    "active": True,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: