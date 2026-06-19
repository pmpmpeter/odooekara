{
    "name": "Device Attendance Sync",
    "version": "1.0",
    "depends": ["hr_attendance",'mail'],
    "data": [
        "security/ir.model.access.csv",
        "views/device_log_view.xml",
        "views/wizard_view.xml",
        "views/menu.xml",
    ],
    "installable": True,
}