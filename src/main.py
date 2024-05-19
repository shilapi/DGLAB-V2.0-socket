import websocket
import _thread
import time
import rel, json
from model import dglab_message


def on_message(ws, message):
    print(message)
    message = json.loads(message)
    message = dglab_message(type_=message['type'], clientId=message['clientId'], targetId=message['targetId'], message=message['message'])
    if message.type_ == "heartbeat":
        heartbeat(ws, message.message)
    elif message.type_ == "bind":
        bind(ws, message)

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    print("Opened connection")
    

targetId = "e08964f0-0310-9220-0246-fb76d29484b4"

def heartbeat(client, message):
    message = int(message)
    if message == 200:
        print("Heartbeat received")
        return True
    else:
        print("Heartbeat failed")
        return False

def bind(client, message:dglab_message):
    if message.message == "targetId":
        print("Bind recieved")
        
        clientId = message.clientId
        
        reply = {
            'type': 'bind',
            'clientId': clientId,
            'targetId': targetId,
            'message': 'DGLAB'
        }
        
        client.send(json.dumps(reply))
    elif message == "200":
        print("Bind success")

def msg(client, message:dglab_message):
    pass


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://ws.dungeon-lab.cn/282ffd66-7b8d-4309-bab3-80e4d4aa677b",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)

    ws.run_forever(dispatcher=rel, reconnect=5)  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()