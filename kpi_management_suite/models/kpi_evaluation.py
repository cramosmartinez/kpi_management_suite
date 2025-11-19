from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import datetime 
import logging

_logger = logging.getLogger(__name__)

# ===================================================================
# 1. WEEKLY EVALUATION (INTERNAL)
# ===================================================================

class KpiTemplate(models.Model):
    _name = 'kpi.template'
    _description = 'KPI Internal Template'

    name = fields.Char('KPI Name', required=True)
    description = fields.Text('Grading Manual (Description)')
    active = fields.Boolean('Active', default=True)
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The KPI name must be unique.')
    ]

class KpiEvaluationWeek(models.Model):
    _name = 'kpi.evaluation.week'
    _description = 'Weekly Evaluation Sheet'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_default_dates(self):
        return fields.Date.today()

    name = fields.Char('Reference', compute='_compute_name', store=True, readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, tracking=True)
    date_start = fields.Date('Start Date (Mon)', required=True, default=_get_default_dates)
    date_end = fields.Date('End Date (Fri)', required=True)
    
    line_ids = fields.One2many('kpi.evaluation.line', 'week_id', string="Evaluation Lines")
    
    final_average = fields.Float(
        string="Weekly Average", 
        compute='_compute_final_average', 
        store=True,
        digits=(16, 4)
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Validated'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    @api.depends('employee_id', 'date_start')
    def _compute_name(self):
        for rec in self:
            if rec.employee_id and rec.date_start:
                rec.name = f"Week {rec.date_start.isocalendar()[1]} - {rec.employee_id.name}"
            else:
                rec.name = "New Evaluation"

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
            raise UserError("You can only load KPIs in Draft state.")

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
    _description = 'Daily KPI Line'

    week_id = fields.Many2one('kpi.evaluation.week', string="Weekly Sheet", ondelete='cascade', required=True)
    kpi_id = fields.Many2one('kpi.template', string="KPI Metric", required=True)
    
    score_monday = fields.Float(string="Mon", default=1.0, digits=(16, 4))
    score_tuesday = fields.Float(string="Tue", default=1.0, digits=(16, 4))
    score_wednesday = fields.Float(string="Wed", default=1.0, digits=(16, 4))
    score_thursday = fields.Float(string="Thu", default=1.0, digits=(16, 4))
    score_friday = fields.Float(string="Fri", default=1.0, digits=(16, 4))

    weekly_average = fields.Float(
        string="Average", 
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
# 2. TASK MANAGEMENT (ADMIN) - Score 1-10
# ===================================================================

class KpiAdminTask(models.Model):
    _name = 'kpi.admin.task'
    _description = 'Task & Project KPI'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    color = fields.Integer(string='Color Index', default=0)
    name = fields.Char('Task Name', required=True, tracking=True)
    employee_id = fields.Many2one('hr.employee', string="Assigned To", required=True, tracking=True)
    
    task_type = fields.Selection([
        ('cotizacion', 'Quotation'),
        ('posteo', 'Social Media'),
        ('desarrollo', 'Development'),
        ('soporte', 'Support'),
        ('otro', 'Other'),
    ], string="Task Type", default='otro')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress_adv', 'In Progress (Adv)'),
        ('in_progress_int', 'In Progress (Med)'),
        ('in_progress_bsc', 'In Progress (Basic)'),
        ('complete', 'Completed'),
        ('overdue', 'Overdue'),
        ('cancel', 'Cancelled'),
    ], string="Status", default='draft', tracking=True, group_expand='_expand_states')

    # Score 1-10
    score = fields.Integer(
        string='Quality Score (1-10)',
        default=0,
        help="Rate the task quality and impact from 1 (Low) to 10 (Excellent)."
    )

    # Computed Percentage for Graphs (0.0 - 1.0)
    score_percentage = fields.Float(
        string='Performance (%)',
        compute='_compute_score_percentage',
        store=True,
        digits=(16, 2)
    )

    date_assigned = fields.Date('Assigned Date', default=fields.Date.today)
    date_deadline = fields.Date('Deadline')
    date_completed = fields.Date('Completion Date')
    
    @api.model
    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    @api.constrains('score')
    def _check_score_range(self):
        for record in self:
            if record.score > 0 and not (1 <= record.score <= 10):
                raise ValidationError("The Quality Score must be between 1 and 10.")
    
    @api.depends('score')
    def _compute_score_percentage(self):
        for record in self:
            record.score_percentage = record.score / 10.0 if record.score else 0.0

# ===================================================================
# 3. CAREER PATH (Certifications) - Traffic Light
# ===================================================================

class KpiCourseLog(models.Model):
    _name = 'kpi.course.log'
    _description = 'Course Progress Log'
    _order = 'date_log desc, create_date desc'

    course_id = fields.Many2one('kpi.course.tracking', string="Course", ondelete='cascade', required=True)
    employee_id = fields.Many2one(related='course_id.employee_id', store=True, readonly=True, string="Employee")

    date_log = fields.Date('Report Date', required=True, default=fields.Date.today)
    report_upload_time = fields.Datetime('Upload Time', default=fields.Datetime.now, readonly=True)
    last_class_info = fields.Char('Last Class/Section', help="Ex: Section 10, Class 152")
    progress_percentage = fields.Float('Progress Reported (%)')
    notes = fields.Text('Notes / Comments')


class KpiCourseTracking(models.Model):
    _name = 'kpi.course.tracking'
    _description = 'Certification Tracking'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Course / Certification Name', required=True, tracking=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, tracking=True)
    
    # TRAFFIC LIGHT: Green, Yellow, Red
    state = fields.Selection([
        ('on_track', 'On Track (Green)'),
        ('late', 'Late Delivery (Yellow)'),
        ('at_risk', 'At Risk / Not Started (Red)'),
    ], string="Delivery Status", default='at_risk', tracking=True)
    
    log_ids = fields.One2many('kpi.course.log', 'course_id', string="Daily Logs")

    total_progress_percentage = fields.Float(
        string="Total Progress (%)",
        compute='_compute_total_progress',
        store=True
    )

    @api.depends('log_ids.progress_percentage')
    def _compute_total_progress(self):
        for course in self:
            if course.log_ids:
                latest_log = course.log_ids.sorted('date_log', reverse=True)[0]
                course.total_progress_percentage = latest_log.progress_percentage
                
                if course.total_progress_percentage > 0 and course.state == 'at_risk':
                    course.state = 'on_track'
            else:
                course.total_progress_percentage = 0.0