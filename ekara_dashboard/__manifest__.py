{
    'name':'Ekara Dashboard',
    'version':'17.0.1.0',
    'author': 'Deekshith',
    'depends':['hr','web','hr_contract','hr_appraisal'],
    'data':[
        'security/ir.model.access.csv',
        'views/hr_dashboard_views.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'ekara_dashboard/static/src/js/hr_dashboard.js',
            'ekara_dashboard/static/src/xml/hr_dashboard.xml',
            'ekara_dashboard/static/src/scss/hr_dashboard.scss',
        ],
    },

    'installable':True,
    'application':True,
}