# -*- coding: utf-8 -*-
from collections import defaultdict
from contextlib import ExitStack, contextmanager
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from hashlib import sha256
from json import dumps
import logging
from markupsafe import Markup
from psycopg2 import OperationalError
import re
from textwrap import shorten
from unittest.mock import patch
import base64
from io import BytesIO
from odoo.tools.misc import xlsxwriter
from num2words import num2words
from odoo import api, fields, models, _, Command
from odoo.addons.base.models.decimal_precision import DecimalPrecision
from odoo.addons.account.tools import format_structured_reference_iso
from odoo.exceptions import UserError, ValidationError, AccessError, RedirectWarning
from odoo.tools import (
    date_utils,
    email_re,
    email_split,
    float_compare,
    float_is_zero,
    float_repr,
    format_amount,
    format_date,
    formatLang,
    frozendict,
    get_lang,
    groupby,
    index_exists,
    is_html_empty,
)

_logger = logging.getLogger(__name__)
import pdb

MAX_HASH_VERSION = 3

PAYMENT_STATE_SELECTION = [
    ('not_paid', 'Not Paid'),
    ('in_payment', 'In Payment'),
    ('paid', 'Paid'),
    ('partial', 'Partially Paid'),
    ('reversed', 'Reversed'),
    ('invoicing_legacy', 'Invoicing App Legacy'),
]

TYPE_REVERSE_MAP = {
    'entry': 'entry',
    'out_invoice': 'out_refund',
    'out_refund': 'entry',
    'in_invoice': 'in_refund',
    'in_refund': 'entry',
    'out_receipt': 'out_refund',
    'in_receipt': 'in_refund',
}

EMPTY = object()

BILL_APPR = ['in_invoice', 'in_receipt', 'in_refund']

class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    expense_type = fields.Selection([
    ("capex", "Capex"),
    ("opex", "Opex")], default='opex', string="Capex/Opex")
    expense_invoice_no = fields.Char(string="Tax/Proforma Invoice No")
    expense_invoice_type_id = fields.Many2one('invoice.type', string="Type of Invoice")
    expense_user_id = fields.Many2one('res.users', string="Requested By", default=lambda self: self.env.user)
    is_payment_approval = fields.Boolean(string="Is Payment Approval", default=False)