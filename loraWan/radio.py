from machine import SPI, Pin
from lora.sx126x import SX1262
import heltec

def get_modem():

# These settings are for LoRa P2P
#     lora_cfg = {
#         "freq_khz": 869000,
#         "sf": 7,
#         "bw": "125",  # kHz
#         "coding_rate": 5,
#         "preamble_len": 8,
#         "output_power": 14,  # dBm
#         "syncword":  0x1424
#         "pa_ramp_us": 80
#      }

#These settings are for LoraWan
    lora_cfg = {
        "freq_khz": 868100,
        "sf": 7,
        "bw": "125",  # kHz
        "coding_rate": 8, # Works only with 4/8
        "preamble_len": 8,
        "output_power": 14,  # dBm
        "syncword":  0x3444 # This setting is important for LoraWan
     }

    # Set up correct spi pins for T-deck
    lora_spi = SPI(1, baudrate=8000000, sck=Pin(heltec.LORA_SCK), mosi=Pin(heltec.LORA_MOSI), miso=Pin(heltec.LORA_MISO))

    return SX1262(spi = lora_spi,
                  cs = Pin(heltec.LORA_CS),
                  busy= Pin(heltec.LORA_BUSY),  # Required
                  dio1=Pin(heltec.LORA_IRQ),   # Optional, recommended
                  reset=Pin(heltec.LORA_RST),  # Optional, recommended
                  dio3_tcxo_millivolts=3300,
                  lora_cfg=lora_cfg)