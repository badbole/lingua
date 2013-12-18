# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Module: translations_error
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
import datetime


class translation_error(osv.Model):
    _name="translation.error"
    _inherit = ['mail.thread']
    _description="Error handling"
    
    _reported_by = [('partner','Partner'),
                    ('employee','Employee')]
    
    _error_states = [('draft','Draft'),
                     ('confirmed','Confirmed'),
                     ('correct','Corrected')]
    _columns={
              'name':fields.char('Name', size=128),
              'state':fields.selection(_error_states,'State'),
              'reported_by':fields.selection(_reported_by, 'Reported by', help = _("Who reported error"), required=1),
              'reported_date':fields.datetime('Date reported'),
              'description':fields.text('Description'),
              'task_ids':fields.many2many('translation.document.task','translation_document_task_error_rel','translation_error_id','translation_document_task_id','Tasks')
              }
    
    _defaults = {
                 'state':'draft'
                 }
    
    def action_error_validate(self, cr, uid, ids, context=None):
        for error in self.browse(cr, uid, ids):
            if len(error.task_ids) == 0:
                raise osv.except_osv(_('Error!'), _('No related documet task found!'\
                                                    '\nIt is not possible to validate error if it is not related to some document or task!'))
            name = self.pool.get('ir.sequence').get(cr,uid,'translation_error')
            self.write(cr, uid, error.id, {'name':name,'state':'confirmed'})
            self.action_error_validate_send_note(cr, uid, ids, error)
            
        return True
    
    def action_error_validate_send_note(self, cr, uid, ids, error, context=None):
        return self.message_post(cr, uid, ids, _('Error %s confirmed' % (error.name)),
                          _("Error is confirmed"),context=context)
    
    def action_error_done(self, cr, uid, ids, context=None):
        for error in self.browse(cr, uid, ids):
            self.write(cr, uid, error.id, {'state':'correct'})
            self.action_error_correct_send_note(cr, uid, ids, error)
        return True
    
    def action_error_correct_send_note(self, cr, uid, ids, error, context=None):
        return self.message_post(cr, uid, ids, _('Error %s corrected' % (error.name)),
                          _("Error is corrected"),context=context)
        
        
class translation_document_task(osv.Model):
    _inherit = "translation.document.task"
    _columns = {
                'error_ids':fields.many2many('translation.error', 'translation_document_task_error_rel', 'translation_document_task_id','translation_error_id','Error' )
                }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: