{
    'name': "Project Extended",

    'description': """
        Project Extended Functionality for Ekara
        
    """,
    'category': 'Project',
    'version': '17.1',
    'depends': [
        'base',
        'mail',
        'contacts',
        'hr',
        'hr_recruitment',
        'account',
        'project',
        'hr_extended',
    ],
    'data': [
        'security/project_security.xml',
        'views/project_project_views.xml',
        'data/mail_template_data.xml',
        'data/project_cron.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
