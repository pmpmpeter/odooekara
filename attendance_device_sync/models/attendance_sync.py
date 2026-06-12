from collections import defaultdict
from datetime import datetime, time, timedelta

from odoo import models
import logging

_logger = logging.getLogger(__name__)

class AttendanceSync(models.AbstractModel):
    _name = "attendance.sync"
    _description = "Attendance Sync Mixin"

    def process_attendance(self, sync_date):

        attendance_obj = self.env["hr.attendance"]
        employee_obj = self.env["hr.employee"]
        device_log_obj = self.env["device.log"]

        start_dt = datetime.combine(sync_date, time.min)
        end_dt = start_dt + timedelta(days=1)

        logs = device_log_obj.search([
            ("processed", "=", False),
            ("log_datetime", ">=", start_dt),
            ("log_datetime", "<", end_dt),
        ])

        if not logs:
            return 0

        grouped = defaultdict(list)

        for log in logs:
            grouped[log.user_id].append(log)

        created = 0

        for user_id, user_logs in grouped.items():

            # sort swipe times
            user_logs = sorted(
                user_logs,
                key=lambda rec: rec.log_datetime
            )

            employee = employee_obj.search(
                [("employee_number", "=", user_id)],
                limit=1
            )

            if not employee:
                _logger.warning(
                    "Employee not found for device user %s",
                    user_id
                )
                continue

            check_in = user_logs[0].log_datetime
            check_out = user_logs[-1].log_datetime

            existing_attendance = attendance_obj.search([
                ("employee_id", "=", employee.id),
                ("check_in", "=", check_in),
            ], limit=1)

            if not existing_attendance:
                attendance_obj.create({
                    "employee_id": employee.id,
                    "check_in": check_in,
                    "check_out": check_out,
                })

                created += 1

            # mark logs processed
            device_log_obj.browse(
                [log.id for log in user_logs]
            ).write({
                "processed": True
            })

        return created