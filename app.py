#!/usr/bin/env python3

from aws_cdk import core

from stacks.back_end.eventbus_stack.eventbus_stack import EventBusStack
from stacks.back_end.serverless_eventbridge_producer_stack.serverless_eventbridge_producer_stack import ServerlessEventBridgeProducerStack
from stacks.back_end.serverless_eventbridge_consumer_stack.serverless_eventbridge_consumer_stack import ServerlessEventBridgeConsumerStack


app = core.App()


# EventBus to receive orders from producers
orders_eventbus_stack = EventBusStack(
    app,
    f"{app.node.try_get_context('project')}-orders-eventbus-stack",
    stack_log_level="INFO",
    description="Miztiik Automation: EventBus to receive orders from producers"
)


# Produce Customer Order Messages
orders_event_producer_stack = ServerlessEventBridgeProducerStack(
    app,
    f"{app.node.try_get_context('project')}-orders-producer-stack",
    stack_log_level="INFO",
    orders_bus=orders_eventbus_stack.orders_bus,
    description="Miztiik Automation: Produce Customer Order Events Messages"
)

# Consume messages from SQS
orders_event_consumer_stack = ServerlessEventBridgeConsumerStack(
    app,
    f"{app.node.try_get_context('project')}-orders-consumer-stack",
    stack_log_level="INFO",
    orders_bus=orders_eventbus_stack.orders_bus,
    description="Miztiik Automation: Consume Customer Order Events Messages"
)

# Stack Level Tagging
_tags_lst = app.node.try_get_context("tags")

if _tags_lst:
    for _t in _tags_lst:
        for k, v in _t.items():
            core.Tags.of(app).add(k, v, apply_to_launched_instances=True)


app.synth()
