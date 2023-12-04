import os
import aws_cdk as cdk

from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as Lambda,
    aws_apigateway as ApiGateway,
    aws_iam as Iam,
    aws_dynamodb as DynamoDB,
    aws_s3 as S3
    # aws_sqs as sqs,
)
from constructs import Construct

class CashTodayCustomersStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.construct_id = construct_id

        #Main methods to create resources

        #Resources required for Image Storage API
        self.create_s3_customers()
        self.create_role_customer_file_storage()
        self.create_apigateway_customers_file_storage()
        
        #Resources required for Cash Today Client API
        self.create_customers_lambda_role()
        self.create_lambda_function_customers()
        self.create_apigateway_customers()
        self.create_dynamodb_customers()
        
    
    def create_s3_customers(self):
        #Creación de la lambda que se integra con API Gateway con lógica de negocio
        life_cycle_rule = S3.LifecycleRule(
                    id="rule-expiration-three-days",
                    abort_incomplete_multipart_upload_after=cdk.Duration.days(1),
                    expiration=cdk.Duration.days(3)
                )

        self.s3_bucket = S3.Bucket(
            self,
            id="cashtoday-customers-storage-id",
            bucket_name="cashtoday-customers-storage",
            removal_policy= cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            lifecycle_rules = [life_cycle_rule]
        )
    
    def create_role_customer_file_storage(self):
        #Creación del Rol y permisos para el bucket

        self.s3_customer_file_storage_role = Iam.Role(self, "cashtoday-customers-filestorage-role",
                                   assumed_by=Iam.ServicePrincipal("apigateway.amazonaws.com"))
        self.s3_customer_file_storage_role.add_managed_policy(Iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonAPIGatewayPushToCloudWatchLogs"))
        self.s3_customer_file_storage_role.add_managed_policy(Iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"))

    
    def create_apigateway_customers_file_storage(self):
        #Creación de la API para subir imagenes y se eliminen en 3 días
        api = ApiGateway.RestApi(
            self,
            'api-cashtoday-customers-file-storage',
            binary_media_types=["image/jpeg", "image/png"],
            description='REST API que almacenará imágenes de clientes Cash Today'
        )

        list_integration_response: ApiGateway.IntegrationResponse = ApiGateway.IntegrationResponse(status_code="200")

        put_integration_options = ApiGateway.IntegrationOptions(
            credentials_role=self.s3_customer_file_storage_role,
            integration_responses=[list_integration_response],
            request_parameters={
                "integration.request.path.bucket": "method.request.path.bucket",
                "integration.request.path.filename": "method.request.path.filename"
            }
        )

        put_integration = ApiGateway.AwsIntegration(
            region="us-east-2",
            service="s3",
            integration_http_method="PUT",
            path="{bucket}/{filename}", 
            options=put_integration_options
        )

        method_response = ApiGateway.MethodResponse(
            status_code="200",
            response_parameters={
                "method.response.header.Content-Type": True,
            }
            )

        resource_bucket_filename = api.root.add_resource('{bucket}').add_resource("{filename}")
        resource_bucket_filename.add_method(
            "PUT",
            put_integration,
            method_responses=[method_response],
            request_parameters={
                "method.request.path.bucket": True,
                "method.request.path.filename": True,
                "method.request.header.Content-Type": True,
            }
        )
    

    def create_customers_lambda_role(self):
        #Creación de Rol y permisos para la lambda de clientes (customers) con los permisos correspondientes
        self.lambda_customers_role = Iam.Role(self, "cashtoday-customers-lambda-role",
                                      assumed_by=Iam.ServicePrincipal("lambda.amazonaws.com"))
        self.lambda_customers_role.add_managed_policy(Iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchFullAccess"))
        self.lambda_customers_role.add_managed_policy(Iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess"))
       
    def create_lambda_function_customers(self):
        #Creación de la lambda con la conexión a dynamoDB y la lógica de los recuros para busqueda, alta, actualización y eliminación
        TOP_LEVEL_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        PATH_CUSTOMERS_FUNCTION_FOLDER = os.path.join(
            TOP_LEVEL_PATH,
            "resources",
            "lambdas",
            "customers",
            "src",
        )

        self.lambda_function = Lambda.Function(
            self,
            id="{}Lambda".format(self.construct_id),
            function_name="cashtoday-customers",
            description="Lambda para guardar, consultar, actualizar y eliminar clientes cash today ",
            code=Lambda.Code.from_asset(PATH_CUSTOMERS_FUNCTION_FOLDER),
            handler="lambda_function.lambda_handler",
            runtime=Lambda.Runtime.PYTHON_3_11,
            timeout=Duration.seconds(30),
            memory_size=128,
            environment={
                "CUSTOMERS_PATH": "/customers",
                "CUSTOMER_PATH": "/customer",
                "HEALTH_PATH": "/health",
                "DYNAMODB_RESOURCE": "dynamodb",
                "DYNAMO_CASHTODAY_CUSTOMERS_TABLE": "cashtoday-customers"
            },
            role=self.lambda_customers_role,
        )

    def create_dynamodb_customers(self):
        #Creación de la tabla de clientes en dynamoDB
        table = DynamoDB.Table(self, "idCashTodayCustomers", table_name="cashtoday-customers",
                       partition_key=DynamoDB.Attribute(
                           name="CustomerId",
                           type=DynamoDB.AttributeType.NUMBER
                       )
                    )
        
        #Creación de los GSIs para la tabla
        table.add_global_secondary_index(
            index_name="GSIPC",
            partition_key=DynamoDB.Attribute(
                name="PostalCode",
                type=DynamoDB.AttributeType.NUMBER
            ),
            read_capacity=10,
            write_capacity=30
        )

        table.add_global_secondary_index(
            index_name="GSICountry",
            partition_key=DynamoDB.Attribute(
                name="Country",
                type=DynamoDB.AttributeType.STRING
            ),
            read_capacity=10,
            write_capacity=30
        )

        table.add_global_secondary_index(
            index_name="GSICity",
            partition_key=DynamoDB.Attribute(
                name="City",
                type=DynamoDB.AttributeType.STRING
            ),
            read_capacity=10,
            write_capacity=30
        )

        table.add_global_secondary_index(
            index_name="GSIIN",
            partition_key=DynamoDB.Attribute(
                name="IdentificationNumber",
                type=DynamoDB.AttributeType.STRING
            ),
            read_capacity=10,
            write_capacity=30
        )
       
        table.add_global_secondary_index(
            index_name="GSINames",
            partition_key=DynamoDB.Attribute(
                name="FisrtName",
                type=DynamoDB.AttributeType.STRING
            ),
            sort_key=DynamoDB.Attribute(
                name="LastName",
                type=DynamoDB.AttributeType.STRING
            ),
            read_capacity=10,
            write_capacity=30
        )
           
    def create_apigateway_customers(self):
        #Creación de la API para administración de clientes: Busqueda, alta, bajas y moficiaciones
        api = ApiGateway.RestApi(
            self,
            'api-cashtoday-customers',
            description='REST API para clientes Cash Today'
        )

        customers_integration = ApiGateway.LambdaIntegration(self.lambda_function)
        
        resource_health = api.root.add_resource("health")
        resource_health.add_method(
            "GET",
            customers_integration,
            #auth
        )
        
        resource_customers = api.root.add_resource("customers")
        resource_customers.add_method(
            "GET",
            customers_integration,
            #auth
        )

        resource_customer = api.root.add_resource("customer")
        resource_customer.add_method(
            "GET",
            customers_integration,
            #auth
        )
        resource_customer.add_method(
            "POST",
            customers_integration,
            #auth
        )
        resource_customer.add_method(
            "PATCH",
            customers_integration,
            #auth
        )
        resource_customer.add_method(
            "DELETE",
            customers_integration,
            #auth
        )
    


