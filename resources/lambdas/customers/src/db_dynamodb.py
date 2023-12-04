import boto3

from constants import DYNAMODB_RESOURCE, DYNAMO_CASHTODAY_CUSTOMERS_TABLE

dynamodb = boto3.resource(DYNAMODB_RESOURCE)
customers_table = dynamodb.Table(DYNAMO_CASHTODAY_CUSTOMERS_TABLE)