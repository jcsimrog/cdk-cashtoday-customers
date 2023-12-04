import json
import logging

from constants import GET_METHOD, POST_METHOD, PUT_METHOD, PATCH_METHOD, DELETE_METHOD, HEALTH_PATH, CUSTOMER_PATH, CUSTOMERS_PATH
from customer_services import (
    build_response, 
    get_customer, 
    get_customers, 
    get_customers_by_pc, 
    get_customers_by_country,
    get_customers_by_city,
    get_customers_by_identification_number,
    get_customers_by_name,
    save_customer, 
    modify_customer, 
    delete_customer
    )

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(event)

    http_method = event['httpMethod']
    path = event['path']

    if http_method == GET_METHOD and path == HEALTH_PATH:
        response = build_response(200)
    elif http_method == GET_METHOD and path == CUSTOMER_PATH:
        response = get_customer(event['queryStringParameters']['customerId'])
    elif http_method == GET_METHOD and path == CUSTOMERS_PATH:
        params = event['queryStringParameters']
        if params is not None:
            postal_code = params.get('postalCode')
            country = params.get('country')
            city = params.get('city')
            identification_number = params.get('identificationNumber')
            first_name = params.get('firstName')
            last_name = params.get('lastName')

            if postal_code is not None:
                response = get_customers_by_pc(postal_code)
            elif country is not None:
                response = get_customers_by_country(country)
            elif city is not None:
                response = get_customers_by_city(city)
            elif identification_number is not None:
                response = get_customers_by_identification_number(identification_number)
            elif first_name is not None and last_name is not None:
                response = get_customers_by_name(first_name, last_name)
            else:    
                response = get_customers()
        else:    
            response = get_customers()
    elif http_method == POST_METHOD and path == CUSTOMER_PATH:
        response = save_customer(json.loads(event['body']))
    elif http_method == PATCH_METHOD and path == CUSTOMER_PATH:
        requestBody = json.loads(event['body'])
        response = modify_customer(requestBody['customerId'], requestBody['updateKey'], requestBody['updateValue'])
    elif http_method == DELETE_METHOD and path == CUSTOMER_PATH:
        requestBody = json.loads(event['body'])
        response = delete_customer(requestBody['customerId'])
    else:
        response = build_response(404, 'Resource Not Found')

    return response