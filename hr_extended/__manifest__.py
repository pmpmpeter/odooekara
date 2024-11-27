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
        'project',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'report/pre_emp_check_report.xml',
        'report/employee_indent_report.xml',
        'report/salary_breakup_report.xml',
        'data/sequence.xml',
        'data/job_levels_demo.xml',
        'data/mail_template_data.xml',
        'wizard/mail_activity_schedule_views.xml',
        'views/hr_config.xml',       
        'views/recruitment_config.xml',        
        'views/employee_indent_view.xml',
        'views/hr_applicant.xml',
        'views/recruitment_config.xml',
        'views/applicant_recruitment_invitation.xml',
        'views/pre_emp_check.xml',
        'views/project_project_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
