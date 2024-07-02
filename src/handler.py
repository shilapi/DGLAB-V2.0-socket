from model import *
from utils import *

from websocket import WebSocketApp
import json, logging


def bind(client: WebSocketApp, message: dglab_message, store: local_data):
    if message.message == "targetId":
        logging.debug("Bind recieved")

        store.targetId = message.clientId

        reply = {
            "type": "bind",
            "clientId": store.clientId,
            "targetId": store.targetId,
            "message": "DGLAB",
        }

        client.send(json.dumps(reply))
    elif message.message == "200":
        logging.info("Bind to remote success")
    elif int(message.message) in code.keys():
        logging.error(code[message][0])


def heartbeat(client: WebSocketApp, message: dglab_message, store: local_data):
    message = int(message.message)
    if message == 200:
        logging.debug("Heartbeating...")
        client.send(
            json.dumps(
                {
                    "type": "heartbeat",
                    "clientId": store.clientId,
                    "targetId": store.targetId,
                    "message": 200,
                }
            )
        )
        return
    elif message in code.keys():
        logging.error(code[message][0])
        return
    else:
        logging.error("Unknown heartbeat message: " + message)
        raise Exception("Unknown heartbeat message: " + message)


def msg(client: WebSocketApp, message: dglab_message, store: local_data):
    messageType = message.message.split("-")[0]
    messageContent = message.message.split("-")[1]
    if messageType == "strength":
        _strength(messageContent, store)
    elif messageType == "pulse":
        _pulse(messageContent, store)
    elif messageType == "clear":
        _clear(messageContent, store)
    pass


def strength_upload(client: WebSocketApp, message: str, store: local_data):
    reply = {
        "type": "msg",
        "clientId": store.clientId,
        "targetId": store.targetId,
        "message": message,
    }
    client.send(json.dumps(reply))
    pass


def break_(client: WebSocketApp, message: dglab_message):
    raise Exception("Connection broken")


def error(client: WebSocketApp, message: dglab_message):
    pass


def response(client: WebSocketApp, message: str, store: local_data):
    reply = {
        "type": "msg",
        "clientId": store.clientId,
        "targetId": store.targetId,
        "message": message,
    }
    client.send(json.dumps(reply))
    pass


def _strength(message: str, store: local_data):
    strenthDataRaw = message.split("+")
    channel = strenthDataRaw[0]
    strength_mode = strenthDataRaw[1]
    strength = strenthDataRaw[2]
    logging.debug(
        "Strength changing: " + channel + "--" + strength_mode + "--" + strength
    )
    if channel == "1":
        if strength_mode == "0":
            if (
                store.channelAStrength - int(strength) > 0
                and store.channelAStrength - int(strength) < store.limitA
            ):
                store.channelAStrength = store.channelAStrength - int(strength)
        elif strength_mode == "1":
            if (
                store.channelAStrength + int(strength) > 0
                and store.channelAStrength + int(strength) < store.limitA
            ):
                store.channelAStrength = store.channelAStrength + int(strength)
        elif strength_mode == "2":
            if int(strength) > 0 and int(strength) < store.limitA:
                store.channelAStrength = int(strength)
    elif channel == "2":
        if strength_mode == "0":
            if (
                store.channelBStrength - int(strength) > 0
                and store.channelBStrength - int(strength) < store.limitB
            ):
                store.channelBStrength = store.channelBStrength - int(strength)
        elif strength_mode == "1":
            if (
                store.channelBStrength + int(strength) > 0
                and store.channelBStrength + int(strength) < store.limitB
            ):
                store.channelBStrength = store.channelBStrength + int(strength)
        elif strength_mode == "2":
            if store.channelBStrength > 0 and store.channelBStrength < store.limitB:
                store.channelBStrength = int(strength)
    pass


def _pulse(message: str, store: local_data):
    channel = message.split(":")[0]
    wave_set = json.loads(message.split(":")[1])
    logging.debug("Pulse changing: " + channel + "--" + str(wave_set))
    dglab_wave_handler(store, wave_set, channel)
    pass


def _clear(message: str, store: local_data):
    channel = message
    pass
