from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import datetime 

# ===================================================================
# 1. KPI INTERNOS (Evaluación Semanal)
# ===================================================================

class KpiTemplate(models.Model):
    _name = 'kpi.template'
    _description = 'Plantilla de KPI Interno'

    name = fields.Char('Nombre KPI', required=True)
    description = fields.Text('Manual de Calificación')
    active = fields.Boolean('Activo', default=True)
    
    _sql_constraints = [('name_uniq', 'unique (name)', 'El nombre del KPI debe ser único.')]

class KpiEvaluationWeek(models.Model):
    _name = 'kpi.evaluation.week'
    _description = 'Hoja de Evaluación Semanal'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Referencia', compute='_compute_name', store=True)
    employee_id = fields.Many2one('hr.employee', string="Colaborador", required=True, tracking=True)
    date_start = fields.Date('Fecha Inicio (Lunes)', required=True, default=fields.Date.today)
    date_end = fields.Date('Fecha Fin (Viernes)', required=True)
    line_ids = fields.One2many('kpi.evaluation.line', 'week_id', string="Líneas")
    
    final_average = fields.Float(string="Promedio Semanal", compute='_compute_final_average', store=True, digits=(16, 4))
    state = fields.Selection([('draft', 'Borrador'), ('done', 'Validado'), ('cancel', 'Cancelado')], default='draft', string="Estado", tracking=True)

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
        if self.state != 'draft': return
        templates = self.env['kpi.template'].search([('active', '=', True)])
        existing = self.line_ids.mapped('kpi_id')
        vals = [{'week_id': self.id, 'kpi_id': t.id} for t in templates if t not in existing]
        if vals: self.env['kpi.evaluation.line'].create(vals)

    def action_validate(self): self.write({'state': 'done'})
    def action_cancel(self): self.write({'state': 'cancel'})
    def action_reset_to_draft(self): self.write({'state': 'draft'})

class KpiEvaluationLine(models.Model):
    _name = 'kpi.evaluation.line'
    _description = 'Línea de Evaluación Diaria'

    week_id = fields.Many2one('kpi.evaluation.week', required=True, ondelete='cascade')
    kpi_id = fields.Many2one('kpi.template', required=True)
    
    score_monday = fields.Float("Lun", default=1.0, digits=(16, 2))
    score_tuesday = fields.Float("Mar", default=1.0, digits=(16, 2))
    score_wednesday = fields.Float("Mié", default=1.0, digits=(16, 2))
    score_thursday = fields.Float("Jue", default=1.0, digits=(16, 2))
    score_friday = fields.Float("Vie", default=1.0, digits=(16, 2))
    weekly_average = fields.Float("Promedio", compute='_compute_avg', store=True, digits=(16, 2))

    @api.depends('score_monday', 'score_tuesday', 'score_wednesday', 'score_thursday', 'score_friday')
    def _compute_avg(self):
        for r in self:
            r.weekly_average = sum([r.score_monday, r.score_tuesday, r.score_wednesday, r.score_thursday, r.score_friday]) / 5.0

# ===================================================================
# 2. KPI TAREAS (Administrativo) - Escala 1-10
# ===================================================================

class KpiAdminTask(models.Model):
    _name = 'kpi.admin.task'
    _description = 'Gestión de Tareas y Proyectos'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    color = fields.Integer('Color Index', default=0)
    name = fields.Char('Nombre Tarea', required=True, tracking=True)
    employee_id = fields.Many2one('hr.employee', string="Asignado a", required=True, tracking=True)
    
    task_type = fields.Selection([
        ('cotizacion', 'Cotización'), ('posteo', 'Posteo'), ('desarrollo', 'Desarrollo'),
        ('soporte', 'Soporte'), ('otro', 'Otro')], string="Tipo", default='otro')
    
    state = fields.Selection([
        ('draft', 'Borrador'), ('in_progress', 'En Curso'), 
        ('complete', 'Completado'), ('overdue', 'Atrasado')], 
        string="Estado", default='draft', tracking=True, group_expand='_expand_states')

    # Puntuación 1-10
    score = fields.Integer(string='Puntuación (1-10)', default=0, tracking=True)
    score_percentage = fields.Float('Rendimiento %', compute='_compute_score_pct', store=True)

    date_deadline = fields.Date('Fecha Límite')
    date_completed = fields.Date('Fecha Completado')
    
    @api.model
    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    @api.constrains('score')
    def _check_score(self):
        for r in self:
            if r.score > 0 and not (1 <= r.score <= 10):
                raise ValidationError("La puntuación debe estar entre 1 y 10.")

    @api.depends('score')
    def _compute_score_pct(self):
        for r in self:
            r.score_percentage = r.score / 10.0 if r.score else 0.0

# ===================================================================
# 3. KPI CERTIFICACIONES (Cursos)
# ===================================================================

class KpiCourseLog(models.Model):
    _name = 'kpi.course.log'
    _description = 'Log de Avance de Curso'
    _order = 'date_log desc'

    course_id = fields.Many2one('kpi.course.tracking', required=True, ondelete='cascade')
    date_log = fields.Date('Fecha', default=fields.Date.today, required=True)
    progress_percentage = fields.Float('Avance Total (%)', required=True)
    notes = fields.Text('Notas')

class KpiCourseTracking(models.Model):
    _name = 'kpi.course.tracking'
    _description = 'Seguimiento de Certificaciones'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Nombre del Curso', required=True, tracking=True)
    employee_id = fields.Many2one('hr.employee', string="Colaborador", required=True)
    log_ids = fields.One2many('kpi.course.log', 'course_id', string="Historial")
    total_progress_percentage = fields.Float('Avance Global (%)', compute='_compute_progress', store=True)

    @api.depends('log_ids.progress_percentage')
    def _compute_progress(self):
        for r in self:
            r.total_progress_percentage = r.log_ids[0].progress_percentage if r.log_ids else 0.0