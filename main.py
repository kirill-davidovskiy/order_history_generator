from datetime import datetime,timedelta
import json
import logging
import configparser
import os


basic_generator, set_of_var  = {'a': 84589, 'c': 45989, 'm': 217728}, {}
order_history, providers, directions, currency_pairs = [], [], [], []
number_of_orders = 0
start_date = datetime.now()
PATH_LOGS = os.getcwd()+"/Logs/"
PATH_DATABASE = os.getcwd()+"/database.json"
logging.basicConfig(filename = PATH_LOGS + datetime.datetime.now().strftime("%d:%m:%Y-%H:%M"), level = logging.INFO)

def create_config(path):
	config = configparser.ConfigParser()
	config.add_section("PATH")
	config.set("PATH", "Logs", PATH_LOGS)
	config.set("PATH", "DataBase", PATH_DATABASE)
	with open(path, "w") as conf_file:
		config.write(conf_file)

def read_config():
    logging.info("Reading config")
    if not os.path.exists(path):
        logging.warn("CANT FIND CONFIG FILE, CREATING STANDART AND USING IT")
        create_config(path)
    else:
        config = configparser.ConfigParser()
        config.read(path)
        PATH_LOGS = config.get("PATH", "Logs")
        PATH_DATABASE = config.get("PATH", "DataBase")
    global number_of_orders, set_of_var, providers, directions, currency_pairs, start_date
    with open('config.json') as config_file:
        data = json.load(config_file)
    number_of_orders = data['number_of_orders']
    set_of_var = data['set_of_var']
    providers = data['providers']
    directions = data['directions']
    currency_pairs = list(data['currency_pairs'].items())
    start_date = datetime.strptime(data['start_date'], '%d/%m/%y %H:%M:%S')


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
    for order in order_history:
        order.append(generator_from_template(set_of_var, order[0], currency_pairs)[0])


def generate_dates():
    global order_history, set_of_var, start_date
    prev = 18603
    prev_date = start_date
    for order in order_history:
        prev = prev + generator_rnd_number(set_of_var, prev) * 15000 + 1
        current_date = prev_date + timedelta(microseconds=prev)
        #order.append(current_date.isoformat(sep='|'))
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