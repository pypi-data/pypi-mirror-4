#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
"Move"
from trytond.model import ModelView, ModelSQL, fields, OPERATORS
from trytond.backend import TableHandler
from trytond.pyson import In, Eval, Not, In, Equal, If, Get, Bool
from decimal import Decimal

STATES = {
    'readonly': In(Eval('state'), ['cancel', 'done']),
}


class Move(ModelSQL, ModelView):
    "Stock Move"
    _name = 'stock.move'
    _description = __doc__
    product = fields.Many2One("product.product", "Product", required=True,
            select=1, states=STATES,
            on_change=['product', 'currency', 'uom', 'company',
                'from_location', 'to_location'],
            domain=[('type', '!=', 'service')])
    uom = fields.Many2One("product.uom", "Uom", required=True, states=STATES,
            domain=[
                ('category', '=',
                    (Eval('product'), 'product.default_uom.category')),
            ],
            context={
                'category': (Eval('product'), 'product.default_uom.category'),
            },
            on_change=['product', 'currency', 'uom', 'company',
                'from_location', 'to_location'])
    unit_digits = fields.Function(fields.Integer('Unit Digits',
        on_change_with=['uom']), 'get_unit_digits')
    quantity = fields.Float("Quantity", required=True,
            digits=(16, Eval('unit_digits', 2)), states=STATES)
    from_location = fields.Many2One("stock.location", "From Location", select=1,
            required=True, states=STATES,
            domain=[('type', 'not in', ('warehouse', 'view'))])
    to_location = fields.Many2One("stock.location", "To Location", select=1,
            required=True, states=STATES,
            domain=[('type', 'not in', ('warehouse', 'view'))])
    shipment_in = fields.Many2One('stock.shipment.in', 'Supplier Shipment',
            readonly=True, select=1, ondelete='CASCADE')
    shipment_out = fields.Many2One('stock.shipment.out', 'Customer Shipment',
            readonly=True, select=1, ondelete='CASCADE')
    shipment_out_return = fields.Many2One('stock.shipment.out.return',
            'Customer Return Shipment', readonly=True, select=1,
            ondelete='CASCADE')
    shipment_in_return = fields.Many2One('stock.shipment.in.return',
            'Supplier Return Shipment', readonly=True, select=1,
            ondelete='CASCADE')
    shipment_internal = fields.Many2One('stock.shipment.internal',
            'Internal Shipment', readonly=True, select=1, ondelete='CASCADE')
    planned_date = fields.Date("Planned Date", states=STATES, select=2)
    effective_date = fields.Date("Effective Date", readonly=True, select=2)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('assigned', 'Assigned'),
        ('done', 'Done'),
        ('cancel', 'Canceled'),
        ], 'State', select=1, readonly=True)
    company = fields.Many2One('company.company', 'Company', required=True,
            states={
                'readonly': Not(Equal(Eval('state'), 'draft')),
            }, domain=[
                ('id', If(In('company', Eval('context', {})), '=', '!='),
                    Get(Eval('context', {}), 'company', 0)),
            ])
    unit_price = fields.Numeric('Unit Price', digits=(16, 4),
            states={
                'invisible': Not(Bool(Eval('unit_price_required'))),
                'required': Bool(Eval('unit_price_required')),
                'readonly': Not(Equal(Eval('state'), 'draft')),
            })
    cost_price = fields.Numeric('Cost Price', digits=(16, 4), readonly=True)
    currency = fields.Many2One('currency.currency', 'Currency',
            states={
                'invisible': Not(Bool(Eval('unit_price_required'))),
                'required': Bool(Eval('unit_price_required')),
                'readonly': Not(Equal(Eval('state'), 'draft')),
            })
    unit_price_required = fields.Function(fields.Boolean('Unit Price Required',
        on_change_with=['from_location', 'to_location']),
        'get_unit_price_required')

    def __init__(self):
        super(Move, self).__init__()
        self._sql_constraints += [
            ('check_move_qty_pos',
                'CHECK(quantity >= 0.0)', 'Move quantity must be positive'),
            ('check_from_to_locations',
                'CHECK(from_location != to_location)',
                'Source and destination location must be different'),
            ('check_shipment',
                'CHECK((COALESCE(shipment_in, 0) / COALESCE(shipment_in, 1) ' \
                        '+ COALESCE(shipment_out, 0) / ' \
                            'COALESCE(shipment_out, 1) ' \
                        '+ COALESCE(shipment_internal, 0) / ' \
                            'COALESCE(shipment_internal, 1) ' \
                        '+ COALESCE(shipment_in_return, 0) / ' \
                            'COALESCE(shipment_in_return, 1) ' \
                        '+ COALESCE(shipment_out_return, 0) / ' \
                            'COALESCE(shipment_out_return, 1)) ' \
                        '<= 1)',
                'Move can be on only one Shipment'),
        ]
        self._constraints += [
            ('check_product_type', 'service_product'),
        ]
        self._order[0] = ('id', 'DESC')
        self._error_messages.update({
            'set_state_draft': 'You can not set state to draft!',
            'set_state_assigned': 'You can not set state to assigned!',
            'set_state_done': 'You can not set state to done!',
            'del_draft_cancel': 'You can only delete draft or cancelled moves!',
            'service_product': 'You can not use service products for a move!',
            })

    def init(self, cursor, module_name):
        # Migration from 1.2: packing renamed into shipment
        table  = TableHandler(cursor, self, module_name)
        table.drop_constraint('check_packing')
        for suffix in ('in', 'out', 'in_return', 'out_return', 'internal'):
            old_column = 'packing_%s' % suffix
            new_column = 'shipment_%s' % suffix
            if table.column_exist(old_column):
                table.index_action(old_column, action='remove')
            table.drop_fk(old_column)
            table.column_rename(old_column, new_column)
        super(Move, self).init(cursor, module_name)

        # Migration from 1.0 check_packing_in_out has been removed
        table  = TableHandler(cursor, self, module_name)
        table.drop_constraint('check_packing_in_out')

        # Add index on create_date
        table.index_action('create_date', action='add')

    def default_planned_date(self, cursor, user, context=None):
        if context and context.get('planned_date'):
            return context.get('planned_date')

    def default_to_location(self, cursor, user, context=None):
        location_obj = self.pool.get('stock.location')
        party_obj = self.pool.get('party.party')
        res = False

        if context is None:
            context = {}

        warehouse = None
        if context.get('warehouse'):
            warehouse = location_obj.browse(cursor, user, context['warehouse'],
                    context=context)

        if context.get('type', '') == 'inventory_in':
            if warehouse:
                res = warehouse.storage_location.id
        elif context.get('type', '') == 'inventory_out':
            if warehouse:
                res = warehouse.output_location.id
        elif context.get('type', '') == 'incoming':
            if warehouse:
                res = warehouse.input_location.id
        elif context.get('type', '') == 'outgoing':
            if context.get('customer'):
                customer = party_obj.browse(cursor, user, context['customer'],
                        context=context)
                res = customer.customer_location.id

        if context.get('to_location'):
            res = context.get('to_location')
        return res

    def default_from_location(self, cursor, user, context=None):
        location_obj = self.pool.get('stock.location')
        party_obj = self.pool.get('party.party')
        res = False

        if context is None:
            context = {}

        warehouse = None
        if context.get('warehouse'):
            warehouse = location_obj.browse(cursor, user, context['warehouse'],
                    context=context)

        if context.get('type', '') == 'inventory_in':
            if warehouse:
                res = warehouse.input_location.id
        elif context.get('type', '') == 'inventory_out':
            if warehouse:
                res = warehouse.storage_location.id
        elif context.get('type', '') == 'outgoing':
            if warehouse:
                res = warehouse.output_location.id
        elif context.get('type', '') == 'incoming':
            if context.get('supplier'):
                supplier = party_obj.browse(cursor, user, context['supplier'],
                        context=context)
                res = supplier.supplier_location.id
            elif context.get('customer'):
                customer = party_obj.browse(cursor, user, context['customer'],
                        context=context)
                res = customer.customer_location.id

        if context.get('from_location'):
            res = context.get('from_location')
        return res

    def default_state(self, cursor, user, context=None):
        return 'draft'

    def default_company(self, cursor, user, context=None):
        if context is None:
            context = {}
        if context.get('company'):
            return context['company']
        return False

    def default_currency(self, cursor, user, context=None):
        company_obj = self.pool.get('company.company')
        currency_obj = self.pool.get('currency.currency')
        if context is None:
            context = {}
        company = None
        if context.get('company'):
            company = company_obj.browse(cursor, user, context['company'],
                    context=context)
            return company.currency.id
        return False

    def on_change_with_unit_digits(self, cursor, user, vals, context=None):
        uom_obj = self.pool.get('product.uom')
        if vals.get('uom'):
            uom = uom_obj.browse(cursor, user, vals['uom'],
                    context=context)
            return uom.digits
        return 2

    def get_unit_digits(self, cursor, user, ids, name, context=None):
        res = {}
        for move in self.browse(cursor, user, ids, context=context):
            res[move.id] = move.uom.digits
        return res

    def on_change_product(self, cursor, user, vals, context=None):
        product_obj = self.pool.get('product.product')
        uom_obj = self.pool.get('product.uom')
        currency_obj = self.pool.get('currency.currency')
        company_obj = self.pool.get('company.company')
        location_obj = self.pool.get('stock.location')

        if context is None:
            context = {}

        res = {
            'unit_price': Decimal('0.0'),
        }
        if vals.get('product'):
            product = product_obj.browse(cursor, user, vals['product'],
                    context=context)
            res['uom'] = product.default_uom.id
            res['uom.rec_name'] = product.default_uom.rec_name
            res['unit_digits'] = product.default_uom.digits
            to_location = None
            if vals.get('to_location'):
                to_location = location_obj.browse(cursor, user,
                        vals['to_location'], context=context)
            if to_location and to_location.type == 'storage':
                unit_price = product.cost_price
                if vals.get('uom') and vals['uom'] != product.default_uom.id:
                    uom = uom_obj.browse(cursor, user, vals['uom'],
                            context=context)
                    unit_price = uom_obj.compute_price(cursor, user,
                            product.default_uom, unit_price, uom,
                            context=context)
                if vals.get('currency') and vals.get('company'):
                    currency = currency_obj.browse(cursor, user,
                            vals['currency'], context=context)
                    company = company_obj.browse(cursor, user,
                            vals['company'], context=context)
                    unit_price = currency_obj.compute(cursor, user,
                            company.currency, unit_price, currency,
                            round=False, context=context)
                res['unit_price'] = unit_price
        return res

    def on_change_uom(self, cursor, user, vals, context=None):
        product_obj = self.pool.get('product.product')
        uom_obj = self.pool.get('product.uom')
        currency_obj = self.pool.get('currency.currency')
        company_obj = self.pool.get('company.company')
        location_obj = self.pool.get('stock.location')

        if context is None:
            context = {}

        res = {
            'unit_price': Decimal('0.0'),
        }
        if vals.get('product'):
            product = product_obj.browse(cursor, user, vals['product'],
                    context=context)
            to_location = None
            if vals.get('to_location'):
                to_location = location_obj.browse(cursor, user,
                        vals['to_location'], context=context)
            if to_location and to_location.type == 'storage':
                unit_price = product.cost_price
                if vals.get('uom') and vals['uom'] != product.default_uom.id:
                    uom = uom_obj.browse(cursor, user, vals['uom'],
                            context=context)
                    unit_price = uom_obj.compute_price(cursor, user,
                            product.default_uom, unit_price, uom,
                            context=context)
                if vals.get('currency') and vals.get('company'):
                    currency = currency_obj.browse(cursor, user,
                            vals['currency'], context=context)
                    company = company_obj.browse(cursor, user,
                            vals['company'], context=context)
                    unit_price = currency_obj.compute(cursor, user,
                            company.currency, unit_price, currency,
                            round=False, context=context)
                res['unit_price'] = unit_price
        return res

    def default_unit_price_required(self, cursor, user, context=None):
        from_location = self.default_from_location(cursor, user,
                context=context)
        to_location = self.default_to_location(cursor,user,
                context=context)
        vals = {
            'from_location': from_location,
            'to_location': to_location,
            }
        return self.on_change_with_unit_price_required(cursor, user,
                vals, context=context)

    def on_change_with_unit_price_required(self, cursor, user, vals,
            context=None):
        location_obj = self.pool.get('stock.location')
        if vals.get('from_location'):
            from_location = location_obj.browse(cursor, user,
                    vals['from_location'], context=context)
            if from_location.type == 'supplier':
                return True
        if vals.get('to_location'):
            to_location = location_obj.browse(cursor, user,
                    vals['to_location'], context=context)
            if to_location.type == 'customer':
                return True
        return False

    def get_unit_price_required(self, cursor, user, ids, name, context=None):
        res = {}
        for move in self.browse(cursor, user, ids, context=context):
            res[move.id] = False
            if move.from_location.type == 'supplier':
                res[move.id] = True
            if move.to_location.type == 'customer':
                res[move.id] = True
        return res

    def check_product_type(self, cursor, user, ids):
        for move in self.browse(cursor, user, ids):
            if move.product.type == 'service':
                return False
        return True

    def get_rec_name(self, cursor, user, ids, name, context=None):
        if not ids:
            return {}
        res = {}
        moves = self.browse(cursor, user, ids, context=context)
        for m in moves:
            res[m.id] = "%s%s %s" % (m.quantity, m.uom.symbol, m.product.rec_name)
        return res

    def search_rec_name(self, cursor, user, name, clause, context=None):
        return [('product',) + clause[1:]]

    def search(self, cursor, user, args, offset=0, limit=None, order=None,
            context=None, count=False, query_string=False):
        location_obj = self.pool.get('stock.location')

        args = args[:]
        def process_args(args):
            i = 0
            while i < len(args):
                #add test for xmlrpc that doesn't handle tuple
                if (isinstance(args[i], tuple) or \
                        (isinstance(args[i], list) and len(args[i]) > 2 and \
                        args[i][1] in OPERATORS)) and \
                        args[i][0] == 'to_location_warehouse':
                    location_id = False
                    if args[i][2]:
                        location = location_obj.browse(cursor, user,
                                args[i][2], context=context)
                        if location.type == 'warehouse':
                            location_id = location.input_location.id
                    args[i] = ('to_location', args[i][1], location_id)
                elif isinstance(args[i], list):
                    process_args(args[i])
                i += 1
        process_args(args)
        return super(Move, self).search(cursor, user, args, offset=offset,
                limit=limit, order=order, context=context, count=count,
                query_string=query_string)

    def _update_product_cost_price(self, cursor, user, product_id, quantity, uom,
                                   unit_price, currency, company, context=None):
        """
        Update the cost price on the given product

        :param cursor: the database cursor
        :param user: the user id
        :param product_id: the id of the product
        :param quantity: the quantity of the product, positive if incoming and
                negative if outgoing
        :param uom: the uom id or a BrowseRecord of the uom
        :param unit_price: the unit price of the product
        :param currency: the currency of the unit price
        :param company: the company id ot a BrowseRecord of the company
        :param context: the context
        """
        uom_obj = self.pool.get('product.uom')
        product_obj = self.pool.get('product.product')
        product_template_obj = self.pool.get('product.template')
        location_obj = self.pool.get('stock.location')
        currency_obj = self.pool.get('currency.currency')
        company_obj = self.pool.get('company.company')
        date_obj = self.pool.get('ir.date')

        if context is None:
            context = {}

        if isinstance(uom, (int, long)):
            uom = uom_obj.browse(cursor, user, uom, context=context)
        if isinstance(currency, (int, long)):
            currency = currency_obj.browse(cursor, user, currency,
                context=context)
        if isinstance(company, (int, long)):
            company = company_obj.browse(cursor, user, company, context=context)

        ctx = context and context.copy() or {}
        ctx['locations'] = location_obj.search(
            cursor, user, [('type', '=', 'storage')], context=context)
        ctx['stock_date_end'] = date_obj.today(cursor, user, context=context)
        product = product_obj.browse(cursor, user, product_id, context=ctx)
        qty = uom_obj.compute_qty(
            cursor, user, uom, quantity, product.default_uom, context=context)

        qty = Decimal(str(qty))
        product_qty = Decimal(str(product.template.quantity))
        # convert wrt currency
        unit_price = currency_obj.compute(
            cursor, user, currency, unit_price, company.currency,
            round=False, context=context)
        # convert wrt to the uom
        unit_price = uom_obj.compute_price(
            cursor, user, uom, unit_price, product.default_uom, context=context)
        if product_qty + qty != Decimal('0.0'):
            new_cost_price = (
                (product.cost_price * product_qty) + (unit_price * qty)
                ) / (product_qty + qty)
        else:
            new_cost_price = product.cost_price

        if hasattr(product_obj, 'cost_price'):
            digits = product_obj.cost_price.digits
        else:
            digits = product_template_obj.cost_price.digits
        new_cost_price = new_cost_price.quantize(
                Decimal(str(10.0**-digits[1])))

        ctx = context.copy()
        ctx['user'] = user
        product_obj.write(
            cursor, 0, product.id, {'cost_price': new_cost_price},
            context=ctx)

    def create(self, cursor, user, vals, context=None):
        location_obj = self.pool.get('stock.location')
        product_obj = self.pool.get('product.product')
        date_obj = self.pool.get('ir.date')

        vals = vals.copy()

        if vals.get('state') == 'done':
            if not vals.get('effective_date'):
                vals['effective_date'] = date_obj.today(cursor, user,
                        context=context)
            currency_id = vals.get('currency', self.default_currency(cursor,
                    user, context=context))
            company_id = vals.get('company', self.default_company(cursor, user,
                    context=context))
            from_location = location_obj.browse(cursor, user,
                    vals['from_location'], context=context)
            to_location = location_obj.browse(cursor, user,
                    vals['to_location'], context=context)
            product = product_obj.browse(cursor, user, vals['product'],
                    context=context)
            if from_location.type == 'supplier' \
                    and product.cost_price_method == 'average':
                self._update_product_cost_price(
                    cursor, user, vals['product'], vals['quantity'],
                    vals['uom'], vals['unit_price'], currency_id,
                    company_id, context=context)
            if to_location.type == 'supplier' \
                    and product.cost_price_method == 'average':
                self._update_product_cost_price(
                    cursor, user, vals['product'], -vals['quantity'],
                    vals['uom'], vals['unit_price'], currency_id,
                    company_id, context=context)
            if not vals.get('cost_price'):
                # Re-read product to get the updated cost_price
                product = product_obj.browse(cursor, user, vals['product'],
                                             context=context)
                vals['cost_price'] = product.cost_price

        elif vals.get('state') == 'assigned':
            if not vals.get('effective_date'):
                vals['effective_date'] = date_obj.today(cursor, user,
                        context=context)
        return super(Move, self).create(cursor, user, vals, context=context)

    def write(self, cursor, user, ids, vals, context=None):
        date_obj = self.pool.get('ir.date')

        if context is None:
            context = {}

        if isinstance(ids, (int, long)):
            ids = [ids]

        if 'state' in vals:
            for move in self.browse(cursor, user, ids, context=context):
                if vals['state'] == 'cancel':
                    vals['effective_date'] = False
                    if move.from_location.type == 'supplier' \
                            and move.state != 'cancel' \
                            and move.product.cost_price_method == 'average':
                        self._update_product_cost_price(
                            cursor, user, move.product.id, -move.quantity,
                            move.uom, move.unit_price, move.currency,
                            move.company, context=context)
                    if move.to_location.type == 'supplier' \
                            and move.state != 'cancel' \
                            and move.product.cost_price_method == 'average':
                        self._update_product_cost_price(
                            cursor, user, move.product.id, move.quantity,
                            move.uom, move.unit_price, move.currency,
                            move.company, context=context)

                elif vals['state'] == 'draft':
                    if move.state == 'done':
                        self.raise_user_error(cursor, 'set_state_draft',
                                context=context)
                elif vals['state'] == 'assigned':
                    if move.state in ('cancel', 'done'):
                        self.raise_user_error(cursor, 'set_state_assigned',
                                context=context)
                    vals['effective_date'] = date_obj.today(cursor, user,
                            context=context)
                elif vals['state'] == 'done':
                    if move.state in ('cancel'):
                        self.raise_user_error(cursor, 'set_state_done',
                                context=context)
                    vals['effective_date'] = date_obj.today(cursor, user,
                            context=context)

                    if move.from_location.type == 'supplier' \
                            and move.state != 'done' \
                            and move.product.cost_price_method == 'average':
                        self._update_product_cost_price(
                            cursor, user, move.product.id, move.quantity,
                            move.uom, move.unit_price, move.currency,
                            move.company, context=context)
                    if move.to_location.type == 'supplier' \
                            and move.state != 'done' \
                            and move.product.cost_price_method == 'average':
                        self._update_product_cost_price(
                            cursor, user, move.product.id, -move.quantity,
                            move.uom, move.unit_price, move.currency,
                            move.company, context=context)
        res = super(Move, self).write(cursor, user, ids, vals, context=context)

        if vals.get('state', '') == 'done':
            #Re-read the move because cost_price has been updated
            for move in self.browse(cursor, user, ids, context=context):
                if not move.cost_price:
                    self.write(cursor, user, move.id, {
                        'cost_price': move.product.cost_price,
                        }, context=context)
        return res

    def delete(self, cursor, user, ids, context=None):
        for move in self.browse(cursor, user, ids, context=context):
            if move.state not in  ('draft', 'cancel'):
                self.raise_user_error(cursor, 'del_draft_cancel',
                        context=context)
        return super(Move, self).delete(cursor, user, ids, context=context)

    def pick_product(self, cursor, user, move, location_quantities, context=None):
        """
        Pick the product across the location. Naive (fast) implementation.

        :param cursor: the database cursor
        :param user: the user id
        :param move: a BrowseRecord of stock.move
        :param location_quantities: a list of tuple (location, available_qty)
            where location is a BrowseRecord of stock.location.
        :param context: the context
        :return: a list of tuple (location, quantity) for quantities
            that can be picked
        """
        to_pick = []
        needed_qty = move.quantity
        for location, available_qty in location_quantities.iteritems():
            # Ignore available_qty when too small
            if available_qty < move.uom.rounding:
                continue
            if needed_qty <= available_qty:
                to_pick.append((location, needed_qty))
                return to_pick
            else:
                to_pick.append((location, available_qty))
                needed_qty -= available_qty
        # Force assignation for consumables:
        if move.product.type == "consumable":
            to_pick.append((move.from_location, needed_qty))
            return to_pick
        return to_pick

    def assign_try(self, cursor, user, moves, context=None):
        '''
        Try to assign moves.
        It will split the moves to assign as much possible.

        :param cursor: the database cursor
        :param user: the user id
        :param moves: a BrowseRecordList of stock.move to assign
        :param context: the context
        :return: True if succeed or False if not
        '''
        product_obj = self.pool.get('product.product')
        uom_obj = self.pool.get('product.uom')
        date_obj = self.pool.get('ir.date')
        location_obj = self.pool.get('stock.location')

        if context is None:
            context = {}

        cursor.lock(self._table)

        local_ctx = context and context.copy() or {}
        local_ctx['stock_date_end'] = date_obj.today(cursor, user,
                context=context)
        local_ctx['stock_assign'] = True
        location_ids = location_obj.search(cursor, user, [
            ('parent', 'child_of', [x.from_location.id for x in moves]),
            ], context=context)
        pbl = product_obj.products_by_location(cursor, user,
            location_ids=location_ids,
            product_ids=[m.product.id for m in moves],
            context=local_ctx)

        success = True
        for move in moves:
            if move.state != 'draft':
                continue
            to_location = move.to_location
            location_qties = {}
            child_ids = location_obj.search(cursor, user, [
                ('parent', 'child_of', [move.from_location.id]),
                ], context=context)
            for location in location_obj.browse(cursor, user, child_ids,
                    context=context):
                if (location.id, move.product.id) in pbl:
                    location_qties[location] = uom_obj.compute_qty(
                        cursor, user, move.product.default_uom,
                        pbl[(location.id, move.product.id)], move.uom,
                        round=False, context=context)

            to_pick = self.pick_product(
                cursor, user, move, location_qties, context=context)

            picked_qties = 0.0
            for _, qty in to_pick:
                picked_qties += qty

            if picked_qties < move.quantity:
                success = False
                first = False
                self.write(cursor, user, move.id, {
                    'quantity': move.quantity - picked_qties,
                    }, context=context)
            else:
                first = True
            for from_location, qty in to_pick:
                values = {
                    'from_location': from_location.id,
                    'quantity': qty,
                    'state': 'assigned',
                    }
                if first:
                    self.write(cursor, user, move.id, values, context=context)
                    first = False
                else:
                    move_id = self.copy(cursor, user, move.id, default=values,
                            context=context)

                qty_default_uom = uom_obj.compute_qty(
                    cursor, user, move.uom, qty, move.product.default_uom,
                    round=False, context=context)

                pbl[(from_location.id, move.product.id)] = \
                    pbl.get((from_location.id, move.product.id), 0.0) - qty_default_uom
                pbl[(to_location.id, move.product.id)]= \
                    pbl.get((to_location.id, move.product.id), 0.0) + qty_default_uom
        return success

Move()
