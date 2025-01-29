"""
File Name: lorawan.py
Original Autor: Mauro Riva
Acquisition Date: 29/10/2024
Original Source: https://github.com/lemariva/uPyLoRaWAN/blob/LoRaWAN/sx127x.py
Description: Script for ABP join communications using LoRaWAN. Encrypts and sends
             packets over LoRaWAN.
"""


from loraWan.encryption_aes import AES
from loraWan import radio
import ubinascii
import time
from random import randint
import os

__DEBUG__ = True

ttn_config = {
    'device_address': bytearray([0x27, 0xFD, 0xF5, 0xB6]),
    'network_key': bytearray(
        [0x28, 0x85, 0xC8, 0xCC, 0xAF, 0xE8, 0x9C, 0xF7, 0x4F, 0x78, 0x50, 0xF1, 0xFE, 0x7B, 0xF2, 0x82]),
    'app_key': bytearray(
        [0x53, 0xEA, 0xE4, 0xAD, 0xC5, 0x53, 0x0D, 0x18, 0xA4, 0x1C, 0x37, 0xDC, 0x85, 0x68, 0x2C, 0x32])
}

frame_counter_file = "frame_counter.txt"

REG_DIO_MAPPING_1 = 0x40
fport = 1

# Frequency plans of TTN for Europe: https://www.thethingsnetwork.org/docs/lorawan/frequency-plans/
uplink_ch = [868100, 868300, 868500,
             867100, 867300, 867500,
             867700, 867900]


downlink_ch = 869525


def save_frame_counter(fc):
    """Save the value of the Frame Counter to a file"""
    try:
        with open(frame_counter_file, 'w') as f:
            f.write(str(fc))
        if __DEBUG__:
            print(f"Frame Counter saved: {fc}")
    except Exception as e:
        print(f"Error saving Frame Counter: {e}")


def load_frame_counter():
    """Loads the Frame Counter value from a file"""
    try:
        if frame_counter_file in os.listdir():
            with open(frame_counter_file, 'r') as f:
                fc = int(f.read())
                if __DEBUG__:
                    print(f"Frame Counter loaded: {fc}")
                return fc
        else:
            return 0
    except Exception as e:
        print(f"Error loading Frame Counter: {e}")
        return 0


frame_counter = load_frame_counter()


def send_data(msg):
    global frame_counter

    shuffle_freq = uplink_ch[randint(0, 7)]
    modem.configure({'freq_khz': shuffle_freq})

    print(f"Sending on {shuffle_freq} Khz")

    buf = lorawan_pkt(msg, len(msg))

    modem.send(buf)

    frame_counter += 1
    save_frame_counter(frame_counter)
    time.sleep(1)


def lorawan_pkt(data, data_length):
    global frame_counter

    enc_data = bytearray(data_length)
    lora_pkt = bytearray(9)

    enc_data[0:data_length] = data[0:data_length]

    aes = AES(
        ttn_config['device_address'],
        ttn_config['app_key'],
        ttn_config['network_key'],
        frame_counter
    )

    enc_data = aes.encrypt(enc_data)
    lora_pkt[0] = REG_DIO_MAPPING_1
    lora_pkt[1] = ttn_config['device_address'][3]
    lora_pkt[2] = ttn_config['device_address'][2]
    lora_pkt[3] = ttn_config['device_address'][1]
    lora_pkt[4] = ttn_config['device_address'][0]
    lora_pkt[5] = 0x00
    lora_pkt[6] = frame_counter & 0x00FF
    lora_pkt[7] = (frame_counter >> 8) & 0x00FF
    lora_pkt[8] = fport
    lora_pkt_len = 9

    if __DEBUG__:
        print("PHYPayload", ubinascii.hexlify(lora_pkt))

    lora_pkt[lora_pkt_len: lora_pkt_len + data_length] = enc_data[0:data_length]

    if __DEBUG__:
        print("PHYPayload with FRMPayload", ubinascii.hexlify(lora_pkt))

    lora_pkt_len += data_length

    mic = bytearray(4)
    mic = aes.calculate_mic(lora_pkt, lora_pkt_len, mic)

    lora_pkt[lora_pkt_len: lora_pkt_len + 4] = mic[0:4]

    lora_pkt_len += 4

    if __DEBUG__:
        print("PHYPayload with FRMPayload + MIC", ubinascii.hexlify(lora_pkt))

    return lora_pkt


modem = radio.get_modem()
