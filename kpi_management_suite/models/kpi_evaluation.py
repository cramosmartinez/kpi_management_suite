from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import datetime 
import logging # <--- ¡CORREGIDO!

_logger = logging.getLogger(__name__)

# ===================================================================
# 1. KPI INTERNOS (Evaluación Semanal)
# ===================================================================

class KpiTemplate(models.Model):
    _name = 'kpi.template'
    _description = 'Plantilla de KPI Interno'

    name = fields.Char('Nombre KPI', required=True)
    description = fields.Text('Manual de Calificación (Descripción)')
    active = fields.Boolean('Activo', default=True)
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'El nombre del KPI debe ser único.')
    ]

class KpiEvaluationWeek(models.Model):
    _name = 'kpi.evaluation.week'
    _description = 'Hoja de Evaluación Semanal'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_default_dates(self):
        return fields.Date.today()

    name = fields.Char('Referencia', compute='_compute_name', store=True, readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Colaborador", required=True, tracking=True)
    date_start = fields.Date('Fecha Inicio (Lunes)', required=True, default=_get_default_dates)
    date_end = fields.Date('Fecha Fin (Viernes)', required=True)
    
    line_ids = fields.One2many('kpi.evaluation.line', 'week_id', string="Líneas de Evaluación")
    
    final_average = fields.Float(
        string="Promedio Semanal", 
        compute='_compute_final_average', 
        store=True,
        digits=(16, 4)
    )
    
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('done', 'Validado'),
        ('cancel', 'Cancelado')
    ], string='Estado', default='draft', tracking=True)

    @api.depends('employee_id', 'date_start')
    def _compute_name(self):
        for rec in self:
            if rec.employee_id and rec.date_start:
                rec.name = f"Semana {rec.date_start.isocalendar()[1]} - {rec.employee_id.name}"
            else:
                rec.name = "Nueva Evaluación"

    @api.onchange('date_start')
    def _onchange_date_start(self):
        if self.date_start:
            self.date_end = self.date_start + datetime.timedelta(days=4)
        else:
            self.date_end = False

    @api.depends('line_ids.weekly_average')
    def _compute_final_average(self):
        for week in self:
            lines = week.line_ids.filtered(lambda l: l.kpi_id.active)
            if not lines:
                week.final_average = 0.0
                continue
            week.final_average = sum(lines.mapped('weekly_average')) / len(lines)

    def action_load_kpi_templates(self):
        self.ensure_one()
        if self.state != 'draft':
            raise UserError("Solo se pueden cargar KPIs en estado Borrador.")

        templates = self.env['kpi.template'].search([('active', '=', True)])
        existing_kpis = self.line_ids.mapped('kpi_id')

        vals_list = []
        for template in templates.filtered(lambda t: t not in existing_kpis):
            vals_list.append({
                'week_id': self.id,
                'kpi_id': template.id,
            })
        
        if vals_list:
            self.env['kpi.evaluation.line'].create(vals_list)
        return True

    def action_validate(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})


class KpiEvaluationLine(models.Model):
    _name = 'kpi.evaluation.line'
    _description = 'Línea de Evaluación de KPI (Diaria)'

    week_id = fields.Many2one('kpi.evaluation.week', string="Semana de Evaluación", ondelete='cascade', required=True)
    kpi_id = fields.Many2one('kpi.template', string="KPI (Métrica)", required=True)
    
    score_monday = fields.Float(string="Lunes", default=1.0, digits=(16, 4))
    score_tuesday = fields.Float(string="Martes", default=1.0, digits=(16, 4))
    score_wednesday = fields.Float(string="Miércoles", default=1.0, digits=(16, 4))
    score_thursday = fields.Float(string="Jueves", default=1.0, digits=(16, 4))
    score_friday = fields.Float(string="Viernes", default=1.0, digits=(16, 4))

    weekly_average = fields.Float(
        string="Promedio Semanal", 
        compute='_compute_weekly_average', 
        store=True,
        digits=(16, 4)
    )

    @api.depends('score_monday', 'score_tuesday', 'score_wednesday', 'score_thursday', 'score_friday')
    def _compute_weekly_average(self):
        for line in self:
            scores = [
                line.score_monday,
                line.score_tuesday,
                line.score_wednesday,
                line.score_thursday,
                line.score_friday
            ]
            line.weekly_average = sum(scores) / 5.0

# ===================================================================
# 2. KPI TAREAS (Administrativo) - Escala 1-10
# ===================================================================

class KpiAdminTask(models.Model):
    _name = 'kpi.admin.task'
    _description = 'KPI Módulo 1: Tareas y Proyectos (Administración)'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    color = fields.Integer(string='Color Index', default=0)
    name = fields.Char('Nombre de Tarea / Proyecto', required=True, tracking=True)
    employee_id = fields.Many2one('hr.employee', string="Colaborador Asignado", required=True, tracking=True)
    
    task_type = fields.Selection([
        ('cotizacion', 'Cotización'),
        ('posteo', 'Posteo'),
        ('desarrollo', 'Desarrollo'),
        ('soporte', 'Soporte'),
        ('otro', 'Otro'),
    ], string="Tipo de Tarea", default='otro')

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('in_progress_adv', 'En curso (Avanzado)'),
        ('in_progress_int', 'En curso (Intermedio)'),
        ('in_progress_bsc', 'En curso (Básico)'),
        ('complete', 'Completo'),
        ('overdue', 'Atrasado'),
        ('cancel', 'Cancelado'),
    ], string="Estado", default='draft', tracking=True, group_expand='_expand_states')

    # Puntuación escala 1-10
    score = fields.Integer(
        string='Puntuación Final (1-10)',
        default=0,
        help="Calificación de la calidad y el impacto de la tarea (1: Muy bajo, 10: Excelente)."
    )

    # Campo calculado de rendimiento (0.0 a 1.0 para gráficos)
    score_percentage = fields.Float(
        string='Rendimiento (%)',
        compute='_compute_score_percentage',
        store=True,
        digits=(16, 2)
    )

    date_assigned = fields.Date('Fecha Asignación', default=fields.Date.today)
    date_deadline = fields.Date('Fecha Límite')
    date_completed = fields.Date('Fecha Completado')
    
    @api.model
    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    @api.constrains('score')
    def _check_score_range(self):
        """Restringe la puntuación a un rango de 1 a 10 si ha sido calificada."""
        for record in self:
            if record.score > 0 and not (1 <= record.score <= 10):
                raise ValidationError("La Puntuación Final debe estar en el rango de 1 a 10.")
    
    @api.depends('score')
    def _compute_score_percentage(self):
        for record in self:
            record.score_percentage = record.score / 10.0 if record.score else 0.0

# ===================================================================
# 3. KPI CURSOS (Certificación) - Con Semáforo y Validaciones
# ===================================================================

class KpiCourseLog(models.Model):
    _name = 'kpi.course.log'
    _description = 'Registro Diario de Avance de Curso'
    _order = 'date_log desc, create_date desc'

    course_id = fields.Many2one('kpi.course.tracking', string="Curso", ondelete='cascade', required=True)
    employee_id = fields.Many2one(related='course_id.employee_id', store=True, readonly=True, string="Colaborador")

    date_log = fields.Date('Fecha de Reporte', required=True, default=fields.Date.today)
    report_upload_time = fields.Datetime('Hora de Subida del Reporte', default=fields.Datetime.now, readonly=True)
    last_class_info = fields.Char('Clase en que se quedó', help="Ej: Sección 10, Clase 152")
    progress_percentage = fields.Float('Porcentaje de Avance Total (%)')
    notes = fields.Text('Notas / Comentarios')


class KpiCourseTracking(models.Model):
    _name = 'kpi.course.tracking'
    _description = 'KPI Módulo 3: Seguimiento de Cursos'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Nombre del Curso', required=True, tracking=True, 
                       help="Ej. React: De cero a experto")
    employee_id = fields.Many2one('hr.employee', string="Colaborador", required=True, tracking=True)
    
    # SEMÁFORO: Verde, Amarillo, Rojo
    state = fields.Selection([
        ('on_track', 'En Tiempo (Verde)'),
        ('late', 'Entrega Tarde (Amarillo)'),
        ('at_risk', 'No Entregado (Rojo)'),
    ], string="Estado de Entrega", default='at_risk', tracking=True)
    
    log_ids = fields.One2many('kpi.course.log', 'course_id', string="Registros Diarios")

    total_progress_percentage = fields.Float(
        string="Progreso Total (%)",
        compute='_compute_total_progress',
        store=True,
        help="Porcentaje de avance total del curso"
    )

    @api.depends('log_ids.progress_percentage')
    def _compute_total_progress(self):
        for course in self:
            if course.log_ids:
                latest_log = course.log_ids.sorted('date_log', reverse=True)[0]
                course.total_progress_percentage = latest_log.progress_percentage
                
                # Automatización opcional: Si hay avance, cambiar a verde
                if course.total_progress_percentage > 0 and course.state == 'at_risk':
                    course.state = 'on_track'
            else:
                course.total_progress_percentage = 0.0