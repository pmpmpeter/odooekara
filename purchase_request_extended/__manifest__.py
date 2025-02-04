# -*- coding: utf-8 -*-
{
    'name': "Purchase Request Extended",

    'summary': """
        Purchase Request Extended of Purchase module for Ekara.""",

    'author': "NITS",
    'website': "http://www.navabrindsol.com",

    'category': 'purchase',
    'version': '0.1',

    'depends': [
        'base',
        'purchase_request',
        'account_budget',
    ],
    'data': [
        'views/purchase_request.xml',
    ],
    'license': 'LGPL-3',
}
