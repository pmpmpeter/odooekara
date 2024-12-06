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
        'hr_extended',
        'account',
        'project',
    ],
    'data': [
        'views/project_project_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
