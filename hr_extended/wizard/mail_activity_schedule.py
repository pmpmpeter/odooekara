# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _


class MailActivitySchedule(models.TransientModel):
    _inherit = 'mail.activity.schedule'

    def action_create_task(self):
        print(self.res_ids, "================")
        project_task_obj = self.env['project.task']
        project_obj = self.env['project.project']
        context = self.env.context

        # Fetch the employee based on active_id
        emp_ids = self.env['hr.employee'].search([('id', '=', context.get('active_id'))])
        print(emp_ids, "--------------------------------")

        # Create the project for the employee's onboarding
        for emp_id in emp_ids:
            project_id = project_obj.create({
                'name': emp_id.name + ' On-boarding for ' + emp_id.department_id.name,
                'display_name': emp_id.name + ' On-boarding for ' + emp_id.department_id.name,
                'label_tasks': 'On-boarding Tasks',
                'user_id': emp_id.user_id.id,
            })

            # List of the 31 onboarding tasks
            task_names = [
                "Signing of Joining Documents",
                "Check if employee is Non-Indian national",
                "Creation of Employee Docket and uploading in HRMS Portal",
                "PF application form completion",
                "HR Policies overview to New Joinee/ Induction",
                "Update employee master data by HR",
                "Creation of opening leave balance by HR",
                "Welcome Note/ Org Announcement/All Employees",
                "Assign employee number",
                "Addition of team members to Unit Share space",
                "Welcome Kit- Stationery",
                "Work Station/ Desk/Location",
                "Photo ID",
                "Business Card",
                "Email ID creation (for TLE, add to TLE database)",
                "Email ID to be included to the DL Group",
                "HRMS ID",
                "System Allocation",
                "Bio Metrics access setup and Bio Metric ID link table",
                "System setup and Active Directory User creation for System Login (NA for TSA, BLR & Cbe)",
                "VPN Access creation (NA for TSA, BLR & Cbe)",
                "UAN number & KYC approval for UAN Portal & (Collect Form 11 of PF Act - only for TSA, BLR)",
                "Send Tax Information packet to Employee by HR",
                "Background Check/ Report Submission & Evaluation",
                "Bank Account opening",
                "Issue ESI Card, if applicable",
                "Send employee details to Insurer for Coverage under GMC & GPA",
                "OPTIONAL- Send Dependent Parent Details to Insurer for coverage under Group Health Insurance",
                "Send Insurance E-card to employee",
                "KRA Form to be sent to Employee by Reporting Manager",
                "To close"
            ]

            # Create individual tasks for each of the 31 tasks
            for task_name in task_names:
                task = project_task_obj.create({
                    'name': task_name,
                    'project_id': project_id.id,
                    'user_ids': [(6, 0, [emp_id.user_id.id])],  # Assigning the task to the employee's manager
                    'display_in_project': True,
                })

        return True