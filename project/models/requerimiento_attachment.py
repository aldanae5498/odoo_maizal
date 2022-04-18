# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import AccessError


class RequerimientoAttachment(models.Model):
    _name = 'project.requerimiento.attachment'
    _inherit = 'ir.attachment'
    prueba = fields.Boolean("Prueba", default=False)
