# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _


class MailActivitySchedule(models.TransientModel):
    _inherit = 'mail.activity.schedule'
   

    
    def action_create_task(self):
        print(self.res_ids,"================")
        project_task_obj = self.env['project.task']
        project_obj = self.env['project.project']
        context = self.env.context
        # emp_ids = self.env['hr.employee'].(2)
        emp_ids = self.env['hr.employee'].search([('id','=',context.get('active_id'))])
        print(emp_ids,"--------------------------------")
        task_ids = project_task_obj.search([('project_id.is_a_master','=',True),('project_id.department_id','in',emp_ids.mapped('department_id').ids),('display_in_project','=',True)])
        for emp_id in emp_ids:
            project_id = project_obj.create({
                        'name': emp_id.name+' On-boarding for '+emp_id.department_id.name,
                        'display_name': emp_id.name+' On-boarding for '+emp_id.department_id.name,
                        'label_tasks': 'On-boarding Tasks',
                        'user_id':emp_id.user_id.id
                })         
            for task_id in task_ids:
                task = project_task_obj.create({
                        'name':task_id.name,
                        'project_id':project_id.id,
                        'user_ids':project_id.user_id.ids,
                    })
                for sub_task_id in task_id.child_ids:
                    project_task_obj.create({
                        'name':sub_task_id.name,
                        'parent_id':task.id,
                        'project_id':project_id.id,
                        'user_ids':project_id.user_id.ids,
                        'display_in_project':False,
                    })
        return True
