{
    'name': "Project Approval Extended",

    'description': """
        Project Extended Functionality for Ekara
        
    """,
    'category': 'Project Task Approval',
    'version': '17.1',
    'depends': [
        'project',
        'project_extended',
        'multi_level_approval_configuration',
    ],
    'data': [
        'views/project_task_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
