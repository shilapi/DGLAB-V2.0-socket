import websocket, json
from model import dglab_message
from handler import *
import pydglab
import asyncio
import logging
import yaml

with open("./config.yaml") as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        logging.error(exc)

logging.basicConfig(
    format="%(module)s [%(levelname)s]: %(message)s",
    level=logging.DEBUG if config["Debug"] else logging.INFO,
)

qrRaw = config["QR_Content"]

store = local_data(clientId=qrRaw[82:])
store.limitA = int(config["Channel_A_limit"])
store.limitB = int(config["Channel_B_limit"])


def on_message(ws, message):
    message = json.loads(message)
    message = dglab_message(
        type_=message["type"],
        clientId=message["clientId"],
        targetId=message["targetId"],
        message=message["message"],
    )
    if message.type_ == "heartbeat":
        heartbeat(ws, message, store)
        return
    elif message.type_ == "bind":
        bind(ws, message, store)
        strength_upload(ws, f"strength-0+0+{store.limitB}+{store.limitA}", store=store)
        return
    elif message.type_ == "msg":
        msg(ws, message, store)
    elif message.type_ == "break":
        break_(ws, message)
    elif message.type_ == "error":
        error(ws, message)
    response(ws, "feedback-0", store)


def on_error(ws, error):
    logging.error(error)


def on_close(ws, close_status_code, close_msg):
    logging.info("WS connection closed")


def on_open(ws):
    logging.info("WS connection opened")


def run_websocket():
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(
        qrRaw[58:],
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    ws.run_forever(
        reconnect=5
    )


async def main():
    dglab = pydglab.dglab()
    await dglab.create()

    async def dglab_handler():
        while True:
            if store.channelAStrength > store.limitA or store.channelAStrength < 0:
                store.channelAStrength = 0
            if store.channelBStrength > store.limitB or store.channelBStrength < 0:
                store.channelBStrength = 0
            await dglab.set_strength_sync(
                store.channelAStrength, store.channelBStrength
            )
            await dglab.set_wave_set_sync(store.channelAWave, store.channelBWave)
            await asyncio.sleep(0.1)

    dglab_task = asyncio.create_task(dglab_handler())

    # Run the synchronous function run_websocket in the event loop without blocking
    loop = asyncio.get_running_loop()
    websocket_task = loop.run_in_executor(None, run_websocket)

    # Wait for both tasks to complete
    await asyncio.gather(dglab_task, websocket_task)


if __name__ == "__main__":
    asyncio.run(main())
