{
    'name': "HR Expense Extended",

    'description': """
        HR Expense Extended Functionality for Ekara
        
    """,
    'category': 'HR',
    'version': '17.1',
    'depends': [
        'base',
        'mail',
        'contacts',
        'hr',
        'hr_expense',
        'hr_recruitment',
        'hr_recruitment_extract',
        'account',
        'product',
        'sale',
        'project',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/payment_approval_config.xml',
        'views/payment_approval.xml',
        'views/payment_approval_report.xml'
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
