#!/usr/bin/env python3

from aws_cdk import core

from event_driven_with_eventbridge.event_driven_with_eventbridge_stack import EventDrivenWithEventbridgeStack


app = core.App()
EventDrivenWithEventbridgeStack(app, "event-driven-with-eventbridge")

app.synth()
