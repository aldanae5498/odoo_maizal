# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Project',
    'version': '1.1',
    'website': 'https://www.odoo.com/page/project-management',
    'category': 'Project',
    'sequence': 10,
    'summary': 'Organize and schedule your projects ',
    'depends': [
        'base_setup',
        'mail',
        'portal',
        'rating',
        'resource',
        'web',
        'web_tour',
        'digest',
    ],
    'description': "",
    'data': [
        'security/project_security.xml',
        'security/ir.model.access.csv',
        'report/project_report_views.xml',
        'views/digest_views.xml',
        'views/rating_views.xml',
        'views/project_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
        'views/mail_activity_views.xml',
        'views/project_assets.xml',
        'views/project_portal_templates.xml',
        'views/project_rating_templates.xml',
        # Requerimiento:
        'views/requerimiento.xml',
        'views/requerimiento_attachment.xml',
        # Requerimiento / Vistas Heredadas:
        'views/requerimiento_inherited_views.xml',        

        # Servicio:
        'views/servicio.xml',

        # Ciclo de Vida:
        'views/ciclo_vida.xml',

        'data/digest_data.xml',
        'data/project_mail_template_data.xml',
        'data/project_data.xml',
        # Requerimiento - Email Template:
        'data/et_nuevo_requerimiento.xml',
        'data/et_requerimiento_radicado.xml',
        'data/et_requerimiento_aprobado.xml',        
    ],
    'qweb': ['static/src/xml/project.xml'],
    'demo': ['data/project_demo.xml'],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
