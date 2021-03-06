import json
import logging
import datetime
import os
import random
import boto3
import uuid
from botocore.exceptions import ClientError


class GlobalArgs:
    OWNER = "Mystique"
    ENVIRONMENT = "production"
    MODULE_NAME = "eventbridge_data_producer"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    MAX_MSGS_TO_PRODUCE = int(os.getenv("MAX_MSGS_TO_PRODUCE", 5))
    EVENT_BUS_NAME = os.getenv("EVENT_BUS_NAME")


def set_logging(lv=GlobalArgs.LOG_LEVEL):
    logging.basicConfig(level=lv)
    logger = logging.getLogger()
    logger.setLevel(lv)
    return logger


def _rand_coin_flip():
    r = False
    if os.getenv("TRIGGER_RANDOM_FAILURES", True):
        if random.randint(1, 100) > 90:
            r = True
    return r


def _gen_uuid():
    """ Generates a uuid string and return it """
    return str(uuid.uuid4())


def send_to_bus(client, evnt_payload):
    if not evnt_payload:
        evnt_payload = []
    try:
        LOG.debug(
            f'{{"evnt_payload":{evnt_payload}}}')
        resp = client.put_events(Entries=[evnt_payload])
    except ClientError as e:
        LOG.error(f"ERROR:{str(e)}")
        raise e
    else:
        return resp


LOG = set_logging()
client = boto3.client("events")


def lambda_handler(event, context):
    resp = {"status": False}
    LOG.debug(f"Event: {json.dumps(event)}")

    _rand_user_name = ["Aarakocra", "Aasimar", "Beholder", "Bugbear", "Centaur", "Changeling", "Deep Gnome", "Deva", "Lizardfolk", "Loxodon", "Mind Flayer",
                       "Minotaur", "Orc", "Shardmind", "Shifter", "Simic Hybrid", "Tabaxi", "Yuan-Ti"]

    _rand_category = ["Books", "Games", "Mobiles", "Groceries", "Shoes", "Stationaries", "Laptops",
                      "Tablets", "Notebooks", "Camera", "Printers", "Monitors", "Speakers", "Projectors", "Cables", "Furniture"]

    _rand_evnt_types = ["sales-events", "inventory-events"]

    try:
        msg_cnt = 0
        p_cnt = 0
        while context.get_remaining_time_in_millis() > 100:
            _s = round(random.random() * 100, 2)
            evnt_body = {
                "request_id": _gen_uuid(),
                "name": random.choice(_rand_user_name),
                "category": random.choice(_rand_category),
                "store_id": f"store_{random.randint(1, 5)}",
                "new_order": True,
                "sales": _s,
                "contact_me": "github.com/miztiik"
            }

            # Randomly make the order type return
            if bool(random.getrandbits(1)):
                evnt_body.pop("new_order", None)
                evnt_body["is_return"] = True

            evnt_payload = {
                "Time": datetime.datetime.now(),
                "Source": "Miztiik-Automation-Data-Producer",
                "DetailType": random.choice(_rand_evnt_types),
                "EventBusName": os.getenv("EVENT_BUS_NAME")
            }

            # Randomly remove store_id from message
            if _rand_coin_flip():
                evnt_body.pop("store_id", None)
                evnt_body["bad_msg"] = True
                p_cnt += 1

            evnt_payload["Detail"] = json.dumps(evnt_body)

            send_to_bus(
                client,
                evnt_payload
            )
            msg_cnt += 1
            LOG.debug(
                f'{{"remaining_time":{context.get_remaining_time_in_millis()}}}')
            if msg_cnt >= GlobalArgs.MAX_MSGS_TO_PRODUCE:
                break
            # End of while
        resp["tot_msgs"] = msg_cnt
        resp["bad_msgs"] = p_cnt
        resp["status"] = True
        LOG.info(f'{{"resp":{json.dumps(resp)}}}')

    except Exception as e:
        LOG.error(f"ERROR:{str(e)}")
        resp["error_message"] = str(e)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": resp
        })
    }
