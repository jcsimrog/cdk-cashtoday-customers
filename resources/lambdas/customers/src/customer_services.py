import logging
import json

from db_dynamodb import customers_table
from boto3.dynamodb.conditions import Key
from custom_encoder import CustomEncoder
from constants import SAVE, UPDATE, DELETE, SUCCESS_MESSAGE

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_customer(customerId):
    try:
        response = customers_table.get_item(
            Key = {
                'CustomerId': int(customerId)
            }
        )
        if 'Item' in response:
            return build_response(200, response['Item'])
        else:
            return build_response(404, {'Message': 'CustomerId: %s not found ' % customerId})
    except:
        logger.exception('Excepción en tiempo de ejecución en getCustomer(customerId)')


def get_customers_by_pc(postalCode):
    try:
        filtering_exp = Key('PostalCode').eq(int(postalCode))
        response = customers_table.query(
            IndexName="GSIPC",
            KeyConditionExpression=filtering_exp,
            ScanIndexForward=False
        )

        result = response['Items']

        body = {
            'Customers': result
        }
        return build_response(200, body)
    except:
        logger.exception('Excepción en tiempo de ejecución en get_customer_by_cp(postalCode)')

def get_customers_by_country(country):
    try:
        filtering_exp = Key('Country').eq(country)
        response = customers_table.query(
            IndexName="GSICountry",
            KeyConditionExpression=filtering_exp,
            ScanIndexForward=False
        )

        result = response['Items']

        body = {
            'Customers': result
        }
        return build_response(200, body)
    except:
        logger.exception('Excepción en tiempo de ejecución en get_customers_by_country(country)')

def get_customers_by_city(city):
    try:
        filtering_exp = Key('City').eq(city)
        response = customers_table.query(
            IndexName="GSICity",
            KeyConditionExpression=filtering_exp,
            ScanIndexForward=False
        )

        result = response['Items']

        body = {
            'Customers': result
        }
        return build_response(200, body)
    except:
        logger.exception('Excepción en tiempo de ejecución en get_customers_by_city(city)')

def get_customers_by_identification_number(identificationNumber):
    try:
        filtering_exp = Key('IdentificationNumber').eq(identificationNumber)
        response = customers_table.query(
            IndexName="GSIIN",
            KeyConditionExpression=filtering_exp,
            ScanIndexForward=False
        )

        result = response['Items']

        body = {
            'Customers': result
        }
        return build_response(200, body)
    except:
        logger.exception('Excepción en tiempo de ejecución en get_customers_by_identification_number(identificationNumber)')

def get_customers_by_name(fisrtName, lastName):
    logger.info(fisrtName + " " + lastName)
    try:
        filtering_exp1 = Key('FisrtName').eq(fisrtName)
        filtering_exp2 = Key('LastName').eq(lastName)
        response = customers_table.query(
            IndexName="GSINames",
            KeyConditionExpression=filtering_exp1 & filtering_exp2,
            ScanIndexForward=False
        )

        result = response['Items']

        body = {
            'Customers': result
        }
        return build_response(200, body)
    except:
        logger.exception('Excepción en tiempo de ejecución en get_customers_by_name(fisrtName, lastName)')


def get_customers():
    try:
        response = customers_table.scan()
        result = response['Items']

        while 'LastEvaluatedKey' in response:
            response = customers_table.scan(ExclusiveStartKey = response['LastEvaluatedKey'])
            result.extend(response['Items'])

        body = {
            'Customers': result
        }
        return build_response(200, body)

    except:
        logger.exception('Excepción en tiempo de ejecución en getCustomers()')


def save_customer(requestBody):
    try:
        customers_table.put_item(Item = requestBody)
        body = {
            'Operation': SAVE,
            'Message': SUCCESS_MESSAGE,
            'Item': requestBody
        }
        return build_response(200, body)
    except:
      logger.exception('Excepción en tiempo de ejecución en saveCustomer()')


def modify_customer(customerId, updateKey, updateValue):
    try:
        response = customers_table.update_item(
            Key = {
                'CustomerId': customerId
            },
            UpdateExpression = 'set %s = :value ' % updateKey,
            ExpressionAttributeValues = {
                ':value': updateValue
            },
            ReturnValues = 'UPDATED_NEW'
        )

        body = {
            'Operation': UPDATE,
            'Message': SUCCESS_MESSAGE,
            'UpdateAttributes': response
        }

        return build_response(200, body)
    except:
        logger.exception('Excepción en tiempo de ejecución en modifyCustomer()')


def delete_customer(customerId):
    try:
        response = customers_table.delete_item(
            Key = {
                'CustomerId': customerId
            },
            ReturnValues = 'ALL_OLD'
        )

        if 'Attributes' in response:
            body = {
                'Operation': DELETE,
                'Message': SUCCESS_MESSAGE,
                'deletedItem': response
            }
            return build_response(200, body)
        else:
            body = {
                'Operation': DELETE,
                'Message': 'CustomerId: %s not found ' % customerId
            }
            return build_response(404, body)
    except:
       logger.exception('Excepción en tiempo de ejecución en deleteCustomer()') 


def build_response(statusCode, body=None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }

    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder)
    return response