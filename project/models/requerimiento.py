# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval

class Requerimiento(models.Model):
    _name = "project.requerimiento"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Requerimiento"
    _order = "name"
    _rec_name = "name"

    name = fields.Char(string='Código de Requerimiento', required=True, copy=False, readonly=True, states={'borrador': [('readonly', False)]}, index=True, default=lambda self: _('Nuevo'))
    titulo = fields.Char("Título", index=True, required=True, track_visibility='onchange')
    project_id = fields.Many2one('project.project', string='Proyecto', required=True)
    fecha_inicial = fields.Datetime("Fecha Inicial", required=True, index=True)
    fecha_limite = fields.Datetime("Fecha Límite", required=True, index=True)
    state = fields.Selection(
        [
            ('borrador', 'Borrador'),
            ('confirmado', 'Aceptado'),
            ('hecho', 'Validado'),
            ('cancelado', 'Devuelto'),
        ],
        string = 'Estado',
        default = 'borrador',
        tracking = True
    )

    # Interesados:
    director_id = fields.Many2one('res.partner', string='Director')
    lider_id = fields.Many2one('res.partner', string='Líder')
    gestor_id = fields.Many2one('res.partner', string='Gestor') 

    # Descripción:
    descripcion = fields.Html("Descripción")

    # Número de documentos:
    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Number of documents attached")

    def _compute_attached_docs_count(self):
        Attachment = self.env['ir.attachment']
        for requerimiento in self:
            requerimiento.doc_count = Attachment.search_count([
                ('res_model', '=', 'project.requerimiento'), ('res_id', '=', requerimiento.id),
            ])    

    # Funciones que cambia el state del requerimiento:
    def action_confirmar(self):
        self.state = 'confirmado'

    def action_hecho(self):
        self.state = 'hecho'

    def action_borrador(self):
        self.state = 'borrador'

    def action_cancelar(self):
        self.state = 'cancelado'                        

    # Secuencia:
    @api.model
    def create(self, vals):
        if vals.get('name', _('Nuevo')) == _('Nuevo'):
            vals['name'] = self.env['ir.sequence'].next_by_code('project.requerimiento') or _('Nuevo')
        res = super(Requerimiento, self).create(vals)
        return res

    # Vista a documentos:
    @api.multi
    def attachment_tree_view(self):
        attachment_action = self.env.ref('base.action_attachment')
        action = attachment_action.read()[0]
        action['domain'] = str([
            ('res_model', '=', 'project.requerimiento'),
            ('res_id', 'in', self.ids) # ids: Todos los ids de el modelo 'project.requerimiento'
        ])
        action['context'] = "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        return action        

    # Botón que envía correo:
    @api.multi
    def btn_send_email(self):
        template_obj = self.env['mail.template'].sudo().search([('name','=','Email Template - Nuevo Requerimiento')], limit=1)
        if template_obj:
            
            # receipt_list = ['abc@gmail.com','xyz@yahoo.com']
            receipt_list = [
                self.director_id.email_formatted,
                self.lider_id.email_formatted,
                self.gestor_id.email_formatted,
                'nancy21156.nietos@gmail.com'          
            ]
            
            # email_cc = ['test@gmail.com']
            email_cc = [self.user_id.email_formatted]
            
            body = template_obj.body_html
            # body=body.replace('--variable_name--',self.name)
            # body=body.replace('--variable_titulo--',self.titulo)

            mail_values = {
            'subject': template_obj.subject,
            'body_html': body,
            'email_to':';'.join(map(lambda x: x, receipt_list)),
            'email_cc':';'.join(map(lambda x: x, email_cc)),
            'email_from': 'aldanae5498@gmail.com',
            }
            create_and_send_email = self.env['mail.mail'].create(mail_values).send()    
