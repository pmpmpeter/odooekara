from datetime import timedelta

from odoo import fields, models


class AttendanceSyncWizard(models.TransientModel):
    _name = "attendance.sync.wizard"
    _description = "Attendance Sync Wizard"

    sync_date = fields.Date(
        required=True,
        default=fields.Date.today
    )

    def action_import_logs(self):

        count = self.env["device.log"].import_logs_from_api(
            self.sync_date
        )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Success",
                "message": f"{count} logs imported",
                "type": "success",
            },
        }

    def action_process_attendance(self):

        created = self.env[
            "attendance.sync"
        ].process_attendance(
            self.sync_date
        )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Success",
                "message": f"{created} attendances created",
                "type": "success",
            },
        }

