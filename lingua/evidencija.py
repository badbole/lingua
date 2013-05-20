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
from osv import osv, fields
from openerp.tools.translate import _
from datetime import datetime, date
from pytz import timezone
import tools
import logging
_logger = logging.getLogger(__name__)
import openerp.addons.decimal_precision as dp

def get_evidencija_objects(self, cr, uid):
    evidencija_obj = self.pool.get('lingua.evidencija')
    evidencija_line_obj = self.pool.get('lingua.evidencija.line')
    return evidencija_obj, evidencija_line_obj

def zagreb_now():
    return datetime.now(timezone('Europe/Zagreb'))

def check_unique_partner(self, cr, uid, partner, object, context=None):
    if object.partner_id.id != partner:
        raise osv.except_osv(_('Error !'), _('Invoicing multi line is possible only for unique partner!'))
    return True

def check_evid_line_name(self, cr, uid, object, context=None):
    if not object.name:
        raise osv.except_osv(_('Error !'), _('Managing unrecived task not possible! Please recive task first'))
    return True

def check_sale_order_state(self, cr, uid, evidencija):
    sale_order_obj = self.pool.get('sale.order')
    for so in evidencija.sale_order:
        if sale_order_obj.browse(cr, uid, so.id).state != 'draft':
            
            raise osv.except_osv(_('Error !'), _('No more quotations, status of sale order %s is: %s !') % (so.name, so.state))
    return True

def create_sale_order(self, cr, uid, partner, pricelist, origin):
    values = {
              'partner_id':partner,
              'partner_invoice_id':partner,
              'partner_shipping_id':partner,
              'pricelist_id':pricelist, 
              'origin':origin
              }
    return self.pool.get('sale.order').create(cr, uid, values)

def create_sale_order_line(self, cr, uid, line_name, sale_order_id, product_id, price, uom_qty ):
    uom_id= get_uos(self, cr, uid)
    tax_id= get_pdv(self, cr, uid)
    values = {'name':line_name,
              'order_id':sale_order_id,
              'product_id':product_id,
              'price_unit':price, # ili cijenu koja je izračunata i količine 1!
              'product_uom':uom_id,
              'product_uos':uom_id,
              'tax_id':[(4,tax_id)],
              'product_uom_qty':uom_qty,
              }
    
    return self.pool.get('sale.order.line').create(cr, uid, values)
            
            
def make_product_from_line(self,cr, uid, evidencija, evidencija_line):
    product_name = generate_product_name(self, evidencija, evidencija_line)
    product_desc = generate_product_desc(self, evidencija, evidencija_line)
    price = get_translation_price(self, evidencija, evidencija_line)
    template = create_product_template(self, cr, uid, product_name, product_desc, price )
    product = create_product_product(self, cr, uid, template, product_name, evidencija_line.name)
    return self.pool.get('lingua.evidencija.line').write(cr, uid, evidencija_line.id, {'product_id':product})

def get_uos(self, cr, uid):
    return self.pool.get('product.uom').search(cr, uid, [('name', '=', 'kart')] )[0]

def get_pdv(self, cr, uid):
    return self.pool.get('account.tax').search(cr, uid, [('name', '=', "25% PDV usluge")] )[0]

def create_product_template(self, cr, uid, name, description, price, context=None ):
    uom_id= get_uos(self, cr, uid)
    tax_id= get_pdv(self, cr, uid)
    prod_temp = {
                'name':name,
                'description': description,
                'uom_id':uom_id,
                'uom_po_id':uom_id,
                #'cost_method':cost, #
                #'category_id': kategorija,
                #'description_sale':"Prodajni opis",
                'taxes_id':[(4,tax_id)], # pdv 25%!!!
                'list_price':price,
                'type':'service'
                }
    return self.pool.get('product.template').create(cr, uid, prod_temp)

def create_product_product(self, cr, uid, template, name, code, context=None):
    prod = {
            'product_tmpl_id':template,
            'name_template':name,
            'default_code':code,
            }
    return self.pool.get('product.product').create(cr, uid, prod)

def generate_product_name(self, evidencija, evid_line):
    return ("Prijevod sa %s na %s jezik" % (evidencija.lang_origin.trans_from, evid_line.language_id.trans_to))

def generate_product_desc(self, evidencija, evid_line):
    #prevoditelja mozda nema
    return ("%s prevedeno na %s " % (evidencija.name, evid_line.language_id.trans_to))

def get_translation_price(self, evidencija, evid_line):
    return evidencija.trans_card * evidencija.price_id.price



class lingua_marketing(osv.osv):
    #TODO Separate module
    _name='lingua.marketing'
    _description = 'Marketing evidencija'
    _columns = {
        'name':fields.char('name', size=64),
        'evidencija_ids':fields.one2many('lingua.evidencija','marketing_id','Income')
                }

class lingua_evidencija(osv.osv):
    _name = 'lingua.evidencija'
    _description = 'Evidention of translations'
    
    _translation_status = [('draft','Draft')
                   ,('open','Open')
                   ,('process','In process')
                   ,('finish','Finished')
                   ,('cancel','Canceled')
                   ]
    
    def onchange_lang_origin(self, cr, uid, ids, lang_origin, context=None):
        if lang_origin:
            if not self.pool.get('hr.employee').search(cr,uid,[('language_ids','=',lang_origin)]):
                raise osv.except_osv(_('Error!'), _('No available translators for this language!.'\
                                                    'Please find a translator for this language in order to assign this translation'))
        return True
    """    
            evidention = self.pool.get('lingua.evidencija').browse(cr, uid, ids)
            if len(evidention):
                test = evidention[0].id
                return True
            else:
                return True
            #result = super(lingua_evidencija,self, cr, uid, ids)
            #result['domain']= result.get('domain',{})
            #result['domain'].update({'evidencija_line_ids':[('','=',prostor_id )]})
        return True
    """
    def _sel_lang_origin(self, cr, uid, context=None):
        lang_obj = self.pool.get('lingua.language')
        ids = lang_obj.search(cr, uid, [('employee_ids', '!=', False )])
        res = lang_obj.read(cr, uid, ids, ['name','id'])
        res= [(r['id'], r['name']) for r in res]
        return res
    
    _columns = {
        'name': fields.char('Name', size=128 , select=1, required=1),
        'seq_no':fields.char('Number', size=64),
        'broj_evidencije':fields.char('Evidention number',size=64),
        'fiskal_prostor_id':fields.many2one('fiskal.prostor','Chapter name', required=1),
        'broj_evidencija_pod': fields.char('Chapter evidention number', size=32),
        'partner_id':fields.many2one('res.partner', 'Partner', required=1),
        'lang_origin':fields.many2one('lingua.language','Origin language', required=1, domain="[('translator_ids', '!=', False )]"), #uzimam samo jezike koji imaju dodijeljenog prevoditelja
        'lang_translate':fields.many2many('lingua.language','lingua_tranlslate_to_res','lingua_languages_id','lingua_evidencija_id', domain="[('translator_ids', '!=', False )]"),
        'date_recived':fields.datetime('Recived', help="Date and time of recieving, leave empty for current date/time"),
        'date_due':fields.datetime('Deadline'),
        'note':fields.text('Note'),
        # TODO! - izračun i filteri/grupiranje
        #'days_remain':fields.function(),
        #'hrs_remain':fields.function(),
        'state':fields.selection (_translation_status,'Evidention status'),
        'evidencija_line_ids':fields.one2many('lingua.evidencija.line','evidencija_id','Translations'),
        'marketing_id':fields.many2one('lingua.marketing','Marketing'),
        'trans_card':fields.float('Text cards', help="Estimated number of cards for translating"),
        'price_id':fields.many2one('lingua.price','Price definition'),
        'sale_order':fields.many2many('sale.order','lingua_evidencija_sale_order_rel', 'lingua_evidencija_id', 'sale_order_id'),
        'invoice':fields.many2one('account.invoice','Invoice'),
        'type_id':fields.many2one('lingua.translation.type', 'Type of translation'),
        #'time_remain':fields.function(_get_remain_time, string="Time remain", type='char', size=32),
        
                }

    _defaults = {
                 'name':'Prijevod ',
                 'state':"draft",
                 'trans_card':1,
                 'price_id':1
                 }
    
    _order = "id desc"
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        try:
            _logger.info( _('Creating translate evidention'))
            return super(lingua_evidencija, self).create(cr, uid, vals, context)
        except Exception, e:
            raise orm.except_orm(_('Unknown Error!'), str(e))
    

    
    
    # jedna evidencija u SO
    def button_evid_2_saleorder(self, cr, uid, ids, context=None):
        evidencija_obj, evidencija_line_obj = get_evidencija_objects(self, cr, uid)
        evidencija = evidencija_obj.browse(cr, uid, ids)[0]
        
        if evidencija.sale_order:
            check_sale_order_state(self, cr, uid, evidencija)
        
        #TODO : get right pricelist for partner! for now i use 1
        so = create_sale_order(self, cr, uid, evidencija.partner_id.id, 1 , evidencija.name)
        
        product_template= self.pool.get('product.template')
        
        trans_price = self.pool.get('lingua.price').browse(cr, uid, evidencija.price_id.id)
        for line in evidencija_line_obj.search(cr, uid, [('evidencija_id', '=', evidencija.id)]): 
            task_line = evidencija_line_obj.browse(cr, uid, line)
            if not task_line.product_id.id:
                make_product_from_line(self, cr, uid, evidencija, task_line)
                task_line = evidencija_line_obj.browse(cr, uid, line)
            template = product_template.browse(cr,uid,task_line.product_id.id )
            #TODO: price i qty refactor!
            create_sale_order_line(self, cr, uid, task_line.name, so, task_line.product_id.id, trans_price.price, evidencija.trans_card)  #template.list_price
        
        return evidencija_obj.write(cr, uid, evidencija.id, {'sale_order':[(4,so)]}) 
    
    
    #Više evidencija u jedna SO
    def action_multi_evidention_2_order(self, cr, uid, ids, context=None):
        evidencija_obj, evidencija_line_obj = get_evidencija_objects(self, cr, uid)
        sel_evidencije=evidencija_obj.browse(cr, uid, ids)
        partner=sel_evidencije[0].partner_id.id
        
        name='EVID : '
        for evidencija in sel_evidencije:
            check_unique_partner(self, cr, uid, partner, evidencija)
            so_origin = ','.join([name,evidencija.name])
        
        so = create_sale_order(self, cr, uid, partner, 1 , so_origin)
        product_template= self.pool.get('product.template')
        trans_price_obj = self.pool.get('lingua.price')
        for evidencija in sel_evidencije:
            trans_price = self.pool.get('lingua.price').browse(cr, uid, evidencija.price_id.id)
            for line in evidencija_line_obj.search(cr, uid, [('evidencija_id', '=', evidencija.id)]): 
                task_line = evidencija_line_obj.browse(cr, uid, line)
                if not task_line.product_id.id:
                    make_product_from_line(self, cr, uid, evidencija, task_line)
                    task_line = evidencija_line_obj.browse(cr, uid, line)
                template = product_template.browse(cr,uid,task_line.product_id.id )
                #TODO: price i qty refactor!
                create_sale_order_line(self, cr, uid, task_line.name, so, task_line.product_id.id, trans_price.price, evidencija.trans_card)
            evidencija_obj.write(cr, uid, evidencija.id, {'sale_order':[(4,so)]})
        return True
    
    
    def button_recive(self, cr, uid, ids, context=None):
        evidencija_obj, evidencija_line_obj = get_evidencija_objects(self, cr, uid)
        evidention = evidencija_obj.browse(cr, uid, ids)[0]
        if not evidention.evidencija_line_ids:
            raise osv.except_osv(_('Error !'), _('No chosen languages for translation!'))
        evidention_line = evidencija_line_obj.search(cr, uid, [('evidencija_id', '=', evidention.id)])
        langs = self.pool.get('lingua.languages')
        seq_no = self.pool.get('ir.sequence').get(cr,uid,'lingua_order')
        vals={
              'state':'open',
              'seq_no':seq_no
              }        
        if not evidention.date_recived:
            vals['date_recived']=zagreb_now()
        for line in evidention_line:
            trans = evidencija_line_obj.browse(cr, uid, line).language_id.iso_code2
            line_name = '-'.join([seq_no, evidention.lang_origin.iso_code2, trans]) 
            line_vals={
                       'name':line_name,
                       'partner_id':evidention.partner_id.id,
                       'language_origin':evidention.lang_origin.id
                       }
            evidencija_line_obj.write(cr, uid, line, line_vals)
        return evidencija_obj.write(cr, uid, evidention.id, vals)
    
    
    
class lingua_evidencija_line (osv.Model):
    _name = 'lingua.evidencija.line'
    _description = 'Signle langugae for translations'
    
    _translation_line_status =[('draft',"Draft")
                               ,('asign',"Asigned")
                               ,('translate',"Translation in progress")
                               ,('lecture',"Lectoring in progress")
                               ,('finish',"Finished")
                               ,('pause',"Paused")
                               ,('cancel',"Canceled")
                               ]
    #TODO Multiline!
    _created_product_type = [('single','One-Line product')
                             ,('combo','Multi-Line Product')
                             ]
    
    
    
    _columns = {
                'name':fields.char('Name',size=64),
                'evidencija_id':fields.many2one('lingua.evidencija','Evidevtion reference'),
                'evidencija_origin':fields.related('evidencija_id','lang_origin', type='many2one', relation="lingua.language", string="Original language"),
                'language_origin':fields.many2one('lingua.language','Origin language'),
                'language_id':fields.many2one('lingua.language','Translated language', required=True),
                'translator_ids':fields.many2many('hr.employee','lingua_evidencija_line_translate_hr_employee_rel','lingua_evidencija_line_id','hr_employee_id', 'Translator'),
                'lector_ids':fields.many2many('hr.employee','lingua_evidencija_line_lector_hr_employee_rel','lingua_evidencija_line_id','hr_employee_id', 'Lector'),
                'partner_id':fields.many2one('res.partner','Partner'),
                'lectoring':fields.boolean ('Mandatory lectoring'),
                'state':fields.selection (_translation_line_status,'Translation status'),
                #'translated_cards':fields.integer('Cards translated'),  #broj prevedenih kartica .. jel mozda treba gledati na decimalu?
                'translation_start':fields.datetime('Translation start'),
                'translation_finish':fields.datetime('Translation finished'),
                'lectoring_start':fields.datetime('Lectoring start'),
                'lectoring_finish':fields.datetime('Lectoring finished'),
                'product_type':fields.selection(_created_product_type,'Product type'),
                'product_id':fields.many2one('product.product', 'Related product'),
                'finish_due':fields.related('evidencija_id','date_due', type='datetime', string='Due date'),
                'sale_order':fields.many2many('sale.order','lingua_evidencija_line_sale_order_rel', 'lingua_evidencija_line_id', 'sale_order_id'),
                'error':fields.many2many('lingua.error','lingua_evidencija_line_error_rel','lingua_evidencija_line_id','lingua_error_id','Error')
                }
    
    _defaults = {
                 'state':"draft",
                 'product_type':'single'
                 }
    _order = "id desc"

    def action_multiline_order(self, cr, uid, ids, context=None):
        evidencija_obj, evidencija_line_obj = get_evidencija_objects(self, cr, uid)
        lines = evidencija_line_obj.browse(cr, uid, ids)
        
        partner=lines[0].partner_id.id
        name='TASK : '
        for line in lines:
            check_unique_partner(self, cr, uid, partner, line)
            check_evid_line_name(self, cr, uid, line)
            name=','.join([name,line.name])
            
        so = create_sale_order(self, cr, uid, partner, 1 , name)
        product_template= self.pool.get('product.template')
        so_tran_line_rel=[]
        for line in lines:
            task_line = evidencija_line_obj.browse(cr, uid, line.id)
            if not line.product_id.id:
                evidencija = evidencija_obj.browse(cr, uid, line.evidencija_id.id)
                make_product_from_line(self, cr, uid, evidencija, line)
                task_line = evidencija_line_obj.browse(cr, uid, line.id)
            template = product_template.browse(cr, uid, task_line.product_id.id )
            create_sale_order_line(self, cr, uid, task_line.name, so, task_line.product_id.id, template.list_price, evidencija.trans_card)
            so_tran_line_rel.append(task_line.id)
        evidencija_obj.write(cr, uid, evidencija.id, {'sale_order':[(4,so)]})
        
                
                             
        return True
          
    def button_translation2product(self, cr, uid, ids, context=None):
        evidencija_obj, evidencija_line_obj = get_evidencija_objects(self, cr, uid)
        evidencija_line=evidencija_line_obj.browse(cr, uid, ids)[0]
        if evidencija_line.product_id:
            #TODO: update proizvoda isl.. 
            return True
        else:
            evidencija = evidencija_obj.browse(cr, uid, evidencija_line.evidencija_id.id)
            return make_product_from_line(self, cr, uid, evidencija, evidencija_line)
        
    

    def onchange_employee_id(self, cr, uid, ids, employee_id , context=None):
        evid_line = self.pool.get('lingua.evidencija.line').browse(cr,uid,ids)[0]
        evidention = self.pool.get('lingua.evidencija').browse(cr, uid, evid_line.evidencija_id.id) 
        if evidention.state == 'open':
            self.pool.get('lingua.evidencija').write(cr, uid, evidention.id, {'state':'process'})
            
        if evid_line.state == 'draft':
            self.pool.get('lingua.evidencija.line').write(cr, uid, evid_line.id, {'state':'asign'})
        return True
    
    def button_translation_start(self, cr, uid, ids, context=None):
        evid_line=self.pool.get('lingua.evidencija.line').browse(cr, uid, ids)[0]
        if evid_line.translation_start:
            values = {
                      'state':'translate'
                      }
        else:
            time=zagreb_now()
            values = {'translation_start':time,
                      'state':'translate'
                      }
        return self.pool.get('lingua.evidencija.line').write(cr, uid, evid_line.id, values)
    
    def button_translation_finish(self, cr, uid, ids, context=None):
        evid_line=self.pool.get('lingua.evidencija.line').browse(cr, uid, ids)[0]
        if evid_line.translation_finish:
            #već postoji datum? jel reopen ili kaj? zasada niš
            return True
        
        time=zagreb_now()
        if evid_line.lectoring:
            values = {'translation_finish':time,
                      'state':'lecture'}
        else:
            values = {'translation_finish':time,
                      'state':'finish'}
        self.pool.get('lingua.evidencija.line').write(cr, uid, evid_line.id, values )
        self.check_evidencija_state(cr, uid, evid_line.evidencija_id.id)
        return True
        
    def button_lectoring_start(self, cr, uid, ids, context=None):
        evid_line=self.pool.get('lingua.evidencija.line').browse(cr, uid, ids)[0]
        if evid_line.lectoring_start:
            values = {'state':'lecture'}
        else:
            time=zagreb_now()
            values = {'lectoring_start':time,
                      'state':'lecture'}
        return self.pool.get('lingua.evidencija.line').write(cr, uid, evid_line.id, values)
    
    def button_lectoring_finish(self, cr, uid, ids, context=None):
        evid_line=self.pool.get('lingua.evidencija.line').browse(cr, uid, ids)[0]
        if evid_line.lectoring_finish:
            #već postoji datum? jel reopen ili kaj? zasada niš
            return True
        time=zagreb_now()
        values = {'lectoring_finish':time,
                      'state':'finished'}
        self.pool.get('lingua.evidencija.line').write(cr, uid, evid_line.id, values)
        self.check_evidencija_state(cr, uid, evid_line.evidencija_id.id)
        return True
        
    def check_evidencija_state(self, cr, uid, evidencija_id, context=None):
        gotovo = True
        for id in self.pool.get('lingua.evidencija').browse(cr, uid, evidencija_id).evidencija_line_ids:
            if not (id.state == "finish") :
                return False
                #gotovo=False
                #break
        #if gotovo :     
        return self.pool.get('lingua.evidencija').write(cr, uid, evidencija_id, {'state':'finish'})
        #"return True
    
           
    def button_pause(self, cr, uid, ids, context=None):
        evid_line=self.pool.get('lingua.evidencija.line').browse(cr, uid, ids)[0]
        if evid_line.state in ('translation','lectoring'):
            return self.pool.get('lingua.evidencija.line').write(cr, uid, evid_line.id, {'state':'paused'} )


class lingua_error(osv.Model):
    _name="lingua.error"
    _description="Error handling"
    
    _columns={
              'name':fields.char('Name', size=64),
              'reported_by':fields.selection([('partner','Partner'),
                                              ('employee','Employee')],'Error reported by', help = _("Who reported error")),
              'reported_date':fields.datetime('Date reported'),
              'description':fields.text('Description'),
              'evidencija_line':fields.many2many('lingua.evidencija.line','lingua_evidencija_line_error_rel','lingua_error_id','lingua_evidencija_line_id','Tasks')
              }


class lingua_translation_type(osv.Model):
    _name = "lingua.translation.type"
    _decription = "Possible translation types"
    _columns = {
                'name':fields.char('Type', size=128),
                'evidention_ids':fields.one2many('lingua.evidencija', 'type_id', 'Evidentions'),
                'employee_ids':fields.many2many('hr.employee', 'lingua_translation_type_hr_employee_rel', 'lingua_translation_type_id', 'hr_employee_id', 'Specialized translators'),
                }