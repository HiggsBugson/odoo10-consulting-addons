# odoo10-consulting-addons
Customized odoo10 modules for Service Companies

- Employee now has a timesheet_product used to record time (setup in Employee HR tab)
- Sale Orders now accept more than one timebased product
- Employees can record worktime from timesheet to SaleOrder/Project (product is chosen automatically)
- While recording worktime it is checked if the SO/Project allows this employee to use his timesheet_product in that SO.
(An Employee with an IT-Support-timesheet_product in HR-Tab cant record time on a SO/Project that only asked for Engineering-Employees)
