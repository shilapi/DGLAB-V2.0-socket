from model import *

from websocket import WebSocketApp
import json

def bind(client: WebSocketApp, message: dglab_message, store: local_data):
    if message.message == "targetId":
        print("Bind recieved")
        
        store.targetId = message.clientId
        
        reply = {
            'type': 'bind',
            'clientId': store.clientId,
            'targetId': store.targetId,
            'message': 'DGLAB'
        }
        
        client.send(json.dumps(reply))
    elif message.message == "200":
        print("Bind success")
    elif int(message.message) in code.keys():
        print(code[message][0])

def heartbeat(client: WebSocketApp, message: dglab_message, store: local_data):
    message = int(message.message)
    if message == 200:
        print("Heartbeating...")
        client.send(json.dumps({
            'type': 'heartbeat',
            'clientId': store.clientId,
            'targetId': store.targetId,
            'message': 200
        }))
        return
    elif message in code.keys():
        print(code[message][0])
        return
    else:
        print("Unknown heartbeat message: " + message)
        raise Exception("Unknown heartbeat message: " + message)

def msg(client: WebSocketApp, message: dglab_message):
    messageType = message.message.split("-")[0]
    messageContent = message.message.split("-")[1]
    if messageType == "strength":
        _strength(messageContent)
    elif messageType == "pulse":
        _pulse(messageContent)
    elif messageType == "clear":
        _clear(messageContent)
    pass

def strength_upload(client: WebSocketApp, message: str, store: local_data):
    reply = {
        'type': 'msg',
        'clientId': store.clientId,
        'targetId': store.targetId,
        'message': message
    }
    client.send(json.dumps(reply))
    pass

def break_(client: WebSocketApp, message: dglab_message):
    raise Exception("Connection broken")

def error(client: WebSocketApp, message: dglab_message):
    pass

def response(client: WebSocketApp, message: str, store: local_data):
    reply = {
        'type': 'msg',
        'clientId': store.clientId,
        'targetId': store.targetId,
        'message': message
    }
    client.send(json.dumps(reply))
    pass

def _strength(message: str):
    strenthDataRaw = message.split("+")
    channel = strenthDataRaw[0]
    strength_mode = strenthDataRaw[1]
    strength = strenthDataRaw[2]
    print("Strength changing: " + channel + "--" + strength_mode + "--" + strength)
    pass

def _pulse(message: str):
    channel = message.split(":")[0]
    wave_set = json.dumps(message.split(":")[1])
    print("Pulse changing: " + channel +"--"+ str(wave_set))
    pass

def _clear(message: str):
    channel = message
    pass
