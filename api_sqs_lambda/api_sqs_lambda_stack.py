from email.mime import base
from sys import api_version
from aws_cdk import (
    aws_sqs as sqs,
    aws_iam as iam,
    aws_apigateway as apigw,
    aws_lambda as _lambda,
    aws_lambda_event_sources as lambda_event_source,
    Stack,
    Aws
)
from constructs import Construct


class ApiSqsLambdaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        """
        SQS Queue
        """
        queue = sqs.Queue(self, "SQSQueue")

        """
        API Gateway IAM Role 
        Permission to call SQS (to enqueue)
        """
        rest_api_role = iam.Role(
            self, "RestAPIRole",
            assumed_by=iam.ServicePrincipal('apigateway.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSQSFullAccess')]
        )

        """
        API Gateway
        """
        base_api = apigw.RestApi(self, 'ApiGW', rest_api_name='testApi')
        base_api.root.add_method('ANY')

        # Resource
        api_resource = base_api.root.add_resource('example')

        # API Integration response object
        # You must setup at least one integration response, and make it the default
        # response, to pass the result returned from the backend to the client.
        integration_response = apigw.IntegrationResponse(
            status_code='200',
            response_templates={
                'application/json': ''
            }
        )

        # Integration option object
        api_integration_options = apigw.IntegrationOptions(
            credentials_role=rest_api_role,
            integration_responses=[integration_response],
            request_templates={
                'application/json': 'Action=SendMessage&MessageBody=$input.body'
            },
            passthrough_behavior=apigw.PassthroughBehavior.NEVER,
            request_parameters={
                "integration.request.header.Content-Type": "'application/x-www-form-urlencoded'"
            }
        )

        # Integration Object for SQS 
        api_resource_sqs_integration = apigw.AwsIntegration(
            service='sqs',
            integration_http_method='POST',
            path="{}/{}".format(Aws.ACCOUNT_ID, queue.queue_name),
            options=api_integration_options
        )

        # Method response object
        method_response = apigw.MethodResponse(status_code='200')

        # Add the API Gateway integration to the 'example' resource 
        api_resource.add_method(
            'POST',
            api_resource_sqs_integration,
            method_responses=[method_response]
        )

        """
        Lambda Function 
        Triggered by the SQS queue 
        """
        sqs_lambda = _lambda.Function(
            self, 'SQSTriggerLambda',
            handler='lambda.handler',
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset('lambda')
        )

        # Create an SQS Event source for Lambda
        sqs_event_source = lambda_event_source.SqsEventSource(queue)

        # Add SQS Event source to Lambda
        sqs_lambda.add_event_source(sqs_event_source)