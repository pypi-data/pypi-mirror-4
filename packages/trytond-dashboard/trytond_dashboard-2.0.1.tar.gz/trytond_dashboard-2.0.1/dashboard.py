#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval, Get


class DashboardAction(ModelSQL, ModelView):
    "Dashboard Action"
    _name = "dashboard.action"

    user = fields.Many2One('res.user', 'User', required=True,
            select=1)
    sequence = fields.Integer('Sequence')
    act_window = fields.Many2One('ir.action.act_window', 'Action',
            required=True, ondelete='CASCADE', domain=[
                ('res_model', '!=', False),
                ('res_model', '!=', ''),
                # XXX copy ir.action rule to prevent access rule error
                ['OR',
                    ('groups', 'in', Get(Eval('context', {}), 'groups', [])),
                    ('groups', '=', None),
                ],
            ])

    def __init__(self):
        super(DashboardAction, self).__init__()
        self._order.insert(0, ('sequence', 'ASC'))

DashboardAction()
