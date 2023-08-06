#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from __future__ import with_statement
import datetime
from trytond.model import ModelView, ModelSQL, fields
from trytond.wizard import Wizard
from trytond.pyson import PYSONEncoder
from trytond.transaction import Transaction
from trytond.tools import safe_eval


class Template(ModelSQL, ModelView):
    _name = "product.template"

    quantity = fields.Function(fields.Float('Quantity'), 'get_quantity')
    forecast_quantity = fields.Function(fields.Float('Forecast Quantity'),
            'get_quantity')

    def get_quantity(self, ids, name):
        res = {}
        if name not in ('quantity', 'forecast_quantity'):
            raise Exception('Bad argument')

        for template in self.browse(ids):
            res[template.id] = 0.0
            for product in template.products:
                res[template.id] += product[name]
        return res

    def __init__(self):
        super(Template, self).__init__()
        self._error_messages.update({
                'change_default_uom': 'You cannot change the default uom for '\
                    'a product which is associated to stock moves.',
            })

    def write(self, ids, vals):
        move_obj = self.pool.get('stock.move')
        cursor = Transaction().cursor
        if not  vals.get("default_uom"):
            return super(Template, self).write(ids, vals)

        for i in range(0, len(ids), cursor.IN_MAX):
            sub_ids = ids[i:i + cursor.IN_MAX]
            res = self.search([
                    ('id', 'in', sub_ids),
                    ('default_uom', '!=', vals['default_uom']),
                    ])

            if res:
                res = move_obj.search([
                        ('product.template', 'in', res),
                        ], limit=1)
                if res:
                    self.raise_user_error('change_default_uom')

        return super(Template, self).write(ids, vals)


Template()

class Product(ModelSQL, ModelView):
    _name = "product.product"

    quantity = fields.Function(fields.Float('Quantity'), 'get_quantity',
            searcher='search_quantity')
    forecast_quantity = fields.Function(fields.Float('Forecast Quantity'),
            'get_quantity', searcher='search_quantity')

    def get_quantity(self, ids, name):
        date_obj = self.pool.get('ir.date')

        if not Transaction().context.get('locations'):
            return dict((id, 0.0) for id in ids)

        context = {}
        if (name == 'quantity'
                and Transaction().context.get('stock_date_end')
                and Transaction().context.get('stock_date_end') >
                date_obj.today()):
            context['stock_date_end'] = date_obj.today()

        if name == 'forecast_quantity':
            context['forecast'] = True
            if not Transaction().context.get('stock_date_end'):
                context['stock_date_end'] = datetime.date.max
        with Transaction().set_context(context):
            pbl = self.products_by_location(
                    location_ids=Transaction().context['locations'],
                    product_ids=ids, with_childs=True)

        res = {}.fromkeys(ids, 0.0)
        for location in Transaction().context['locations']:
            for product in ids:
                res[product] += pbl.get((location, product), 0.0)
        return res

    def _search_quantity_eval_domain(self, line, domain):
        field, operator, operand = domain
        value = line.get(field)
        if value == None:
            return False
        if operator not in ("=", ">=", "<=", ">", "<", "!="):
            return False
        if operator == "=":
            operator= "=="
        return (safe_eval(str(value) + operator + str(operand)))

    def search_quantity(self, name, domain=None):
        date_obj = self.pool.get('ir.date')

        if not (Transaction().context.get('locations') and domain):
            return []

        context = {}
        if (name == 'quantity'
                and Transaction().context.get('stock_date_end')
                and Transaction().context.get('stock_date_end') >
                date_obj.today()):
            context['stock_date_end'] = date_obj.today()

        if name == 'forecast_quantity':
            context['forecast'] = True
            if not Transaction().context.get('stock_date_end'):
                context['stock_date_end'] = datetime.date.max

        with Transaction().set_context(context):
            pbl = self.products_by_location(
                    location_ids=Transaction().context['locations'],
                    with_childs=True, skip_zero=False).iteritems()

        processed_lines = []
        for (location, product), quantity in pbl:
            processed_lines.append({'location': location, #XXX useful ?
                                    'product': product,
                                    name: quantity})

        res= [line['product'] for line in processed_lines \
                    if self._search_quantity_eval_domain(line, domain)]
        return [('id', 'in', res)]



    def products_by_location(self, location_ids, product_ids=None,
            with_childs=False, skip_zero=True):
        """
        Compute for each location and product the stock quantity in the default
        uom of the product.

        The context with keys:
                stock_date_end: if set the date of the stock computation.
                stock_date_start: if set return the delta of the stock
                    between the two dates, (ignored if stock_date_end is
                    missing).
                stock_assign: if set compute also the assigned moves as done.
                forecast: if set compute the forecast quantity.
                stock_destinations: A list of location ids. If set, restrict the
                    computation to moves from and to those locations.
                stock_skip_warehouse: if set, quantities on a warehouse are no
                    more quantities of all child locations but quantities of the
                    storage zone.

        :param location_ids: the ids of locations
        :param product_ids: the ids of the products
                if None all products are used
        :param with_childs: a boolean to compute also for child locations
        :param skip_zero: a boolean to list also items with zero quantity
        :return: a dictionary with (location id, product id) as key
                and quantity as value
        """
        uom_obj = self.pool.get("product.uom")
        product_obj = self.pool.get("product.product")
        rule_obj = self.pool.get('ir.rule')
        location_obj = self.pool.get('stock.location')
        date_obj = self.pool.get('ir.date')

        today = date_obj.today()

        if not location_ids:
            return {}
        cursor = Transaction().cursor
        context = Transaction().context.copy()
        # Skip warehouse location in favor of their storage location
        # to compute quantities. Keep track of which ids to remove
        # and to add after the query.
        location_ids = set(location_ids)
        storage_to_remove = set()
        wh_to_add = {}
        for location in location_obj.browse(location_ids):
            if (location.type == 'warehouse'
                    and Transaction().context.get('stock_skip_warehouse')):
                location_ids.remove(location.id)
                if location.storage_location.id not in location_ids:
                    storage_to_remove.add(location.storage_location.id)
                location_ids.add(location.storage_location.id)
                wh_to_add[location.id] = location.storage_location.id
        location_ids = list(location_ids)

        move_query, move_val = rule_obj.domain_get('stock.move')

        if not context.get('stock_date_end'):
            context['stock_date_end'] = datetime.date.max

        # date end in the past or today: filter on state done
        if (context['stock_date_end'] < today
                or (context['stock_date_end'] == today
                    and not context.get('forecast'))):
            state_date_clause = \
                '('\
                    '(state in (%s, %s)) '\
                'AND '\
                    '('\
                        '('\
                            '(effective_date IS NULL) '\
                        'AND ' \
                            '(planned_date <= %s) '\
                        ') '\
                    'OR '\
                        '(effective_date <= %s)'\
                    ')'\
                ')'
            state_date_vals = ["done",
                    context.get('stock_assign') and 'assigned' or 'done',
                    context['stock_date_end'],
                    context['stock_date_end'],
                    ]
        # future date end: filter move on state done and date
        # before today, or on all state and date between today and
        # date_end.
        else:
            state_date_clause = \
                '(' \
                    '('\
                        '(state in (%s, %s)) '\
                    'AND '\
                        '('\
                            '('\
                                '(effective_date IS NULL) '\
                            'AND ' \
                                '(planned_date <= %s) '\
                            ') '\
                        'OR '\
                            '(effective_date <= %s)' \
                        ')'\
                    ')'\
                'OR '\
                    '('\
                        '(state in (%s, %s, %s)) '\
                    'AND '\
                        '('\
                            '(' \
                                '(effective_date IS NULL) '\
                            'AND '\
                                '(COALESCE(planned_date, %s) <= %s) '\
                            'AND '\
                                '(COALESCE(planned_date, %s) >= %s)'\
                            ')'\
                        'OR '\
                            '(' \
                                '(effective_date <= %s) '\
                            'AND '\
                                '(effective_date >= %s)'\
                            ')'\
                        ')'\
                    ')'\
                ')'

            state_date_vals = [
                'done', context.get('stock_assign') and 'assigned' or 'done',
                today, today,
                'done', 'assigned', 'draft',
                datetime.date.max, context['stock_date_end'],
                datetime.date.max, today,
                context['stock_date_end'], today,
                ]

        if context.get('stock_date_start'):
            if  context['stock_date_start'] > today:
                state_date_clause += 'AND '\
                        '('\
                            '(state in (%s, %s, %s)) '\
                        'AND '\
                            '('\
                                '('\
                                    '(effective_date IS NULL) '\
                                'AND '\
                                    '('\
                                        '(planned_date >= %s) '\
                                    'OR '\
                                        '(planned_date IS NULL)'\
                                    ')'\
                                ') '\
                            'OR '\
                                '(effective_date >= %s)'\
                            ')'\
                        ')'
                state_date_vals.extend(['done', 'assigned', 'draft',
                     context['stock_date_start'], context['stock_date_start']])
            else:
                state_date_clause += 'AND '\
                        '('\
                            '('\
                                '(state in (%s, %s, %s)) '\
                            'AND '\
                                '('\
                                    '('\
                                        '(effective_date IS NULL) '\
                                    'AND '\
                                        '('\
                                            '(planned_date >= %s) '\
                                        'OR '\
                                            '(planned_date IS NULL)'\
                                        ') '\
                                    ')'\
                                'OR '\
                                    '(effective_date >= %s)'\
                                ')'\
                            ') '\
                        'OR '\
                            '('\
                                '(state in (%s, %s)) '\
                            'AND '\
                                '('\
                                    '('\
                                        '(effective_date IS NULL) '\
                                    'AND '\
                                        '('\
                                            '('\
                                                '(planned_date >= %s) '\
                                            'AND '\
                                                '(planned_date < %s)'\
                                            ') '\
                                        'OR '\
                                            '(planned_date IS NULL)'\
                                        ')'\
                                    ') '\
                                'OR '\
                                    '('\
                                        '(effective_date >= %s) '\
                                    'AND '\
                                        '(effective_date < %s)'\
                                    ')'\
                                ')'\
                            ')'\
                        ')'

                state_date_vals.extend(['done', 'assigned', 'draft',
                    today, today,
                    'done',
                    context.get('stock_assign') and 'assigned' or 'done',
                    context['stock_date_start'], today,
                    context['stock_date_start'], today,
                    ])

        if with_childs:
            query, args = location_obj.search([
                ('parent', 'child_of', location_ids),
                ], query_string=True, order=[])
            where_clause = " IN (" + query + ") "
            where_vals = args
        else:
            where_clause = " IN (" + \
                ",".join(('%s',) * len(location_ids)) + ") "
            where_vals = location_ids[:]

        if move_query:
            where_clause += " AND " + move_query + " "
            where_vals += move_val

        product_template_join = ""
        if product_ids:
            where_clause += "AND product in (" + \
                ",".join(('%s',) * len(product_ids)) + ")"
            where_vals += product_ids
        else:
            where_clause += "AND product_template.active = %s"
            where_vals.append(True)
            product_template_join = \
                    "JOIN product_product "\
                        "ON (stock_move.product = product_product.id) "\
                    "JOIN product_template "\
                        "ON (product_product.template = "\
                            "product_template.id) "\


        if context.get('stock_destinations'):
            destinations = context.get('stock_destinations')
            dest_clause_from = " AND from_location in ("
            dest_clause_from += ",".join(('%s',) * len(destinations))
            dest_clause_from += ") "
            dest_clause_to = " AND to_location in ("
            dest_clause_to += ",".join(('%s',) * len(destinations))
            dest_clause_to += ") "
            dest_vals = destinations

        else:
            dest_clause_from = dest_clause_to =""
            dest_vals = []

        # The main select clause is a union between two similar
        # subqueries. One that sums incoming moves towards locations
        # and on that sums outgoing moves. UNION ALL is used because
        # we already know that there will be no duplicates.
        select_clause = \
                "SELECT location, product, uom, sum(quantity) AS quantity "\
                "FROM ( "\
                    "SELECT to_location AS location, product, uom, "\
                        "sum(quantity) AS quantity "\
                    "FROM stock_move " + product_template_join + \
                    "WHERE (%s) " \
                        "AND to_location %s "\
                    "GROUP BY to_location, product ,uom "\
                    "UNION ALL "\
                    "SELECT from_location AS location, product, uom, "\
                        "-sum(quantity) AS quantity "\
                    "FROM stock_move " + product_template_join + \
                    "WHERE (%s) " \
                        "AND from_location %s "\
                    "GROUP BY from_location, product, uom "\
                ") AS T GROUP BY T.location, T.product, T.uom"

        cursor.execute(select_clause % (
                state_date_clause, where_clause + dest_clause_from,
                state_date_clause, where_clause + dest_clause_to),
                    state_date_vals + where_vals + dest_vals + \
                    state_date_vals + where_vals + dest_vals)
        raw_lines = cursor.fetchall()

        res = {}
        res_location_ids = []
        uom_ids = []
        res_product_ids = []
        for line in raw_lines:
            for id_list, position in ((res_location_ids, 0), (uom_ids, 2),
                                      (res_product_ids, 1)):
                if line[position] not in id_list:
                    id_list.append(line[position])

        uom_by_id = dict((x.id, x) for x in uom_obj.browse(uom_ids))
        default_uom = dict((x.id, x.default_uom) for x in product_obj.browse(
            product_ids or res_product_ids))

        for line in raw_lines:
            location, product, uom, quantity = line
            key = (location, product)
            res.setdefault(key, 0.0)
            res[key] += uom_obj.compute_qty(uom_by_id[uom], quantity,
                    default_uom[product], round=False)

        # Propagate quantities on from child locations to their parents
        if with_childs:
            # Fetch all child locations
            all_location_ids = location_obj.search([
                ('parent', 'child_of', location_ids),
                ])
            locations = location_obj.browse(all_location_ids)
            # Generate a set of locations without childs and a dict
            # giving the parent of each location.
            leafs = set(all_location_ids)
            parent = {}
            for location in locations:
                if not location.parent: continue
                if location.parent.id in leafs:
                    leafs.remove(location.parent.id)
                parent[location.id] = location.parent.id
            locations = set((l.id for l in locations))
            while leafs:
                for l in leafs:
                    locations.remove(l)
                    if l not in parent:
                        continue
                    for product in res_product_ids:
                        res.setdefault((parent[l], product), 0)
                        res[(parent[l], product)] += res.get((l,product), 0)
                next_leafs = set(locations)
                for l in locations:
                    if l not in parent:
                        continue
                    if parent[l] in next_leafs and parent[l] in locations:
                        next_leafs.remove(parent[l])
                leafs = next_leafs

            # clean result
            for location, product in res.keys():
                if location not in location_ids:
                    del res[(location, product)]

        # Round quantities
        for location, product in res:
            key = (location, product)
            res[key] = uom_obj.compute_qty(default_uom[product], res[key],
                    default_uom[product], round=True)

        # Complete result with missing products if asked
        if not skip_zero:
            # Search for all products, even if not linked with moves
            if product_ids:
                all_product_ids = product_ids
            else:
                all_product_ids = self.pool.get("product.product").search([])
            keys = ((l,p) for l in location_ids for p in all_product_ids)
            for location_id, product_id in keys:
                if (location_id, product_id) not in res:
                    res[(location_id, product_id)] = 0.0

        if wh_to_add:
            for wh, storage in wh_to_add.iteritems():
                for product in product_ids:
                    if (storage, product) in res:
                        res[(wh, product)] = res[(storage, product)]
                        if storage in storage_to_remove:
                            del res[(storage, product)]

        return res

    def view_header_get(self, value, view_type='form'):
        value = super(Product, self).view_header_get(value,
                view_type=view_type)
        if not Transaction().context.get('locations'):
            return value
        location_obj = self.pool.get('stock.location')
        locations = location_obj.browse(Transaction().context.get('locations'))
        return value + " (" + ",".join(l.name for l in locations) + ")"

Product()


class ChooseStockDateInit(ModelView):
    _name = 'stock.product_stock_date.init'
    _description = "Compute stock quantities"
    forecast_date = fields.Date(
        'At Date', help='Allow to compute expected '\
            'stock quantities for this date.\n'\
            '* An empty value is an infinite date in the future.\n'\
            '* A date in the past will provide historical values.')

    def default_forecast_date(self):
        date_obj = self.pool.get('ir.date')
        return date_obj.today()

ChooseStockDateInit()

class OpenLocation(Wizard):
    'Products by Locations'
    _name = 'stock.location.open'
    states = {
        'init': {
            'result': {
                'type': 'form',
                'object': 'stock.product_stock_date.init',
                'state': [
                    ('end', 'Cancel', 'tryton-cancel'),
                    ('open', 'Open', 'tryton-ok', True),
                ],
            },
        },
        'open': {
            'result': {
                'type': 'action',
                'action': '_action_open_location',
                'state': 'end',
            },
        },
    }

    def _action_open_location(self, data):
        model_data_obj = self.pool.get('ir.model.data')
        act_window_obj = self.pool.get('ir.action.act_window')
        act_window_id = model_data_obj.get_id('stock',
                'act_location_quantity_tree')
        res = act_window_obj.read(act_window_id)

        context = {}
        context['product'] = data['id']
        if data['form']['forecast_date']:
            context['stock_date_end'] = data['form']['forecast_date']
        else:
            context['stock_date_end'] = datetime.date.max
        res['pyson_context'] = PYSONEncoder().encode(context)

        return res

OpenLocation()
