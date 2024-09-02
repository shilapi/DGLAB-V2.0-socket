from model import *
from PIL import ImageGrab
from pyzbar.pyzbar import decode

import yaml, logging

with open("./config.yaml") as stream:
    try:
        config = yaml.safe_load(stream)
        Wave_convert_ratio = int(config["Wave_convert_ratio"])
    except yaml.YAMLError as exc:
        logging.error(exc)


def convert_to_waveset(strength: int, freq: int) -> tuple[int, int, int]:
    ms_per_wave = 1000 / freq
    X = int(ms_per_wave / Wave_convert_ratio)
    Y = int(ms_per_wave - X)
    Z = int(strength / 5)
    return X, Y, Z


def dglab_wave_handler(
    store: local_data, wave: list[(tuple[int, int, int])], channel: str
):
    waveset = []
    for i in wave:
        # 对每组波形进行切分，以1:4比例丢弃后3/4
        freq = int(i[0:2], 16)
        strength = int(i[8:10], 16)
        waveset.append(convert_to_waveset(strength, freq))
    if channel == "A":
        store.channelAWave = waveset
    elif channel == "B":
        store.channelBWave = waveset
    return

def decode_qr_code(image):
    decoded_objects = decode(image)
    qr_data = [obj.data.decode('utf-8') for obj in decoded_objects]
    return qr_data

def find_qr_code():
    qrcodes = decode_qr_code(ImageGrab.grab())
    if len(qrcodes) < 1:
        return ""
    qrcode = ""
    for i in range(len(qrcodes)):
        if qrcodes[i].find("wss://") != -1 or qrcodes[i].find("ws://") != -1:
            qrcode = qrcodes[i]
            break
    
    return qrcode