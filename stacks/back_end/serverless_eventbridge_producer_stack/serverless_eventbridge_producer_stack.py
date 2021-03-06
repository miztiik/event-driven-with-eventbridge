from aws_cdk import aws_cloudwatch as _cw
from aws_cdk import aws_iam as _iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_logs as _logs
from aws_cdk import core


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


class ServerlessEventBridgeProducerStack(core.Stack):

    def __init__(
        self,
        scope: core.Construct,
        construct_id: str,
        stack_log_level: str,
        orders_bus,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ################################################
        #######                                  #######
        #######     EventBridge Data Producer    #######
        #######                                  #######
        ################################################

        # Read Lambda Code
        try:
            with open("stacks/back_end/serverless_eventbridge_producer_stack/lambda_src/eventbridge_data_producer.py",
                      encoding="utf-8",
                      mode="r"
                      ) as f:
                data_producer_fn_code = f.read()
        except OSError:
            print("Unable to read Lambda Function Code")
            raise

        data_producer_fn = _lambda.Function(
            self,
            "eventBridgeDataProducerFn",
            function_name=f"data_producer_fn",
            description="Produce data events and push to EventBridge",
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.InlineCode(
                data_producer_fn_code),
            handler="index.lambda_handler",
            timeout=core.Duration.seconds(5),
            reserved_concurrent_executions=1,
            environment={
                "LOG_LEVEL": f"{stack_log_level}",
                "APP_ENV": "Production",
                "MAX_MSGS_TO_PRODUCE": "5",
                "EVENT_BUS_NAME": f"{orders_bus.event_bus_name}",
                "TRIGGER_RANDOM_FAILURES": "True"
            }
        )

        # Grant our Lambda Producer privileges to write to EventBridge
        orders_bus.grant_put_events(data_producer_fn)

        data_producer_fn_version = data_producer_fn.latest_version
        data_producer_fn_version_alias = _lambda.Alias(
            self,
            "dataProducerFnAlias",
            alias_name="MystiqueAutomation",
            version=data_producer_fn_version
        )

        # Create Custom Loggroup for Producer
        data_producer_lg = _logs.LogGroup(
            self,
            "dataProducerLogGroup",
            log_group_name=f"/aws/lambda/{data_producer_fn.function_name}",
            removal_policy=core.RemovalPolicy.DESTROY,
            retention=_logs.RetentionDays.ONE_DAY
        )

        # Restrict Produce Lambda to be invoked only from the stack owner account
        data_producer_fn.add_permission(
            "restrictLambdaInvocationToOwnAccount",
            principal=_iam.AccountRootPrincipal(),
            action="lambda:InvokeFunction",
            source_account=core.Aws.ACCOUNT_ID
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

        output_1 = core.CfnOutput(
            self,
            "eventBridgeDataProducer",
            value=f"https://console.aws.amazon.com/lambda/home?region={core.Aws.REGION}#/functions/{data_producer_fn.function_name}",
            description="Produce data events and push to EventBridge Queue."
        )

