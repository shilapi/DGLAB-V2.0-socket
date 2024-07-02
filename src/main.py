import websocket
import _thread
import time
import rel, json
from model import dglab_message
from handler import *
import pydglab
from pydglab import model
import asyncio

qrRaw = "https://www.dungeon-lab.com/app-download.php#DGLAB-SOCKET#wss://ws.dungeon-lab.cn/7f6238c1-fed1-41b0-a697-4d68ce914cfc"

store = local_data(clientId=qrRaw[82:])

dglab = pydglab.dglab()
asyncio.run(dglab.create())

def converter_to_waveset(self, strength: int, freq: int) -> tuple[int, int, int]:
    """
    Convert strength and frequency to the wave set format.
    """
    wave1 = int(((freq - 10) / 230) * 990 + 10 - wave2)
    wave2 = int(strength / 5)
    wave3 = strength

    return wave1, wave2, wave3

async def dglab_handler():
    await dglab.set_strength_sync(store.channelAStrength, store.channelBStrength)
    await dglab.set_wave_set_sync

async def dglab_wave_handler(wave: list[(tuple[int, int, int])]):
    for i in wave:

def on_message(ws, message):
    #print(message)
    message = json.loads(message)
    message = dglab_message(type_=message['type'], clientId=message['clientId'], targetId=message['targetId'], message=message['message'])
    if message.type_ == "heartbeat":
        heartbeat(ws, message, store)
        return
    elif message.type_ == "bind":
        bind(ws, message, store)
        strength_upload(ws, f"strength-0+0+{store.limitB}+{store.limitA}", store=store)
        return
    elif message.type_ == "msg":
        msg(ws, message)
    elif message.type_ == "break":
        break_(ws, message)
    elif message.type_ == "error":
        error(ws, message)
    response(ws, 'feedback-0', store)

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    print("Opened connection")
    

if __name__ == "__main__":
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(qrRaw[58:],
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    ws.run_forever(dispatcher=rel, reconnect=5)  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()