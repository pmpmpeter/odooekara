# -*- coding: utf-8 -*-
{
    'name': "employee_indent",

    'category': 'Human Resources/Recruitment',
    'version': '0.1',

    'depends': ['base', 'hr'],

    'data': [
        'security/ir.model.access.csv',
        'views/employee_indent_view_form.xml',
        'views/job_levels_master.xml',
        'views/position_name_master.xml',
    ],

    'demo': [
        'data/job_levels_demo.xml',
    ]

}
