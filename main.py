from datetime import datetime, timedelta
import json
import logging
import configparser
import os

basic_generator, set_of_var = {'a': 84589, 'c': 45989, 'm': 217728}, {}
order_history, providers, directions, currency_pairs = [], [], [], []
number_of_orders = 0
start_date = datetime.now()
PATH_LOGS = (str(os.getcwd() + "/Logs/"))
PATH_DATABASE = os.getcwd() + "/database.json"
#logging.basicConfig(level=logging.INFO,
#                   filename=PATH_LOGS + datetime.now().strftime("%d:%m:%Y-%H:%M")+".txt")


def create_config(path):
    global number_of_orders, start_date
    config = configparser.ConfigParser()
    config.add_section("PATH")
    config.set("PATH", "logs", PATH_LOGS)
    config.set("PATH", "database", PATH_DATABASE)
    config.set("VALUES", "number_of_orders", 2000)
    config.set("VALUES", "start_date", "12/07/20 00:00:00")
    config.set("VALUES", "percent_of_red", 0.15)
    config.set("VALUES", "percent_of_blue", 0.3)
    with open(path, "w") as conf_file:
        config.write(conf_file)


def read_config(path):
    global number_of_orders, start_date
    #logging.info("Reading config")
    if not os.path.exists(path):
        #logging.warn("CANT FIND CONFIG FILE, CREATING STANDART AND USING IT")
        create_config(path)
        read_config(path)
    else:
        config = configparser.ConfigParser()
        config.read(path)
        PATH_LOGS = config.get("PATH", "logs")
        PATH_DATABASE = config.get("PATH", "database")
        number_of_orders = int(config.get("VALUES", "number_of_orders"))
        start_date = datetime.strptime(config.get("VALUES", "start_date"), '%d/%m/%y %H:%M:%S')


def get_data():
    global set_of_var, providers, directions, currency_pairs
    with open('database.json') as config_file:
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
    for order in order_history:
        prev = generator_rnd_number(set_of_var, prev_id)
        if prev % 7 == 0 and prev % 5 == 0:
            while (prev > 10):
                prev = prev // 10
            prev_id = prev_id + prev + 1
            order.append(prev_id)
            order.append(start_id + prev_id)
        else:
            prev_id += 1
            order.append(prev_id)
            order.append(start_id + prev_id)


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
        #curency pair
        order.append(generator_from_template(set_of_var, order[0], currency_pairs)[0])

        #px
        course = generator_from_template(set_of_var, order[0], currency_pairs)[1]
        delta = generator_rnd_number(set_of_var, order[0])
        if delta % 2 == 0:
            while delta>0.05:
                delta = delta / 10
            order.append(float('{:.6f}'.format(course + course * delta)))
        else:
            while delta>0.05:
                delta = delta / 10
            order.append(float('{:.6f}'.format(course - course * delta)))

        #volume
        volume = generator_rnd_number(set_of_var,order[0]) % 1000
        order.append(volume)


def generate_dates():
    global order_history, set_of_var, start_date
    prev = 18603
    prev_date = start_date
    for order in order_history:
        prev = prev + generator_rnd_number(set_of_var, prev) * 15000 + 1
        current_date = prev_date + timedelta(microseconds=prev)
        # order.append(current_date.isoformat(sep='|'))
        order.append(current_date)


def main():
    init()
    generate_id()
    generate_provider()
    generate_direction()
    generate_currency()
    generate_dates()
    for order in order_history:
        print(order)


main()