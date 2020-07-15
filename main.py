from datetime import datetime, timedelta
from prettytable import PrettyTable
import json
import logging
import configparser
import os

basic_generator, set_of_var = {'a': 84589, 'c': 45989, 'm': 217728}, {}
orders, order_history, providers, directions, currency_pairs = [], [], [], [], []
number_of_orders, percent_of_red, percent_of_blue = 0, 0.15, 0.3
start_date = datetime.now()
PATH_DATABASE = os.getcwd() + "/database.json"
workflow = [
    [["To Provider", "Partially Filled"], ["To Provider", "Rejected"],
     ["To Provider", "Filled"], ["Partially Filled", "Filled"],
     ["Rejected"],["Partially Filled"]],
    [["New", "To Provider", "Filled"], ["New", "To Provider", "Partially Filled"],
     ["New", "To Provider", "Rejected"]],
    [["New"], ["New", "To Provider"]]
]


def create_config(path):
    global number_of_orders, start_date
    config = configparser.ConfigParser()
    config.add_section("PATH")
    config.set("PATH", "database", PATH_DATABASE)
    config.set("VALUES", "number_of_orders", 2000)
    config.set("VALUES", "start_date", "12/07/20 00:00:00")
    with open(path, "w") as conf_file:
        config.write(conf_file)


def read_config(path):
    global number_of_orders, start_date
    if not os.path.exists(path):
        create_config(path)
        read_config(path)
    else:
        config = configparser.ConfigParser()
        config.read(path)
        PATH_DATABASE = config.get("PATH", "database")
        number_of_orders = int(config.get("VALUES", "number_of_orders"))
        start_date = datetime.strptime(config.get("VALUES", "start_date"), '%d/%m/%y %H:%M:%S')


def get_data():
    global set_of_var, providers, directions, currency_pairs, PATH_DATABASE
    with open(PATH_DATABASE) as config_file:
        data = json.load(config_file)
    set_of_var = data['set_of_var']
    providers = data['providers']
    directions = data['directions']
    currency_pairs = list(data['currency_pairs'].items())


def init():
    global order_history, number_of_orders
    read_config("config.cfg")
    get_data()
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


def generate_id():
    global order_history, set_of_var
    prev = 2350
    prev_id = 1
    start_id = 1000000000
    counter = 0
    for order in order_history:
        prev = generator_rnd_number(set_of_var, prev_id)
        if prev % 7 == 0 and prev % 5 == 0:
            while (prev > 10):
                prev = prev // 10
            prev_id = prev_id + prev + 1
            order.append(counter)
            order.append(start_id + prev_id)
        else:
            prev_id += 1
            order.append(counter)
            order.append(start_id + prev_id)
        counter +=1


def generate_provider():
    global order_history, set_of_var, providers
    update_generator_vars()
    for order in order_history:
        order.append(generator_from_template(set_of_var, order[0], providers))


def generate_direction():
    global order_history, set_of_var, directions
    update_generator_vars()
    for order in order_history:
        order.append(generator_from_template(set_of_var, order[0], directions))


def generate_currency():
    global order_history, set_of_var, currency_pairs
    update_generator_vars()
    prev = 1
    for order in order_history:
        pair_course = generator_from_template(set_of_var, order[0], currency_pairs)

        # curency pair
        order.append(pair_course[0])

        # px
        course = pair_course[1]
        delta = generator_rnd_number(set_of_var, order[0])
        if delta % 2 == 0:
            while delta > 0.05:
                delta = delta / 10
            order.append(float('{:.6f}'.format(course + course * delta)))
        else:
            while delta > 0.05:
                delta = delta / 10
            order.append(float('{:.6f}'.format(course - course * delta)))

        # volume
        volume = generator_rnd_number(set_of_var, order[0]) % 1000
        order.append(volume)



def generate_status():
    global order_history
    number_of_blue = int(number_of_orders * percent_of_blue)
    number_of_red = int(number_of_orders * percent_of_red)
    number_of_green = number_of_orders - number_of_blue - number_of_red
    counter, zone = 0, 0
    for order in order_history:
        update_generator_vars()
        order.append(generator_from_template(set_of_var, order[0], workflow[zone]))
        counter +=1
        if counter>number_of_blue + number_of_green:
            zone = 2
        elif counter>number_of_blue:
            zone = 1


def generate_filled():
    global order_history, set_of_var, start_date
    update_generator_vars()
    for order in order_history:
        px, vx = [], []
        for status in order[7]:
            if status == "New" or status == "To Provider" or status == "Rejected":
                px.append("Null")
                vx.append("Null")
            elif status == "Filled":
                px.append(order[5])
                vx.append(order[6])
            else:
                price = 0
                delta = generator_rnd_number(set_of_var, order[0])
                if delta % 2 == 0:
                    while delta > 0.05:
                        delta = delta / 10
                    price = float('{:.6f}'.format(order[5] + order[5] * delta))
                    px.append(price)
                else:
                    while delta > 0.05:
                        delta = delta / 10
                    price = float('{:.6f}'.format(order[5] - order[5] * delta))
                    px.append(price)
                vx.append('{:.2f}'.format(order[6]/price))
        order.append(px)
        order.append(vx)



def generate_dates():
    global order_history, set_of_var, start_date
    update_generator_vars()
    prev_x = 18603
    order_date = start_date
    for order in order_history:
        dates = []
        prev_x = prev_x + generator_rnd_number(set_of_var, prev_x * 10 + 1)
        current_date = order_date + timedelta(milliseconds=prev_x)
        order_delta = prev_x
        dates.append(current_date.isoformat(sep='|'))
        for i in range(len(order[7])-1):
            order_delta = order_delta + generator_rnd_number(set_of_var, order_delta) * 1000 + 1
            current_date =  current_date + timedelta(microseconds=order_delta)
            dates.append(current_date.isoformat(sep='|'))
        order.append(dates)


def generate_history():
    generate_id()
    generate_provider()
    generate_direction()
    generate_currency()
    generate_status()
    generate_dates()
    generate_filled()

def transfer_history_to_orders():
    global orders, order_history
    for order in order_history:
        for i in range(len(order[8])):
            temp_order = []
            temp_order.append(order[0])
            temp_order.append(order[1])
            temp_order.append(order[2])
            temp_order.append(order[3])
            temp_order.append(order[4])
            temp_order.append(order[5])
            temp_order.append(order[6])
            temp_order.append(order[7][i])
            temp_order.append(order[8][i])
            temp_order.append(order[9][i])
            temp_order.append(order[10][i])
            orders.append(temp_order)
    orders = sorted(orders, key=lambda x: x[8])


def output():
    global orders
    table = PrettyTable()
    table.field_names = ["#","ID","Provider,","Direction","Currency","P(init)","V(init)","Status","Date","P(filled)","V(filled)"]
    for order in orders:
        table.add_row(order)
    print(table)


def main():
    init()
    generate_history()
    transfer_history_to_orders()
    output()


if __name__ == "__main__":
    main()
