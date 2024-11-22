{
    'name': "HR Extended",

    'description': """
        HR Extended Functionality for Ekara
        
    """,
    'category': 'HR',
    'version': '17.1',
    'depends': [
        'base',
        'mail',
        'contacts',
        'hr',
        'hr_recruitment',
        'hr_recruitment_extract',
        'account',
        'product',
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sequence.xml',
        # 'data/ir_cron.xml',
        'data/job_levels_demo.xml',
        'data/mail_template_data.xml',
        # 'data/ir_cron.xml',
        'views/recruitment_config.xml',
        'views/position_name_master.xml',
        'views/pre_emp_check.xml',
        'views/employee_indent_view_form.xml',
        'views/job_levels_master.xml',
        'views/hr_applicant_changes.xml',
        'views/recruitment_config.xml',
        'views/applicant_recruitment_invitation.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
