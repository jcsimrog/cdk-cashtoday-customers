import aws_cdk as core
import aws_cdk.assertions as assertions

from cash_today_customers.cash_today_customers_stack import CashTodayCustomersStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cash_today_customers/cash_today_customers_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CashTodayCustomersStack(app, "cash-today-customers")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
