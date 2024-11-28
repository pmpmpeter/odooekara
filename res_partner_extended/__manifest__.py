{
    'name': 'Res Partner Extended for Ekara',
    'category': 'Partner',
    'author': "NITS",
    'website': "www.navabrindsol.com",
    'version': '17.0',
    'description': "NITS Address Book",
    'depends': ['base','contacts','sale','purchase'],
    'data': [
        "security/security.xml",
        # "security/ir.model.access.csv",
        "views/res_partner.xml",
        
    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
