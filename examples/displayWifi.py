"""
File Name: displayWifi.py
Author: Irene Pereda Serrano
Created On: 17/04/2024
Description: This file is an example about how to print WiFi information on the OLED screen
"""

from oled import oledSetup
from wifi import connectWifi
import os
from dotenv import load_dotenv

load_dotenv()

WIFI_SSID = os.getenv("WIFI_SSID")
WIFI_PASSWORD = os.getenv("WIFI_PASSWORD")

oled = oledSetup.oled

if connectWifi.connect_wifi(WIFI_SSID, WIFI_PASSWORD):
    oled.fill(0)
    oled.text('CONECTADO A IP:', 0, 0)
    oled.text('HELLO WiFi ESP32', 0, 55)
    oled.show()
