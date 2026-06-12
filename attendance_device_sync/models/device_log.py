import requests

from odoo import api, fields, models
from odoo.exceptions import UserError


class DeviceLog(models.Model):
    _name = "device.log"
    _description = "Biometric Device Log"
    _order = "log_datetime desc"

    user_id = fields.Char(required=True, index=True)
    log_datetime = fields.Datetime(required=True, index=True)
    serial_number = fields.Char()
    device_name = fields.Char()
    processed = fields.Boolean(default=False)

    _sql_constraints = [
        (
            "unique_device_log",
            "unique(user_id, log_datetime, serial_number)",
            "Duplicate device log found."
        )
    ]

    @api.model
    def import_logs_from_api(self, sync_date):
        """
        Import logs for selected date
        """

        url = "https://sohcm.com/SmartApp_ess/api/SwipeDetails/GetDeviceLogs"

        params = {
            "APIKey": "285411042616",
            "AccountName": "ekaraglobe",
            "FromDate": sync_date.strftime("%Y-%m-%d"),
            "ToDate": sync_date.strftime("%Y-%m-%d"),
        }

        try:
            response = requests.get(
                url,
                params=params,
                timeout=60
            )

            response.raise_for_status()

            data = response.json()

        except Exception as e:
            raise UserError(str(e))

        imported = 0

        for row in data:

            user_id = row.get("UserId")
            log_date = row.get("LogDate")

            if not user_id or not log_date:
                continue

            log_datetime = log_date.replace("T", " ")

            existing = self.search([
                ("user_id", "=", user_id),
                ("log_datetime", "=", log_datetime),
                ("serial_number", "=", row.get("SerialNumber")),
            ], limit=1)

            if existing:
                continue

            self.create({
                "user_id": user_id,
                "log_datetime": log_datetime,
                "serial_number": row.get("SerialNumber"),
                "device_name": row.get("DeviceSName"),
            })

            imported += 1

        return imported