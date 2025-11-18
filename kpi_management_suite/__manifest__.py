{
    'name': "Suite de Gestión y Evaluación de KPIs",
    'summary': 'Herramienta integral para medir rendimiento semanal, tareas y avance de certificaciones por colaborador.',
    'description': """
        Módulo de Gestión de Desempeño y KPIs (Key Performance Indicators).
        Incluye tres segmentos de gestión para una evaluación completa del talento:
        1.  Evaluación Semanal Interna (Puntualidad, Imagen, Limpieza, Agenda).
        2.  Seguimiento de Tareas y Proyectos con puntuación de calidad (Escala 1-10).
        3.  Control de Avance de Cursos y Certificaciones.
        Incluye un Tablero de Mando (Dashboard) totalmente gráfico y responsive.
    """,
    'version': '17.0.1.0.0',
    'category': 'Human Resources/Productivity',
    'author': "Carlos Ramos", # Nombre de tu empresa comercial
    'website': "https://github.com/cramosmartinez", 
    'license': 'AGPL-3',
    'currency': 'USD',
    'price': 10, # Precio inicial
    
    # Dependencias obligatorias para RRHH, Chat, y el Dashboard
    'depends': ['base', 'hr', 'mail', 'board'],
    
    'data': [
        'security/ir.model.access.csv',
        'views/kpi_views.xml',
        'views/kpi_dashboard.xml', 
        'views/kpi_menu.xml',
    ],
    
    'installable': True,
    'application': True,
}