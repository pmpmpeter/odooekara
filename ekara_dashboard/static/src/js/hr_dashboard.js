/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class EkaraDashboard extends Component {

    setup() {

        this.orm = useService("orm");
        this.action = useService("action");

        this.state = useState({
            headcount: 0,
            male: 0,
            female: 0,
            attrition: 0,
            department: [],
        });

        onWillStart(async () => {

            const result = await this.orm.call(
                "hr.dashboard",
                "get_dashboard_data",
                []
            );

            Object.assign(this.state, result);

        });
    }


    openEmployees() {

        this.action.doAction({

            type: "ir.actions.act_window",

            name: "Employees",

            res_model: "hr.employee",

            view_mode: "tree,form",

            views: [
                [false, "tree"],
                [false, "form"]
            ],

            target: "current",

            domain: []

        });

    }


    openMaleEmployees() {

        this.action.doAction({

            type: "ir.actions.act_window",

            name: "Male Employees",

            res_model: "hr.employee",

            view_mode: "tree,form",

            views: [
                [false, "tree"],
                [false, "form"]
            ],

            target: "current",

            domain: [
                ['gender','=','male']
            ]

        });

    }


    openFemaleEmployees() {

        this.action.doAction({

            type: "ir.actions.act_window",

            name: "Female Employees",

            res_model: "hr.employee",

            view_mode: "tree,form",

            views: [
                [false, "tree"],
                [false, "form"]
            ],

            target: "current",

            domain: [
                ['gender','=','female']
            ]

        });

    }



    openAttrition() {

        this.action.doAction({

            type: "ir.actions.act_window",

            name: "Attrition Employees",

            res_model: "hr.employee",

            view_mode: "tree,form",

            views: [
                [false, "tree"],
                [false, "form"]
            ],

            target: "current",

            domain: [
                ['active','=',false]
            ]

        });

    }


    openDepartment(id){

    if (!this.action){
        return;
    }

    this.action.doAction({

        type:'ir.actions.act_window',

        name:'Department Employees',

        res_model:'hr.employee',

        view_mode:'tree,form',

        views:[
            [false,'tree'],
            [false,'form']
        ],

        domain:[
            ['department_id','=',id]
        ],

        target:'current'

    });

}

}

EkaraDashboard.template =
"ekara_dashboard.Dashboard";

registry.category("actions").add(
    "ekara_dashboard_tag",
    EkaraDashboard
);