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
    "name" : "Translations sale",
    "description" : """
Evidention of translations
==========================

Author: Davor Bojkić - bole @ DAJ MI 5     www.dajmi5.com

Contributions: Borko Augustin - borko @ abs95.com
               Vlado Jerbic   - vlado @ abs95.com

Summary: 

- Translation 
    - prices (-25% simplicity, -50% - likness, +40% PRIORITY)
    - make product from - evidention, document, document task
    
       
    - 

""",
    "version" : "1.00",
    "author" : "DAJ MI 5",
    "category" : "",
    "website": "http://www.dajmi5.com",

    'depends': [
                'translations',
                'sale',
                ],
    
    'update_xml': [
                   'config_data.xml',
                   'marketing_view.xml',
                   #'product_view.xml',
                   'translations_sale_view.xml',
                   'security/ir.model.access.csv',
                   ],
    "active": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
