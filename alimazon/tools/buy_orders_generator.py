#!/usr/bin/env python

from uuid import uuid4
from datetime import datetime, timedelta
import numpy as np
import random
import click
import json

from products_service import ProductsService
from random_util import _random_prices, _random_quantities, _truncated_lognormal_sequence, _to_price, _random_products
from date_util import sample_datetime_sequence, today_string, ensure_datetime
import jsonl

products = ProductsService()

def generate_random_buy_orders(settings):
    n_orders = settings['buy_orders_count']
    end_date = datetime.strptime(settings['end_date'], '%Y-%m-%d %H:%M:%S')
    start_date = datetime.strptime(settings['start_date'], '%Y-%m-%d %H:%M:%S')
    samplers = _create_data_samplers(settings)
    supplier_profile = next(samplers['supplier_profile_sampler'])

    for _ in range(n_orders):
        for timestamp in _create_purchase_dates(start_date, end_date, supplier_profile):
            yield _random_buy_order(timestamp, samplers)


def _create_data_samplers(settings):
    return {
        'product_sampler': _random_products(),
        'supplier_profile_sampler': _random_supplier_profiles(settings['supplier_profiles']),
        'product_price_sampler': _random_prices(
            settings['min_product_price'],
            settings['max_product_price']),
        'product_quantity_sampler': _random_quantities(
            settings['min_product_quantity'],
            settings['max_product_quantity']),
    }


def _random_supplier_profiles(supplier_profiles):
    weights = list(map(lambda profile: profile['occurrence_probability'], supplier_profiles))
    while True:
        yield np.random.choice(supplier_profiles, p=weights)


def _create_purchase_dates(start_date, end_date, profile):
    start_date = ensure_datetime(start_date)
    end_date = ensure_datetime(end_date)

    return sample_datetime_sequence(
        start_date,
        end=end_date,
        step=timedelta(days=profile['purchase_recurring_period_days']),
        sample_probability=profile['purchase_probability'])


def _random_buy_order(timestamp, samplers):
    product_price = next(samplers['product_price_sampler'])
    quantity = next(samplers['product_quantity_sampler'])
    product_id = next(samplers['product_sampler']).id
    return {
        'id': str(uuid4()),
        'timestamp': timestamp.isoformat(),
        'product_id': product_id,
        'quantity': quantity,
        'total': _to_price(quantity * product_price)
    }


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option(
    '-c', '--conf-file',
    help="""
    JSON format Stock purchase orders configuration file (e.g. buy_orders.conf). If it is not specified, default values will be used.
    """,
    type=str
)
def _smoke_test(conf_file):
    if conf_file:
        with open(conf_file) as json_conf_file:
            settings = json.load(json_conf_file)
    else:
        today = datetime.today()
        one_month = today + timedelta(weeks=4)
        settings = {
            'buy_orders_count': 10000,
            'start_date': today.strftime("%Y-%m-%d %H:%M:%S"),
            'end_date': one_month.strftime("%Y-%m-%d %H:%M:%S"),
            'min_product_price': 1.0,
            'max_product_price': 10000,
            'min_product_quantity': 1,
            'max_product_quantity': 100,
            'supplier_profiles': [
                {
                    'type': 'approved',
                    'occurrence_probability': 0.15,
                    'purchase_recurring_period_days': 6,
                    'purchase_probability': 0.65,

                },
                {
                    'type': 'prefered',
                    'occurrence_probability': 0.65,
                    'purchase_recurring_period_days': 2,
                    'purchase_probability': 0.85
                },
                {
                    'type': 'strategic',
                    'occurrence_probability': 0.20,
                    'purchase_recurring_period_days': 5,
                    'purchase_probability': 0.70
                }
            ],
        }
    orders = generate_random_buy_orders(settings)

    def generate_suffix(index):
        return '_{0}_{1:05}'.format(today_string(), index)

    jsonl.write_to_files('./resources/buy-orders/part.jsonl.gz',
                         orders,
                         max_records_per_file=5000,
                         suffix_generator=generate_suffix)


if __name__ == '__main__':
    _smoke_test()
