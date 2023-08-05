#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
"Sales extension for managing leads and opportunities"
import datetime
import time
from trytond.model import ModelView, ModelSQL, ModelWorkflow, fields
from trytond.wizard import Wizard
from trytond.backend import FIELDS
from trytond.pyson import Equal, Eval, Not, In, If, Get, PYSONEncoder

STATES = [
    ('lead', 'Lead'),
    ('opportunity', 'Opportunity'),
    ('converted', 'Converted'),
    ('cancelled', 'Cancelled'),
    ('lost', 'Lost'),
]
_STATES_START = {
    'readonly': Not(Equal(Eval('state'), 'lead')),
}
_STATES_STOP = {
    'readonly': In(Eval('state'), ['converted', 'lost', 'cancelled']),
}

class SaleOpportunity(ModelWorkflow, ModelSQL, ModelView):
    'Sale Opportunity'
    _name = "sale.opportunity"
    _description = __doc__
    _history = True
    _rec_name = 'description'

    party = fields.Many2One('party.party', 'Party', required=True, select=1,
        on_change=['party'], states=_STATES_STOP, depends=['state'])
    address = fields.Many2One('party.address', 'Address',
            domain=[('party', '=', Eval('party'))],
            select=2, depends=['party', 'state'],
            states=_STATES_STOP)
    company = fields.Many2One('company.company', 'Company', required=True,
            select=1, states=_STATES_STOP, domain=[
                ('id', If(In('company', Eval('context', {})), '=', '!='),
                    Get(Eval('context', {}), 'company', 0)),
            ], on_change=['company'], depends=['state'])
    currency = fields.Function(fields.Many2One('currency.currency',
        'Currency'), 'get_currency')
    currency_digits = fields.Function(fields.Integer('Currency Digits'),
            'get_currency_digits')
    amount = fields.Numeric('Amount', digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits'], help='Estimated revenue amount')
    warehouse = fields.Many2One('stock.location', 'Warehouse',
            domain=[('type', '=', 'warehouse')], states={
                'required': Equal(Eval('state'), 'converted'),
                'readonly': In(Eval('state'),
                    ['converted', 'lost', 'cancelled']),
            })
    payment_term = fields.Many2One('account.invoice.payment_term',
            'Payment Term', states={
                'required': Equal(Eval('state'), 'converted'),
                'readonly': In(Eval('state'),
                    ['converted', 'lost', 'cancelled']),
            })
    employee = fields.Many2One('company.employee', 'Employee', required=True,
            states=_STATES_STOP, depends=['state', 'company'],
            domain=[('company', '=', Eval('company'))])
    start_date = fields.Date('Start Date', required=True, select=1,
            states=_STATES_START, depends=['state'])
    end_date = fields.Date('End Date', select=2, readonly=True, states={
        'invisible': Not(In(Eval('state'),
            ['converted', 'cancelled', 'lost'])),
    }, depends=['state'])
    description = fields.Char('Description', required=True,
            states=_STATES_STOP, depends=['state'])
    comment = fields.Text('Comment', states=_STATES_STOP)
    lines = fields.One2Many('sale.opportunity.line', 'opportunity', 'Lines',
            states=_STATES_STOP, depends=['state'])
    state = fields.Selection(STATES, 'State', required=True, select=1,
            sort=False, readonly=True)
    probability = fields.Integer('Conversion Probability',
            states={
                'readonly': Not(In(Eval('state'), ['opportunity', 'lead'])),
            }, depends=['state'], help="Percentage between 0 and 100")
    history = fields.One2Many('sale.opportunity.history', 'opportunity',
            'History', readonly=True)
    lost_reason = fields.Text('Reason for loss', states={
        'invisible': Not(Equal(Eval('state'), 'lost')),
    }, depends=['state'])
    sale = fields.Many2One('sale.sale', 'Sale', readonly=True, states={
        'invisible': Not(Equal(Eval('state'), 'converted')),
        }, depends=['state'])

    def __init__(self):
        super(SaleOpportunity, self).__init__()
        self._order.insert(0, ('start_date', 'DESC'))
        self._sql_constraints += [
            ('check_percentage',
                'CHECK(probability >= 0 AND probability <= 100)',
                'Probability must be between 0 and 100!')
        ]
        self._rpc.update({
            'button_lead': True,
        })

    def default_state(self, cursor, user, context=None):
        return 'lead'

    def default_start_date(self, cursor, user, context=None):
        date_obj = self.pool.get('ir.date')
        return date_obj.today(cursor, user, context=context)

    def default_probability(self, cursor, user, context=None):
        return 50

    def default_company(self, cursor, user, context=None):
        if context is None:
            context = {}
        return context.get('company', False)

    def default_employee(self, cursor, user_id, context=None):
        user_obj = self.pool.get('res.user')
        employee_obj = self.pool.get('company.employee')

        if context is None:
            context = {}
        employee_id = None
        if context.get('employee'):
            employee_id = context['employee']
        else:
            user = user_obj.browse(cursor, user_id, user_id, context=context)
            if user.employee:
                employee_id = user.employee.id
        if employee_id:
            return employee_id
        return False

    def default_payment_term(self, cursor, user, context=None):
        payment_term_obj = self.pool.get('account.invoice.payment_term')
        payment_term_ids = payment_term_obj.search(cursor, user,
                self.payment_term.domain, context=context)
        if len(payment_term_ids) == 1:
            return payment_term_ids[0]
        return False

    def default_warehouse(self, cursor, user, context=None):
        location_obj = self.pool.get('stock.location')
        location_ids = location_obj.search(cursor, user,
                self.warehouse.domain, context=context)
        if len(location_ids) == 1:
            return location_ids[0]
        return False

    def get_currency(self, cursor, user, ids, name, context=None):
        res = {}
        for opportunity in self.browse(cursor, user, ids, context=context):
            res[opportunity.id] = opportunity.company.currency.id
        return res

    def get_currency_digits(self, cursor, user, ids, name, context=None):
        res = {}
        for opportunity in self.browse(cursor, user, ids, context=context):
            res[opportunity.id] = opportunity.company.currency.digits
        return res

    def on_change_company(self, cursor, user, values, context=None):
        company_obj = self.pool.get('company.company')

        res = {}
        if values.get('company'):
            company = company_obj.browse(cursor, user, values['company'],
                    context=context)
            res['currency'] = company.currency.id
            res['currency.rec_name'] = company.currency.rec_name
            res['currency_digits'] = company.currency.digits
        return res

    def on_change_party(self, cursor, user, values, context=None):
        party_obj = self.pool.get('party.party')
        payment_term_obj = self.pool.get('account.invoice.payment_term')

        res = {
            'payment_term': False,
        }
        if values.get('party'):
            party = party_obj.browse(cursor, user, values['party'],
                    context=context)
            if party.payment_term:
                res['payment_term'] = party.payment_term.id
        if not res['payment_term']:
            res['payment_term'] = self.default_payment_term(cursor, user,
                    context=context)
        if res['payment_term']:
            res['payment_term.rec_name'] = payment_term_obj.browse(cursor, user,
                    res['payment_term'], context=context).rec_name
        return res

    def set_end_date(self, cursor, user, opportunity_id, state, context=None):
        """
        This will fill the end_date for a lead/opportunity and change the state

        :param cursor: the database cursor
        :param user: the user id
        :param opportunity_id: the id of the opportunity
        :param state: the target state
        :param context: the context
        """
        date_obj = self.pool.get('ir.date')
        self.write(cursor, user, opportunity_id, {
            'end_date': date_obj.today(cursor, user, context=context),
            'state': state,
            }, context=context)

    def button_lead(self, cursor, user, ids, context=None):
        self.workflow_trigger_create(cursor, user, ids, context=context)
        return True

    def _get_sale_line_opportunity_line(self, cursor, user, opportunity,
            context=None):
        '''
        Return sale line values for each opportunity line

        :param cursor: the database cursor
        :param user: the user id
        :param opportunity: the BrowseRecord of opportunity
        :param context: the context

        :return: a dictionary with opportunity line id as key
            and a dictionary of sale line values as value
        '''
        line_obj = self.pool.get('sale.opportunity.line')
        res = {}
        for line in opportunity.lines:
            val = line_obj.get_sale_line(cursor, user, line, context=context)
            if val:
                res[line.id] = val
        return res

    def _get_sale_opportunity(self, cursor, user, opportunity, context=None):
        '''
        Return sale values for an opportunity

        :param cursor: the database cursor
        :param user: the user id
        :param opportunity: the BrowseRecord of the opportunity
        :param context: the context

        :return: a dictionary with sale fields as key and sale values as value
        '''
        res = {
            'description': opportunity.description,
            'party': opportunity.party.id,
            'payment_term': opportunity.payment_term.id,
            'company': opportunity.company.id,
            'warehouse': opportunity.warehouse.id,
            'invoice_address': opportunity.address and opportunity.address.id,
            'shipment_address': opportunity.address and opportunity.address.id,
            'currency': opportunity.company.currency.id,
            'comment': opportunity.comment,
        }
        return res

    def create_sale(self, cursor, user, opportunity_id, context=None):
        '''
        Create a sale for the opportunity

        :param cursor: the database cursor
        :param user: the user id
        :param opportunity_id: the id of the opportunity
        :param context: the context
        '''
        sale_obj = self.pool.get('sale.sale')
        sale_line_obj = self.pool.get('sale.line')
        line_obj = self.pool.get('sale.opportunity.line')

        if context is None:
            context = {}

        opportunity = self.browse(cursor, user, opportunity_id,
                context=context)

        values = self._get_sale_opportunity(cursor, user, opportunity,
                context=context)
        sale_line_values = self._get_sale_line_opportunity_line(cursor, user,
                opportunity, context=context)

        ctx = context.copy()
        ctx['user'] = user
        sale_id = sale_obj.create(cursor, 0, values, context=ctx)

        for line_id, values in sale_line_values.iteritems():
            values['sale'] = sale_id
            sale_line_id = sale_line_obj.create(cursor, 0, values,
                    context=ctx)
            line_obj.write(cursor, user, line_id, {
                'sale_line': sale_line_id,
                }, context=context)

        self.write(cursor, user, opportunity_id, {
            'sale': sale_id,
            }, context=context)
        return sale_id

SaleOpportunity()


class SaleOpportunityLine(ModelSQL, ModelView):
    'Sale Opportunity Line'
    _name = "sale.opportunity.line"
    _description = __doc__
    _rec_name = "product"
    _history = True

    opportunity = fields.Many2One('sale.opportunity', 'Opportunity')
    sequence = fields.Integer('Sequence')
    product = fields.Many2One('product.product', 'Product', required=True,
            domain=[('salable', '=', True)], on_change=['product', 'unit'])
    quantity = fields.Float('Quantity', required=True,
            digits=(16, Eval('unit_digits', 2)), depends=['unit_digits'])
    unit = fields.Many2One('product.uom', 'Unit', required=True)
    unit_digits = fields.Function(fields.Integer('Unit Digits',
        on_change_with=['unit']), 'get_unit_digits')
    sale_line = fields.Many2One('sale.line', 'Sale Line', readonly=True,
            states={
                'invisible': Not(Equal(Get(Eval('_parent_opportunity', {}),
                        'state'), 'converted')),
            })

    def __init__(self):
        super(SaleOpportunityLine, self).__init__()
        self._order.insert(0, ('sequence', 'ASC'))

    def on_change_with_unit_digits(self, cursor, user, vals, context=None):
        uom_obj = self.pool.get('product.uom')
        if vals.get('unit'):
            uom = uom_obj.browse(cursor, user, vals['unit'],
                    context=context)
            return uom.digits
        return 2

    def get_unit_digits(self, cursor, user, ids, name, context=None):
        res = {}
        for line in self.browse(cursor, user, ids, context=context):
            if line.unit:
                res[line.id] = line.unit.digits
            else:
                res[line.id] = 2
        return res

    def on_change_product(self, cursor, user, vals, context=None):
        product_obj = self.pool.get('product.product')

        if context is None:
            context = {}
        if not vals.get('product'):
            return {}
        res = {}

        product = product_obj.browse(cursor, user, vals['product'],
                context=context)
        category = product.sale_uom.category
        if not vals.get('unit') \
                or vals.get('unit') not in [x.id for x in category.uoms]:
            res['unit'] = product.sale_uom.id
            res['unit.rec_name'] = product.sale_uom.rec_name
            res['unit_digits'] = product.sale_uom.digits
        return res

    def get_sale_line(self, cursor, user, line, context=None):
        '''
        Return sale line values for opportunity line

        :param cursor: the database cursor
        :param user: the user id
        :param line: the BrowseRecord of the line
        :param context: the context

        :return: a dictionary with sale line fields as key
            and sale line values as value
        '''
        sale_line_obj = self.pool.get('sale.line')
        res = {
            'type': 'line',
            'quantity': line.quantity,
            'unit': line.unit.id,
            'product': line.product.id,
        }
        res.update(sale_line_obj.on_change_product(cursor, user, {
            'product': line.product.id,
            'unit': line.unit.id,
            'quantity': line.quantity,
            '_parent_sale.party': line.opportunity.party.id,
            '_parent_sale.currency': line.opportunity.company.currency.id,
            }, context=context))
        return res

SaleOpportunityLine()


class One2ManyHistory(fields.One2Many):

    def get(self, cursor, user, ids, model, name, values=None,
            context=None):
        opportunity2id = {}
        histories = model.browse(cursor, user, ids, context=context)
        opportunity2id = dict((history.opportunity.id, history.id) for
                history in histories)
        res = super(One2ManyHistory, self).get(cursor, user,
                opportunity2id.keys(), model, name, values=values,
                context=context)
        return dict((opportunity2id[i], j) for i, j in res.iteritems())


class SaleOpportunityHistory(ModelSQL, ModelView):
    'Sale Opportunity History'
    _name = 'sale.opportunity.history'
    _description = __doc__

    date = fields.DateTime('Change Date')
    opportunity = fields.Many2One('sale.opportunity', 'Sale Opportunity')
    user = fields.Many2One('res.user', 'User')
    party = fields.Many2One('party.party', 'Party', datetime_field='date')
    address = fields.Many2One('party.address', 'Address',
            datetime_field='date')
    company = fields.Many2One('company.company', 'Company',
            datetime_field='date')
    employee = fields.Many2One('company.employee', 'Employee',
            datetime_field='date')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date', states={
        'invisible': Not(In(Eval('state'),
            ['converted', 'cancelled', 'lost'])),
    }, depends=['state'])
    description = fields.Char('Description')
    comment = fields.Text('Comment')
    lines = One2ManyHistory('sale.opportunity.line', 'opportunity', 'Lines',
            datetime_field='date')
    state = fields.Selection(STATES, 'State')
    probability = fields.Integer('Conversion Probability')
    lost_reason = fields.Text('Reason for loss', states={
        'invisible': Not(Equal(Eval('state'), 'lost')),
    }, depends=['state'])


    def __init__(self):
        super(SaleOpportunityHistory, self).__init__()
        self._order.insert(0, ('date', 'DESC'))

    def _table_query_fields(self, context=None):
        opportunity_obj = self.pool.get('sale.opportunity')
        table = '%s__history' % opportunity_obj._table
        return [
            'MIN("%s".__id) AS id' % table,
            '"%s".id AS opportunity' % table,
            'MIN(COALESCE("%s".write_date, "%s".create_date)) AS date' % (table, table),
            'COALESCE("%s".write_uid, "%s".create_uid) AS user' % (table, table),
        ] + ['"%s"."%s"' % (table, name) for name, field in self._columns.iteritems()
                if name not in ('id', 'opportunity', 'date', 'user')
                and not hasattr(field, 'set')]

    def _table_query_group(self, context=None):
        opportunity_obj = self.pool.get('sale.opportunity')
        table = '%s__history' % opportunity_obj._table
        return [
            '"%s".id' % table,
            'COALESCE("%s".write_uid, "%s".create_uid)' % (table, table),
        ] + ['"%s"."%s"' % (table, name)
                for name, field in self._columns.iteritems()
                if name not in ('id', 'opportunity', 'date', 'user')
                and not hasattr(field, 'set')]

    def table_query(self, context=None):
        opportunity_obj = self.pool.get('sale.opportunity')
        return (('SELECT ' + \
                (', '.join(self._table_query_fields(context=context))) + \
                ' FROM "%s__history" '
                'GROUP BY ' + \
                (', '.join(self._table_query_group(context=context)))) % \
                opportunity_obj._table, [])

    def read(self, cursor, user, ids, fields_names=None, context=None):
        res = super(SaleOpportunityHistory, self).read(cursor, user, ids,
                fields_names=fields_names, context=context)

        # Remove microsecond from timestamp
        for values in res:
            if 'date' in values:
                if isinstance(values['date'], basestring):
                    values['date'] = datetime.datetime(
                        *time.strptime(values['date'],
                            '%Y-%m-%d %H:%M:%S.%f')[:6])
                values['date'] = values['date'].replace(microsecond=0)
        return res

SaleOpportunityHistory()


class SaleOpportunityEmployee(ModelSQL, ModelView):
    'Sale Opportunity per Employee'
    _name = 'sale.opportunity_employee'
    _description = __doc__

    employee = fields.Many2One('company.employee', 'Employee')
    number = fields.Integer('Number')
    converted = fields.Integer('Converted')
    conversion_rate = fields.Function(fields.Float('Conversion Rate',
        help='In %'), 'get_conversion_rate')
    lost = fields.Integer('Lost')
    company = fields.Many2One('company.company', 'Company')
    currency = fields.Function(fields.Many2One('currency.currency',
        'Currency'), 'get_currency')
    currency_digits = fields.Function(fields.Integer('Currency Digits'),
            'get_currency_digits')
    amount = fields.Numeric('Amount', digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits'])
    converted_amount = fields.Numeric('Converted Amount',
            digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits'])
    conversion_amount_rate = fields.Function(fields.Float(
        'Conversion Amount Rate', help='In %'), 'get_conversion_amount_rate')

    def _converted_state(self, context=None):
        return ['converted']

    def _lost_state(self, context=None):
        return ['lost']

    def table_query(self, context=None):
        opportunity_obj = self.pool.get('sale.opportunity')
        if context is None:
            context = {}
        clause = ' '
        args = [True]
        if context.get('start_date'):
            clause += 'AND start_date >= %s '
            args.append(context['start_date'])
        if context.get('end_date'):
            clause += 'AND start_date <= %s '
            args.append(context['end_date'])
        return ('SELECT DISTINCT(employee) AS id, '
                    'MAX(create_uid) AS create_uid, '
                    'MAX(create_date) AS create_date, '
                    'MAX(write_uid) AS write_uid, '
                    'MAX(write_date) AS write_date, '
                    'employee, '
                    'company, '
                    'COUNT(1) AS number, '
                    'SUM(CASE WHEN state IN (' + ','.join("'%s'" % x
                        for x in self._converted_state(context=context)) + ') '
                        'THEN 1 ELSE 0 END) AS converted, '
                    'SUM(CASE WHEN state IN (' + ','.join("'%s'" % x
                        for x in self._lost_state(context=context)) + ') '
                        'THEN 1 ELSE 0 END) AS lost, '
                    'SUM(amount) AS amount, '
                    'SUM(CASE WHEN state IN (' + ','.join("'%s'" % x
                        for x in self._converted_state(context=context)) + ') '
                        'THEN amount ELSE 0 END) AS converted_amount '
                'FROM "' + opportunity_obj._table + '" '
                'WHERE %s ' \
                + clause + \
                'GROUP BY employee, company', args)

    def get_conversion_rate(self, cursor, user, ids, name, context=None):
        res = {}
        for record in self.browse(cursor, user, ids, context=context):
            if record.number:
                res[record.id] = float(record.converted) / record.number * 100.0
            else:
                res[record.id] = 0.0
        return res

    def get_currency(self, cursor, user, ids, name, context=None):
        res = {}
        for record in self.browse(cursor, user, ids, context=context):
            res[record.id] = record.company.currency.id
        return res

    def get_currency_digits(self, cursor, user, ids, name, context=None):
        res = {}
        for record in self.browse(cursor, user, ids, context=context):
            res[record.id] = record.company.currency.digits
        return res

    def get_conversion_amount_rate(self, cursor, user, ids, name, context=None):
        res = {}
        for record in self.browse(cursor, user, ids, context=context):
            if record.amount:
                res[record.id] = (float(record.converted_amount) /
                        float(record.amount) * 100.0)
            else:
                res[record.id] = 0.0
        return res

SaleOpportunityEmployee()


class OpenSaleOpportunityEmployeeInit(ModelView):
    'Open Sale Opportunity per Employee Init'
    _name = 'sale.open_opportunity_employee.init'
    _description = __doc__
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')

OpenSaleOpportunityEmployeeInit()


class OpenSaleOpportunityEmployee(Wizard):
    'Open Sale Opportunity per Employee'
    _name = 'sale.open_opportunity_employee'
    states = {
        'init': {
            'result': {
                'type': 'form',
                'object': 'sale.open_opportunity_employee.init',
                'state': [
                    ('end', 'Cancel', 'tryton-cancel'),
                    ('open', 'Open', 'tryton-ok', True),
                ],
            },
        },
        'open': {
            'result': {
                'type': 'action',
                'action': '_action_open',
                'state': 'end',
            },
        },
    }

    def _action_open(self, cursor, user, data, context=None):
        model_data_obj = self.pool.get('ir.model.data')
        act_window_obj = self.pool.get('ir.action.act_window')
        act_window_id = model_data_obj.get_id(cursor, user, 'sale_opportunity',
                'act_opportunity_employee_form', context=context)
        res = act_window_obj.read(cursor, user, act_window_id, context=context)
        res['pyson_context'] = PYSONEncoder().encode({
            'start_date': data['form']['start_date'],
            'end_date': data['form']['end_date'],
            })
        return res

OpenSaleOpportunityEmployee()


class SaleOpportunityMonthly(ModelSQL, ModelView):
    'Sale Opportunity per Month'
    _name = 'sale.opportunity_monthly'
    _description = __doc__

    year = fields.Char('Year')
    month = fields.Integer('Month')
    year_month = fields.Function(fields.Char('Year-Month'),
            'get_year_month')
    number = fields.Integer('Number')
    converted = fields.Integer('Converted')
    conversion_rate = fields.Function(fields.Float('Conversion Rate',
        help='In %'), 'get_conversion_rate')
    lost = fields.Integer('Lost')
    company = fields.Many2One('company.company', 'Company')
    currency = fields.Function(fields.Many2One('currency.currency',
        'Currency'), 'get_currency')
    currency_digits = fields.Function(fields.Integer('Currency Digits'),
            'get_currency_digits')
    amount = fields.Numeric('Amount', digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits'])
    converted_amount = fields.Numeric('Converted Amount',
            digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits'])
    conversion_amount_rate = fields.Function(fields.Float(
        'Conversion Amount Rate', help='In %'), 'get_conversion_amount_rate')

    def __init__(self):
        super(SaleOpportunityMonthly, self).__init__()
        self._order.insert(0, ('year', 'DESC'))
        self._order.insert(1, ('month', 'DESC'))

    def _converted_state(self, context=None):
        return ['converted']

    def _lost_state(self, context=None):
        return ['lost']

    def table_query(self, context=None):
        opportunity_obj = self.pool.get('sale.opportunity')
        type_id = FIELDS[self.id._type].sql_type(self.id)[0]
        type_year = FIELDS[self.year._type].sql_type(self.year)[0]
        return ('SELECT CAST(id AS ' + type_id + ') AS id, create_uid, '
                    'create_date, write_uid, write_date, '
                    'CAST(year AS ' + type_year + ') AS year, month, company, '
                    'number, converted, lost, amount, converted_amount '
                'FROM ('
                    'SELECT EXTRACT(MONTH FROM start_date) + '
                            'EXTRACT(YEAR FROM start_date) * 100 AS id, '
                        'MAX(create_uid) AS create_uid, '
                        'MAX(create_date) AS create_date, '
                        'MAX(write_uid) AS write_uid, '
                        'MAX(write_date) AS write_date, '
                        'EXTRACT(YEAR FROM start_date) AS year, '
                        'EXTRACT(MONTH FROM start_date) AS month, '
                        'company, '
                        'COUNT(1) AS number, '
                        'SUM(CASE WHEN state IN (' + ','.join("'%s'" % x
                        for x in self._converted_state(context=context)) + ') '
                        'THEN 1 ELSE 0 END) AS converted, '
                        'SUM(CASE WHEN state IN (' + ','.join("'%s'" % x
                        for x in self._lost_state(context=context)) + ') '
                        'THEN 1 ELSE 0 END) AS lost, '
                        'SUM(amount) AS amount, '
                        'SUM(CASE WHEN state IN (' + ','.join("'%s'" % x
                        for x in self._converted_state(context=context)) + ') '
                        'THEN amount ELSE 0 END) AS converted_amount '
                    'FROM "' + opportunity_obj._table + '" '
                    'GROUP BY year, month, company) AS "' + self._table + '"',
                [])

    def get_conversion_rate(self, cursor, user, ids, name, context=None):
        res = {}
        for record in self.browse(cursor, user, ids, context=context):
            if record.number:
                res[record.id] = float(record.converted) / record.number * 100.0
            else:
                res[record.id] = 0.0
        return res

    def get_year_month(self, cursor, user, ids, name, context=None):
        res = {}
        for record in self.browse(cursor, user, ids, context=context):
            res[record.id] = '%s-%s' % (record.year, int(record.month))
        return res

    def get_currency(self, cursor, user, ids, name, context=None):
        res = {}
        for record in self.browse(cursor, user, ids, context=context):
            res[record.id] = record.company.currency.id
        return res

    def get_currency_digits(self, cursor, user, ids, name, context=None):
        res = {}
        for record in self.browse(cursor, user, ids, context=context):
            res[record.id] = record.company.currency.digits
        return res

    def get_conversion_amount_rate(self, cursor, user, ids, name, context=None):
        res = {}
        for record in self.browse(cursor, user, ids, context=context):
            if record.amount:
                res[record.id] = (float(record.converted_amount) /
                        float(record.amount) * 100.0)
            else:
                res[record.id] = 0.0
        return res

SaleOpportunityMonthly()


class SaleOpportunityEmployeeMonthly(ModelSQL, ModelView):
    'Sale Opportunity per Employee per Month'
    _name = 'sale.opportunity_employee_monthly'
    _description = __doc__

    year = fields.Char('Year')
    month = fields.Integer('Month')
    employee = fields.Many2One('company.employee', 'Employee')
    number = fields.Integer('Number')
    converted = fields.Integer('Converted')
    conversion_rate = fields.Function(fields.Float('Conversion Rate',
        help='In %'), 'get_conversion_rate')
    lost = fields.Integer('Lost')
    company = fields.Many2One('company.company', 'Company')
    currency = fields.Function(fields.Many2One('currency.currency',
        'Currency'), 'get_currency')
    currency_digits = fields.Function(fields.Integer('Currency Digits'),
            'get_currency_digits')
    amount = fields.Numeric('Amount', digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits'])
    converted_amount = fields.Numeric('Converted Amount',
            digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits'])
    conversion_amount_rate = fields.Function(fields.Float(
        'Conversion Amount Rate', help='In %'), 'get_conversion_amount_rate')

    def __init__(self):
        super(SaleOpportunityEmployeeMonthly, self).__init__()
        self._order.insert(0, ('year', 'DESC'))
        self._order.insert(1, ('month', 'DESC'))
        self._order.insert(2, ('employee', 'ASC'))

    def _converted_state(self, context=None):
        return ['converted']

    def _lost_state(self, context=None):
        return ['lost']

    def table_query(self, context=None):
        opportunity_obj = self.pool.get('sale.opportunity')
        type_id = FIELDS[self.id._type].sql_type(self.id)[0]
        type_year = FIELDS[self.year._type].sql_type(self.year)[0]
        return ('SELECT CAST(id AS ' + type_id + ') AS id, create_uid, '
                    'create_date, write_uid, write_date, '
                    'CAST(year AS ' + type_year + ') AS year, month, '
                    'employee, company, number, converted, lost, amount, '
                    'converted_amount '
                'FROM ('
                    'SELECT EXTRACT(MONTH FROM start_date) + '
                            'EXTRACT(YEAR FROM start_date) * 100 + '
                            'employee * 1000000 AS id, '
                        'MAX(create_uid) AS create_uid, '
                        'MAX(create_date) AS create_date, '
                        'MAX(write_uid) AS write_uid, '
                        'MAX(write_date) AS write_date, '
                        'EXTRACT(YEAR FROM start_date) AS year, '
                        'EXTRACT(MONTH FROM start_date) AS month, '
                        'employee, '
                        'company, '
                        'COUNT(1) AS number, '
                        'SUM(CASE WHEN state IN (' + ','.join("'%s'" % x
                        for x in self._converted_state(context=context)) + ') '
                        'THEN 1 ELSE 0 END) AS converted, '
                        'SUM(CASE WHEN state IN (' + ','.join("'%s'" % x
                        for x in self._lost_state(context=context)) + ') '
                        'THEN 1 ELSE 0 END) AS lost, '
                        'SUM(amount) AS amount, '
                        'SUM(CASE WHEN state IN (' + ','.join("'%s'" % x
                        for x in self._converted_state(context=context)) + ') '
                        'THEN amount ELSE 0 END) AS converted_amount '
                    'FROM "' + opportunity_obj._table + '" '
                    'GROUP BY year, month, employee, company) '
                'AS "' + self._table + '"', [])

    def get_conversion_rate(self, cursor, user, ids, name, context=None):
        res = {}
        for record in self.browse(cursor, user, ids, context=context):
            if record.number:
                res[record.id] = float(record.converted) / record.number * 100.0
            else:
                res[record.id] = 0.0
        return res

    def get_currency(self, cursor, user, ids, name, context=None):
        res = {}
        for record in self.browse(cursor, user, ids, context=context):
            res[record.id] = record.company.currency.id
        return res

    def get_currency_digits(self, cursor, user, ids, name, context=None):
        res = {}
        for record in self.browse(cursor, user, ids, context=context):
            res[record.id] = record.company.currency.digits
        return res

    def get_conversion_amount_rate(self, cursor, user, ids, name, context=None):
        res = {}
        for record in self.browse(cursor, user, ids, context=context):
            if record.amount:
                res[record.id] = (float(record.converted_amount) /
                        float(record.amount) * 100.0)
            else:
                res[record.id] = 0.0
        return res

SaleOpportunityEmployeeMonthly()
