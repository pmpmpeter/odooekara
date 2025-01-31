# -*- coding: utf-8 -*-
{
    'name': "Document Access Management",

    'summary': "Document Access Management",

    'description': """
        The Document Access Management module enables smooth handling of documents 
        while implementing strong security measures to regulate user permissions and access control.
    """,
    'author': "NITS",
    'category': 'Hidden',
    'version': '0.1',
    'depends': ['base','mail'],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'report/document_report.xml',
        'report/ir_actions_report.xml',
        'data/ir_sequence_data.xml',
        'data/cron_data.xml',
        'views/document_view.xml',
        'views/document_request_view.xml',
        'views/menu_items.xml',
        'wizard/multi_download_reason_view.xml',
    ],
    
    'license': 'LGPL-3',
}
