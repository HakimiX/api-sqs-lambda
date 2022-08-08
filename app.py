#!/usr/bin/env python3
import os

import aws_cdk as cdk

from api_sqs_lambda.api_sqs_lambda_stack import ApiSqsLambdaStack


app = cdk.App()
ApiSqsLambdaStack(app, "ApiSqsLambdaStack")

app.synth()
