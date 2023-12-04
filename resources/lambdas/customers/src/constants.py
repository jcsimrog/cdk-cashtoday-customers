import os

#CONSTANTES PARA BD DYNAMO
DYNAMODB_RESOURCE = os.getenv('DYNAMODB_RESOURCE')
DYNAMO_CASHTODAY_CUSTOMERS_TABLE = os.getenv('DYNAMO_CASHTODAY_CUSTOMERS_TABLE')

#CONSTANTES PARA METODOS Y RUTAS
HEALTH_PATH = os.getenv('HEALTH_PATH')
CUSTOMER_PATH = os.getenv('CUSTOMER_PATH')
CUSTOMERS_PATH = os.getenv('CUSTOMERS_PATH')
GET_METHOD = 'GET'
POST_METHOD = 'POST'
PUT_METHOD = 'PUT'
PATCH_METHOD = 'PATCH'
DELETE_METHOD = 'DELETE'

#OPERACIONES Y MENSAJES DEL SERVICIO
SAVE = "SAVE"
UPDATE = "UPDATE"
DELETE = "DELETE"
SUCCESS_MESSAGE = "SUCCESS"