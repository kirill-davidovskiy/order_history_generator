import datetime
import json
import logging


basic_generator, set_of_var  = {'a': 84589, 'c': 45989, 'm': 217728}, {}
order_history, providers, directions, currency_pairs = [], [], [], []
number_of_orders = 0


def get_config():
    global number_of_orders, set_of_var, providers, directions, currency_pairs
    with open('config.json') as config_file:
        data = json.load(config_file)
    print("Type:", type(data))
    number_of_orders = data['number_of_orders']
    set_of_var = data['set_of_var']
    providers = data['providers']
    directions = data['directions']
    currency_pairs = list(data['currency_pairs'].items())


def init():
    global order_history, number_of_orders
    get_config()
    for i in range(number_of_orders):
        order_history.append([])

def generator_rnd_number(set_of_var, prev):
    return (set_of_var['a'] * prev + set_of_var['c']) % set_of_var['m']


def generator_from_template(set_of_var, prev, collection):
    return collection[(set_of_var['a'] * prev + set_of_var['c']) % set_of_var['m'] % len(collection)]


def update_generator_vars():
    global set_of_var
    set_of_var['a'] = generator_rnd_number(basic_generator, set_of_var['a'])
    set_of_var['c'] = generator_rnd_number(basic_generator, set_of_var['c'])
    set_of_var['m'] = generator_rnd_number(basic_generator, set_of_var['m'])
    print(set_of_var)


def generate_id():
    global order_history, set_of_var
    prev = 2350
    prev_id = 1
    start_id = 1000000000
    for order in order_history:
        prev = generator_rnd_number(set_of_var, prev_id)
        if prev % 7 == 0 and prev % 5 == 0:
            while(prev > 10):
                prev = prev // 10
            prev_id = prev_id + prev + 1
            order.append(prev_id)
            order.append(start_id + prev_id)
        else:
            prev_id += 1
            order.append(prev_id)
            order.append(start_id + prev_id)


def generate_provider():
    global order_history, set_of_var
    update_generator_vars()
    providers = ['FXCM', 'SQM']
    for order in order_history:
        order.append(generator_from_template(set_of_var, order[0], providers))


def generate_direction():
    global order_history, set_of_var
    update_generator_vars()
    directions = ['Sell', 'Buy']
    for order in order_history:
        order.append(generator_from_template(set_of_var, order[0], directions))


def generate_currency():
    global order_history, set_of_var
    update_generator_vars()
    currency_pairs = ['EUR/USD', 'GBP/USD', 'USD/CHF', 'USD/JPY', 'AUD/USD', 'NZD/USD', 'CAD/CHF', 'CAD/JPY', 'CHF/JPY',
                     'EUR/AUD', 'EUR/CAD', 'EUR/CHF', 'EUR/GBP', 'EUR/JPY', 'EUR/NZD', 'GBP/AUD', 'GBP/CAD', 'NZD/CAD',
                     'NZD/CHF', 'NZD/JPY']
    for order in order_history:
        order.append(generator_from_template(set_of_var, order[0], currency_pairs))


def generate_dates():
    global order_history, set_of_var
    currentDate = datetime.datetime.now()
    currentDate += datetime.timedelta(microseconds = 100500)
    for order in order_history:
        order.append(generator_from_template(set_of_var, order[0], currency_pairs))


def main():
    init()
    generate_id()
    generate_provider()
    generate_direction()
    generate_currency()
    for order in order_history:
        print(order)

main()