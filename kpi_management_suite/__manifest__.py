{
    'name': "Suite de Gestión de KPIs",
    'summary': 'Evaluación de Desempeño 360: Internos, Tareas y Certificaciones.',
    'description': """
        Solución integral para la gestión del rendimiento del talento humano.
        
        Módulos Incluidos:
        1. Evaluación Semanal (KPIs Internos): Medición de cumplimiento de normativas.
        2. Gestión de Tareas (Administrativo): Seguimiento de proyectos con escala de calidad 1-10.
        3. Plan de Carrera (Certificaciones): Tracking de avance en cursos.
        
        Incluye Tablero de Mando (Dashboard) totalmente gráfico y responsive.
    """,
    'version': '17.0.1.1', 
    'category': 'Human Resources',
    'author': "Carlos Ramos",
    'website': "https://github.com/cramosmartinez",
    'license': 'AGPL-3',
    'application': True,
    'installable': True,
    
   
    'price': 15.00,
    'currency': 'USD',
    
   
    'depends': ['base', 'hr', 'mail', 'board'],
    
   
    'images': ['static/description/cover.png'],
    
    
    'data': [
        'security/ir.model.access.csv',
        'views/kpi_views.xml',
        'views/kpi_dashboard.xml',
        'views/kpi_menu.xml',
    ],
}