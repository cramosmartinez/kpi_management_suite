{
    'name': "KPI Management & Performance Suite",
    'summary': '360° Evaluation: Weekly KPIs, Tasks Quality (1-10) & Certifications Tracking.',
    'description': """
        Comprehensive HR Solution for Talent Performance Management.
        
        Key Features:
        1. **Weekly Internal KPIs:** Track punctuality, presentation, and compliance.
        2. **Task Management (Admin):** Project tracking with a simplified 1-10 Quality Scale.
        3. **Career Path (Certifications):** Course progress tracking with Traffic Light status (Green/Yellow/Red).
        
        Includes a fully **Responsive Executive Dashboard** for real-time analysis.
    """,
    'version': '17.0.1.6.0', # Subí la versión
    'category': 'Human Resources',
    'author': "Carlos Ramos", # Tu nombre o empresa
    'website': "github.com/cramosmartinez", 
    'license': 'AGPL-3',
    'application': True,
    'installable': True,
    
    # Configuración de Venta
    'price': 15.00,
    'currency': 'USD',
    
    'depends': ['base', 'hr', 'mail', 'board'],
    
    # Imágenes
    'images': ['static/description/cover.png'],
    
    'data': [
        'security/ir.model.access.csv',
        'views/kpi_views.xml',
        'views/kpi_dashboard.xml',
        'views/kpi_menu.xml',
    ],
}