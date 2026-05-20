from odoo import models, api

class HrDashboard(models.AbstractModel):

    _name='hr.dashboard'

    @api.model
    def get_dashboard_data(self):

        Employee=self.env['hr.employee']

        total=Employee.search_count([])

        male=Employee.search_count(
            [('gender','=','male')]
        )

        female=Employee.search_count(
            [('gender','=','female')]
        )

        departments=[]

        data=Employee.read_group(
            [],
            ['department_id'],
            ['department_id']
        )

        for d in data:

            if d['department_id']:

                departments.append({

                    'id':d['department_id'][0],
                    'name':d['department_id'][1],
                    'count':d['department_id_count']

                })

        return{

            'headcount':total,
            'male':male,
            'female':female,
            'department':departments,
            'attrition':0

        }