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

from osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import psycopg2


class translation_price(osv.osv):
    _name="translation.price"
    _description = "Prices forming"
    
    def digitron(self, cr, uid, ids, origin, parent, discount, price, context=None):
        if not parent : return True 
        if context is None : context={}
        base=self.pool.get('translation.price').browse(cr, uid, parent).price
        res={}
        
        if origin =='price':
            if round((base*(100-discount)/100),2) == price:
                return True
            else :
                res['discount'] = 100-(price*100/base)
        elif origin == 'discount':
            if price == 0: price = base
            if round(100-(price*100/base),2) == discount:
                return True
            else : 
                res['price'] = base*(100-discount)/100
        return {'value':res}
    

        
    
    _columns = {
                'name':fields.char('Price name', size=64),
                'parent_id':fields.many2one('translation.price','Price base', 'Base price used for calculating actual price'),
                'child_ids':fields.one2many('translation.price','parent_id', string="Child product price"),
                'price':fields.float('Price', digits_compute=dp.get_precision('Product Price'), help="Price for translation"),
                'discount_name':fields.char('Discount description', size=128),
                'discount':fields.float('Discount %' ,digits_compute=dp.get_precision('Product Price'), help="Percentage as number (20)% (not decimal 0,2)!"),
                #'parent_left': fields.integer('Left Parent', select=1),
                #'parent_right': fields.integer('Right Parent', select=1),
                }
    




def get_default_price(self, cr, uid, context=None):
    return self.pool.get('translation.price').search(cr, uid, [])[0]



class translation_evidention(osv.Model):
    _inherit = 'translation.evidention'
    
    def get_uos(self, cr, uid):
        return self.pool.get('product.uom').search(cr, uid, [('name', '=', 'card')] )[0]
    
    def select_price(self, cr, uid, price1, price2, price3):
            if price3 : price=price3
            elif price2 : price= price2
            elif price1 : price=price1
            else: price = self.pool.get('translation.price').search(cr, uid, [])[0]
            ammount = self.pool.get('translation.price').browse(cr, uid, price).price
            return price, ammount
    
    _get_product_type = [(1,'Task=Product (translate and lectoring)'),
                         (2,'(Task=Product Translate, Product Lectoring)'),
                         (3,'Document=Product (aaa trans to bbb,ccc) (T+L)'),
                         (4,'(Document=Product Translate, Product Lector)'),
                         (5,'(Single product, all tasks in description)')]
    _columns = {
                'marketing_id':fields.many2one('translation.marketing','Marketing'),
                'price_id':fields.many2one('translation.price','Price template'),
                'product_id':fields.one2many('translation.product','evidention_id','Translations'),
                'product_type':fields.selection(_get_product_type, 'Product type', help="Rules for generating and invoicing translation", required=1),
                'avans':fields.float('Advace ammount',digits_compute=dp.get_precision('Product Price')),
                'so_ids':fields.many2many('sale.order','translation_evidention_so_rel','translation_evidention_id','sale_order_id','Sale orders')
              
                }
    
    _defaults = {
                 'product_type' :1,
                 }
    def action_avans_invoice(self, cr, uid, id, context=None):
        
        evid_obj = self.browse(cr, uid, id )
        if evid_obj.avans == 0 : return False
        #TODO
        
        return True
    
    def load_trans_product_list(self, cr, uid, product_id, context=None):
        res =[]
        prod = {}
        total = 0
        for pr in product_id:
            prod['id'] = pr.id
            prod['product_type'] = pr.product_type
            prod['product_id'] = pr.product_id.id
            prod['name'] = pr.name
            prod['description'] = pr.description
            prod['price'] = pr.price_id.price
            prod['units'] = pr.units
            prod['discount'] = pr.discount
            prod['price_amount'] = pr.price_amount
            total += pr.price_amount
            res.append(prod)
        return res, total
    
    def trans_product_preview_generate(self, cr, uid, ids, context=None):
        if context == None: context={}
        product_list = []
        for evidention in self.browse(cr, uid, ids):
            prod_={}
            price3 = evidention.price_id.id
            for document in evidention.document_ids: 
                cards = 0.0
                price2 = document.price_id.id
                description2 = "Prijevod %s sa %s na " %(document.name, document.language_id.trans_from)
                desc_lang2 = ""
                for task in document.task_ids:
                    cards += document.cards_estm
                    price1 = task.price_id.id
                    if task.language_id.trans_to:
                        desc_lang2 += ', ' + task.language_id.trans_to
                    if evidention.product_type == 1 :
                        self.prepare_translation_product_type_1(cr, uid, evidention, document, task, product_list)
                if evidention.product_type == 3:
                    pass
        return product_list
    
    def write_new_translation_products(self, cr, uid, prod_list, context=None):
        pr_list=[]
        total = 0
        tr_prod = self.pool.get('translation.product')
        for line in prod_list:
            line['id'] = tr_prod.create(cr, uid, line)
            
            #prod_list.append('id': tr_prod.create(cr, uid, line))
            total += line['price_amount']
            pr_list.append(line)
        return pr_list, total
    
    
    
    def action_sale_order_cards_done(self, cr, uid, ids, context=None):
        assert len(ids)==0, 'This option should only be used on one evidention'
        evidention = self.browse(cr, uid, ids[0])
        
        return True
   
    
    def action_sale_order_generate(self, cr, uid, ids, context=None):
        tr_prod=self.pool.get('translation.product')
        for evidention in self.browse(cr, uid, ids):
            so_list=[]
            for so in evidention.so_ids:
                if so.state not in ('draft','sent'):
                    raise osv.except_osv(_('Error!'), _('No more Quotations, Sale order %s is confirmed!' % (so.name)))
                so_list.append({'so_id':so.id, 'so_total':so.amount_untaxed, 'so_lines':so.order_line})
            trans_prod_list = {}
            #trans_prod_list_new = self.trans_product_preview_generate(cr, uid, ids, context=None)
            if not evidention.product_id:
                trans_prod_list_new = self.trans_product_preview_generate(cr, uid, ids, context=None)
                trans_prod_list, tr_total = self.write_new_translation_products(cr, uid, trans_prod_list_new)
            else: 
                trans_prod_list, tr_total = self.load_trans_product_list(cr, uid, evidention.product_id)
            
            #move to mew function
            so = self.create_sale_order(cr, uid, evidention.partner_id.id, 1 , evidention.ev_sequence)
            for product in trans_prod_list:
                #if so_list == []:
                prod_id= self.create_product_product(cr, uid, product)
                tr_prod.write(cr, uid, product['id'],{'product_id':prod_id})
                product['product_id']=prod_id
                self.create_sale_order_line(cr, uid, so, product)
            self.write(cr, uid, evidention.id,{'so_ids':[(4,so)]})

        return True 

    def get_default_tax(self, cr, uid):
        #ovo bolje"
        return self.pool.get('account.tax').search(cr, uid, [('name', '=', "25% PDV usluge")] )[0]
    
    
    
    def prepare_translation_product_type_1(self, cr, uid, evidention, document, task, product_list, context=None):
        prod_={}
        price, ammount = self.select_price(cr, uid, task.price_id.id, document.price_id.id, evidention.price_id.id)
        prod_['name'] = task.name
        prod_['description'] = 'Prevod %s \nsa %s na %s' % (document.name, document.language_id.trans_from, task.language_id.trans_to)
        prod_['units'] = document.cards_estm
        prod_['price_id'] = price
        prod_['price'] = ammount
        prod_['price_amount']=ammount * document.cards_estm
        prod_['evidention_id'] = evidention.id
        prod_['document_id'] = document.id
        prod_['task_id']= task.id
        prod_['product_type'] = 1
        
        return product_list.append(prod_)
    
    def create_product_template(self, cr, uid, product, context=None):
        uom_id=self.get_uos(cr, uid)
        tax_id=self.get_default_tax(cr, uid)
        prod_template = {
                         'name':product['name'],
                         'description': product['description'],
                         'uom_id':uom_id,
                         'uom_po_id':uom_id,
                    #'category_id': kategorija,
                        'taxes_id':[(4,tax_id)], # pdv 25%!!!
                        'list_price':product['price_amount'],
                        'type':'service'
                        }
        return self.pool.get('product.template').create(cr, uid, prod_template)
    
    def create_product_product(self, cr, uid, product, context=None):
        template= self.create_product_template(cr, uid, product)
        prod_vals = {'product_tmpl_id':template,
                     'name_template':product['name'],
                     #'default_code':product.name,
                     }
        return self.pool.get('product.product').create(cr, uid, prod_vals)
    
    def create_sale_order(self, cr, uid, partner, pricelist, origin):
        values = {
                  'partner_id':partner,
                  'partner_invoice_id':partner,
                  'partner_shipping_id':partner,
                  'pricelist_id':pricelist, 
                  'origin':origin
                  }
        return self.pool.get('sale.order').create(cr, uid, values)
    
    def create_sale_order_line(self, cr, uid, so, product, context=None ):
        uom_id= self.get_uos(cr, uid)
        tax_id= self.get_default_tax(cr, uid)
        values = {'name':product['description'],
                  'order_id':so,
                  'product_id':product['product_id'],
                  'price_unit':product['price'], # ili cijenu koja je izračunata i količine 1!
                  'product_uom':uom_id,
                  'product_uos':uom_id,
                  'tax_id':[(4,tax_id)],
                  'product_uom_qty':product['units'],
                  }
        return self.pool.get('sale.order.line').create(cr, uid, values)


class translation_document(osv.Model):
    _inherit = 'translation.document'
    _columns = {
                'price_id':fields.many2one('translation.price','Price template'),
                'product_id':fields.one2many('translation.product','document_id','Products')
                }
    

class translation_document_task(osv.Model):
    _inherit = 'translation.document.task'
    _columns = {
                'price_id':fields.many2one('translation.price','Price template'),
                'product_id':fields.one2many('translation.product','task_id','Products'),
                
                }

"""
 BOLEEEE KAKOOOO SI GLUUUPPP!!!!!
class sale_order(osv.osv):
    _name= 'sale.order'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns = {
                'trans_evid_ids':fields.many2many('translation.evidention','translation_evidention_so_rel','sale_order_id','translation_evidention_id','Evidentions')
                }
"""
class sale_order(osv.osv):
    _inherit= 'sale.order'
    #_inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns = {
                'trans_evid_ids':fields.many2many('translation.evidention','translation_evidention_so_rel','sale_order_id','translation_evidention_id','Evidentions')
                }

def calculate_price(self, price, units, discount):
        assert price>0 and units>0
        return price * units * (100.00-discount)/100

class translation_product(osv.Model):
    _name = "translation.product"
    _description = "Translation products - pre sale"
    
    def onchange_product_price(self, cr, uid, ids, price_id, context=None):
        res={}
        price=self.pool.get('translation.price').browse(cr, uid, price_id).price
        prod = self.browse(cr, uid, ids[0])
        res['price_amount'] = calculate_price(self, price, prod.units, prod.discount)
        return {'value':res}
    
    def onchange_discount(self, cr, uid, ids, discount, context=None):
        res={}
        prod=self.browse(cr, uid, ids[0])
        res['price_amount'] = calculate_price(self, prod.price_id.price, prod.units, discount)
        return {'value':res}
    
    def onchange_units(self, cr, uid, ids, units, context=None):
        res={}
        prod=self.browse(cr, uid, ids[0])
        res['price_amount'] = calculate_price(self, prod.price_id.price, units, prod.discount)
        return {'value':res}
    
    
        
    _columns = {
                'name':fields.char('Code', size=128),
                'description':fields.text('Product description'),
                'price_id':fields.many2one('translation.price','Price'),
                'price_amount':fields.float('Amount' ),# dodati float na dvije decimale!
                'units':fields.float('Units'),
                'discount':fields.float('Discount'),
                'evidention_id':fields.many2one('translation.evidention','Evidention'),
                'document_id':fields.many2one('translation.document','Document'),
                'task_id':fields.many2one('translation.document.task','Task'),
                'product_type':fields.integer('Product type'),
                'product_id':fields.many2one('product.product','Product'),
                'partner_id':fields.many2one('res.partner','Partner'),
                }

