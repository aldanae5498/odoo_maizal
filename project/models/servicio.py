# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from curses.ascii import NUL
from datetime import timedelta

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval

class Servicio(models.Model):
    _name = "project.servicio"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Servicio"
    _order = "titulo"
    _rec_name = "titulo"

    titulo = fields.Char("Título", index=True, required=True, track_visibility='onchange')
