import json
import logging


def get_customer_orders(customer_id: str):
    logging.info("RETRIEVER::start - Retrieving customer orders...")
    with open("data/customer_orders.json", "r") as file:
        customer_orders = json.load(file)
    logging.info("RETRIEVER::end - Retrieving customer orders...")
    return customer_orders
