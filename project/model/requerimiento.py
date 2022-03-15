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
    _order = "titulo"
    _rec_name = "titulo"

    titulo = fields.Char("Título", index=True, required=True, track_visibility='onchange')
    fecha_limite = fields.Datetime("Fecha Límite", required=True, index=True)
    task_id = fields.Many2one('project.task', string='Tarea')
    attachment_id = fields.Many2one('ir.attachment', string="Adjunte documento")
    descripcion_documento = fields.Text("Descripción")

    # Interesados:
    director_id = fields.Many2one('res.partner', string='Director')
    lider_id = fields.Many2one('res.partner', string='Líder')
    gestor_id = fields.Many2one('res.partner', string='Gestor')

    estatus = fields.Selection([
        ('0', 'Radicado'),
        ('1', 'Asignado'),
        ('2', 'Aceptado'),
        ('3', 'Pendiente'),
        ('4', 'Finalizado'),
        ('5', 'Cancelado'),
        ], default='0', index=True, string="Estatus")    

    # Aceptación:
    fecha_inicial = fields.Datetime("Fecha Inicial", required=True, index=True)

    # Descripción:
    descripcion = fields.Text("Descripción")

    @api.model
    def aceptar_requerimiento(self):
        return True
