# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from curses.ascii import NUL
from datetime import timedelta

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval

class CicloDeVida(models.Model):
    _name = "project.ciclo.vida"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Ciclo de Vida"
    _order = "nombre"
    _rec_name = "nombre"

    nombre = fields.Char("Nombre", index=True, required=True, track_visibility='onchange')
