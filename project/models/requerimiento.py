# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from curses.ascii import NUL
from datetime import timedelta, datetime

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval

class Requerimiento(models.Model):
    _name = "project.requerimiento"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Requerimiento"
    _order = "name"
    _rec_name = "name"

    name = fields.Char(string='Código de Requerimiento', required=True, copy=False, readonly=True, states={'borrador': [('readonly', False)]}, index=True, default=lambda self: _('Esperando aprobación'))
    titulo = fields.Char("Título", index=True, required=True, track_visibility='onchange')
    
    project_id = fields.Many2one(
        'project.project', 
        string='Proyecto', 
        required=False,
        track_visibility='onchange',
        change_default=True,
    )

    ciclo_vida_id = fields.Many2one(
        'project.ciclo.vida', 
        string='Ciclo de Vida', 
        required=False,
        track_visibility='onchange',
        change_default=True,
    )    
    
    '''
    project_id = fields.Many2one(
        'project.project', 
        string='Proyecto', 
        required=False,
        states={
            'aprobado': [('required', True)],
        },
        # default=lambda self: self.env.context.get('default_project_id'), 
        index=True, 
        track_visibility='onchange',
        change_default=True,
    )    
    '''

    fecha_inicial = fields.Datetime("Fecha Inicial")
    
    fecha_limite = fields.Datetime(
        "Fecha Límite", 
        required=False, 
        index=True, 
    )

    fecha_radicacion = fields.Datetime("Fecha de Radicación", required=False, readonly=True)
    fecha_aprobacion = fields.Datetime("Fecha de Aprobación", required=False, readonly=True)    

    state = fields.Selection(
        [
            ('borrador', 'Borrador'),
            ('radicado', 'Radicado'),
            ('aprobado', 'Aprobado'),
            ('cancelado', 'Devuelto'),
        ],
        string = 'Estado',
        default = 'borrador',
        tracking = True
    )

    # Interesados:
    director_id = fields.Many2one(
        'res.partner', 
        string='Director',
        required=False,
    )

    lider_id = fields.Many2one(
        'res.partner', 
        string='Líder',
        required=False,
    )

    gestor_id = fields.Many2one(
        'res.partner', 
        string='Gestor',
        required=False,
    ) 

    # Descripción:
    descripcion = fields.Html("Descripción")

    # Número de documentos:
    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Number of documents attached")

    # Servicios:
    '''
    s_tarjeta_debito = fields.Boolean(string='Tarjeta de Débito', default=False)
    s_tarjeta_credito = fields.Boolean(string='Tarjeta de Crédito', default=False)
    s_autorizador = fields.Boolean(string='Autorizador', default=False)
    s_compensacion_redes = fields.Boolean(string='Compensación Redes', default=False)
    s_compensacion_bpo = fields.Boolean(string='Compensación BPO', default=False)
    s_compensacion_entidades_financieras = fields.Boolean(string='Compensación Entidades Financieras', default=False)
    '''

    servicio_ids = fields.Many2many('project.servicio', 'project_requerimiento_project_servicio_rel', 'project_requerimiento_id', 'project_servicio_id', string='Servicios')

    # Color para el kanban:
    color = fields.Integer(string='Color Index', default=0, compute='change_color_on_kanban')

    def change_color_on_kanban(self):
        """    this method is used to chenge color index    base on fee status    ----------------------------------------    :return: index of color for kanban view    """    
        for record in self:
            color = 0
            if record.state == 'borrador':
                color = 4 # Azul claro
            elif record.state == 'radicado':
                color = 11 # Morado
            elif record.state == 'aprobado':
                color = 10 # Verde
            else: # cancelado
                color = 1 # Rojo

            record.color = color

    def _compute_attached_docs_count(self):
        Attachment = self.env['project.requerimiento.attachment']
        for requerimiento in self:
            requerimiento.doc_count = Attachment.search_count([
                ('res_model', '=', 'project.requerimiento'), ('res_id', '=', requerimiento.id),
            ])    

    @api.multi
    def unlink(self):
        for requerimiento in self:
            if requerimiento.project_id:
                raise UserError(_('No puede eliminar un requerimiento asociado a un proyecto. Lo puede archivar o establecer el campo de proyecto como vacío.'))
        return super(Requerimiento, self).unlink()    

    # Funciones que cambia el state del requerimiento:
    def action_radicar(self):
        nombre_cliente = self.create_uid.name
        correo_cliente = self.create_uid.login
        name = self.name
        titulo = self.titulo
        fecha = datetime.now()

        # Contexto del correo:
        ctx = {}
        ctx['nombre_cliente'] = nombre_cliente
        ctx['email_to'] = correo_cliente
        ctx['name'] = name
        ctx['titulo'] = titulo
        ctx['fecha'] = fecha
        
        # Enviar correo:
        template_id = self.env.ref('project.et_requerimiento_radicado').id
        template = self.env['mail.template'].browse(template_id)
        template.with_context(ctx).send_mail(self.id, force_send=True)

        self.env.user.notify_success(message=f'¡Requerimiento radicado exitosamente!')
        self.state = 'radicado'

    def action_aprobar(self):
        nombre_cliente = self.create_uid.name
        correo_cliente = self.create_uid.login
        name = self.name
        titulo = self.titulo
        fecha = datetime.now()

        # Contexto del correo:
        ctx = {}
        ctx['nombre_cliente'] = nombre_cliente
        ctx['email_to'] = correo_cliente
        ctx['name'] = name
        ctx['titulo'] = titulo
        ctx['fecha'] = fecha
        
        # Enviar correo:
        template_id = self.env.ref('project.et_requerimiento_aprobado').id
        template = self.env['mail.template'].browse(template_id)
        template.with_context(ctx).send_mail(self.id, force_send=True)

        self.env.user.notify_success(message='¡Requerimiento aprobado exitosamente!')
        self.state = 'aprobado'

    def enviar_correo_aprobacion(self):
        nombre_cliente = self.create_uid.name
        correo_cliente = self.create_uid.login
        name = self.name
        titulo = self.titulo
        fecha = datetime.now()

        # Contexto del correo:
        ctx = {}
        ctx['nombre_cliente'] = nombre_cliente
        ctx['email_to'] = correo_cliente
        ctx['name'] = name
        ctx['titulo'] = titulo
        ctx['fecha'] = fecha
        
        # Enviar correo:
        template_id = self.env.ref('project.et_requerimiento_aprobado').id
        template = self.env['mail.template'].browse(template_id)
        template.with_context(ctx).send_mail(self.id, force_send=True)

    def action_borrador(self):
        self.env.user.notify_success(message='El requerimiento ha sido establecido como borrador')
        self.state = 'borrador'

    def action_devolver(self):
        self.env.user.notify_warning(message='El requerimiento ha sido devuelto')
        self.state = 'borrador'
        # self.state = 'cancelado'                        

    '''
    @api.onchange('project_id')
    def onchange_project_id(self):    
        self.env.user.notify_success(message='Project ID: ' + str(self.project_id.codigo))
    '''

    def get_codigo_requerimiento(self, project_id, codigo_proyecto):
        count_pro_req = self.env['project.requerimiento'].search_count([('project_id', '=', project_id)])
        count_pro_req = count_pro_req + 1
        count_pro_req = str(count_pro_req)
        if len(count_pro_req) == 1:
            count_pro_req = '0' + count_pro_req

        # Código del Requerimiento:
        codigo_requerimiento = str(codigo_proyecto) + '-' + str(count_pro_req)
        return codigo_requerimiento

    # ============================ Crear ============================ #
    '''
    @api.model
    def create(self, vals):
        context = dict(self.env.context, mail_create_nolog=True)
        res = super(Requerimiento, self.with_context(context)).create(vals)

        if vals:
            nombre_cliente = self.create_uid.name
            correo_cliente = self.create_uid.login
            name = self.name
            titulo = self.titulo
            fecha = datetime.now()

            # Contexto del correo:
            ctx = {}
            ctx['nombre_cliente'] = nombre_cliente
            ctx['email_to'] = correo_cliente
            ctx['name'] = name
            ctx['titulo'] = titulo
            ctx['fecha'] = fecha

            # Enviar correo:
            template_id = self.env.ref('project.et_nuevo_requerimiento').id
            template = self.env['mail.template'].browse(template_id)
            template.with_context(ctx).send_mail(self.id, force_send=True)

            self.env.user.notify_success(message='¡Requerimiento creado exitosamente!')
        
        return res
    '''

    '''
    @api.model
    def create(self, vals):
        res = super(Requerimiento, self).create(vals)

        nombre_cliente = self.create_uid.name
        correo_cliente = self.create_uid.login
        name = self.name
        titulo = self.titulo
        fecha = datetime.now()

        # Contexto del correo:
        ctx = {}
        ctx['nombre_cliente'] = nombre_cliente
        ctx['email_to'] = correo_cliente
        ctx['name'] = name
        ctx['titulo'] = titulo
        ctx['fecha'] = fecha

        # Enviar correo:
        template_id = self.env.ref('project.et_nuevo_requerimiento').id
        template = self.env['mail.template'].browse(template_id)
        template.with_context(ctx).send_mail(self.id, force_send=True)

        return res       
    '''

    # ============================ Editar ============================ #
    # Secuencia:
    @api.multi
    def write(self, values):
        project_id = values.get('project_id')
        state = values.get('state')

        if state == 'borrador' or state == 'radicado':
            values['name'] = 'Esperando aprobación'
            if state == 'borrador':
                values['project_id'] = False
                values['director_id'] = ''
                values['lider_id'] = ''
                values['gestor_id'] = ''
            else:
                values['fecha_radicacion'] = datetime.now()
        else:
            codigo_proyecto = self.env['project.project'].search([('id', '=', project_id)], limit=1).codigo

            if codigo_proyecto == False:
                values['name'] = 'Esperando asignación de proyecto'
            else:
                count_pro_req = self.env['project.requerimiento'].search_count([('project_id', '=', project_id)])
                count_pro_req = count_pro_req + 1
                count_pro_req = str(count_pro_req)
                if len(count_pro_req) == 1:
                    count_pro_req = '0' + count_pro_req

                # Código del Requerimiento:
                codigo_requerimiento = self.get_codigo_requerimiento(project_id, codigo_proyecto)

                # Verificando si existe un requerimiento con éste código:
                row_count = self.env['project.requerimiento'].search_count([('name', '=', codigo_proyecto)])
                if row_count > 0:
                    codigo_requerimiento = self.get_codigo_requerimiento(project_id, codigo_proyecto)

                # Asignando código:
                values['name'] = codigo_requerimiento
                
                # Enviando correo de aprobación:
                self.enviar_correo_aprobacion()
                
                # Mostrando notificación:
                self.env.user.notify_success(message='¡Requerimiento aprobado exitosamente!')
                
                # X el requerimiento:
                values['state'] = 'aprobado'
                values['fecha_aprobacion'] = datetime.now()
        
        return super(Requerimiento, self).write(values)
        
    # Vista a documentos:
    @api.multi
    def attachment_tree_view(self):
        attachment_action = self.env.ref('project.action_requerimiento_attachment')
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

    @api.model
    def _get_default_partner(self):
        if 'default_project_id' in self.env.context:
            default_project_id = self.env['project.project'].browse(self.env.context['default_project_id'])
            return default_project_id.exists().partner_id

    def _get_default_stage_id(self):
        """ Gives default stage_id """
        project_id = self.env.context.get('default_project_id')
        if not project_id:
            return False
        return self.stage_find(project_id, [('fold', '=', False)])

    @api.model
    def _default_company_id(self):
        if self._context.get('default_project_id'):
            return self.env['project.project'].browse(self._context['default_project_id']).company_id
        return self.env['res.company']._company_default_get()

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = [('id', 'in', stages.ids)]
        if 'default_project_id' in self.env.context:
            search_domain = ['|', ('project_ids', '=', self.env.context['default_project_id'])] + search_domain

        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    @api.model
    def get_empty_list_help(self, help):
        tname = _("requerimiento")
        project_id = self.env.context.get('default_project_id', False)
        if project_id:
            name = self.env['project.project'].browse(project_id).label_requerimientos
            if name: tname = name.lower()

        self = self.with_context(
            empty_list_help_id=self.env.context.get('default_project_id'),
            empty_list_help_model='project.project',
            empty_list_help_document_name=tname,
        )
        return super(Requerimiento, self).get_empty_list_help(help)
