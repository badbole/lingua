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
from openerp.tools.translate import _

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
                }
    




def get_default_price(self, cr, uid, context=None):
    return self.pool.get('translation.price').search(cr, uid, [])[0]

class translation_evidention(osv.Model):
    _inherit = 'translation.evidention'
    
    _get_product_type = [(1,'Task=Product (translate and lectoring)'),
                         (2,'(Task=Product Translate, Product Lectoring)'),
                         (3,'Document=Product (aaa trans to bbb,ccc) (T+L)'),
                         (4,'(Document=Product Translate, Product Lector)'),
                         (5,'(Single product, all tasks in description)')]
    _columns = {
                'price_id':fields.many2one('translation.price','Price template'),
                'product_id':fields.one2many('translation.product','evidention_id','Translations'),
                'product_type':fields.selection(_get_product_type, 'Product type', help="Rules for generating and invoicing translation", required=1),
                'avans':fields.float('Advace ammount',digits_compute=dp.get_precision('Product Price'))
                #'so_ids':fields.many2many('sale.order','translation_evidention_so_rel','translation_evidention_id','sale_order_id','Sale orders')
                }
    
    _defaults = {
                 'product_type' :1,
                 }

    
    def action_sale_order_generate(self, cr, uid, ids, context=None):
        
        for evidencija in self.browse(cr, uid, ids):
            so = create_sale_order(self, cr, uid, evidencija.partner_id.id, 1 , evidencija.sequence)
            products = []
            for product in evidencija.product_id:
                if not product.product_id:
                    create_product_product(self, cr, uid, product)
                create_sale_order_line(self, cr, uid, so, product)
                pass
            pass
        return True
    
    def action_product_preview_generate(self, cr, uid, ids, context=None):
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
                        prepare_translation_product_type_1(self, cr, uid, evidention, document, task, product_list)
                if evidention.product_type == 3:
                    pass
        
        
        #create all
        prod = self.pool.get('translation.product')
        
        type=product_list[0]['product_type']
        evid=product_list[0]['evidention_id']
        exist = prod.search(cr, uid, [('evidention_id','=',evid),('product_type','=',type)])
        if len(exist) == 0:
            for line in product_list:
                sale = [prod.create(cr, uid, line)]
                
        elif len(exist) > 0:
            # update values, write chatter
            pass
        return True


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
                'product_id':fields.one2many('translation.product','task_id','Products')
                }
"""
class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
                'trans_product_ids':fields.many2many('translation.product','translation_product_so_rel','sale_order_id', 'translation_product_id','Translations'),
                'trans_evidention_ids':fields.many2many('translation.evidention','translation_evidention_so_rel','sale_order_id','translation_evidention_id','Evidentions')
                }
"""
class translation_product(osv.Model):
    _name = "translation.product"
    _description = "Translation products - pre sale"
    
    def onchange_product_price(self, cr, uid, ids, price_id, context=None):
        res={}
        price=self.pool.get('translation.price').browse(cr, uid, price_id).price
        prod = self.browse(cr, uid, ids[0])
        units = prod.units
        discount = prod.discount
        res['price_amount'] = price * units * (100.00-discount)/100
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
                #'so_ids':fields.many2many('sale.order','translation_product_so_rel', 'translation_product_id','sale_order_id','Sale orders'),
                
                }

def get_uos(self, cr, uid):
    return self.pool.get('product.uom').search(cr, uid, [('name', '=', 'card')] )[0]

def get_default_tax(self, cr, uid):
    #ovo bolje"
    return self.pool.get('account.tax').search(cr, uid, [('name', '=', "25% PDV usluge")] )[0]

def select_price(self, cr, uid, price1, price2, price3):
        if price3 : price=price3
        elif price2 : price= price2
        elif price1 : price=price1
        else: price = self.pool.get('translation.price').search(cr, uid, [])[0]
        ammount = self.pool.get('translation.price').browse(cr, uid, price).price
        return price, ammount

def prepare_translation_product_type_1(self, cr, uid, evidention, document, task, product_list, context=None):
    prod_={}
    price, ammount = select_price(self, cr, uid, task.price_id.id, document.price_id.id, evidention.price_id.id)
    prod_['name'] = task.name
    prod_['description'] = 'Prevod %s \nsa %s na %s' % (document.name, document.language_id.trans_from, task.language_id.trans_to)
    prod_['units'] = document.cards_estm
    prod_['price_id'] = price
    prod_['price_amount']=ammount * document.cards_estm
    prod_['evidention_id'] = evidention.id
    prod_['document_id'] = document.id
    prod_['task_id']= task.id
    prod_['product_type'] = 1
    
    return product_list.append(prod_)

def create_product_template(self, cr, uid, product, context=None):
    uom_id=get_uos(self, cr, uid)
    tax_id=get_default_tax(self, cr, uid)
    prod_template = {
                     'name':product.name,
                     'description': product.description,
                     'uom_id':uom_id,
                     'uom_po_id':uom_id,
                #'category_id': kategorija,
                    'taxes_id':[(4,tax_id)], # pdv 25%!!!
                    'list_price':product.price_id.price,
                    'type':'service'
                    }
    return self.pool.get('product.template').create(cr, uid, prod_template)

def create_product_product(self, cr, uid, product, context=None):
    template= create_product_template(self, cr, uid, product)
    prod_vals = {'product_tmpl_id':template,
                 'name_template':product.name,
                 'default_code':product.name,
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
    uom_id= get_uos(self, cr, uid)
    tax_id= get_default_tax(self, cr, uid)
    values = {'name':product.name,
              'order_id':so,
              'product_id':product.product_id.id,
              'price_unit':product.price_amount, # ili cijenu koja je izračunata i količine 1!
              'product_uom':uom_id,
              'product_uos':uom_id,
              'tax_id':[(4,tax_id)],
              'product_uom_qty':product.units,
              }
    return self.pool.get('sale.order.line').create(cr, uid, values)