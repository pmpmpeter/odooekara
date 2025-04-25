# -*- coding: utf-8 -*-
{
    'name': "Purchase Order Extended",

    'summary': """
        Purchase Order Extended of Purchase module for Ekara.""",

    'author': "NITS",
    'website': "http://www.navabrindsol.com",

    'category': 'purchase',
    'version': '0.1',

    'depends': [
        'base',
        'purchase',
        'purchase_stock',
        'stock',
        'l10n_in',
        'l10n_in_purchase',
        'purchase_requisition',
        'account',
        'account_budget',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizard/po_matrix_approve_reason.xml',
        'views/purchase_order.xml',
        'views/res_config_settings.xml',
        'views/stock_lot.xml',
	'views/purchase_order_type.xml',
    ],
    'license': 'LGPL-3',
}
