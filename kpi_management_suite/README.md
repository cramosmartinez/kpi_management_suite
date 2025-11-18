# 🌟 Suite de Gestión de KPIs y Evaluación 360°  
### _Módulo para Odoo 17 – kpi_management_suite_

![Odoo Version](https://img.shields.io/badge/Odoo-17.0-purple.svg)
![License](https://img.shields.io/badge/License-AGPL--3-blue.svg)

**Una solución integral para medir desempeño, gestionar productividad y potenciar el crecimiento del talento humano dentro de Odoo.**

---

## 📌 Descripción General

La **Suite de Gestión de KPIs** transforma la forma en que tu organización evalúa el rendimiento, centralizando procesos que antes se manejaban en hojas de cálculo, formularios o sistemas externos.

Este módulo proporciona una vista completa del desempeño de cada colaborador mediante tres ejes integrados:

1. **Cumplimiento Interno:** seguimiento semanal de normativas y comportamiento.
2. **Productividad Administrativa:** control de tareas, calidad y avance operativo.
3. **Crecimiento Profesional:** progreso en cursos, habilidades y certificaciones.

Todo se visualiza en un **Dashboard Ejecutivo** moderno y responsivo que consolida métricas clave en tiempo real.

---

## 🚀 Características

### ⭐ 1. Dashboard Ejecutivo
- Diseño vertical y 100% responsive.
- Gráficos dinámicos: dona, barras apiladas y curvas de tendencia.
- Indicadores clave agregados por colaborador o por departamento.
- Comparativa visual de los tres segmentos de rendimiento.

### ⭐ 2. Gestión de Tareas y Calidad
- Escala simplificada **1–10**, con guía visual intuitiva.
- Indicadores de calidad por color.
- Flujo Kanban con estados personalizables.
- Validaciones para asegurar la consistencia de las calificaciones.

### ⭐ 3. Evaluación Semanal (KPIs Internos)
- Plantillas de evaluación personalizables.
- Promedios y consolidación automática.
- Historial completo de evaluaciones por colaborador.

### ⭐ 4. Plan de Carrera y Certificaciones
- Ranking de avance entre colaboradores.
- Registro cronológico del desarrollo profesional.
- Evolución porcentual de cursos y habilidades.

---

## 🧩 Módulos Requeridos

Asegúrate de tener instalados los siguientes módulos base de Odoo:

```
hr
mail
board
```

---

## 🛠 Instalación

1. Descarga o clona este repositorio dentro de la carpeta `addons` de tu instancia Odoo.
2. Reinicia el servidor:

```bash
./odoo-bin -c odoo.conf -u kpi_management_suite
```

3. En Odoo, ve al menú **Apps** y activa el módulo.
4. Configura tus plantillas desde:  
   **Gestión de Talento > Configuración > Plantillas KPI**

---

## ⚙️ Configuración Inicial

### Para comenzar a usar la suite:
1. Crea criterios de evaluación semanal (KPIs internos).  
2. Define proyectos o áreas para evaluar productividad.  
3. Registra cursos y certificados en el plan de carrera.  
4. Asigna responsables y colaboradores según la estructura de tu empresa.  

---

## 📸 Capturas de Pantalla  
*(Se mostrarán automáticamente cuando publiques el módulo en la Odoo App Store o agregues imágenes al repositorio)*

- Dashboard Integral  
- Vista de Tareas con escala de calidad  
- Kanban Productivo  
- Panel de Certificaciones  

---

## 📂 Estructura del Repositorio

```
kpi_management_suite/
│── models/
│── views/
│── security/
│── static/
│   └── description/
│── data/
│── __manifest__.py
│── README.md
```

---

## 👨‍💻 Autor y Soporte

**Desarrollado por:** Soluciones Empresariales  
**Contacto:** cramosmartinez5@gmail.com  

Para soporte, implementación o personalización, contáctanos y con gusto te ayudamos a adaptar la suite a las necesidades de tu empresa.
