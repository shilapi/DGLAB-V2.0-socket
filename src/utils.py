from model import *

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
        logging.debug("wave: " + i)
        logging.debug("freq: " + str(freq))
        logging.debug("strength: " + str(strength))
        waveset.append(convert_to_waveset(strength, freq))
    if channel == "A":
        store.channelAWave = waveset
    elif channel == "B":
        store.channelBWave = waveset
    logging.debug("waveset: " + str(waveset))
    return
