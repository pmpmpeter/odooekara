from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class KraMaster(models.Model):
    _name = "kra.master"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "KRA Master"

    name=fields.Char(string="Name")
    details_ids = fields.One2many('kra.details', 'kra_id', string="KRA Details")
    active = fields.Boolean(string="Active", default=True)

    @api.constrains('details_ids')
    def _check_details_weightage(self):
        for record in self:
            total_weightage = sum(line.weightage for line in record.details_ids)
            if total_weightage != 100:
                raise ValidationError(
                    f"The total weightage of KRA Master details must equal 100. Currently, it is {total_weightage}."
                )

    def unlink(self):
        """Check if the record is referenced before deletion."""
        related_fields = self.env['ir.model.fields'].search([
            ('ttype', 'in', ['many2one', 'many2many']),
            ('relation', '=', 'kra.master'),
        ])
        for record in self:
            for field in related_fields:
                model = self.env[field.model]
                if field.ttype == 'many2one':
                    references = model.search([(field.name, '=', record.id)])
                elif field.ttype == 'many2many':
                    references = model.search([(field.name, 'in', [record.id])])
                else:
                    continue

                if references:
                    model_name = self.env['ir.model']._get(field.model).name
                    referenced_ids = references.mapped('id')
                    raise ValidationError(
                        f"You cannot delete the record '{record.name}' as it is referenced in the model '{model_name}'."
                    )
        return super(KraMaster, self).unlink()


class KraDetails(models.Model):
    _name = "kra.details"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "KRA Details"

    kra_id = fields.Many2one('kra.master', string="KRA Master", ondelete='cascade')

    category = fields.Char(string="Category", required=True)
    business_unit = fields.Text(string="Business Unit")
    kra_type = fields.Char(string="KRA")
    goal_description = fields.Char(string="Goal Description")
    weightage = fields.Float(string="Weightage")

    @api.constrains('weightage')
    def _validate_weightage_values(self):
        for record in self:
            if record.weightage < 0:
                raise ValidationError("Negative values are not allowed for Weightage.")
