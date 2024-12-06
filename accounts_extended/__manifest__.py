{
    'name': 'Accounts Extended',
    'version': '1.0',
    'category': 'Accounting',
    'description': """ 
        Extended functionality of Accounts for Ekara""",
    'author': 'NITS',
    'website': 'https://www.navabrindsol.com/',
    'depends': [
        'base',
        'account',
        'account_accountant',
        'analytic',
        'sale',
        'l10n_in',
        'l10n_in_reports_gstr',
        'hr_expense_extended',
        'payment',
    ],
    'data': [
        'views/account_move.xml',
    ],
    'license': 'LGPL-3',

}
