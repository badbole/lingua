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

from osv import osv, fields, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import psycopg2
from openerp import netsvc

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
    
    def get_default_price(self, cr, uid, context=None):
        return self.pool.get('translation.price').search(cr, uid, [])[0]
    
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
    
class translation_evidention(osv.Model):
    _inherit = 'translation.evidention'
    
    _get_product_type = [(1,'Task=Product (translate and lectoring)'),
                         (2,'(Task=Product Translate, Product Lectoring)'),
                         (3,'Document=Product (aaa trans to bbb,ccc) (T+L)'),
                         (4,'(Document=Product Translate, Product Lector)'),
                         (5,'(Single product, all tasks in description)')]
    
    def onchange_partner_id(self, cr, uid, ids, partner, context=None):
        if not partner:
            return {'value': {'payment_term': False, 'fiscal_position': False}}
        if ids and ids[0]:
            self.write(cr, uid, ids[0],{})
        part = self.pool.get('res.partner').browse(cr, uid, partner, context=context)
        payment_term = part.property_payment_term and part.property_payment_term.id or False
        fiscal_position = part.property_account_position and part.property_account_position.id or False
        return {'value': {'payment_term': payment_term, 'fiscal_position': fiscal_position}}
    
    _columns = {
                'marketing_id':fields.many2one('translation.marketing','Marketing'),
                'price_id':fields.many2one('translation.price','Price template'),
                'product_id':fields.one2many('translation.product','evidention_id','Translations'),
                'product_type':fields.selection(_get_product_type, 'Product type', help="Rules for generating and invoicing translation", required=1),
                'avans':fields.float('Advace ammount',digits_compute=dp.get_precision('Product Price')),
                'so_ids':fields.many2many('sale.order','translation_evidention_so_rel','translation_evidention_id','sale_order_id','Sale orders'),
                'company_id':fields.many2one('res.company','Company'),
                'fiscal_position':fields.many2one('account.fiscal.position', 'Fiscal position'),
                'payment_term':fields.many2one('account.payment.term', 'Payment term')
                #'orders':fields.one2many('sale.order', 'id', '' )
                }
    
    _defaults = {
                 'price_id': 1,
                 'product_type' :1,
                 'company_id': 1    #TODO MULTICOMPANY...
                 }
    
    
    
    def check_translated_cards(self, cr, uid, ids, context=None):
        for evidention in self.browse(cr, uid, ids):
            for prod in evidention.product_id:
                if prod.units != prod.task_id.trans_cards:
                    prod.write({'units':prod.task_id.trans_cards})
        
        return True
    
    def evidention_quotation_generate(self, cr, uid, ids, context=None):
        for evidention in self.browse(cr, uid, ids):
            so = self.create_sale_order(cr, uid, evidention)
            for product in evidention.product_id:
                self.create_sale_order_line(cr, uid, so, product, evidention.fiscal_position.id)
        return True
    
    def create_sale_order_line(self, cr, uid, so, product, fiscal_position=False, context=None ):
        uom_id = self.pool.get('product.uom').search(cr, uid, [('name', '=', 'card')] )[0]
        taxes=[]
        for tax in product.tax_ids:
            taxes.append(tax.id) 
        values = {'name':product.description,
                  'order_id':so,
                  'product_id':product.product_id.id,
                  'price_unit':product.price, 
                  'product_uom':uom_id,
                  'product_uos':uom_id,
                  'tax_id':taxes and [(6,0,taxes)] or False,
                  'product_uom_qty':product.units,
                  'discount':product.discount,
                  }
        return self.pool.get('sale.order.line').create(cr, uid, values)
    
    def create_sale_order(self, cr, uid, evidention, fis_position=None, payment=None, context=None):
        values = {
                  'partner_id':evidention.partner_id.id,
                  'partner_invoice_id':evidention.partner_id.id,
                  'partner_shipping_id':evidention.partner_id.id,
                  'fiscal_position':evidention.fiscal_position.id,
                  'payment_term':evidention.payment_term.id,
                  'pricelist_id': 1, #pricelist, 
                  'origin':evidention.ev_sequence,
                  'trans_evid_ids':[(6,0,[evidention.id])]
                  }
        return self.pool.get('sale.order').create(cr, uid, values)
    
    def _get_partner_fiscal_position(self, cr, uid, partner, context=None):
        if not partner:
            return {'value': {'partner_invoice_id': False, 'partner_shipping_id': False,  'payment_term': False, 'fiscal_position': False}}
        part = self.pool.get('res.partner').browse(cr, uid, partner, context=context)
        payment_term = part.property_payment_term and part.property_payment_term.id or False
        fiscal_position = part.property_account_position and part.property_account_position.id or False
        fis_pos = part.property_account_position or False
        return fiscal_position, fis_pos, payment_term
    
    def evidention_products_generate(self, cr, uid, ids, context=None):
        for evidention in self.browse(cr, uid, ids):
            if not evidention.product_id:
                new_product_list= self._generate_product_list(cr, uid, ids, evidention)
                self._create_translation_products(cr, uid, new_product_list)
        return True
    
    def _create_translation_products(self, cr, uid, new_product_list, context=None ):
        trans_product = self.pool.get('translation.product')
        for product in new_product_list:
            prod_id = self._create_product_product(cr, uid, product, context=None) #radim pravi proizvod
            tprod_vals={
                        'name':product['name'],
                        'description':product['description'],
                        'price_id':product['price_id'],
                        'price':product['price'],
                        'units':product['units'],
                        'tax_ids':[(6,0, product['tax_ids'])],
                        'evidention_id':product['evidention_id'],
                        'document_id':product['document_id'],
                        'task_id':product['task_id'],
                        'product_type':product['product_type'],
                        'product_id':prod_id,
                        'partner_id':product['partner_id'],
                        }
            trans_product.create(cr, uid, tprod_vals)
        return True
    
    def _create_product_product(self, cr, uid, product, context=None):
        template= self._create_product_template(cr, uid, product)
        prod_vals = {'product_tmpl_id':template,
                     'name_template':product['name'],
                     }#'default_code':product.name,
        return self.pool.get('product.product').create(cr, uid, prod_vals)
    
    def _create_product_template(self, cr, uid, product, context=None):
        uom_id=self.pool.get('product.uom').search(cr, uid, [('name', '=', 'card')] )[0]
        ir_values = self.pool.get('ir.values')
        product['tax_ids'] = ir_values.get_default(cr, uid, 'product.product', 'taxes_id', company_id=1)
        
        assert product['tax_ids'] , 'You need to define default taxes'
        prod_template = {
                         'name':product['name'],
                         'description': product['description'],
                         'uom_id':uom_id,
                         'uom_po_id':uom_id,
                         'tax_ids':[(6,0, product['tax_ids'])],
                         'list_price':product['price'],
                         'type':'service'
                          }#'category_id': kategorija,
        return self.pool.get('product.template').create(cr, uid, prod_template)
    
    def _generate_product_list(self, cr ,uid, ids, evidention, prod_type=None, context=None):
        if prod_type==None:
            prod_type=evidention.product_type
        product_list=[]
        for document in evidention.document_ids: 
            description2 = _("Translation of %s from %s to ") %(document.name, document.language_id.trans_from)
            desc_languages = ""
            for task in document.task_ids:
                desc_languages += ', ' + task.language_id.trans_to
                if prod_type == 1 :
                    prod_={}
                    prod_['name'] = task.name
                    prod_['description'] = _('Translation of %s \nfrom %s to %s') % (document.name, document.language_id.trans_from, task.language_id.trans_to)
                    prod_['units'] = document.cards_estm
                    prod_['evidention_id'] = evidention.id
                    prod_['document_id'] = document.id
                    prod_['task_id']= task.id
                    prod_['product_type'] = 1
                    prod_['price'] = evidention.price_id.price
                    prod_['partner_id']=evidention.partner_id.id
                    prod_['price_id']=evidention.price_id.id or 1
                    product_list.append(prod_)
                    
                if evidention.product_type == 3:
                    pass
        return product_list
#############################################################################################
##############################################################################################
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

class sale_order(osv.osv):
    _inherit= 'sale.order'
    _columns = {
                'trans_evid_ids':fields.many2many('translation.evidention','translation_evidention_so_rel','sale_order_id','translation_evidention_id','Evidentions')
                }
    
class account_tax(osv.Model):
    _inherit = "account.tax"
    _columns = {
                't_prod_ids':fields.many2many('translation.product','trans_product_taxes_rel','tax_ids','t_prod_ids','Taxes'),
                }
    
class translation_product(osv.Model):
    _name = "translation.product"
    _description = "Translation products - pre sale"
    
    
    
    def _get_total(self, cr, uid, ids, field_names, field_value, context=None):
        res={}
        tax_obj=self.pool.get('account.tax')
        for prod in self.browse(cr, uid, ids):
            total_untaxed = prod.price*prod.units*(100.00-prod.discount)/100
            total_tax=1
            for tax in prod.tax_ids:
                total_tax = total_tax * tax_obj.browse(cr, uid, tax.id).amount
            # OUCH! NOT SO GOOD , this only works for tax on price, 
            #if complicated taxes applied use with caution
            total_tax = total_tax * total_untaxed
            total = total_untaxed + total_tax
            res[prod.id] = {'total_untaxed':total_untaxed,
                            'total_tax': total_tax,
                            'total': total}
        return res

    
    def onchange_product_price(self, cr, uid, ids, price_id, context=None):
        res={}
        new_price = self.pool.get('translation.price').browse(cr, uid, price_id).price
        self.write(cr, uid, ids[0], {'price':new_price})
        res['price'] = new_price
        return {'value':res}
    
    _columns = {
                'name':fields.char('Name', size=128),
                'description':fields.text('Description'),
                'price_id':fields.many2one('translation.price','Price type'),
                'price':fields.float('Price', readonly=True ),# dodati float na dvije decimale!
                'units':fields.float('Units'),
                'discount':fields.float('Discount'),
                'tax_ids':fields.many2many('account.tax','trans_product_taxes_rel','t_prod_ids','tax_ids','Taxes'),
                'total_untaxed':fields.function(_get_total, type="float", string='Total untaxed', multi='total'),
                'total_tax':fields.function(_get_total, type="float", string="Tax", multi='total'),
                'total':fields.function(_get_total, type="float", string="Total", multi='total'),
                'evidention_id':fields.many2one('translation.evidention','Evidention'),
                'document_id':fields.many2one('translation.document','Document'),
                'task_id':fields.many2one('translation.document.task','Task'),
                'product_type':fields.integer('Product type'),#translation generator type
                'product_id':fields.many2one('product.product','Product'),
                'partner_id':fields.many2one('res.partner','Partner'),
                }


