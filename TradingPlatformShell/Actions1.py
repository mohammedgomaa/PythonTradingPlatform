from TradeInterface import current_time
from TradingPlatformShell.StringParsers import *
from TradingPlatformShell.Utils import *


#
#
#
def action_default(_, data):
    job_server = data['job_server']
    job_server.list_done_tasks()
    return False


#
#
#
def action_quit(_, data):
    job_server = data['job_server']
    job_server.quit()
    job_server.join()
    job_server.list_done_tasks()
    return True


#
#
#
def action_jobs_list(_, data):
    job_server = data['job_server']
    job_server.list_done_tasks()
    job_server.list_open_tasks()
    return False


#
#
#
def action_jobs_remove(params, data):
    job_server = data['job_server']
    try:
        task_id = int(float(params[0]))
    except ValueError:
        print('invalid task id')
        return False

    job_server.list_done_tasks()
    job_server.remove(task_id)
    return False


#
#
#
def action_time(_, data):
    print(current_time().strftime('%Y-%m-%d %H:%M'))
    return False


#
#
#
def action_quote(params, data):
    trade = data['trade']
    symbol = params[0].strip().upper()

    try:
        quote = trade.get_quote([symbol])[0][1]
    except ValueError as e:
        print(str(e))
        return False

    price = (float(quote['ask']) + float(quote['bid'])) / 2.0
    try:
        pe = price / float(quote['eps'])
    except ZeroDivisionError:
        pe = 0.0
    try:
        stock_yield = float(quote['annualDividend']) * 100.0 / price
    except ZeroDivisionError:
        stock_yield = 0.0

    print(quote['symbolDesc'])
    print('price           = ' + str(round(price, 2)) + '    ( sell for ' + str(quote['bid']) + ' / buy for ' + str(quote['ask']) + ' )       (' + str(quote['bidSize']) + '/' + str(quote['askSize']) + ')')
    print('yield           = %.1f%%' % stock_yield)
    print('P/E             = %.1f' % pe)
    print('eps             = ' + str(quote['eps']))
    print('eps estimated   = ' + str(quote['estEarnings']))
    return False


#
#
#
def action_order_list(_, data):
    trade = data['trade']
    not_visualized = 0
    marker = None

    table = []
    while True:
        try:
            order_list, marker, not_parsed = trade.list_orders(count=25, marker=marker)
        except ValueError as e:
            print(str(e))
            return False
        not_visualized += not_parsed

        for o in order_list:
            table.append(format_order(o))

        if marker is None:
            break

    print(tabulate(table, stralign='left', tablefmt='plain'))
    if not_visualized != 0:
        print('warning:  +' + str(not_visualized) + ' orders')

    return False


#
#
#
def action_positions_list(_, data):
    trade = data['trade']

    request_orders = 25
    marker = 0
    positions_ = []
    while True:
        try:
            positions = trade.list_positions(count=request_orders, marker=marker)
        except ValueError as e:
            print(str(e))
            return False

        positions_ += positions
        if len(positions) < request_orders:
            break
        time.sleep(0.5)
        marker += request_orders

    # trim decimals
    positions = [(x[0], x[1], x[2], round(x[2] * x[1] / 1000.0), round(x[2] * x[1] - x[3]), round((x[2] * x[1] - x[3]) * 100.0 / x[3], 1)) for x in positions_]
    positions.sort(key=lambda x: -x[5])

    total_invested = sum([(x[2] * x[1]) for x in positions_])
    total_gain = sum([(x[2] * x[1] - x[3]) for x in positions_])
    positions.append(('', None, None, round(total_invested / 1000.0), round(total_gain), None))

    # print
    print(tabulate(positions, headers=['symbol', 'qty', 'last price', 'amount (K)', 'gain', '      %'], stralign='left'))
    return False


#
#
#
def action_balance(_, data):
    trade = data['trade']
    try:
        value, cash_settled, cash_unsettled = trade.get_account_balance()
        print(tabulate([['Total value = ', value], ['Total cash  = ', cash_settled + cash_unsettled], ['Unsettled   = ', cash_unsettled]], stralign='left', tablefmt='plain'))
    except ValueError as e:
        print(str(e))

    return False


#
#
#
def action_cancel(params, data):
    trade = data['trade']
    try:
        print(trade.cancel_order(int(params[0])))
    except ValueError as e:
        print(str(e))
    return False


#
#
#
def action_check(params, data):
    trade = data['trade']
    try:
        status = trade.check_order_status(int(params[0]))
        if status is None:
            print('order does not exists.')
        else:
            print('status = ' + status)
    except ValueError as e:
        print(str(e))
    return False


#
#
#
def action_list_quote(_, data):
    for i in data['quote_server'].list_quote():
        print(i)
    return False


#
#
#
def action_w_create(params, data):
    trade = data['trade']
    symbol = params[0].strip().upper()

    # check if the symbol exists
    try:
        trade.get_quote([symbol])[0][1]
    except ValueError as e:
        print(str(e))
        return False

    data['figure_server'].add_figure(params[0])
    return False


#
#
#
def action_w_remove(params, data):
    symbol = params[0].strip().upper()
    if symbol == '*':
        for s in data['figure_server'].list_figure():
            data['figure_server'].remove_figure(s)
    else:
        data['figure_server'].remove_figure(symbol)
    return False


#
#
#
def help_calc():
    print('')
    print('    = AAPL               -> price of AAPL')
    print('')
    print('    = AAPL 120.0         -> gain if AAPL goes to 120.0')
    print('')
    print('    = AAPL 10%           -> gain if AAPL rise 10%')
    print('')
    print('    = AAPL 120.0 3       -> gain if AAPL goes to 120.0 for quantity 3')
    print('')
    print('    = 2.0*4.1            -> 8.2')
    print('')


def action_calc(params, data):
    #
    val1, is_quote = string_to_price_or_quote_price(params[0], data['trade'])
    if val1 is None:
        print('invalid source expression')
        return False

    if len(params) == 1:
        print(val1)
        return False

    #
    is_relative = False
    val2, _ = string_to_price_or_quote_price(params[1], data['trade'])
    if val2 is None:
        val2 = string_to_relative(params[1])
        if val2 is None:
            print('invalid target expression')
            return False
        val2 = val1 * (1.0 + val2)
        is_relative = True

    #
    qty = None
    if len(params) > 2:
        try:
            qty = float(params[2])
        except ValueError:
            pass
    else:
        if is_quote:
            qty = check_positions_quantity(params[0], data)

    #
    try:
        increase = round((val2 - val1) * 100.0 / val1, 2)
        if increase < 0:
            txt = ['drop:     ', 'drop:     ', 'loss:     ']
        else:
            txt = ['gain:     ', 'raise:    ', 'earning:  ']

        if not is_relative:
            print(txt[0] + str(increase) + '%')
        else:
            print(txt[1] + str(round(val1, 2)) + '$ -> ' + str(round(val2, 2)) + '$')
        if qty is not None:
            value_change = round(abs(val2 - val1) * qty)
            print(txt[2] + str(value_change) + '$')
    except ValueError:
        print('error in evaluating the expression')

    return False

#
#
#
