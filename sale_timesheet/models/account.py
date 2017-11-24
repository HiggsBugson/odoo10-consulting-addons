
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models
from odoo.exceptions import ValidationError
import logging
logger = logging.getLogger(__name__)

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.model
    def create(self, values):
        if values.get('task_id'):
            task = self.env['project.task'].browse(values['task_id'])
            values['so_line'] = task.sale_line_id.id or values.get('so_line', False)
        values.update(self._get_timesheet_cost(values))
        return super(AccountAnalyticLine, self).create(values)

    @api.multi
    def write(self, values):
        so_lines = self.mapped('so_line')
        if values.get('task_id'):
            task = self.env['project.task'].browse(values['task_id'])
            values['so_line'] = task.sale_line_id.id or values.get('so_line', False)
        for line in self:
            values.update(line._get_timesheet_cost(values))
            super(AccountAnalyticLine, line).write(values)

        # Update delivered quantity on SO lines which are not linked to the analytic lines anymore
        so_lines -= self.mapped('so_line')
        if so_lines:
            so_lines.with_context(force_so_lines=so_lines).sudo()._compute_analytic()
        return True

    def _get_timesheet_cost(self, values):
        values = values if values is not None else {}
        if values.get('project_id') or self.project_id:
            if values.get('amount'):
                return {}
            unit_amount = values.get('unit_amount', 0.0) or self.unit_amount
            user_id = values.get('user_id') or self.user_id.id or self._default_user()
            user = self.env['res.users'].browse([user_id])
            emp = self.env['hr.employee'].search([('user_id', '=', user_id)], limit=1)
            cost = emp and emp.timesheet_cost or 0.0
            uom = (emp or user).company_id.project_time_mode_id
            # Nominal employee cost = 1 * company project UoM (project_time_mode_id)
            return {
                'amount': -unit_amount * cost,
                'product_uom_id': uom.id,
                'account_id': values.get('account_id') or self.account_id.id or emp.account_id.id,
            }
        return {}

    def _get_sale_order_line(self, vals=None):
        result = dict(vals or {})
        if self.project_id:
            #IF THERE IS NO SALE ORDER, GET COST PRICE FROM PRODUCT
            so = self.env['sale.order'].search([('project_id','=',self.account_id.id)])
            if not so:
                #result.update(self._get_timesheet_cost(result))
                if result.get('amount')==0.0:
                	result.update({'amount' : -result.get('unit_amount')*(self.env['product.template'].search([('id','=',result.get('product_id'))])).standard_price})
                logger.error("ILJA DEBUG: %s", result )
                return super(AccountAnalyticLine, self)._get_sale_order_line(vals=result)
            #IF THERE IS A SALE ORDER GET DATA FROM THE SALE_ORDER LINES MENTIONING CURRENT PRODUCT
            if result.get('so_line'):
                sol = self.env['sale.order.line'].browse([result['so_line']])
            else:
                sol = self.so_line
            if not sol:
                lines = self.env['sale.order.line'].search([
                    ('order_id.project_id', '=', self.account_id.id),
                    ('state', 'in', ('sale', 'done')),
                    ('product_id.track_service', '=', 'timesheet'),
                    ('product_id.type', '=', 'service')])
                for line in lines:
                    if line.product_id.id == vals['product_id']:
                       sol = line
            if sol:
                result.update({
                    'so_line': sol.id,
                    'product_id': sol.product_id.id,
                    'amount': -(sol.product_id.standard_price)*result.get('unit_amount')
                })
                if result.get('amount')==-0.0:
                    result.update(self._get_timesheet_cost(result))
                logger.error("ILJA DEBUG2: %s",result)
            else:
               raise ValidationError("You can not record time on this project because your worktime product can not be found in the Sale Order.")
        return super(AccountAnalyticLine, self)._get_sale_order_line(vals=result)
