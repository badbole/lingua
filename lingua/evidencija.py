# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Module: l10n_hr_fiskal
#    Author: Davor Bojkić
#    mail:   bole@dajmi5.com
#    Copyright (C) 2012- Daj Mi 5, 
#                  http://www.dajmi5.com
#    Contributions: Hrvoje ThePython - Free Code!
#                   Goran Kliska (AT) Slobodni Programi
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



    
class lingua_evidencija(osv.Model):
    _name = 'lingua.evidencija'
    _description = 'Evidention of translations'
    
    _columns = {
        'name': fields.char('Name', size=128 , select=1),
        'broj_evidencije':fields.char('Evidention number',size=32),
        'fiskal_prostor_id':fields.many2one('fiskal.prostor',string='Chapter name'),
        'broj_evidencija_pod': fields.char('Chapter evidention number', size=32),
        'partner_id':fields.many2one('res.partner','partner_id', 'Partner'),
        'employee_id':fields.many2one('hr.employee', 'employee_id','Employee'),
        'lang_origin':fields.many2one('lingua.language','language_id','Origin language'),
        'lang_translate':fields.many2many('lingua.language','lingua_tranlslate_to_res','lingua_languages_id','lingua_evidencija_id'),
        'date_recived':fields.datetime('Recived', help="Date and time of recieving"),
        'date_due':fields.datetime('Pickup time'),
        'note':fields.text('Note'),
        'lectoring':fields.boolean ('Mandatory lectoring'),
        'state':fields.selection (( ('draft','Draft')
                                   ,('recived','Recived')
                                   ,('translate','Translating')
                                   ,('lector','Lectoring')
                                   ,('finished','Finished')
                                   ,('delivered','Delivered')
                                   ,('canceled','Canceled')
                                   )
                                  ,'Translation status'),
                }

    _defaults = {
                 'state':"draft"
                 }

    _constraints={}

"""
    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        default.update({
            'fiskal_log_ids':False,
            'uredjaj_ids':False,
            'state':False
        })
        return super(fiskal_prostor, self).copy(cr, uid, id, default, context)
"""   
