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
    _name = 'lungua.evidencija'
    _description = 'Evidencija prijevoda'
    
    _columns = {
        'name': fields.char('Naziv evidencije prijevoda', size=128 , select=1),
        'broj_evidencije':fields.char('Broj evidencija',size=32),
        'broj_evidencija_pod': fields.char('Broj Evidencije Podruznica', required="True", size=20),
        'partner_id':fields.many2one('res.partner','partner_id', 'Partner'),
        'user_id':fields.one2many('res.users', 'user_id','Korisnik-prevoditelj'),
        #'lang_origin':fields.one2many('prijevod.jezici','jezici_id'),
        #'lang_trans':fields.one2many('prijevod.jezici','prijevod_jezici_id'),
        'date_recived':fields.datetime('Zaprimljeno', help="datum i vrijeme zaprimanja"),
        'date_due':fields.datetime('Vrijeme podizanja'),
        'state':fields.selection (( ('draft','Zaprimljeno')
                                   ,('active','U procesu')
                                   ,('closed','Prevedeno')
                                   ,('canceled','Otkazano')
                                   )
                                  ,'Status prijevoda'),
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
