{
    "name": "Partial Payment Adjustment",
    'version': '17.0.5.4.3',
    "description": """
        Partial Payment Adjustment.
    """,
    'price': 100,
    'currency': 'USD',
    'license': 'OPL-1',
    "author" : "Navabrind IT Solutions Pvt Ltd -Bhuvaneswari",
    'sequence': 1,
    "email": 'bhuvaneswari.b@navabrindit.com',
    "website":'https://navabrindsol.com/',
    'category':"Accounting",
    'summary':"Partial Payment Adjustment",
    "depends": [
        "account",
        "account_accountant",
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/partial_payment.xml'
    ],
    'css': [],
    'js': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}

