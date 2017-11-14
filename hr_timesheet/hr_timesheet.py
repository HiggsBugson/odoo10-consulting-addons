# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    task_id = fields.Many2one('project.task', 'Task')
    project_id = fields.Many2one('project.project', 'Project', domain=[('allow_timesheets', '=', True)])
    department_id = fields.Many2one('hr.department', "Department", related='user_id.employee_ids.department_id', store=True, readonly=True)

    @api.onchange('project_id')
    def onchange_project_id(self):
        self.task_id = False

    @api.model
    def create(self, vals):
        if vals.get('project_id'):
            project = self.env['project.project'].browse(vals.get('project_id'))
            vals['account_id'] = project.analytic_account_id.id
            user_resource = self.env['resource.resource'].search([('user_id','=',self.env.uid)])
            employee = self.env['hr.employee'].search([('resource_id','=',user_resource.id)])
            vals['product_id'] = employee.timesheet_product.id
        return super(AccountAnalyticLine, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('project_id'):
            project = self.env['project.project'].browse(vals.get('project_id'))
            vals['account_id'] = project.analytic_account_id.id
            user_resource = self.env['resource.resource'].search([('user_id','=',self.env.uid)])
            employee = self.env['hr.employee'].search([('resource_id','=',user_resource.id)])
            vals['product_id'] = employee.timesheet_product.id
        return super(AccountAnalyticLine, self).write(vals)
