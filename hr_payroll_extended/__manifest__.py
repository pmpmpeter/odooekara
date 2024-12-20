{
    'name': 'Employee Payroll Integration',
    'version': '17.0',
    'category': 'Human Resources',
    'summary': 'Integrate custom employee fields with the hr_payroll module.',

    'author': 'Your Company',
    'depends': [
        'hr',
        'hr_payroll', 'report_xlsx',
        'base',
    ],
    'data': [
        'reports/payroll_for_the_month.xml',
        'views/hr_payslip.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
