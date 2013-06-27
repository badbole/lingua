# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Module: mikra_co
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

class product_template(osv.Model):
    _inherit = "product.template"
    
    def _izracunaj(self, cr, uid, ids, field_name, field_values, context=None):
        res={}
        for prod in self.browse(cr, uid, ids):
            if prod.nabavna_eur:
                res[prod.id] = {'nabavna_75': prod.nabavna_eur * 7.5,
                                'nabavna_80': prod.nabavna_eur * 8}
        return res
    
    def digitron (self, cr, uid, ids, p_base=None, fak1=None, fak2=None, context=None):
        if isinstance(ids, int): ids = [ids]
        res={}
        for p in self.pool.get('product.template').browse(cr, uid, ids):
            
            if p_base :
                base = p_base
            else :
                base = p.p_base and p.p_base or False
            base_p = ( base=='n75' and p.nabavna_75 or
                       base=='n80' and p.nabavna_80 or
                       base=='hrk' and p.nabavna_kn or False  )
            f1 = fak1 or p.fak1 
            f2 = fak2 or p.fak2
            if f1!=0 and f2!=0 and base_p:
                res[p.id]={'prodajna':base_p*f1*f2}
                
        return res
    
    
            
    _columns = {
                'nabavna_kn':fields.float('Nabavna KN',help="nabavna cijena u kunama"),
                'nabavna_eur':fields.float('Nabavna EUR',help="nabavna cijena u eurima"),
                'nabavna_75':fields.function(_izracunaj, string='Nabavna 7.5', type="float", multi="tecaj",help="nabavna cijena (eur) po tečaju 7,5", store = True),
                'nabavna_80':fields.function(_izracunaj, string='Nabavna 8.0', type="float", multi="tecaj", help="nabavna cijena (eur) po tečaju 8.0", store = True),
                'fak1':fields.float('Faktor1'),
                'fak2':fields.float('Faktor2'),
                'p_base':fields.selection([('n75','Nabavna  7.5'),('n80','Nabavna 8.0'),('hrk','Nabavna tecaj')],'Osnovica',help="Odabir osnove za izračun javne cijene"),
                'prodajna':fields.float('Prodajna', help="Pregled prodajne cijene prije uvrštenja")
                }
    
    _defaults = {
                 'fak1':1,
                 'fak2':1,
                 'p_base':'n75',
                 }
    
class product_product(osv.Model):
    _inherit = 'product.product'
    
    def onchange_digitron(self, cr, uid, ids, p_base, fak1, fak2):
        prod = self.browse(cr, uid, ids[0]).product_tmpl_id.id
        t = self.pool.get('product.template')
        return {'value':t.digitron(cr, uid, prod, p_base, fak1, fak2)[ids[0]]}
    
    def primjeni_na_kategoriju(self, cr, uid, ids, context=None):
        prod=self.browse(cr, uid, ids[0])
        template = prod.product_tmpl_id
        tcat = template.categ_id.id
        selected = self. pool.get('product.template').search(cr, uid, [('categ_id','=',tcat)])

        values=self.pool.get('product.template').digitron(cr, uid, selected, template.p_base, template.fak1, template.fak2)
        t=self.pool.get('product.template')
        for val in values:
            t.write(cr, uid, val, {'list_price' : values[val]['prodajna']})
            
        return True
                

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: