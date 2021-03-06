from aws_cdk import core
from aws_cdk import aws_events as _evnts


class GlobalArgs:
    """
    Helper to define global statics
    """

    OWNER = "MystiqueAutomation"
    ENVIRONMENT = "production"
    REPO_NAME = "event-driven-with-eventbridge"
    SOURCE_INFO = f"https://github.com/miztiik/{REPO_NAME}"
    VERSION = "2021_03_06"
    MIZTIIK_SUPPORT_EMAIL = ["mystique@example.com", ]


class EventBusStack(core.Stack):

    def __init__(
        self,
        scope: core.Construct,
        construct_id: str,
        stack_log_level: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        id_prefix_str = f"evntDriven"

        self.orders_bus = _evnts.EventBus(
            self,
            "ordersEventBus",
            event_bus_name="store-orders"
        )

        self.orders_bus.apply_removal_policy(
            core.RemovalPolicy.DESTROY
        )

        ###########################################
        ################# OUTPUTS #################
        ###########################################
        output_0 = core.CfnOutput(
            self,
            "AutomationFrom",
            value=f"{GlobalArgs.SOURCE_INFO}",
            description="To know more about this automation stack, check out our github page."
        )

        output_2 = core.CfnOutput(
            self,
            "msgConsumer",
            value=f"https://console.aws.amazon.com/lambda/home?region={core.Aws.REGION}#/functions/{self.orders_bus.event_bus_name}",
            description="Orders EventBus"
        )
