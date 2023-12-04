#!/usr/bin/env python3
import os
import aws_cdk as cdk
from stacks.cash_today_customers_stack import CashTodayCustomersStack


app = cdk.App()
cashtoday_customers_stack = CashTodayCustomersStack(
    app, 
    "CashTodayCustomersStack",
    env={
        "account": os.getenv("CDK_DEFAULT_ACCOUNT"),
        "region": os.getenv("CDK_DEFAULT_REGION"),
    }
)

cdk.Tags.of(cashtoday_customers_stack).add("Environment", "Development")
cdk.Tags.of(cashtoday_customers_stack).add("RepositoryUrl", "https://github.com/jcrojas/aws-cdk-cashtoday-customers")
cdk.Tags.of(cashtoday_customers_stack).add("Source", "aws-cdk-cashtoday-customers")
cdk.Tags.of(cashtoday_customers_stack).add("Owner", "Juan Carlos Rojas Hernández")

app.synth()
