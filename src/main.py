import websocket, json
from model import dglab_message
from handler import *
import pydglab
import asyncio
import logging
import yaml
import time
from rich.table import Table
from rich.live import Live

with open("./config.yaml") as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        logging.error(exc)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(module)s [%(levelname)s]: %(message)s"
)

if config["Debug"]:
    fh = logging.FileHandler("debug.log")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
sh.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(sh)

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
        logger.info("Heartbeat received")
        return
    elif message.type_ == "bind":
        bind(ws, message, store)
        strength_upload(ws, f"strength-0+0+{store.limitB}+{store.limitA}", store=store)
        logger.info("Bind successed")
        return
    elif message.type_ == "msg":
        msg(ws, message, store)
        strength_upload(ws, f"strength-{store.channelAStrength}+{store.channelBStrength}+{store.limitB}+{store.limitA}", store=store)
    elif message.type_ == "break":
        break_(ws, message)
    elif message.type_ == "error":
        error(ws, message)
    response(ws, "feedback-0", store)


def on_error(ws, error):
    logger.error(error)


def on_close(ws, close_status_code, close_msg):
    logger.info("WS connection closed")


def on_open(ws):
    logger.info("WS connection opened")


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


def generate_table():
    table = Table()
    table.add_column('Key')
    table.add_column('Value')
    
    table.add_row('Channel A Strength', str(store.channelAStrength))
    table.add_row('Channel B Strength', str(store.channelBStrength))
    table.add_row('Channel A Limit', str(store.limitA))
    table.add_row('Channel B Limit', str(store.limitB))
    table.add_row('Channel A Wave', str(store.channelAWave))
    table.add_row('Channel B Wave', str(store.channelBWave))
    table.caption = f'Client ID: {store.clientId} \n Target ID: {store.targetId}'
    return table


async def loopAll(dglab: pydglab.dglab):
    with Live(generate_table(), refresh_per_second=10) as live:
        while True:
            time.sleep(0.1)
            live.update(generate_table())
            if store.channelAStrength > store.limitA or store.channelAStrength < 0:
                store.channelAStrength = 0
            if store.channelBStrength > store.limitB or store.channelBStrength < 0:
                store.channelBStrength = 0
            await dglab.set_strength_sync(
                store.channelAStrength, store.channelBStrength
            )
            await dglab.set_wave_set_sync(store.channelAWave, store.channelBWave)
            logger.debug("Strength and wave set updated")

async def main():
    dglab = pydglab.dglab()
    await dglab.create()

    # Run the synchronous function run_websocket in the event loop without blocking
    loop = asyncio.get_running_loop()
    websocket_task = loop.run_in_executor(None, run_websocket)

    # Wait for both tasks to complete
    await asyncio.gather(loopAll(dglab), websocket_task)


if __name__ == "__main__":
    asyncio.run(main())
